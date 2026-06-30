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
IPO_ANALYSIS_FILE = os.path.join(DATA_DIR, "ipo_analysis.json")
CRYPTO_FILE = os.path.join(DATA_DIR, "crypto_data.json")
IPO_FILE = os.path.join(DATA_DIR, "ipo_data.json")

# ── OpenRouter allowlist assigned to every key ────────────────────
_ALL_MODELS = [
    "cohere/north-mini-code:free",
    "nvidia/llama-nemotron-rerank-vl-1b-v2:free",
    "nvidia/nemotron-3.5-content-safety:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "poolside/laguna-xs.2:free",
    "poolside/laguna-m.1:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "qwen/qwen3-coder:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
]

OPENROUTER_KEY_MODELS: dict = {
    1: list(_ALL_MODELS),
    2: list(_ALL_MODELS),
    3: list(_ALL_MODELS),
    4: list(_ALL_MODELS),
    5: list(_ALL_MODELS),
    6: list(_ALL_MODELS),
    7: list(_ALL_MODELS),
    8: list(_ALL_MODELS),
}

CRYPTO_ANALYSIS_PROMPT = """Act as a senior crypto analyst with expertise in token economics, on-chain metrics, and airdrop risk assessment.

Project:
Name: {name}
Ticker: {ticker}
Category: {category}
Chain: {chain}
Description: {description}
Status: {status}

Return EXACTLY this JSON (no other text, no markdown):
{{
  "summary": "1-2 sentence elevator pitch — what the project does, its market position, and unique value proposition.",
  "business_overview": "Detailed explanation of the product, target market, business model, and revenue/capture mechanism.",
  "market_analysis": "TAM/SAM/SOM framing, competitive landscape, differentiation, and growth catalysts vs headwinds.",
  "tokenomics": "Token supply, distribution, vesting, utility, and emission schedule. Note concentration risks.",
  "on_chain_metrics": "TVL, active addresses, transaction volume, DEX liquidity. Use realistic estimates if unknown and mark them as estimates.",
  "team_and_backers": "Team background, investors, advisors, and prior shipped products. Note any red flags or standout credentials.",
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
  "swot": {{
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "threats": ["Threat 1", "Threat 2"]
  }},
  "verdict": "2-3 sentence balanced outlook — who should care, what to watch, and a clear directional call.",
  "final_rating": "BUY",
  "final_rating_score": 7.5
}}

Constraints:
- sentiment ∈ {{"bullish","bearish","neutral"}}
- conviction_score ∈ 0-100
- risk_assessment fields ∈ {{"low","medium","high"}}
- final_rating ∈ {{"STRONG BUY","BUY","HOLD","SELL","STRONG SELL"}}
- final_rating_score ∈ 0-10 (one decimal)
- All text fields must be non-empty strings, no placeholders like "N/A" or "TBD"
- Return ONLY the JSON object, no markdown fences, no commentary"""

