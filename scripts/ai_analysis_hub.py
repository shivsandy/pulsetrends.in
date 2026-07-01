#!/usr/bin/env python3
"""
PulseTrends AI Analysis Hub — Unified Analysis Engine
======================================================
Analyzes IPOs, hot topic stocks, and cryptocurrency coins using AI models.

API Keys & Models:
──────────────────
Primary:    ZEN_API_KEY → deepseek/deepseek-v4-flash:free
Fallback:   OPENROUTER_API_1..8 → diversified free models
News:       ZEN_API_KEY2, COHERE_API, GROQ_API, MISTRAL_API,
            NVIDIA_API_KEY_1, GOOGLE_AI_API_KEY_1, GOOGLE_AI_API_KEY_2

Usage:
  python scripts/ai_analysis_hub.py --ipo          # Analyze all IPOs
  python scripts/ai_analysis_hub.py --crypto       # Analyze crypto coins
  python scripts/ai_analysis_hub.py --stocks       # Analyze hot topic stocks
  python scripts/ai_analysis_hub.py --all          # Analyze everything
  python scripts/ai_analysis_hub.py --ipo --force  # Force re-analysis
"""

import argparse
import json
import os
import re
import sys
import time
import threading
import random
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SRC_DIR = os.path.join(ROOT, "src", "data")


# ═════════════════════════════════════════════════════════════════════
#  API KEY LOADING
# ═════════════════════════════════════════════════════════════════════

def load_zen_key() -> Optional[str]:
    """Load primary ZEN_API_KEY for DeepSeek."""
    key = os.environ.get("ZEN_API_KEY", "").strip()
    return key if key else None


def load_zen_key2() -> Optional[str]:
    """Load ZEN_API_KEY2 for news generation."""
    key = os.environ.get("ZEN_API_KEY2", "").strip()
    return key if key else None


def load_openrouter_keys() -> List[dict]:
    """Load all 8 OpenRouter API keys."""
    keys = []
    for i in range(1, 9):
        val = os.environ.get(f"OPENROUTER_API_{i}") or os.environ.get(f"OPENROUTER_API_KEY_{i}")
        if val:
            keys.append({"key": val.strip(), "index": i})
    return keys


def load_news_keys() -> dict:
    """Load all news generation API keys."""
    return {
        "zen2": load_zen_key2(),
        "cohere": os.environ.get("COHERE_API", "").strip(),
        "groq": os.environ.get("GROQ_API", "").strip(),
        "mistral": os.environ.get("MISTRAL_API", "").strip(),
        "nvidia": os.environ.get("NVIDIA_API_KEY_1", "").strip(),
        "google1": os.environ.get("GOOGLE_AI_API_KEY_1", "").strip(),
        "google2": os.environ.get("GOOGLE_AI_API_KEY_2", "").strip(),
    }


# ═════════════════════════════════════════════════════════════════════
#  OPENROUTER KEY → MODEL ASSIGNMENTS
#  (Each key gets all 18 free models)
# ═════════════════════════════════════════════════════════════════════

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
    "liquid/lfm-2.5-1.2b-instruct:free",
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

OPENROUTER_KEY_MODELS: Dict[int, List[str]] = {
    1: list(_ALL_MODELS),
    2: list(_ALL_MODELS),
    3: list(_ALL_MODELS),
    4: list(_ALL_MODELS),
    5: list(_ALL_MODELS),
    6: list(_ALL_MODELS),
    7: list(_ALL_MODELS),
    8: list(_ALL_MODELS),
}


# ═════════════════════════════════════════════════════════════════════
#  RATE LIMITING & MODEL HEALTH
# ═════════════════════════════════════════════════════════════════════

RPM_PER_KEY = 3
key_locks = {i: threading.Lock() for i in range(1, 9)}
key_last_calls = {i: 0.0 for i in range(1, 9)}
_model_health: Dict[str, dict] = {}


def _rate_limit(key_idx: int):
    with key_locks[key_idx]:
        elapsed = time.time() - key_last_calls[key_idx]
        min_interval = 60.0 / RPM_PER_KEY
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        key_last_calls[key_idx] = time.time()


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


