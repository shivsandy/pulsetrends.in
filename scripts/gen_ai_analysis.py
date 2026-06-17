#!/usr/bin/env python3
"""
Genuine AI analysis for all 2,001 IPOs using OpenRouter.
One LLM call per IPO generates 13-section analysis + scores as structured JSON.
Uses all 8 API keys with 20+ free models in rotation.

Usage:
    python scripts/gen_ai_analysis.py           # incremental (skip existing)
    python scripts/gen_ai_analysis.py --force    # regenerate all
"""
import json, os, re, sys, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SRC_DIR = os.path.join(ROOT, "src", "data")

# ── Models per key (distributed to spread load) ────────────────────
OPENROUTER_KEY_MODELS = {
    # Each key gets its assigned primary model + distributed fallbacks
    1: [
        "nex-agi/nex-n2-pro:free",                          # Primary
        "nvidia/nemotron-3.5-content-safety:free",           # Fallback
        "nvidia/nemotron-3-nano-30b-a3b:free",               # Distributed
    ],
    2: [
        "nvidia/nemotron-3.5-content-safety:free",           # Primary
        "nvidia/nemotron-3-ultra-550b-a55b:free",            # Fallback
        "liquid/lfm-2.5-1.2b-thinking:free",                 # Distributed
    ],
    3: [
        "nvidia/nemotron-3-ultra-550b-a55b:free",            # Primary
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", # Fallback
        "nvidia/nemotron-nano-12b-v2-vl:free",               # Distributed
    ],
    4: [
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", # Primary
        "poolside/laguna-xs.2:free",                         # Fallback
        "qwen/qwen3-next-80b-a3b-instruct:free",             # Distributed
    ],
    5: [
        "poolside/laguna-xs.2:free",                         # Primary
        "poolside/laguna-m.1:free",                          # Fallback
        "openai/gpt-oss-120b:free",                          # Distributed
    ],
    6: [
        "poolside/laguna-m.1:free",                          # Primary
        "google/gemma-4-26b-a4b-it:free",                     # Fallback
        "qwen/qwen3-coder:free",                             # Distributed
    ],
    7: [
        "google/gemma-4-26b-a4b-it:free",                    # Primary
        "google/gemma-4-31b-it:free",                         # Fallback
        "meta-llama/llama-3.3-70b-instruct:free",            # Distributed
    ],
    8: [
        "google/gemma-4-31b-it:free",                        # Primary
        "nvidia/nemotron-3-super-120b-a12b:free",             # Fallback
        "meta-llama/llama-3.2-3b-instruct:free",             # Distributed
        "nousresearch/hermes-3-llama-3.1-405b:free",         # Distributed
    ],
}

# ── Rate limiting ──────────────────────────────────────────────────
RPM_PER_KEY = 3
key_locks = {i: threading.Lock() for i in range(1, 9)}
key_last_calls = {i: 0.0 for i in range(1, 9)}

def _rate_limit(key_idx: int):
    with key_locks[key_idx]:
        elapsed = time.time() - key_last_calls[key_idx]
        min_interval = 60.0 / RPM_PER_KEY
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        key_last_calls[key_idx] = time.time()

# ── Model health tracking ──────────────────────────────────────────
_model_health: dict = {}

def _health_key(key_idx: int, model: str) -> str:
    return f"key{key_idx}:{model}"

def _is_healthy(key_idx: int, model: str) -> bool:
    h = _model_health.get(_health_key(key_idx, model))
    if h and h["cooldown"] > time.time():
        return False
    return True

def _mark_success(key_idx: int, model: str):
    k = _health_key(key_idx, model)
    h = _model_health.get(k)
    if not h:
        h = {"cooldown": 0, "consecutive": 0}
        _model_health[k] = h
    h["consecutive"] = 0

def _mark_failure(key_idx: int, model: str, status_code: int = None):
    k = _health_key(key_idx, model)
    h = _model_health.get(k)
    if not h:
        h = {"cooldown": 0, "consecutive": 0}
        _model_health[k] = h
    h["consecutive"] = h.get("consecutive", 0) + 1
    now = time.time()
    if status_code == 429:
        h["cooldown"] = now + 300
    elif status_code and 500 <= status_code < 600:
        h["cooldown"] = now + 180
    else:
        h["cooldown"] = now + 60

# ── OpenRouter call ────────────────────────────────────────────────
def _call_openrouter(api_key: str, model: str, prompt: str, system: str, timeout: int = 120) -> str:
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
        "temperature": 0.1,
        "max_tokens": 8192,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=timeout,
    )
    if resp.status_code != 200:
        body = resp.text[:200] if resp.text else ""
        raise Exception(f"HTTP {resp.status_code}: {body}")
    payload = resp.json()
    if "choices" not in payload or not payload["choices"]:
        raise Exception("No choices in response")
    return payload["choices"][0]["message"]["content"]