IPO_ANALYSIS_PROMPT = """Act as a senior equity research analyst with expertise in IPO valuation, fundamentals, and Indian & US primary markets.

Company:
Name: {name}
Ticker: {ticker}
Exchange: {exchange}
Sector: {sector}
Industry: {industry}
Price Band: {price_band}
Lot Size: {lot_size}
Issue Size: {issue_size}
GMP: {gmp} ({gmp_percent}%)
Subscription Status: {subscription_status}
Description: {description}
About: {about}

Return EXACTLY this JSON (no other text, no markdown):
{{
  "summary": "1-2 sentence elevator pitch — what the company does, market position, and IPO thesis.",
  "business_overview": "Detailed explanation of products/services, target segments, revenue mix, and unit economics.",
  "market_analysis": "TAM/SAM, competitive landscape, moat, and industry tailwinds vs headwinds.",
  "financials": "Revenue, EBITDA, PAT growth over 3 years. Margins, ROCE, ROE. Note auditor concerns if any.",
  "valuation": "P/E vs industry peers, EV/EBITDA, P/B. Compare with listed peers. Flag premium/discount.",
  "ipo_structure": "Fresh issue vs OFS mix, promoter holding post-issue, use of proceeds, anchor investors.",
  "team_and_promoters": "Promoter background, management track record, board composition, governance quality.",
  "sentiment": "bullish",
  "conviction_score": 75,
  "key_drivers": ["Driver 1", "Driver 2", "Driver 3"],
  "risks": ["Risk 1", "Risk 2", "Risk 3"],
  "risk_assessment": {{
    "overall_risk": "medium",
    "valuation_risk": "medium",
    "business_risk": "low",
    "governance_risk": "low",
    "market_risk": "medium",
    "regulatory_risk": "low",
    "liquidity_risk": "medium",
    "promoter_risk": "medium"
  }},
  "swot": {{
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "threats": ["Threat 1", "Threat 2"]
  }},
  "verdict": "2-3 sentence balanced outlook — who should apply, what to watch, and a clear directional call.",
  "final_rating": "SUBSCRIBE",
  "final_rating_score": 7.5
}}

Constraints:
- sentiment ∈ {{"bullish","bearish","neutral"}}
- conviction_score ∈ 0-100
- risk_assessment fields ∈ {{"low","medium","high"}}
- final_rating ∈ {{"STRONG SUBSCRIBE","SUBSCRIBE","NEUTRAL","AVOID","STRONG AVOID"}}
- final_rating_score ∈ 0-10 (one decimal)
- All text fields must be non-empty strings, no placeholders like "N/A" or "TBD"
- Return ONLY the JSON object, no markdown fences, no commentary"""


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


_model_health: Dict[str, dict] = {}


def _call_openrouter(api_key: str, model: str, prompt: str, system: str, timeout: int = 90) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=timeout,
    )
    if resp.status_code != 200:
        body = resp.text[:200] if resp.text else ""
        print(f"[Crypto Analyzer] HTTP {resp.status_code} from OR/{model}: {body}")
        return None
    payload = resp.json()
    if "choices" not in payload or not payload["choices"]:
        return None
    return payload["choices"][0]["message"]["content"]


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


def _analysis_key_crypto(project: dict) -> str:
    tid = (project.get("id") or "").strip().lower()
    if tid:
        return f"crypto:{tid}"
    ticker = (project.get("ticker") or "").strip().upper()
    return f"crypto:{ticker}"


def _analysis_key_ipo(ipo: dict) -> str:
    tid = (ipo.get("id") or "").strip().lower()
    if tid:
        return f"ipo:{tid}"
    name = (ipo.get("name") or "").strip().lower()
    return f"ipo:{name}"


def generate_crypto_analysis(project: dict, api_keys: List[dict]) -> Optional[dict]:
    prompt = CRYPTO_ANALYSIS_PROMPT.format(
        name=project.get("name", ""),
        ticker=project.get("ticker", ""),
        category=project.get("category", ""),
        chain=project.get("chain", ""),
        description=project.get("description", ""),
        status=project.get("status", ""),
    )
    system = "You are a senior crypto analyst. Always respond with valid JSON only, no markdown fences."

    for entry in api_keys:
        kidx = entry["index"]
        preferred = OPENROUTER_KEY_MODELS.get(kidx, [])
        for model in _healthy_models("openrouter", kidx, preferred):
            try:
                start = time.time()
                text = _call_openrouter(entry["key"], model, prompt, system)
                latency = time.time() - start
                result = _parse_json(text)
                if result:
                    _record_success("openrouter", kidx, model, latency)
                    print(f"[Crypto Analyzer] OK OR key{kidx} model={model} ({latency:.1f}s)")
                    return result
                print(f"[Crypto Analyzer] Bad JSON from OR/{model}, trying next")
                _record_failure("openrouter", kidx, model)
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code if hasattr(e, "response") else None
                _record_failure("openrouter", kidx, model, code)
                print(f"[Crypto Analyzer] Fail OR key{kidx} model={model}: {e}")
            except Exception as e:
                _record_failure("openrouter", kidx, model)
                print(f"[Crypto Analyzer] Fail OR key{kidx} model={model}: {e}")

    return None