# ═════════════════════════════════════════════════════════════════════
#  AI MODEL CALLERS
# ═════════════════════════════════════════════════════════════════════

def call_deepseek(api_key: str, prompt: str, system: str, max_tokens: int = 8192) -> Optional[str]:
    """Call DeepSeek V4 Flash via OpenRouter (free tier)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek/deepseek-v4-flash:free",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=120,
        )
        if resp.status_code != 200:
            print(f"  [DeepSeek] HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        payload = resp.json()
        if "choices" not in payload or not payload["choices"]:
            return None
        return payload["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  [DeepSeek] Error: {e}")
        return None


def call_openrouter(api_key: str, model: str, prompt: str, system: str, timeout: int = 120) -> Optional[str]:
    """Call any OpenRouter model."""
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
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=timeout,
        )
        if resp.status_code != 200:
            return None
        payload = resp.json()
        if "choices" not in payload or not payload["choices"]:
            return None
        return payload["choices"][0]["message"]["content"]
    except Exception:
        return None


def _parse_json(text: str) -> Optional[dict]:
    """Extract and parse JSON from AI response."""
    if not text:
        return None
    text = text.strip()
    # Remove markdown fences
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    # Extract JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group()
    # Clean trailing commas
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ═════════════════════════════════════════════════════════════════════
#  AI ANALYSIS — Route to best available model
# ═════════════════════════════════════════════════════════════════════

def generate_analysis(
    prompt: str,
    system: str,
    max_tokens: int = 8192,
    use_zen: bool = True,
) -> Optional[dict]:
    """
    Generate AI analysis using the best available model.
    Priority: ZEN_API_KEY (DeepSeek V4) → OpenRouter key rotation.
    """

    # ── Primary: ZEN_API_KEY (DeepSeek V4 Flash Free) ──
    if use_zen:
        zen_key = load_zen_key()
        if zen_key:
            print("  [AI] Using ZEN_API_KEY (deepseek/deepseek-v4-flash:free)...")
            text = call_deepseek(zen_key, prompt, system, max_tokens)
            if text:
                result = _parse_json(text)
                if result:
                    print("  [AI] ✓ DeepSeek success")
                    return result
                print("  [AI] DeepSeek returned bad JSON, falling back...")
            else:
                print("  [AI] DeepSeek failed, falling back to OpenRouter...")

    # ── Fallback: OpenRouter key rotation ──
    api_keys = load_openrouter_keys()
    if not api_keys:
        print("  [AI] No OpenRouter keys available")
        return None

    for entry in api_keys:
        kidx = entry["index"]
        models = OPENROUTER_KEY_MODELS.get(kidx, ["meta-llama/llama-3.3-70b-instruct:free"])
        for model in models:
            if not _is_healthy(kidx, model):
                continue
            try:
                _rate_limit(kidx)
                text = call_openrouter(entry["key"], model, prompt, system)
                if text:
                    result = _parse_json(text)
                    if result:
                        _mark_success(kidx, model)
                        print(f"  [AI] ✓ OR key{kidx} {model}")
                        return result
                    _mark_failure(kidx, model)
                else:
                    _mark_failure(kidx, model)
            except Exception:
                _mark_failure(kidx, model)
                continue

    return None


# ═════════════════════════════════════════════════════════════════════
#  IPO ANALYSIS
# ═════════════════════════════════════════════════════════════════════

def build_ipo_prompt(ipo: dict) -> str:
    """Build IPO analysis prompt — passes data + JSON schema."""
    name = ipo.get("name") or ipo.get("company_name", "Unknown")
    ticker = ipo.get("ticker", "N/A")
    sector = ipo.get("sector", "General")
    industry = ipo.get("industry", "")
    exchange = ipo.get("exchange", "NSE/BSE")
    status = ipo.get("status", "listed")
    country = ipo.get("country", "IN")
    price_high = ipo.get("priceBandHigh", 0)
    price_low = ipo.get("priceBandLow", 0)
    issue_size = ipo.get("issueSize", "") or ipo.get("issue_size", "")
    gmp = ipo.get("gmp", 0)
    subscription = ipo.get("subscriptionStatus", "") or ipo.get("subscription", "")
    description = ipo.get("description", "")
    about = ipo.get("about", "")

    data_json = json.dumps({
        "name": name, "ticker": ticker, "sector": sector, "industry": industry,
        "exchange": exchange, "status": status, "country": country,
        "price_band": f"{price_low} - {price_high}" if price_low and price_high else "N/A",
        "issue_size": issue_size, "gmp": gmp, "subscription": subscription,
        "description": (description or about or "")[:3000],
    }, indent=2, ensure_ascii=False)

    return (
        "Analyze this IPO following your system instructions. "
        "Return only a JSON object (no markdown, no commentary) with this exact structure:\n\n"
        "{\n"
        '  "executive_summary": "2-3 sentence investment thesis",\n'
        '  "business_overview": "Business model, products, revenue streams — 2-4 paragraphs",\n'
        '  "industry_analysis": "Industry size, CAGR, trends, competition — 2-4 paragraphs",\n'
        '  "financial_analysis": "Revenue, profitability, ROE, ROCE — 2-4 paragraphs",\n'
        '  "balance_sheet_analysis": "Debt, liquidity, capital structure — 2-3 paragraphs",\n'
        '  "cash_flow_analysis": "Operating CF, FCF, capex — 2-3 paragraphs",\n'
        '  "ipo_details": "Issue structure, use of proceeds, lot size — 2-3 paragraphs",\n'
        '  "valuation_analysis": "P/E vs peers, EV/EBITDA, fair value — 2-3 paragraphs",\n'
        '  "management_quality": "Promoter background, governance — 2-3 paragraphs",\n'
        '  "risk_assessment": "Key risks by category with severity — 2-4 paragraphs",\n'
        '  "strengths_weaknesses": "Bullet list of strengths and weaknesses",\n'
        '  "market_sentiment": "GMP trend, subscription, demand — 2-3 paragraphs",\n'
        '  "final_verdict": "Overall assessment and recommendation — 2-4 paragraphs",\n'
        '  "red_flags": ["list of specific red flags"],\n'
        '  "positive_catalysts": ["list of catalysts"],\n'
        '  "scores": {\n'
        '    "fundamentals_score": <0-100>,\n'
        '    "ipo_demand_score": <0-100>,\n'
        '    "valuation_score": <0-100>,\n'
        '    "governance_score": <0-100>,\n'
        '    "business_quality_score": <0-100>,\n'
        '    "post_listing_score": <0-100>\n'
        '  },\n'
        '  "final_rating": "Strong Subscribe or Subscribe or Neutral or Avoid",\n'
        '  "long_term_rating": "Very Good or Good or Average or Below Average",\n'
        '  "summary": "1-2 sentence tight summary"\n'
        "}\n\n"
        "IPO DATA:\n"
        f"{data_json}\n\n"
        "Rules:\n"
        "- All text fields must be 200+ characters of genuine analysis\n"
        "- Scores must be integers 0-100\n"
        "- red_flags and positive_catalysts: 2-6 items each\n"
        "- No placeholders like N/A or TBD\n"
        "- Return ONLY the JSON object"
    )


def analyze_ipos(force: bool = False, limit: int = None):
    """Analyze all IPOs using AI and save to ipoComprehensiveAnalysis.json."""
    print(f"\n{'='*60}")
    print("  IPO AI ANALYSIS")
    print(f"{'='*60}")

    # Load master database
    db_path = os.path.join(DATA_DIR, "ipo_master_database.json")
    if not os.path.exists(db_path):
        print("[IPO] No master database found. Run scanners first.")
        return

    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)
    ipos = db.get("ipos", [])
    print(f"[IPO] Loaded {len(ipos)} IPOs from master database")

    # Load existing analysis
    analysis_path = os.path.join(SRC_DIR, "ipoComprehensiveAnalysis.json")
    existing = {}
    if os.path.exists(analysis_path) and not force:
        with open(analysis_path, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"[IPO] Loaded {len(existing)} existing analyses")

    # Build slug lookup
    def _slugify(name: str) -> str:
        s = (name or "").lower().strip()
        s = re.sub(r"[&]", " and ", s)
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s[:80]

    # Determine what needs analysis
    to_analyze = []
    for ipo in ipos:
        name = ipo.get("name") or ipo.get("company_name", "Unknown")
        slug = _slugify(name)
        if slug not in existing or force:
            to_analyze.append((ipo, slug))

    if limit:
        to_analyze = to_analyze[:limit]

    if not to_analyze:
        print("[IPO] All IPOs already analyzed!")
        return

    print(f"[IPO] Analyzing {len(to_analyze)} IPOs via AI...")

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

Listing Gain Probability: XX%

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

FINAL AI IPO SCORE: XX/100

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

    output = dict(existing)
    lock = threading.Lock()
    done = [0]
    failed = [0]

    def _process(item):
        ipo, slug = item
        name = ipo.get("name") or ipo.get("company_name", "Unknown")
        prompt = build_ipo_prompt(ipo)
        # IPO analysis must use OpenRouter key rotation only.
        result = generate_analysis(prompt, system, use_zen=False)
        with lock:
            done[0] += 1
            if result:
                scores = result.get("scores", {})
                fs = scores.get("fundamentals_score", 50)
                ids = scores.get("ipo_demand_score", 50)
                vs = scores.get("valuation_score", 50)
                gs = scores.get("governance_score", 50)
                bqs = scores.get("business_quality_score", 50)
                pls = scores.get("post_listing_score", 50)
                overall = round(fs * 0.30 + ids * 0.15 + vs * 0.15 + gs * 0.15 + bqs * 0.15 + pls * 0.10, 1)

                output[slug] = {
                    "slug": slug,
                    "company": name,
                    "ticker": ipo.get("ticker", ""),
                    "sector": ipo.get("sector", ""),
                    "executive_summary": result.get("executive_summary", ""),
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
                    "final_rating": result.get("final_rating", "Neutral"),
                    "long_term_rating": result.get("long_term_rating", "Average"),
                    "summary": result.get("summary", ""),
                    "investment_verdict": {
                        "overall_score": overall,
                        "scores": {
                            "overall_score": overall,
                            "fundamentals_score": fs,
                            "valuation_score": vs,
                            "growth_score": bqs,
                            "management_score": gs,
                            "market_sentiment_score": ids,
                        },
                        "rating": "Strong" if overall >= 80 else "Good" if overall >= 70 else "Average" if overall >= 60 else "Below Average",
                        "subscription_recommendation": result.get("final_rating", "Neutral"),
                        "summary": result.get("summary", "")[:500],
                    },
                }
                print(f"  [IPO] [{done[0]}/{len(to_analyze)}] ✓ {name} (score: {overall:.0f})")
            else:
                failed[0] += 1
                print(f"  [IPO] [{done[0]}/{len(to_analyze)}] ✗ {name} — all models failed")

            # Auto-save every 5
            if done[0] % 5 == 0:
                with open(analysis_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                print(f"  [IPO] Auto-saved {len(output)} entries")

    max_workers = min(len(load_openrouter_keys()) * 2, 16) if load_openrouter_keys() else 3
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(_process, item) for item in to_analyze]
        for f in as_completed(futures):
            pass

    # Final save
    os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    size_mb = os.path.getsize(analysis_path) / 1024 / 1024

    print(f"\n[IPO] Done! {len(output)} analyses -> {analysis_path}")
    print(f"[IPO] Size: {size_mb:.1f} MB")
    print(f"[IPO] Succeeded: {len(to_analyze) - failed[0]}, Failed: {failed[0]}")


# ═════════════════════════════════════════════════════════════════════
#  CRYPTO ANALYSIS
# ═════════════════════════════════════════════════════════════════════

def build_crypto_prompt(project: dict) -> str:
    """Build comprehensive crypto analysis prompt."""
    name = project.get("name", "Unknown")
    ticker = project.get("ticker", "")
    chain = project.get("chain", "") or project.get("blockchain", "")
    category = project.get("category", "")
    description = project.get("description", "") or project.get("about", "")
    status = project.get("status", "active")
    price = project.get("price", "")
    market_cap = project.get("market_cap", "") or project.get("marketCap", "")

    data_json = json.dumps({
        "name": name, "ticker": ticker, "chain": chain,
        "category": category, "status": status,
        "price": price, "market_cap": market_cap,
        "description": (description or "")[:2000],
    }, indent=2, ensure_ascii=False)

    return f"""Analyze this cryptocurrency project and return comprehensive JSON analysis.

