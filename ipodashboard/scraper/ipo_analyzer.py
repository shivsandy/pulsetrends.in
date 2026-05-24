import json
import os
import random
import re
import time
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

GOOGLE_FREE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

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
                    prompt_price = pricing.get("prompt", "1")
                    try:
                        if float(prompt_price) == 0.0:
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


ANALYSIS_PROMPT = """Act as an IPO analyst. Analyze the following IPO and return ONLY valid JSON.

Company: {company_name}
Symbol: {symbol}
Exchange: {exchange}
Country: {country}
Price Band: {price_band}
Status: {status}

Return EXACTLY this JSON structure:
{{
  "about": "Company overview — what it does, business model, industry.",
  "ipo_details": "IPO details like size, price band, dates, lot size, listing exchange.",
  "financial_summary": "Revenue, Profit, Debt, EPS if known based on model knowledge.",
  "financial_trend": "1-2 sentence overview of financial trend.",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "risks": [
    {{"text": "Risk description 1", "indicator": "🟢"}},
    {{"text": "Risk description 2", "indicator": "🟡"}},
    {{"text": "Risk description 3", "indicator": "🔴"}}
  ],
  "scores": {{
    "financial_health": 75,
    "growth_potential": 80,
    "risk": 65,
    "attractiveness": 72
  }},
  "ai_analysis": "Short balanced analysis paragraph (2-3 sentences). Note: This is AI-generated based on model knowledge and should not be considered financial advice.",
  "verdict": "Listing gain potential, long-term outlook, and Subscribe / Avoid / Neutral recommendation."
}}
Important: "risks" must be an array of objects with "text" and "indicator" fields (indicator is 🟢 🟡 or 🔴). "scores" must have all 4 fields as integers 0-100. Return ONLY the JSON, no other text."""


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
    return resp.json()["choices"][0]["message"]["content"]


def _call_google(api_key: str, model: str, prompt: str) -> Optional[str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    resp = requests.post(
        f"{url}?key={api_key}",
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
        },
        timeout=120,
    )
    if resp.status_code != 200:
        raise Exception(f"Google {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise Exception("Google returned no candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise Exception("Google returned empty parts")
    return parts[0].get("text", "")


def _parse_analysis_response(raw: str) -> Optional[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        required = ["about", "financial_summary", "strengths", "risks", "ai_analysis", "verdict", "scores"]
        if all(k in data for k in required):
            if isinstance(data["strengths"], list) and isinstance(data["risks"], list):
                return data
        return None
    except (json.JSONDecodeError, TypeError):
        return None


def generate_analysis(ipo: dict, api_keys: List[dict], google_keys: List[dict], models: List[str]) -> Optional[dict]:
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
        healthy = _healthy_models("openrouter", key_index, models)
        if not healthy:
            continue

        for model in healthy:
            try:
                print(f"[IPO Analyzer] OR key{key_index} model={model} -> {ipo.get('company_name', '')}")
                start = time.time()
                raw = _call_openrouter(entry["key"], model, prompt)
                latency = time.time() - start
                parsed = _parse_analysis_response(raw)
                if parsed:
                    _record_success("openrouter", key_index, model, latency)
                    print(f"[IPO Analyzer] OK OR key{key_index} model={model} ({latency:.1f}s)")
                    return parsed
                else:
                    print(f"[IPO Analyzer] Bad JSON from {model}, trying next")
                    _record_failure("openrouter", key_index, model)
            except Exception as e:
                status_code = None
                if hasattr(e, "status_code"):
                    status_code = e.status_code
                _record_failure("openrouter", key_index, model, status_code)
                print(f"[IPO Analyzer] Fail OR key{key_index} model={model}: {e}")
                continue

    for entry in google_keys:
        key_index = entry["index"]
        healthy = _healthy_models("google", key_index, GOOGLE_FREE_MODELS)
        if not healthy:
            continue

        for model in healthy:
            try:
                print(f"[IPO Analyzer] GA key{key_index} model={model} -> {ipo.get('company_name', '')}")
                start = time.time()
                raw = _call_google(entry["key"], model, prompt)
                latency = time.time() - start
                parsed = _parse_analysis_response(raw)
                if parsed:
                    _record_success("google", key_index, model, latency)
                    print(f"[IPO Analyzer] OK GA key{key_index} model={model} ({latency:.1f}s)")
                    return parsed
                else:
                    print(f"[IPO Analyzer] Bad JSON from {model}, trying next")
                    _record_failure("google", key_index, model)
            except Exception as e:
                status_code = None
                if hasattr(e, "status_code"):
                    status_code = e.status_code
                _record_failure("google", key_index, model, status_code)
                print(f"[IPO Analyzer] Fail GA key{key_index} model={model}: {e}")
                continue

    print(f"[IPO Analyzer] All models exhausted for {ipo.get('company_name', '')}")
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
            api_keys.append({"key": val, "index": i})

    google_keys = []
    for i in range(1, 3):
        val = os.environ.get(f"GOOGLE_AI_API_KEY_{i}")
        if val:
            google_keys.append({"key": val, "index": i})

    if not api_keys and not google_keys:
        print("[IPO Analyzer] No API keys set, skipping")
        return

    models = discover_free_models(api_keys) if api_keys else FALLBACK_FREE_MODELS
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
        result = generate_analysis(ipo, api_keys, google_keys, models)
        if result:
            key = _analysis_key(ipo)
            cache[key] = result
            save_cache(cache)
        else:
            print(f"[IPO Analyzer] Failed to generate analysis for {ipo.get('company_name', '')}")

    print(f"[IPO Analyzer] Done. {len(cache)} total analyses cached")