def generate_ipo_analysis(ipo: dict, api_keys: List[dict]) -> Optional[dict]:
    price_band = ipo.get("priceBand") or ipo.get("price_band") or {}
    if isinstance(price_band, dict):
        pb_high = price_band.get("high", "")
        pb_low = price_band.get("low", "")
        price_band_str = f"Rs.{pb_low} - Rs.{pb_high}" if pb_low and pb_high else "TBA"
    else:
        price_band_str = str(price_band) if price_band else "TBA"

    prompt = IPO_ANALYSIS_PROMPT.format(
        name=ipo.get("name", ""),
        ticker=ipo.get("ticker", ""),
        exchange=ipo.get("exchange", ""),
        sector=ipo.get("sector", ""),
        industry=ipo.get("industry", ""),
        price_band=price_band_str,
        lot_size=ipo.get("lotSize", ipo.get("lot_size", "")),
        issue_size=ipo.get("issueSize", ipo.get("issue_size", "")),
        gmp=ipo.get("gmp", ""),
        gmp_percent=ipo.get("gmpPercent", ipo.get("gmp_percent", "")),
        subscription_status=ipo.get("subscriptionStatus", ipo.get("subscription_status", "")),
        description=ipo.get("description", ""),
        about=ipo.get("about", ""),
    )
    system = "You are a senior equity research analyst. Always respond with valid JSON only, no markdown fences."

    for entry in api_keys:
        kidx = entry["index"]
        preferred = OPENROUTER_KEY_MODELS.get(kidx, [])
        for model in _healthy_models("openrouter", kidx, preferred):
            try:
                start = time.time()
                text = _call_openrouter(entry["key"], model, prompt, system)
                latency = time.time() - start
                result = _parse_json(text)
                if result:
                    _record_success("openrouter", kidx, model, latency)
                    print(f"[IPO Analyzer] OK OR key{kidx} model={model} ({latency:.1f}s)")
                    return result
                print(f"[IPO Analyzer] Bad JSON from OR/{model}, trying next")
                _record_failure("openrouter", kidx, model)
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code if hasattr(e, "response") else None
                _record_failure("openrouter", kidx, model, code)
                print(f"[IPO Analyzer] Fail OR key{kidx} model={model}: {e}")
            except Exception as e:
                _record_failure("openrouter", kidx, model)
                print(f"[IPO Analyzer] Fail OR key{kidx} model={model}: {e}")

    return None


def load_cache(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(cache: dict, path: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"[Crypto Analyzer] Saved {len(cache)} analyses to {path}")


def generate_airdrop_analysis(project: dict, api_keys: List[dict]) -> Optional[dict]:
    """Generate AI analysis for a single airdrop project."""
    steps_str = "; ".join(project.get("steps", []) or project.get("actions", []) or [])
    prompt = AIRDROP_ANALYSIS_PROMPT.format(
        name=project.get("name", ""),
        category=project.get("category", "airdrop"),
        chain=project.get("chain", ""),
        description=(project.get("about") or project.get("description", ""))[:500],
        status=project.get("status", "active"),
        steps=steps_str[:300],
        estimated_value=project.get("estimated_value", ""),
    )
    system = "You are a senior airdrop analyst. Always respond with valid JSON only, no markdown fences."

    for entry in api_keys:
        kidx = entry["index"]
        preferred = OPENROUTER_KEY_MODELS.get(kidx, [])
        for model in _healthy_models("openrouter", kidx, preferred):
            try:
                start = time.time()
                text = _call_openrouter(entry["key"], model, prompt, system)
                latency = time.time() - start
                result = _parse_json(text)
                if result:
                    _record_success("openrouter", kidx, model, latency)
                    print(f"[Airdrop Analyzer] OK OR key{kidx} model={model} ({latency:.1f}s)")
                    return result
                print(f"[Airdrop Analyzer] Bad JSON from OR/{model}, trying next")
                _record_failure("openrouter", kidx, model)
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code if hasattr(e, "response") else None
                _record_failure("openrouter", kidx, model, code)
                print(f"[Airdrop Analyzer] Fail OR key{kidx} model={model}: {e}")
            except Exception as e:
                _record_failure("openrouter", kidx, model)
                print(f"[Airdrop Analyzer] Fail OR key{kidx} model={model}: {e}")

    return None


def analyze_crypto(projects: List[dict], api_keys: List[dict], max_workers: int = 5):
    if not api_keys:
        print("[Crypto Analyzer] No OpenRouter keys, skipping crypto analysis")
        return
    cache = load_cache(ANALYSIS_FILE)
    to_analyze = []
    for proj in projects:
        if _analysis_key_crypto(proj) not in cache:
            to_analyze.append(proj)

    if not to_analyze:
        print(f"[Crypto Analyzer] All {len(projects)} crypto projects already analyzed, nothing to do")
        return

    print(f"[Crypto Analyzer] {len(to_analyze)}/{len(projects)} crypto projects need analysis ({len(cache)} cached)")

    lock = threading.Lock()
    done = [0]

    def _process(proj):
        name = proj.get("name", "")
        result = generate_crypto_analysis(proj, api_keys)
        with lock:
            done[0] += 1
            if result:
                cache[_analysis_key_crypto(proj)] = result
                save_cache(cache, ANALYSIS_FILE)
                print(f"[Crypto Analyzer] [{done[0]}/{len(to_analyze)}] OK {name}")
            else:
                print(f"[Crypto Analyzer] [{done[0]}/{len(to_analyze)}] FAIL {name}")

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(_process, proj) for proj in to_analyze]
        for f in as_completed(futures):
            pass

    print(f"[Crypto Analyzer] Done. {len(cache)} total crypto analyses cached")