def _parse_json(text: str) -> dict:
    if not text:
        raise Exception("Empty response")
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group()
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    return json.loads(text)

# ── Prompt building ────────────────────────────────────────────────
def build_prompt(ipo: dict) -> str:
    name = ipo.get("company_name", "Unknown")
    ticker = ipo.get("ticker", "N/A")
    sector = ipo.get("sector", "General")
    industry = ipo.get("industry", "")
    exchange = ipo.get("exchange", "NSE/BSE")
    status = ipo.get("status", "listed")
    ipo_date = ipo.get("ipo_date", "")
    country = ipo.get("country", "IN")
    price_band = ipo.get("price_band", ipo.get("price_range", ""))
    issue_size = ipo.get("issue_size", "")
    lot_size = ipo.get("lot_size", "")
    gmp = ipo.get("gmp", "")
    subscription = ipo.get("subscription", "")
    description = ipo.get("description", "")
    about = ipo.get("about", "")
    risk_factors = ipo.get("risk_factors", [])
    red_flags = ipo.get("red_flags", [])
    bull_case = ipo.get("bull_case", [])
    bear_case = ipo.get("bear_case", [])

    data_json = json.dumps({
        "name": name, "ticker": ticker, "sector": sector, "industry": industry,
        "exchange": exchange, "status": status, "ipo_date": ipo_date, "country": country,
        "price_band": price_band, "issue_size": issue_size, "lot_size": lot_size,
        "gmp": gmp, "subscription": subscription,
        "description": description[:2000] if description else "",
        "about": about[:2000] if about else "",
        "risk_factors": risk_factors[:10],
        "red_flags": red_flags[:10],
        "bull_case": bull_case[:8],
        "bear_case": bear_case[:8],
    }, indent=2, ensure_ascii=False)

    prompt_body = """Analyze the following IPO and return a JSON object.

IPO DATA:
""" + data_json + """

Return EXACTLY this JSON structure — no markdown fences, no commentary, just pure JSON:

{
  "executive_summary": "2-3 sentence overview company, sector, and investment thesis",
  "business_overview": "Business model, products, revenue streams, customer base, competitive position — 2-4 paragraphs",
  "industry_analysis": "Industry size, growth rate, trends, regulatory environment, competitive intensity, entry barriers — 2-4 paragraphs",
  "financial_analysis": "Revenue growth, profitability, ROE, ROCE, margin trends — use the data provided. If limited data, state what's needed. 2-4 paragraphs",
  "balance_sheet_analysis": "Debt levels, liquidity, capital structure, contingent liabilities — 2-3 paragraphs",
  "cash_flow_analysis": "Operating cash flow, FCF, capex needs, cash conversion — 2-3 paragraphs",
  "ipo_details": "Issue structure (fresh vs OFS), use of proceeds, lot size, price band, pre/post promoter holding — 2-3 paragraphs",
  "valuation_analysis": "P/E vs peers, EV/EBITDA, fair value range, upside/downside — 2-3 paragraphs",
  "management_quality": "Promoter background, CEO/CFO experience, governance track record, board composition — 2-3 paragraphs",
  "risk_assessment": "Key risks by category (business, financial, regulatory, governance) with severity — 2-4 paragraphs",
  "strengths_weaknesses": "Bullet list of key strengths and key weaknesses",
  "market_sentiment": "GMP trend, subscription data, institutional demand, peer comparison — 2-3 paragraphs",
  "final_verdict": "Overall assessment, short-term listing outlook, long-term outlook, clear recommendation — 2-4 paragraphs",
  "red_flags": ["list of specific red flags"],
  "positive_catalysts": ["list of positive catalysts"],
  "scores": {
    "fundamentals_score": <0-100>,
    "ipo_demand_score": <0-100>,
    "valuation_score": <0-100>,
    "governance_score": <0-100>,
    "business_quality_score": <0-100>,
    "post_listing_score": <0-100>
  },
  "final_rating": "Strong Subscribe or Subscribe or Neutral or Avoid or Strong Avoid",
  "long_term_rating": "Very Good or Good or Average or Below Average",
  "summary": "1-2 sentence tight summary"
}

Rules:
- All text fields must be 200+ characters of genuine market analysis — no placeholders like "N/A", "TBD", or "requires further data"
- Scores must be integers 0-100 reflecting genuine analysis of the data available
- red_flags and positive_catalysts: 2-6 items each, specific to this company
- Return ONLY the JSON object, no other text"""
    return prompt_body