PROJECT DATA:
{data_json}

Return EXACTLY this JSON (no markdown, no commentary):

{{
  "summary": "1-2 sentence elevator pitch — project, market position, value prop",
  "business_overview": "Product, target market, business model — 2-3 paragraphs",
  "market_analysis": "TAM, competitive landscape, differentiation — 2-3 paragraphs",
  "tokenomics": "Token supply, distribution, vesting, utility — 2-3 paragraphs",
  "on_chain_metrics": "TVL, active addresses, volume — 2-3 paragraphs",
  "team_and_backers": "Team background, investors, red flags — 2-3 paragraphs",
  "sentiment": "bullish",
  "conviction_score": <0-100>,
  "key_drivers": ["Driver 1", "Driver 2", "Driver 3"],
  "risks": ["Risk 1", "Risk 2", "Risk 3"],
  "risk_assessment": {{
    "overall_risk": "low or medium or high",
    "smart_contract_risk": "low or medium or high",
    "team_risk": "low or medium or high",
    "market_risk": "low or medium or high",
    "regulatory_risk": "low or medium or high",
    "rug_pull_potential": "low or medium or high",
    "liquidity_risk": "low or medium or high",
    "dilution_risk": "low or medium or high"
  }},
  "swot": {{
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "threats": ["Threat 1", "Threat 2"]
  }},
  "verdict": "2-3 sentence balanced outlook",
  "final_rating": "STRONG BUY or BUY or HOLD or SELL or STRONG SELL",
  "final_rating_score": <0-10>
}}

