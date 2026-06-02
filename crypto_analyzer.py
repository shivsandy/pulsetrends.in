import json
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ANALYSIS_FILE = os.path.join(DATA_DIR, "crypto_analysis.json")
CRYPTO_FILE = os.path.join(DATA_DIR, "crypto_data.json")

FALLBACK_FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-32b:free",
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-chat:free",
    "microsoft/phi-4:free",
]

GOOGLE_FREE_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]

_model_health: Dict[str, dict] = {}


def _health_key(provider: str, key_index: int, model: str) -> str:
    return f"{provider}:key{key_index}:{model}"


def _record_success(provider: str, key_index: int, model: str, latency: float):
    key = _health_key(provider, key_index, model)
    h = _model_health.get(key)
    if not h:
        h = {"success": 0, "failures": 0, "consecutive": 0, "cooldown": 0.0}
        _model_health[key] = h
    h["success"] += 1
    h["consecutive"] = 0
    h["latency"] = latency


def _record_failure(provider: str, key_index: int, model: str, status_code: Optional[int] = None):
    key = _health_key(provider, key_index, model)
    h = _model_health.get(key)
    if not h:
        h = {"success": 0, "failures": 0, "consecutive": 0, "cooldown": 0.0}
        _model_health[key] = h
    h["failures"] += 1
    h["consecutive"] += 1
    now = time.time()
    if status_code == 429:
        h["cooldown"] = now + 300
    elif status_code and 500 <= status_code < 600:
        h["cooldown"] = now + 180
    else:
        h["cooldown"] = now + 120


def _healthy_models(provider: str, key_index: int, models: List[str]) -> List[str]:
    now = time.time()
    healthy = []
    for model in models:
        key = _health_key(provider, key_index, model)
        h = _model_health.get(key)
        if h and h["cooldown"] > now:
            continue
        score = 1.0
        if h:
            total = h["success"] + h["failures"]
            if total > 0:
                score -= (h["failures"] / total) * 0.5
            score -= h["consecutive"] * 0.2
        healthy.append((max(score, 0.1), model))
    random.shuffle(healthy)
    healthy.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in healthy]


def discover_free_models(api_keys: List[dict]) -> List[str]:
    discovered = set()
    for entry in api_keys:
        try:
            resp = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {entry['key']}"},
                timeout=15,
            )
            if resp.status_code == 200:
                for m in resp.json().get("data", []):
                    pricing = m.get("pricing", {})
                    try:
                        if float(pricing.get("prompt", "1")) == 0.0:
                            mid = m.get("id", "")
                            if not mid.endswith(":free"):
                                mid = mid + ":free"
                            discovered.add(mid)
                    except (ValueError, TypeError):
                        pass
        except Exception:
            pass
        if discovered:
            break
    if discovered:
        sorted_models = sorted(discovered)
        print(f"[Crypto Analyzer] Discovered {len(sorted_models)} free models")
        return sorted_models
    print(f"[Crypto Analyzer] Model discovery failed, using {len(FALLBACK_FREE_MODELS)} fallback models")
    return list(FALLBACK_FREE_MODELS)


ANALYSIS_PROMPT = """Act as a crypto analyst with expertise in airdrop and token risk assessment. Analyze the following project and return ONLY valid JSON.

Name: {name}
Ticker: {ticker}
Category: {category}
Chain: {chain}
Description: {description}
Status: {status}

Return EXACTLY this JSON structure:
{{
  "summary": "Project overview — what it does, its market position, and key value proposition.",
  "market_analysis": "Analysis of market positioning, competition, and growth potential.",
  "sentiment": "bullish",
  "conviction_score": 75,
  "key_drivers": ["Driver 1", "Driver 2", "Driver 3"],
  "risks": ["Risk 1", "Risk 2", "Risk 3"],
  "risk_assessment": {{
    "overall_risk": "medium",
    "smart_contract_risk": "low",
    "team_risk": "medium",
    "market_risk": "medium",
    "regulatory_risk": "low",
    "rug_pull_potential": "low",
    "liquidity_risk": "medium",
    "dilution_risk": "medium"
  }},
  "verdict": "Balanced assessment and outlook for this project."
}}
Important: sentiment must be one of "bullish", "bearish", or "neutral". conviction_score must be 0-100. risk_assessment fields must be one of "low", "medium", or "high". Return ONLY the JSON, no other text."""