# ── Entry generation ───────────────────────────────────────────────
def generate_entry(ipo: dict, slug: str, api_keys: list) -> dict:
    prompt = build_prompt(ipo)
    system = "You are a senior equity research analyst with 20 years of experience in IPO valuation, fundamental analysis, and Indian/US primary markets."

    for entry in api_keys:
        kidx = entry["index"]
        models = OPENROUTER_KEY_MODELS.get(kidx, ["meta-llama/llama-3.3-70b-instruct:free"])
        for model in models:
            if not _is_healthy(kidx, model):
                continue
            try:
                _rate_limit(kidx)
                text = _call_openrouter(entry["key"], model, prompt, system)
                result = _parse_json(text)
                _mark_success(kidx, model)

                scores = result.get("scores", {})
                fs = scores.get("fundamentals_score", 50)
                ids = scores.get("ipo_demand_score", 50)
                vs = scores.get("valuation_score", 50)
                gs = scores.get("governance_score", 50)
                bqs = scores.get("business_quality_score", 50)
                pls = scores.get("post_listing_score", 50)
                overall = round(fs * 0.30 + ids * 0.15 + vs * 0.15 + gs * 0.15 + bqs * 0.15 + pls * 0.10, 1)

                def sl(v):
                    if v >= 80: return "Strong"
                    if v >= 70: return "Good"
                    if v >= 60: return "Average"
                    if v >= 50: return "Below Average"
                    return "Weak"

                rating = result.get("final_rating", "Neutral")
                ltr = result.get("long_term_rating", "Average")
                summary = result.get("summary", "")

                cat_scores = [
                    {"key": "bq", "label": "Business Quality", "score": round(bqs / 10, 1)},
                    {"key": "fin", "label": "Financial Strength", "score": round(fs / 10, 1)},
                    {"key": "val", "label": "Valuation", "score": round(vs / 10, 1)},
                    {"key": "dem", "label": "Demand & Hype", "score": round(ids / 10, 1)},
                    {"key": "risk", "label": "Risk Safety", "score": round(gs / 10, 1)},
                ]

                return {
                    "slug": slug,
                    "company": ipo.get("company_name", "Unknown"),
                    "ticker": ipo.get("ticker", ""),
                    "sector": ipo.get("sector", ""),
                    "executive_summary": summary,
                    "business_overview": result.get("business_overview", ""),
                    "industry_analysis": result.get("industry_analysis", ""),
                    "financial_analysis": result.get("financial_analysis", ""),
                    "balance_sheet_analysis": result.get("balance_sheet_analysis", ""),
                    "cash_flow_analysis": result.get("cash_flow_analysis", ""),
                    "ipo_details": result.get("ipo_details", ""),
                    "valuation_analysis": result.get("valuation_analysis", ""),
                    "management_quality": result.get("management_quality", ""),
                    "risk_assessment": result.get("risk_assessment", ""),
                    "strengths_weaknesses": result.get("strengths_weaknesses", ""),
                    "market_sentiment": result.get("market_sentiment", ""),
                    "red_flags": result.get("red_flags", []),
                    "positive_catalysts": result.get("positive_catalysts", []),
                    "final_verdict": result.get("final_verdict", ""),
                    "section_20_scorecard": {
                        "categories": cat_scores,
                        "total_score": round(overall / 10, 1),
                        "interpretation": sl(overall),
                    },
                    "section_13_market_performance": {
                        "stock_pe": "N/A",
                        "analysis": f"AI Score: {overall:.1f}/100",
                    },
                    "section_21_final_verdict": {
                        "long_term_rating": ltr,
                        "subscription_recommendation": rating,
                        "summary": summary[:500],
                    },
                    "investment_verdict": {
                        "overall_score": overall,
                        "rating": sl(overall),
                        "long_term_rating": ltr,
                        "subscription_recommendation": rating,
                        "scores": {
                            "overall_score": overall,
                            "fundamentals_score": fs,
                            "valuation_score": vs,
                            "growth_score": bqs,
                            "management_score": gs,
                            "market_sentiment_score": ids,
                        },
                        "summary": summary[:500],
                    },
                }
            except Exception as e:
                code = None
                if hasattr(e, "response") and hasattr(e.response, "status_code"):
                    code = e.response.status_code
                _mark_failure(kidx, model, code)
                continue

    # Fallback if all models/keys failed — return template
    return None