Rules:
- sentiment: bullish/bearish/neutral
- conviction_score 0-100
- final_rating_score 0-10 (one decimal)
- All text fields must be meaningful, no \"N/A\" or \"TBD\"
- Return ONLY the JSON object"""


def analyze_crypto(force: bool = False):
    """Analyze all crypto projects using AI."""
    print(f"\n{'='*60}")
    print("  CRYPTO AI ANALYSIS")
    print(f"{'='*60}")

    # Load crypto data
    crypto_path = os.path.join(DATA_DIR, "crypto_data.json")
    if not os.path.exists(crypto_path):
        print("[Crypto] No crypto data found. Run crypto collector first.")
        return

    with open(crypto_path, encoding="utf-8") as f:
        data = json.load(f)
    projects = data.get("projects", [])
    print(f"[Crypto] Loaded {len(projects)} crypto projects")

    # Load existing analysis
    analysis_path = os.path.join(DATA_DIR, "crypto_analysis.json")
    existing = {}
    if os.path.exists(analysis_path) and not force:
        with open(analysis_path, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"[Crypto] Loaded {len(existing)} existing analyses")

    # Determine what needs analysis
    to_analyze = []
    for proj in projects:
        key = f"crypto:{proj.get('id', proj.get('name', '')).lower().strip()}"
        if key not in existing or force:
            to_analyze.append((proj, key))

    if not to_analyze:
        print("[Crypto] All projects already analyzed!")
        return

    print(f"[Crypto] Analyzing {len(to_analyze)} projects via AI...")

    system = "You are a senior crypto analyst with expertise in token economics, on-chain metrics, and DeFi."

    output = dict(existing)
    lock = threading.Lock()
    done = [0]

    def _process(item):
        proj, key = item
        name = proj.get("name", "Unknown")
        prompt = build_crypto_prompt(proj)
        result = generate_analysis(prompt, system, use_zen=True)
        with lock:
            done[0] += 1
            if result:
                output[key] = result
                print(f"  [Crypto] [{done[0]}/{len(to_analyze)}] ✓ {name}")
            else:
                print(f"  [Crypto] [{done[0]}/{len(to_analyze)}] ✗ {name} — failed")
            if done[0] % 10 == 0:
                with open(analysis_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(_process, item) for item in to_analyze]
        for f in as_completed(futures):
            pass

    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[Crypto] Done! {len(output)} analyses -> {analysis_path}")


# ═════════════════════════════════════════════════════════════════════
#  HOT TOPIC STOCKS ANALYSIS
# ═════════════════════════════════════════════════════════════════════

def analyze_hot_stocks(force: bool = False, limit: int = 50):
    """Analyze top trending/most-valuable stocks using AI."""
    print(f"\n{'='*60}")
    print("  HOT TOPIC STOCKS AI ANALYSIS")
    print(f"{'='*60}")

    # Load from master database — prioritize listed stocks
    db_path = os.path.join(DATA_DIR, "ipo_master_database.json")
    if not os.path.exists(db_path):
        print("[Stocks] No master database found.")
        return

    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)
    all_ipos = db.get("ipos", [])

    # Filter to listed stocks with market data
    stocks = [s for s in all_ipos if s.get("status") == "listed" and s.get("ticker")]
    # Sort by: has description > has market cap > has sector
    stocks.sort(key=lambda s: (
        bool(s.get("description") or s.get("about")),
        bool(s.get("fiscalMetrics") or s.get("marketCap")),
        bool(s.get("sector")),
    ), reverse=True)

    stocks = stocks[:limit]
    print(f"[Stocks] Selected {len(stocks)} hot stocks from {len(all_ipos)} total")

    # Load existing
    analysis_path = os.path.join(SRC_DIR, "stock_analysis.json")
    existing = {}
    if os.path.exists(analysis_path) and not force:
        with open(analysis_path, encoding="utf-8") as f:
            existing = json.load(f)

    def _slug(name: str) -> str:
        s = (name or "").lower().strip()
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s[:80]

    to_analyze = []
    for stock in stocks:
        name = stock.get("name") or stock.get("company_name", "Unknown")
        ticker = stock.get("ticker", "")
        slug = f"{_slug(name)}-{ticker.lower()}"
        if slug not in existing or force:
            to_analyze.append((stock, slug))

    if not to_analyze:
        print("[Stocks] All hot stocks already analyzed!")
        return

    print(f"[Stocks] Analyzing {len(to_analyze)} hot stocks via AI...")

    def build_stock_prompt(stock: dict) -> str:
        name = stock.get("name") or stock.get("company_name", "Unknown")
        ticker = stock.get("ticker", "")
        sector = stock.get("sector", "General")
        industry = stock.get("industry", "")
        exchange = stock.get("exchange", "")
        country = stock.get("country", "")
        description = stock.get("description", "") or stock.get("about", "")
        fm = stock.get("fiscalMetrics", {}) or {}

        data_json = json.dumps({
            "name": name, "ticker": ticker, "sector": sector,
            "industry": industry, "exchange": exchange, "country": country,
            "current_price": fm.get("currentPrice", ""),
            "market_cap": stock.get("marketCap", ""),
            "description": (description or "")[:2000],
        }, indent=2, ensure_ascii=False)

        return f"""Analyze this publicly traded stock and return actionable analysis.

