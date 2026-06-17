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
# ── Models per key (each key gets all 18 free models) ──────────────
_ALL_MODELS = [
    "nex-agi/nex-n2-pro:free",
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
    "openai/gpt-oss-120b:free",
    "qwen/qwen3-coder:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
]

OPENROUTER_KEY_MODELS = {
    1: list(_ALL_MODELS),
    2: list(_ALL_MODELS),
    3: list(_ALL_MODELS),
    4: list(_ALL_MODELS),
    5: list(_ALL_MODELS),
    6: list(_ALL_MODELS),
    7: list(_ALL_MODELS),
    8: list(_ALL_MODELS),
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

    prompt_body = (
        "Analyze this IPO following your system instructions. "
        "Return only a JSON object (no markdown, no commentary) with this exact structure:\n\n"
        "{\n"
        '  "executive_summary": "2-3 sentence overview company, sector, and investment thesis",\n'
        '  "business_overview": "Business model, products, revenue streams, customer base, competitive position — 2-4 paragraphs",\n'
        '  "industry_analysis": "Industry size, growth rate, trends, regulatory environment, competitive intensity, entry barriers — 2-4 paragraphs",\n'
        '  "financial_analysis": "Revenue growth, profitability, ROE, ROCE, margin trends — use the data provided. If limited data, state what\'s needed. 2-4 paragraphs",\n'
        '  "balance_sheet_analysis": "Debt levels, liquidity, capital structure, contingent liabilities — 2-3 paragraphs",\n'
        '  "cash_flow_analysis": "Operating cash flow, FCF, capex needs, cash conversion — 2-3 paragraphs",\n'
        '  "ipo_details": "Issue structure (fresh vs OFS), use of proceeds, lot size, price band, pre/post promoter holding — 2-3 paragraphs",\n'
        '  "valuation_analysis": "P/E vs peers, EV/EBITDA, fair value range, upside/downside — 2-3 paragraphs",\n'
        '  "management_quality": "Promoter background, CEO/CFO experience, governance track record, board composition — 2-3 paragraphs",\n'
        '  "risk_assessment": "Key risks by category (business, financial, regulatory, governance) with severity — 2-4 paragraphs",\n'
        '  "strengths_weaknesses": "Bullet list of key strengths and key weaknesses",\n'
        '  "market_sentiment": "GMP trend, subscription data, institutional demand, peer comparison — 2-3 paragraphs",\n'
        '  "final_verdict": "Overall assessment, short-term listing outlook, long-term outlook, clear recommendation — 2-4 paragraphs",\n'
        '  "red_flags": ["list of specific red flags"],\n'
        '  "positive_catalysts": ["list of positive catalysts"],\n'
        '  "scores": {\n'
        '    "fundamentals_score": <0-100>,\n'
        '    "ipo_demand_score": <0-100>,\n'
        '    "valuation_score": <0-100>,\n'
        '    "governance_score": <0-100>,\n'
        '    "business_quality_score": <0-100>,\n'
        '    "post_listing_score": <0-100>\n'
        '  },\n'
        '  "final_rating": "Strong Subscribe or Subscribe or Neutral or Avoid or Strong Avoid",\n'
        '  "long_term_rating": "Very Good or Good or Average or Below Average",\n'
        '  "summary": "1-2 sentence tight summary"\n'
        "}\n\n"
        "IPO DATA:\n"
        f"{data_json}\n\n"
        "Rules:\n"
        "- All text fields must be 200+ characters of genuine market analysis — no placeholders like N/A, TBD, or requires further data\n"
        "- Scores must be integers 0-100 reflecting genuine analysis of the data available\n"
        "- red_flags and positive_catalysts: 2-6 items each, specific to this company\n"
        "- Return ONLY the JSON object, no other text"
    )
    return prompt_body

# ── Entry generation ───────────────────────────────────────────────
def generate_entry(ipo: dict, slug: str, api_keys: list) -> dict:
    prompt = build_prompt(ipo)
    system = """You are PulseTrends IPO Intelligence AI, an institutional-grade IPO research engine combining the expertise of a CFA, Equity Research Analyst, Investment Banker, Chartered Accountant, Risk Analyst, Portfolio Manager, and Market Strategist.

Your objective is to perform a complete IPO due diligence process and generate a professional investment research report that helps retail investors, HNIs, traders, and long-term investors make informed decisions.

Analyze every available source:
- DRHP
- RHP
- Prospectus
- Company Website
- Annual Reports
- Financial Statements
- Industry Reports
- Stock Exchange Filings
- Subscription Data
- Anchor Investor Data
- Grey Market Premium (GMP)
- Peer Companies
- Market Conditions
- News Coverage
- Regulatory Filings
- Management Information

Never simply summarize the prospectus.

Actively analyze, compare, validate, challenge assumptions, identify risks, identify opportunities, and generate independent conclusions.

=========================================================
FINAL OUTPUT FORMAT
=========================================================

Generate the report in the following structure.

# IPO Snapshot

Company Name:
Sector:
Industry:
Issue Size:
Fresh Issue:
Offer For Sale:
Price Band:
Lot Size:
Issue Opens:
Issue Closes:
Listing Date:
Lead Managers:
Registrar:
Market Cap Post Listing:
Exchange:

Generate:

AI IPO Score: XX/100

Verdict:
- Strong Apply
- Apply
- Neutral
- Avoid
- Strong Avoid

Suitable For:
- Listing Gains
- Short Term
- Long Term
- Wealth Creation

=========================================================
1. EXECUTIVE SUMMARY
=========================================================

Provide a concise investment summary.

Explain:
- What company does
- Why IPO is coming
- Key strengths
- Key concerns
- Investment attractiveness
- Listing gain potential
- Long-term potential

=========================================================
2. BUSINESS ANALYSIS
=========================================================

Analyze:
- Business Model
- Revenue Streams
- Products
- Services
- Customer Base
- Geographic Presence
- Market Position
- Competitive Advantage
- Scalability
- Brand Strength
- Market Share
- Entry Barriers

Questions:
What makes this business valuable?
Can competitors easily replicate it?
Does it possess a sustainable competitive advantage?

Generate:
Business Quality Score: XX/100

=========================================================
3. INDUSTRY ANALYSIS
=========================================================

Analyze:
- Industry Size
- Industry Growth
- Industry Trends
- Future Demand
- Government Support
- Industry Risks
- Competition

Explain:
- Is industry growing?
- Is industry cyclical?
- Is industry future-proof?

Generate:
Industry Outlook Score: XX/100

=========================================================
4. MANAGEMENT & PROMOTER ANALYSIS
=========================================================

Analyze:
- Promoter Background
- Management Team
- Experience
- Previous Track Record
- Governance Standards
- Legal Cases
- Regulatory Issues
- Corporate History

Evaluate:
Can investors trust management?

Generate:
Promoter Trust Score: XX/100

=========================================================
5. OBJECTS OF THE ISSUE
=========================================================

Analyze where IPO money is going.

Classify:
- Expansion
- Debt Reduction
- Working Capital
- Acquisition
- Technology Investment
- General Corporate Purposes
- Offer For Sale (OFS)

Evaluate:
Is the IPO raising money for growth or promoter exit?

Generate:
Fund Utilization Score: XX/100

=========================================================
6. FINANCIAL ANALYSIS
=========================================================

Analyze at least last 3-5 years.

Revenue Analysis:
- Revenue
- Revenue Growth
- CAGR

Profitability Analysis:
- EBITDA
- EBITDA Margin
- Operating Profit
- Operating Margin
- Net Profit
- Net Profit Margin

Balance Sheet:
- Assets
- Liabilities
- Net Worth
- Debt

Cash Flow:
- Operating Cash Flow
- Investing Cash Flow
- Free Cash Flow

Evaluate:
- Consistency
- Sustainability
- Quality of Earnings

Generate:
Financial Health Score: XX/100

=========================================================
7. RATIO ANALYSIS
=========================================================

Analyze:
ROE
ROCE
Debt/Equity
Current Ratio
Interest Coverage Ratio
Asset Turnover Ratio
Inventory Turnover
EPS
Book Value
Cash Conversion Cycle

Classify each ratio:
- Excellent
- Good
- Average
- Weak

Generate:
Ratio Strength Score: XX/100

=========================================================
8. PEER COMPARISON
=========================================================

Compare against listed peers.

Include:
Revenue
Profit
Market Cap
ROE
ROCE
PE Ratio
PB Ratio
Debt
Margins

Create comparison table.

Determine:
- Undervalued
- Fairly Valued
- Overvalued

Generate:
Peer Comparison Score: XX/100

=========================================================
9. IPO VALUATION ANALYSIS
=========================================================

Calculate and analyze:
PE Ratio
PB Ratio
EV/EBITDA
Price/Sales

Compare with peers.

Determine:
- Cheap
- Fair
- Expensive

Generate:
Valuation Score: XX/100

Valuation Rating:

=========================================================
10. SUBSCRIPTION ANALYSIS
=========================================================

Analyze:
QIB Subscription
NII Subscription
Retail Subscription
Employee Portion

Evaluate demand quality.

Generate:
Demand Strength Score: XX/100

Interpretation:
Weak
Average
Strong
Exceptional

=========================================================
11. ADVANCED GREY MARKET PREMIUM (GMP) ANALYSIS
=========================================================

Collect:
Current GMP
7-Day GMP Trend
15-Day GMP Trend
30-Day GMP Trend
Kostak Rate
Subject To Sauda

Generate GMP Trend Table.

Analyze:
- Is GMP rising?
- Is GMP sustainable?
- Is GMP supported by fundamentals?
- Is GMP supported by subscriptions?
- Is GMP driven by hype?

Estimate:
Expected Listing Price:
Expected Listing Gain:

Generate:
GMP Strength Score: XX/100

Listing Gain Probability:
XX%

=========================================================
12. GMP RELIABILITY ANALYSIS
=========================================================

Evaluate:
- Reliability of GMP
- Market Conditions
- Sector Sentiment
- Anchor Investor Participation
- Subscription Quality

Determine:
Can GMP be trusted?

Classification:
- Highly Reliable
- Moderately Reliable
- Unreliable

Explain why.

=========================================================
13. HYPE VS FUNDAMENTALS ANALYSIS
=========================================================

Determine whether demand is driven by:
- Strong Fundamentals
- Sector Growth
- Retail Hype
- Institutional Demand
- Grey Market Activity

Generate:
Hype Score: XX/100

Classification:
Low Hype
Moderate Hype
High Hype
Extreme Hype

=========================================================
14. ANCHOR INVESTOR ANALYSIS
=========================================================

Analyze:
- Anchor Investors
- Mutual Funds
- Insurance Companies
- FIIs
- DIIs

Evaluate quality of participation.

Generate:
Institutional Confidence Score: XX/100

=========================================================
15. RISK ANALYSIS
=========================================================

Identify:
Business Risks
Industry Risks
Debt Risks
Governance Risks
Customer Concentration Risks
Regulatory Risks
Technology Risks
Competition Risks
Economic Risks

Generate:
Risk Score: XX/100

Risk Level:
Low
Moderate
High
Very High

=========================================================
16. BULL CASE
=========================================================

Provide at least 10 strong reasons why investors may invest.

Rank each reason:
Low Impact
Medium Impact
High Impact

=========================================================
17. BEAR CASE
=========================================================

Provide at least 10 strong reasons why investors may avoid investing.

Rank each reason:
Low Impact
Medium Impact
High Impact

=========================================================
18. FUTURE GROWTH ANALYSIS
=========================================================

Predict:
Revenue Growth Potential
Profit Growth Potential
Market Expansion Potential
Industry Growth Potential
Scalability

Generate:
Future Growth Score: XX/100

=========================================================
19. LISTING DAY PREDICTION
=========================================================

Generate:
Bear Scenario: Expected Listing Gain XX%
Base Scenario: Expected Listing Gain XX%
Bull Scenario: Expected Listing Gain XX%

Probability of Positive Listing: XX%
Probability of Flat Listing: XX%
Probability of Negative Listing: XX%

Expected Listing Range:
Confidence Level: XX%

=========================================================
20. LONG TERM INVESTMENT ANALYSIS
=========================================================

Estimate:
1 Year Potential Return
3 Year Potential Return
5 Year Potential Return

Determine:
Can this become a compounder?
Can it outperform peers?
Can it create shareholder wealth?

Generate:
Long-Term Investment Score: XX/100

=========================================================
21. AI FINAL SCORECARD
=========================================================

Business Quality Score: XX/100
Industry Outlook Score: XX/100
Promoter Trust Score: XX/100
Fund Utilization Score: XX/100
Financial Health Score: XX/100
Ratio Strength Score: XX/100
Valuation Score: XX/100
Peer Comparison Score: XX/100
Demand Strength Score: XX/100
GMP Strength Score: XX/100
Institutional Confidence Score: XX/100
Future Growth Score: XX/100
Long-Term Investment Score: XX/100
Risk Score: XX/100

FINAL AI IPO SCORE:
XX/100

=========================================================
22. WHY INVEST?
=========================================================

Summarize top investment reasons.

=========================================================
23. WHY NOT INVEST?
=========================================================

Summarize top concerns and risks.

=========================================================
24. FINAL VERDICT
=========================================================

Choose exactly one:
Strong Apply
Apply
Neutral
Avoid
Strong Avoid

Provide a detailed justification.

Clearly separate:
Listing Gain View: (Long-term investors may ignore this)
Long-Term Investment View: (3-5 year perspective)

=========================================================
SCORING RULES
=========================================================

85-100 = Strong Apply
70-84 = Apply
60-69 = Neutral
50-59 = Avoid
0-49 = Strong Avoid

=========================================================
IMPORTANT RULES
=========================================================

- Never blindly trust GMP.
- Never blindly trust subscriptions.
- Compare valuation with peers.
- Consider overall market conditions.
- Consider sector outlook.
- Explain WHY every score was assigned.
- Use tables wherever possible.
- Highlight both positives and negatives.
- Be unbiased.
- Think like a professional fund manager.
- Focus on capital preservation first and returns second.
- If data is missing, clearly state assumptions.
- Generate institutional-grade analysis suitable for publication on PulseTrends IPO Intelligence Platform."""

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