def analyze_ipos(ipos: List[dict], api_keys: List[dict], max_workers: int = 8, batch_size: int = 50):
    if not api_keys:
        print("[IPO Analyzer] No OpenRouter keys, skipping IPO analysis")
        return
    cache = load_cache(IPO_ANALYSIS_FILE)
    to_analyze = []
    for ipo in ipos:
        if _analysis_key_ipo(ipo) not in cache:
            to_analyze.append(ipo)
            if len(to_analyze) >= batch_size:
                break

    if not to_analyze:
        print(f"[IPO Analyzer] All {len(ipos)} IPOs already analyzed, nothing to do")
        return

    remaining = len(ipos) - len(cache) - len(to_analyze)
    print(f"[IPO Analyzer] Analyzing {len(to_analyze)} IPOs this run ({len(cache)} cached, ~{remaining} remaining)")

    lock = threading.Lock()
    done = [0]

    def _process(ipo):
        name = ipo.get("name", "")
        result = generate_ipo_analysis(ipo, api_keys)
        with lock:
            done[0] += 1
            if result:
                cache[_analysis_key_ipo(ipo)] = result
                save_cache(cache, IPO_ANALYSIS_FILE)
                print(f"[IPO Analyzer] [{done[0]}/{len(to_analyze)}] OK {name}")
            else:
                print(f"[IPO Analyzer] [{done[0]}/{len(to_analyze)}] FAIL {name}")

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(_process, ipo) for ipo in to_analyze]
        for f in as_completed(futures):
            pass

    print(f"[IPO Analyzer] Done. {len(cache)} total IPO analyses cached ({len(ipos) - len(cache)} remaining)")


def load_or_keys() -> List[dict]:
    keys = []
    for i in range(1, 9):
        val = os.environ.get(f"OPENROUTER_API_{i}")
        if val:
            keys.append({"key": val, "index": i})
    return keys


def load_projects() -> List[dict]:
    try:
        with open(CRYPTO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("projects", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_ipos() -> List[dict]:
    try:
        with open(IPO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("ipos", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


if __name__ == "__main__":
    api_keys = load_or_keys()
    if not api_keys:
        print("[Crypto Analyzer] No OPENROUTER_API_1..8 keys set, exiting")
        raise SystemExit(0)

    projects = load_projects()
    print(f"[Crypto Analyzer] Loaded {len(projects)} crypto projects")
    analyze_crypto(projects, api_keys)

    ipos = load_ipos()
    print(f"[IPO Analyzer] Loaded {len(ipos)} IPOs")
    analyze_ipos(ipos, api_keys)