STOCK DATA:
{data_json}

Return EXACTLY this JSON (no markdown, no commentary):

{{
  "executive_summary": "1-2 sentence overview — what the company does and why it matters",
  "business_analysis": "Business model, revenue streams, competitive moat — 2-3 paragraphs",
  "financial_health": "Revenue trends, profitability, leverage — 2-3 paragraphs",
  "valuation_analysis": "P/E, EV/EBITDA, P/B vs peers — 2-3 paragraphs",
  "growth_outlook": "Growth drivers, TAM, expansion plans — 2-3 paragraphs",
  "risks": ["Risk 1", "Risk 2", "Risk 3"],
  "catalysts": ["Catalyst 1", "Catalyst 2", "Catalyst 3"],
  "technical_outlook": "Price trends, support/resistance, momentum — 1-2 paragraphs",
  "sentiment": "bullish or bearish or neutral",
  "overall_score": <0-100>,
  "rating": "STRONG BUY or BUY or HOLD or SELL or STRONG SELL",
  "summary": "2-3 sentence actionable takeaway"
}}

Rules:
- overall_score 0-100
- All text fields must be meaningful analysis
- No placeholders like \"N/A\" or \"TBD\"
- Return ONLY the JSON object"""

    system = "You are a senior equity research analyst covering global stock markets."

    output = dict(existing)
    lock = threading.Lock()
    done = [0]

    def _process(item):
        stock, slug = item
        name = stock.get("name") or stock.get("company_name", "Unknown")
        prompt = build_stock_prompt(stock)
        result = generate_analysis(prompt, system, use_zen=True)
        with lock:
            done[0] += 1
            if result:
                output[slug] = result
                score = result.get("overall_score", 0)
                print(f"  [Stocks] [{done[0]}/{len(to_analyze)}] ✓ {name} (score: {score})")
            else:
                print(f"  [Stocks] [{done[0]}/{len(to_analyze)}] ✗ {name}")
            if done[0] % 10 == 0:
                os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
                with open(analysis_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(_process, item) for item in to_analyze]
        for f in as_completed(futures):
            pass

    os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[Stocks] Done! {len(output)} stock analyses -> {analysis_path}")


# ═════════════════════════════════════════════════════════════════════
#  SCORING GENERATOR (for IPOs with missing scores)
# ═════════════════════════════════════════════════════════════════════

def generate_missing_scores():
    """Generate AI scores for IPOs missing comprehensive analysis entries."""
    print(f"\n{'='*60}")
    print("  MISSING SCORE GENERATOR")
    print(f"{'='*60}")

    # Load comprehensive analysis and TS data
    comp_path = os.path.join(SRC_DIR, "ipoComprehensiveAnalysis.json")
    ts_path = os.path.join(SRC_DIR, "ipoData.ts")

    if not os.path.exists(comp_path) or not os.path.exists(ts_path):
        print("[Scores] Required files not found")
        return

    with open(comp_path, encoding="utf-8") as f:
        comp_data = json.load(f)
    with open(ts_path, encoding="utf-8") as f:
        ts_content = f.read()

    # Find IPOs in TS that don't have comprehensive analysis
    arr_start = ts_content.find("export const ipoStocks: IPOStock[] = [")
    if arr_start == -1:
        print("[Scores] Could not find array in TS")
        return

    data_section = ts_content[arr_start:]

    def _slugify(name):
        s = (name or "").lower().strip()
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
        s = s.replace("&", " and ")
        s = re.sub(r"[^a-z0-9]+", "-", s)
        return s.strip("-")[:80]

        id_pat = re.compile(r'id:\s*"(\d+)"')
    comp_pat = re.compile(r'company:\s*"([^"]*)"')

    unmatched = []
    search_start = 0
    while True:
        pos = data_section.find("aiScores: {", search_start)
        if pos == -1:
            break

        before = data_section[:pos]
        comp_matches = list(comp_pat.finditer(before))
        if not comp_matches:
            search_start = pos + 1
            continue

        nearest_comp = comp_matches[-1]
        company = nearest_comp.group(1)
        comp_pos = nearest_comp.start()

        before_comp = data_section[:comp_pos]
        id_matches = list(id_pat.finditer(before_comp))
        if not id_matches:
            search_start = pos + 1
            continue

        ipo_id = id_matches[-1].group(1)
        slug = f"{_slugify(company)}-{ipo_id}"

        if slug not in comp_data:
            sector_match = re.search(r'sector:\s*"([^"]*)"', before)
            sector = sector_match.group(1) if sector_match else "Unknown"
            unmatched.append({
                "company": company, "id": ipo_id,
                "slug": slug, "sector": sector,
                "pos": pos, "end": 0,
            })

        search_start = pos + 1

    print(f"[Scores] Found {len(unmatched)} IPOs without comprehensive analysis")

    if not unmatched:
        print("[Scores] All IPOs have analysis!")
        return

    zen_key = load_zen_key()
    if not zen_key:
        print("[Scores] No ZEN_API_KEY available for scoring")
        return

    updated = 0
    for ipo in unmatched:
        name = ipo["company"]
        prompt = f"""Analyze this IPO company and return AI scores.