# ── Helpers ────────────────────────────────────────────────────────
def slugify(name):
    s = (name or "").lower().strip()
    s = re.sub(r"[&]", " and ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]

def extract_slugs_from_ts():
    ts_path = os.path.join(SRC_DIR, "ipoData.ts")
    with open(ts_path, encoding="utf-8") as f:
        ts = f.read()
    slugs = []
    pattern = re.compile(r'id:\s*"(\d+)"[\s\S]*?company:\s*"([^"]+)"')
    for m in pattern.finditer(ts):
        slugs.append((m.group(2), m.group(1), f"{slugify(m.group(2))}-{m.group(1)}"))
    return slugs

def load_api_keys():
    keys = []
    for i in range(1, 9):
        val = os.environ.get(f"OPENROUTER_API_{i}") or os.environ.get(f"OPENROUTER_API_KEY_{i}")
        if val:
            keys.append({"key": val.strip(), "index": i})
    return keys

# ── Main ───────────────────────────────────────────────────────────
def main():
    FORCE = "--force" in sys.argv
    LIMIT = None
    for arg in sys.argv:
        if arg.startswith("--limit="):
            try: LIMIT = int(arg.split("=")[1])
            except: pass

    api_keys = load_api_keys()
    if not api_keys:
        print("[AI Analysis] No OPENROUTER_API_1..8 keys found.")
        print("[AI Analysis] Set them as environment variables and try again.")
        sys.exit(1)
    print(f"[AI Analysis] Loaded {len(api_keys)} OpenRouter API keys")

    with open(os.path.join(DATA_DIR, "ipo_master_database.json"), encoding="utf-8") as f:
        db = json.load(f)
    master_lookup = {}
    for ipo in db["ipos"]:
        master_lookup[ipo.get("company_name", "").lower().strip()] = ipo
    print(f"[AI Analysis] Loaded {len(master_lookup)} master DB entries")

    src_path = os.path.join(SRC_DIR, "ipoComprehensiveAnalysis.json")
    existing = {}
    try:
        with open(src_path, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"[AI Analysis] Loaded {len(existing)} existing entries")
    except (FileNotFoundError, json.JSONDecodeError):
        print("[AI Analysis] No existing file found")

    slug_map = extract_slugs_from_ts()
    print(f"[AI Analysis] Found {len(slug_map)} IPOs in TS")

    company_to_slug = {}
    for company, id_val, slug in slug_map:
        company_to_slug[company.lower().strip()] = (id_val, slug)

    to_process = []
    for company_lower, (id_val, slug) in company_to_slug.items():
        ipo = master_lookup.get(company_lower)
        if not ipo:
            continue
        if not FORCE and slug in existing:
            continue
        to_process.append((ipo, slug))

    if LIMIT and len(to_process) > LIMIT:
        to_process = to_process[:LIMIT]
        print(f"[AI Analysis] Limited to {LIMIT} IPOs for testing")

    if not to_process:
        print("[AI Analysis] All IPOs already analyzed, nothing to do (use --force to redo)")
        sys.exit(0)

    print(f"[AI Analysis] Processing {len(to_process)}/{len(slug_map)} IPOs via OpenRouter")
    print(f"[AI Analysis] ~{len(to_process) // (len(api_keys) * RPM_PER_KEY)} min estimated")

    output = {}

    # Load existing entries that we should keep
    if not FORCE:
        for slug, entry in existing.items():
            output[slug] = entry

    lock = threading.Lock()
    done = [0]
    failed = [0]

    def _process(item):
        ipo, slug = item
        name = ipo.get("company_name", "Unknown")
        result = generate_entry(ipo, slug, api_keys)
        with lock:
            done[0] += 1
            if result:
                output[slug] = result
                failed[0] = failed[0]
                print(f"[AI Analysis] [{done[0]}/{len(to_process)}] OK {name}")
            else:
                failed[0] += 1
                print(f"[AI Analysis] [{done[0]}/{len(to_process)}] FAIL {name}")
            if done[0] % 5 == 0:
                with open(src_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                size_mb = os.path.getsize(src_path) / 1024 / 1024
                print(f"[AI Analysis] Auto-saved {len(output)} entries ({size_mb:.1f} MB)")

    max_workers = min(len(api_keys) * 2, 16)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(_process, item) for item in to_process]
        for f in as_completed(futures):
            pass

    # Final save
    with open(src_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    size_mb = os.path.getsize(src_path) / 1024 / 1024

    print(f"\n[AI Analysis] Done! {len(output)} entries -> {src_path}")
    print(f"[AI Analysis] Size: {size_mb:.1f} MB")
    print(f"[AI Analysis] Succeeded: {len(to_process) - failed[0]}, Failed: {failed[0]}")

if __name__ == "__main__":
    main()