def _call_openrouter(api_key: str, model: str, prompt: str) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a crypto analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_google(api_key: str, model: str, prompt: str) -> Optional[str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    data = {
        "contents": [{"parts": [{"text": f"You are a crypto analyst. Respond with valid JSON only.\n\n{prompt}"}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
    }
    resp = requests.post(url, json=data, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    candidates = result.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "")
    return None


def _parse_json(text: str) -> Optional[dict]:
    if not text:
        return None
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def generate_analysis(project: dict, api_keys: List[dict], google_keys: List[dict], models: List[str]) -> Optional[dict]:
    prompt = ANALYSIS_PROMPT.format(
        name=project.get("name", ""),
        ticker=project.get("ticker", ""),
        category=project.get("category", ""),
        chain=project.get("chain", ""),
        description=project.get("description", ""),
        status=project.get("status", ""),
    )

    for gkey_entry in google_keys:
        gkey_idx = gkey_entry["index"]
        for gmodel in GOOGLE_FREE_MODELS:
            healthy = _healthy_models("google", gkey_idx, [gmodel])
            if not healthy:
                continue
            try:
                start = time.time()
                text = _call_google(gkey_entry["key"], gmodel, prompt)
                latency = time.time() - start
                result = _parse_json(text)
                if result:
                    _record_success("google", gkey_idx, gmodel, latency)
                    print(f"[Crypto Analyzer] OK GA key{gkey_idx} model={gmodel} ({latency:.1f}s)")
                    return result
                print(f"[Crypto Analyzer] Bad JSON from {gmodel}, trying next")
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code if hasattr(e, "response") else None
                _record_failure("google", gkey_idx, gmodel, code)
                print(f"[Crypto Analyzer] Fail GA key{gkey_idx} model={gmodel}: {e}")

    for entry in api_keys:
        kidx = entry["index"]
        for model in _healthy_models("openrouter", kidx, models):
            try:
                start = time.time()
                text = _call_openrouter(entry["key"], model, prompt)
                latency = time.time() - start
                result = _parse_json(text)
                if result:
                    _record_success("openrouter", kidx, model, latency)
                    print(f"[Crypto Analyzer] OK OR key{kidx} model={model} ({latency:.1f}s)")
                    return result
                print(f"[Crypto Analyzer] Bad JSON from {model}, trying next")
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code if hasattr(e, "response") else None
                _record_failure("openrouter", kidx, model, code)
                print(f"[Crypto Analyzer] Fail OR key{kidx} model={model}: {e}")
            except Exception as e:
                _record_failure("openrouter", kidx, model)
                print(f"[Crypto Analyzer] Fail OR key{kidx} model={model}: {e}")

    return None


def _analysis_key(project: dict) -> str:
    tid = (project.get("id") or "").strip().lower()
    if tid:
        return tid
    ticker = (project.get("ticker") or "").strip().upper()
    return ticker


def needs_analysis_refresh() -> bool:
    try:
        with open(ANALYSIS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return True
        analyses = data
        if not analyses:
            return True
        try:
            with open(CRYPTO_FILE, encoding="utf-8") as f:
                crypto = json.load(f)
            projects = crypto.get("projects", [])
            all_analyzed = all(_analysis_key(p) in analyses for p in projects)
            if all_analyzed:
                print(f"[Crypto Analyzer] All {len(projects)} projects analyzed, checking age...")
                return False
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return True


def load_cache() -> dict:
    try:
        with open(ANALYSIS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(cache: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"[Crypto Analyzer] Saved {len(cache)} analyses to {ANALYSIS_FILE}")


def analyze(projects: List[dict]):
    api_keys = []
    for i in range(1, 5):
        val = os.environ.get(f"IPO_AI_API_KEY_{i}")
        if val:
            api_keys.append({"key": val, "index": i})

    google_keys = []
    for i in range(1, 3):
        val = os.environ.get(f"GOOGLE_AI_API_KEY_{i}")
        if val:
            google_keys.append({"key": val, "index": i})

    if not api_keys and not google_keys:
        print("[Crypto Analyzer] No API keys set, skipping analysis")
        return

    models = discover_free_models(api_keys) if api_keys else list(FALLBACK_FREE_MODELS)
    cache = load_cache()

    to_analyze = []
    for proj in projects:
        key = _analysis_key(proj)
        if key not in cache:
            to_analyze.append(proj)

    if not to_analyze:
        print(f"[Crypto Analyzer] All {len(projects)} projects already analyzed, nothing to do")
        return

    print(f"[Crypto Analyzer] {len(to_analyze)}/{len(projects)} projects need analysis ({len(cache)} cached)")

    lock = threading.Lock()
    done = [0]

    def _process(proj):
        name = proj.get("name", "")
        result = generate_analysis(proj, api_keys, google_keys, models)
        if result:
            key = _analysis_key(proj)
            with lock:
                cache[key] = result
                save_cache(cache)
                done[0] += 1
                print(f"[Crypto Analyzer] [{done[0]}/{len(to_analyze)}] OK {name}")
            return
        with lock:
            done[0] += 1
            print(f"[Crypto Analyzer] [{done[0]}/{len(to_analyze)}] FAIL {name}")

    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(_process, proj) for proj in to_analyze]
        for f in as_completed(futures):
            pass

    print(f"[Crypto Analyzer] Done. {len(cache)} total analyses cached")


if __name__ == "__main__":
    try:
        with open(CRYPTO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        projects = data.get("projects", [])
        print(f"[Crypto Analyzer] Loaded {len(projects)} projects")
        analyze(projects)
    except FileNotFoundError:
        print(f"[Crypto Analyzer] No crypto_data.json found. Run crypto_collector.py first.")