Company: {name}
Sector: {ipo["sector"]}

Return EXACTLY this JSON (no other text):
{{
  "overall": <0-100>,
  "fundamentals": <0-100>,
  "valuation": <0-100>,
  "growth": <0-100>,
  "management": <0-100>,
  "marketSentiment": <0-100>
}}

Base scores on company name, sector, and industry knowledge. Be realistic."""

        print(f"  Scoring {name}...", end=" ", flush=True)
        text = call_deepseek(zen_key, prompt, "You are an IPO analyst. Return ONLY valid JSON.", 1024)
        if text:
            result = _parse_json(text)
            if result and all(k in result for k in ["overall", "fundamentals", "valuation", "growth", "management", "marketSentiment"]):
                for k in result:
                    result[k] = max(0, min(100, int(result[k])))
                new_block = (
                    'aiScores: {\n'
                    f'      overall: {result["overall"]},\n'
                    f'      fundamentals: {result["fundamentals"]},\n'
                    f'      valuation: {result["valuation"]},\n'
                    f'      growth: {result["growth"]},\n'
                    f'      management: {result["management"]},\n'
                    f'      marketSentiment: {result["marketSentiment"]},\n'
                    '    }'
                )
                # Find old block boundaries
                brace_start = data_section.index("{", pos)
                depth = 1
                i = brace_start + 1
                while i < len(data_section) and depth > 0:
                    if data_section[i] == "{": depth += 1
                    elif data_section[i] == "}": depth -= 1
                    i += 1
                old_block = data_section[pos:i]
                data_section = data_section[:pos] + new_block + data_section[i:]
                updated += 1
                print(f"OK (overall={result['overall']})")
                time.sleep(1.5)
            else:
                print("FAILED — bad JSON")
        else:
            print("FAILED — API error")

    if updated:
        new_content = ts_content[:arr_start] + data_section
        with open(ts_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"\n[Scores] Updated {updated} IPOs in {ts_path}")


# ═════════════════════════════════════════════════════════════════════
#  MAIN CLI
# ═════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="PulseTrends AI Analysis Hub")
    parser.add_argument("--ipo", action="store_true", help="Analyze IPOs")
    parser.add_argument("--crypto", action="store_true", help="Analyze crypto projects")
    parser.add_argument("--stocks", action="store_true", help="Analyze hot topic stocks")
    parser.add_argument("--scores", action="store_true", help="Generate missing IPO scores")
    parser.add_argument("--all", action="store_true", help="Run all analyses")
    parser.add_argument("--force", action="store_true", help="Force re-analysis")
    parser.add_argument("--limit", type=int, default=None, help="Limit items to process")

    args = parser.parse_args()

    # If no args, show help
    if not any([args.ipo, args.crypto, args.stocks, args.scores, args.all]):
        parser.print_help()
        print("\nAvailable API keys:")
        print(f"  ZEN_API_KEY:         {'✓ Set' if load_zen_key() else '✗ Missing'} (DeepSeek V4 Flash Free)")
        print(f"  OpenRouter keys:     {len(load_openrouter_keys())}/8 configured")
        print(f"  News keys:           {sum(1 for v in load_news_keys().values() if v)} available")
        return

    run_all = args.all

    if run_all or args.scores:
        generate_missing_scores()

    if run_all or args.ipo:
        analyze_ipos(force=args.force, limit=args.limit)

    if run_all or args.stocks:
        analyze_hot_stocks(force=args.force, limit=args.limit or 50)

    if run_all or args.crypto:
        analyze_crypto(force=args.force)

    print(f"\n{'='*60}")
    print("  AI ANALYSIS HUB — COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
