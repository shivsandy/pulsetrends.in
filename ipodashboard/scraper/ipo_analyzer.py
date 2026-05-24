import json
import os
import random
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests

ANALYSIS_FILE = None
FALLBACK_FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-32b:free",
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-chat:free",
    "microsoft/phi-4:free",
]

_model_health: Dict[str, dict] = {}

def _health_key(key_index: int, model: str) -> str:
    return f"key{key_index}:{model}"

def _record_success(key_index: int, model: str, latency: float):
    key = _health_key(key_index, model)
    h = _model_health.get(key)
    if not h:
        h = {"success": 0, "failures": 0, "consecutive": 0, "cooldown": 0.0}
        _model_health[key] = h
    h["success"] += 1
    h["consecutive"] = 0
    h["latency"] = latency

def _record_failure(key_index: int, model: str, status_code: Optional[int] = None):
    key = _health_key(key_index, model)
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

def _healthy_models(key_index: int, models: List[str]) -> List[str]:
    now = time.time()
    healthy = []
    for model in models:
        key = _health_key(key_index, model)
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
                    prompt_price = pricing.get("prompt", "1")
                    try:
                        if float(prompt_price) == 0.0:
                            mid = m.get("id", "")
                            if mid.endswith(":free") or ":free" not in mid:
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
        print(f"[IPO Analyzer] Discovered {len(sorted_models)} free models")
        return sorted_models

    print(f"[IPO Analyzer] Model discovery failed, using {len(FALLBACK_FREE_MODELS)} fallback models")
    return list(FALLBACK_FREE_MODELS)


def _analysis_key(ipo: dict) -> str:
    symbol = (ipo.get("symbol") or "").strip().upper()
    country = (ipo.get("country") or "Global").strip()
    if symbol:
        return f"{symbol}-{country}"
    name = (ipo.get("company_name") or "").strip().lower().replace(" ", "-")[:20]
    return f"{name}-{country}"


ANALYSIS_PROMPT = """You are an IPO research analyst. Given the following IPO details, provide a structured analysis as JSON only.

Company: {company_name}
Symbol: {symbol}
Exchange: {exchange}
Country: {country}
Price Band: {price_band}
Status: {status}

Return valid JSON with exactly these fields:
- "about": A 2-3 sentence description of what the company does, its business model, and industry.
- "financials": Key financial information including estimated revenue, growth metrics, margins, or relevant financial context based on publicly known data about this company.
- "strengths": An array of 2-4 bullet points summarizing competitive advantages.
- "risks": An array of 2-4 bullet points summarizing key risk factors.
- "ai_analysis": A 1-paragraph balanced investment outlook.

Return ONLY the JSON object, no other text."""


def _call_openrouter(api_key: str, model: str, prompt: str) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a financial analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=120,
    )
    if resp.status_code != 200:
        raise Exception(f"OpenRouter {resp.status_code}: {resp.text[:200]}")
    content = resp.json()["choices"][0]["message"]["content"]
    return content


def _parse_analysis_response(raw: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        required = ["about", "financials", "strengths", "risks", "ai_analysis"]
        if all(k in data for k in required):
            if isinstance(data["strengths"], list) and isinstance(data["risks"], list):
                return data
        return None
    except (json.JSONDecodeError, TypeError):
        return None


def generate_analysis(ipo: dict, api_keys: List[dict], models: List[str]) -> Optional[dict]:
    prompt = ANALYSIS_PROMPT.format(
        company_name=ipo.get("company_name", "Unknown"),
        symbol=ipo.get("symbol", "N/A"),
        exchange=ipo.get("exchange", "N/A"),
        country=ipo.get("country", "Global"),
        price_band=ipo.get("price_band", "N/A"),
        status=ipo.get("status", "upcoming"),
    )

    for entry in api_keys:
        key_index = entry["index"]
        healthy = _healthy_models(key_index, models)
        if not healthy:
            continue

        for model in healthy:
            try:
                print(f"[IPO Analyzer] key{key_index} model={model} -> {ipo.get('company_name', '')}")
                start = time.time()
                raw = _call_openrouter(entry["key"], model, prompt)
                latency = time.time() - start

                parsed = _parse_analysis_response(raw)
                if parsed:
                    _record_success(key_index, model, latency)
                    print(f"[IPO Analyzer] OK key{key_index} model={model} ({latency:.1f}s)")
                    return parsed
                else:
                    print(f"[IPO Analyzer] Bad JSON from {model}, trying next")
                    _record_failure(key_index, model)
            except Exception as e:
                status_code = None
                if hasattr(e, "status_code"):
                    status_code = e.status_code
                _record_failure(key_index, model, status_code)
                print(f"[IPO Analyzer] Fail key{key_index} model={model}: {e}")
                continue

    print(f"[IPO Analyzer] All keys/models exhausted for {ipo.get('company_name', '')}")
    return None


def _set_analysis_path():
    global ANALYSIS_FILE
    if ANALYSIS_FILE:
        return
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    ANALYSIS_FILE = os.path.join(data_dir, "ipo_analysis.json")


def load_cache() -> dict:
    _set_analysis_path()
    if os.path.exists(ANALYSIS_FILE):
        try:
            with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            pass
    return {}


def save_cache(cache: dict):
    _set_analysis_path()
    base_dir = os.path.dirname(ANALYSIS_FILE)
    os.makedirs(base_dir, exist_ok=True)
    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"[IPO Analyzer] Saved {len(cache)} analyses to {ANALYSIS_FILE}")


def analyze(ipos: List[dict]):
    api_keys = []
    for i in range(1, 5):
        val = os.environ.get(f"IPO_AI_API_KEY_{i}")
        if val:
            api_keys.append({"key": val, "index": i, "cooldown": 0.0})

    if not api_keys:
        print("[IPO Analyzer] No IPO_AI_API_KEY_1..4 set, skipping")
        return

    models = discover_free_models(api_keys)
    cache = load_cache()

    upcoming = [x for x in ipos if x.get("status") == "upcoming"]
    to_analyze = []
    for ipo in upcoming:
        key = _analysis_key(ipo)
        if key not in cache:
            to_analyze.append(ipo)

    if not to_analyze:
        print(f"[IPO Analyzer] All {len(upcoming)} upcoming IPOs already analyzed, nothing to do")
        return

    print(f"[IPO Analyzer] {len(to_analyze)}/{len(upcoming)} upcoming IPOs need analysis ({len(cache)} cached)")

    for idx, ipo in enumerate(to_analyze):
        print(f"[IPO Analyzer] [{idx + 1}/{len(to_analyze)}] {ipo.get('company_name', '')}")
        result = generate_analysis(ipo, api_keys, models)
        if result:
            key = _analysis_key(ipo)
            cache[key] = result
            save_cache(cache)
        else:
            print(f"[IPO Analyzer] Failed to generate analysis for {ipo.get('company_name', '')}")

    print(f"[IPO Analyzer] Done. {len(cache)} total analyses cached")
