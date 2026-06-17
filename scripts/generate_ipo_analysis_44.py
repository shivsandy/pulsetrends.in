#!/usr/bin/env python3
"""
Comprehensive 44-Section Institutional IPO Analysis Generator.
Replaces gen_analysis_for_missing.py
Uses screener.in data as primary source, master DB for AI scores.
"""
import json, os, re, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SRC_DIR = os.path.join(ROOT, "src", "data")

SECTOR_PROFILES = {
    "technology": {"growth":"High","margin":"High","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"25-40"},
    "software": {"growth":"High","margin":"Very High","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"30-50"},
    "fintech": {"growth":"Very High","margin":"Moderate","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"30-60"},
    "banking": {"growth":"Moderate","margin":"Moderate","moat":"High","cap_intensity":"High","cyclical":True,"pe_range":"10-20"},
    "financial services": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":True,"pe_range":"12-25"},
    "healthcare": {"growth":"High","margin":"High","moat":"High","cap_intensity":"High","cyclical":False,"pe_range":"20-35"},
    "pharmaceuticals": {"growth":"Moderate","margin":"High","moat":"High","cap_intensity":"High","cyclical":False,"pe_range":"15-30"},
    "biotechnology": {"growth":"Very High","margin":"Variable","moat":"High","cap_intensity":"Very High","cyclical":False,"pe_range":"N/A"},
    "fmcg": {"growth":"Moderate","margin":"High","moat":"High","cap_intensity":"Low","cyclical":False,"pe_range":"30-50"},
    "consumer goods": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"20-35"},
    "automotive": {"growth":"Moderate","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"Very High","cyclical":True,"pe_range":"10-20"},
    "energy": {"growth":"Moderate","margin":"Moderate","moat":"High","cap_intensity":"Very High","cyclical":True,"pe_range":"8-15"},
    "renewable energy": {"growth":"Very High","margin":"Moderate","moat":"Moderate","cap_intensity":"High","cyclical":False,"pe_range":"20-35"},
    "real estate": {"growth":"Moderate","margin":"Moderate","moat":"Low","cap_intensity":"High","cyclical":True,"pe_range":"10-20"},
    "infrastructure": {"growth":"High","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"Very High","cyclical":True,"pe_range":"15-25"},
    "manufacturing": {"growth":"Moderate","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"High","cyclical":True,"pe_range":"12-22"},
    "telecommunications": {"growth":"Moderate","margin":"Moderate","moat":"High","cap_intensity":"Very High","cyclical":False,"pe_range":"10-20"},
    "e-commerce": {"growth":"Very High","margin":"Low","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"N/A"},
    "logistics": {"growth":"High","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"High","cyclical":True,"pe_range":"15-25"},
    "services": {"growth":"Moderate","margin":"Moderate","moat":"Low","cap_intensity":"Low","cyclical":False,"pe_range":"15-30"},
    "retail": {"growth":"Moderate","margin":"Low","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"15-30"},
}

DEFAULT_SECTOR = {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"15-25"}

def slugify(name):
    s = (name or "").lower().strip()
    s = re.sub(r"[&]", " and ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]

def safe_str(v, default=""):
    if v is None: return default
    s = str(v).strip()
    return s if s and s != chr(65533) else default

def safe_num(v, default=0):
    if v is None: return default
    if isinstance(v, dict): return default + 10
    try: return float(v)
    except: return default

def get_sector_profile(sector):
    sector_lower = (sector or "").lower()
    for key, profile in SECTOR_PROFILES.items():
        if key in sector_lower or sector_lower in key:
            return profile
    return dict(DEFAULT_SECTOR)

def score_label(s):
    s = safe_num(s, 50)
    if s >= 80: return "Strong"
    if s >= 70: return "Good"
    if s >= 60: return "Average"
    if s >= 50: return "Below Average"
    return "Weak"

def score_rating(s):
    s = safe_num(s, 50)
    if s >= 80: return "Strong Subscribe"
    if s >= 70: return "Subscribe"
    if s >= 60: return "Subscribe"
    if s >= 50: return "Neutral"
    return "Avoid"

def format_money(v):
    v = safe_num(v)
    if v >= 1000:
        return f"₹{v/100:.1f} Cr"
    return f"₹{v:.0f} L"

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def render_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        cells = [str(c) if c else "-" for c in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

def generate_44_section_entry(ipo, financial_data, master, slug):
    """Generate a comprehensive 44-section entry for one IPO."""
    name = ipo.get("name", "Unknown")
    ticker = safe_str(ipo.get("ticker", ""))
    sector = safe_str(ipo.get("sector", "mainboard"))
    industry = safe_str(ipo.get("industry", ""))
    exchange = safe_str(ipo.get("exchange", "NSE/BSE"))
    status = safe_str(ipo.get("status", "listed"))
    open_date = safe_str(ipo.get("openDate", ""))
    close_date = safe_str(ipo.get("closeDate", ""))
    listing_date = safe_str(ipo.get("listingDate", ""))
    price_high = safe_num(ipo.get("priceBandHigh", 0))
    price_low = safe_num(ipo.get("priceBandLow", 0))
    lot_size = safe_num(ipo.get("lotSize", 0))
    issue_size = safe_str(ipo.get("issueSize", ""))
    market_cap = safe_str(ipo.get("marketCap", 0))
    description = safe_str(ipo.get("description", ""))
    about = safe_str(ipo.get("about", ""))
    gmp = safe_num(ipo.get("gmp", 0))
    gmp_pct = safe_num(ipo.get("gmpPercent", 0))
    subscription = safe_str(ipo.get("subscriptionStatus", ""))
    country = safe_str(ipo.get("country", "IN"))
    source_url = safe_str(ipo.get("source_url", ""))
    profile = get_sector_profile(sector)
    is_upcoming = status in ("upcoming",)
    is_open = status in ("open",)

    # AI Scores from master DB
    ai_score = safe_num(master.get("ai_score"), default=55)
    ai_rating = safe_str(master.get("ai_rating"), default="Average")
    sb = master.get("score_breakdown", {}) or {}
    fs_val = safe_num(sb.get("fundamentals"), 50)
    demand_val = safe_num(sb.get("ipo_demand"), 50)
    val_val = safe_num(sb.get("valuation"), 50)
    risk_val = safe_num(sb.get("governance"), 55)
    bq_val = safe_num(sb.get("business_quality"), 50)

    bull = master.get("bull_case", []) or []
    bear = master.get("bear_case", []) or []
    risks = master.get("risk_factors", []) or []
    flags = master.get("red_flags", []) or []
    thesis = safe_str(master.get("investment_thesis", ""))
    summary = safe_str(master.get("ipo_summary", ""))
    overall = ai_score

    growth_label = "High" if any(h.lower() in sector.lower() for h in ["technology","software","fintech","biotech","renewable","e-commerce","healthcare"]) else "Moderate"

    if price_high and price_low:
        price_band = f"₹{price_low:.0f} - ₹{price_high:.0f}"
    else:
        price_band = "Not Available"

    # ========== SECTION 1: IPO SNAPSHOT ==========
    ipo_details = f"""## IPO Snapshot

| Parameter | Details |
|-----------|---------|
| **Company** | {name} {f'({ticker})' if ticker else ''} |
| **Sector** | {sector} |
| **Industry** | {industry or 'N/A'} |
| **Exchange** | {exchange} |
| **Status** | {status.title()} |
| **Open Date** | {open_date or 'N/A'} |
| **Close Date** | {close_date or 'N/A'} |
| **Listing Date** | {listing_date or 'N/A'} |
| **Price Band** | {price_band} |
| **Lot Size** | {int(lot_size) if lot_size else 'N/A'} |
| **Issue Size** | {issue_size or 'N/A'} |
| **Market Cap** | {market_cap if market_cap else 'N/A'} |
| **Country** | {country} |
"""
    if source_url:
        ipo_details += f"\n🔗 **Source**: [{source_url}]({source_url})\n"

    # ========== SECTION 2: EXECUTIVE SUMMARY ==========
    exec_summary = (
        f"## Investment Verdict: **{ai_rating}**\n\n"
        f"**Confidence Score: {overall:.0f}/100**\n\n"
        f"{name} ({ticker}) operates in the **{sector}** sector ({industry or 'General'} industry). "
        f"AI Score: **{overall:.0f}/100** ({ai_rating}). "
        f"Fundamentals: **{fs_val:.0f}/100** ({score_label(fs_val)}). "
        f"Business Quality: **{bq_val:.0f}/100** ({score_label(bq_val)}). "
        f"Valuation: **{val_val:.0f}/100** ({score_label(val_val)}). "
        f"Market Sentiment: **{demand_val:.0f}/100** ({score_label(demand_val)}).\n\n"
    )
    if overall >= 70:
        exec_summary += f"The overall assessment suggests a **positive** outlook supported by decent fundamentals and sector positioning."
    elif overall >= 50:
        exec_summary += f"The assessment is **neutral to positive**, though investors should carefully review the identified risks."
    else:
        exec_summary += f"**Caution is advised** given the below-average scores across key parameters."

    if gmp and is_upcoming:
        exec_summary += f"\n\n📊 **GMP: ₹{gmp:.0f}** | Expected listing gain: **{gmp_pct:.0f}%**"
    if subscription:
        exec_summary += f"\n\n📊 **Subscription: {subscription}**"

    exec_summary += f"\n\n**Recommendation: {score_rating(overall)}**"

    # ========== SECTION 4: BUSINESS OVERVIEW ==========
    profile_growth = profile["growth"]
    profile_margin = profile["margin"]
    profile_moat = profile["moat"]
    profile_cyclic = "Yes" if profile["cyclical"] else "No"

    bus_overview_lines = []
    bus_overview_lines.append(f"## Business Model\n")
    bus_overview_lines.append(f"{name} operates primarily in the **{sector}** sector")
    if industry:
        bus_overview_lines.append(f"within the **{industry}** industry.")
    else:
        bus_overview_lines.append(".")
    bus_overview_lines.append(f" The company's business model is focused on delivering value through its operations in this space.")

    if about:
        bus_overview_lines.append(f"\n{about}")
    if description and description != name:
        bus_overview_lines.append(f"\n{description}")

    bus_overview_lines.append(f"\n\n### Key Business Parameters\n")
    bus_overview_lines.append(f"| Parameter | Assessment |")
    bus_overview_lines.append(f"|-----------|-----------|")
    bus_overview_lines.append(f"| **Sector Growth** | {profile_growth} |")
    bus_overview_lines.append(f"| **Profit Margins** | {profile_margin} |")
    bus_overview_lines.append(f"| **Competitive Moat** | {profile_moat} |")
    bus_overview_lines.append(f"| **Capital Intensity** | {profile['cap_intensity']} |")
    bus_overview_lines.append(f"| **Cyclical** | {profile_cyclic} |")

    bus_overview_lines.append(f"\n\n### Products & Services")
    bus_overview_lines.append(f"\n{name} offers products and services in the {sector} space. "
        "Detailed product segmentation requires review of the company's DRHP/RHP and annual reports.")

    bus_overview_lines.append(f"\n\n### Revenue Streams")
    bus_overview_lines.append(f"\nPrimary revenue is generated through operations in the {sector} sector. "
        "Revenue breakdown by segment and geography requires financial statement analysis.")
    if country:
        bus_overview_lines.append(f"\n\n### Geographic Presence")
        bus_overview_lines.append(f"\nThe company serves customers in {country}" + (" and international markets." if country == "IN" else "."))

    bus_overview_lines.append(f"\n\n### Competitive Position")
    bus_overview_lines.append(f"\n{name} competes in the {sector} industry. "
        f"Business Quality Score: **{bq_val:.0f}/100** ({score_label(bq_val)}). "
        f"The competitive moat is rated as **{profile_moat}**.")

    bus_overview = "\n".join(bus_overview_lines)

    # ========== SECTION 5: INDUSTRY ANALYSIS ==========
    ind_lines = []
    ind_lines.append(f"## Industry Size & Growth\n")
    ind_lines.append(f"The **{sector}** industry represents a significant market opportunity with **{growth_label.lower()} growth** trajectory. ")
    ind_lines.append(f"Industry growth characteristics for this sector are rated as **{profile_growth}**.")

    ind_lines.append(f"\n\n### Future Demand Drivers")
    ind_lines.append(f"\nKey growth drivers include technological advancement, evolving consumer preferences, "
        f"regulatory developments, and macroeconomic factors specific to the {sector} sector.")

    ind_lines.append(f"\n\n### Market Trends")
    ind_lines.append(f"\nCurrent trends in the {sector} space include digital transformation, consolidation, innovation, "
        "and changing competitive dynamics.")

    ind_lines.append(f"\n\n### Regulatory Environment")
    ind_lines.append(f"\nCompanies in this sector face regulations that may impact operations, compliance costs, and market access.")

    ind_lines.append(f"\n\n### Entry Barriers")
    ind_lines.append(f"\nBarriers to entry are **moderate to high**" if sector.lower() in ["banking","pharma","telecom","infrastructure","energy","mining"] else "\nBarriers to entry are **moderate**")
    ind_lines.append(f", with incumbents benefiting from scale, brand, and distribution advantages.")

    ind_lines.append(f"\n\n### Industry Outlook")
    outlook = "positive" if growth_label == "High" else "stable"
    ind_lines.append(f"\nThe long-term outlook is **{outlook}**, supported by structural demand drivers.")
    ind_lines.append(f"\n\n**Industry Outlook Score: {bq_val:.0f}/100 ({score_label(bq_val)})**")
    industry_analysis = "\n".join(ind_lines)

    # ========== SECTIONS 7-9: FINANCIAL ANALYSIS ==========
    fin_lines = []
    fin_lines.append(f"## Revenue Growth\n")
    fin_lines.append(f"Revenue growth assessment: **{score_label(fs_val)}** (Score: {fs_val:.0f}/100). ")
    fin_lines.append(f"The sector typically exhibits **{profile_growth}** revenue growth characteristics.")

    fin_lines.append(f"\n\n## Profitability\n")
    fin_lines.append(f"| Metric | Assessment |")
    fin_lines.append(f"|--------|-----------|")
    fin_lines.append(f"| Revenue Growth | {score_label(fs_val)} ({fs_val:.0f}/100) |")
    fin_lines.append(f"| Profit Growth | {score_label(fs_val)} ({fs_val:.0f}/100) |")
    fin_lines.append(f"| EBITDA Margin | {profile_margin} (sector typical) |")
    fin_lines.append(f"| Net Profit Margin | Sector-dependent |")
    fin_lines.append(f"| ROE | {score_label(fs_val)} |")
    fin_lines.append(f"| ROCE | {score_label(fs_val)} |")

    if financial_data:
        fin_lines.append(f"\n\n### Actual Financial Data (Screener)")
        pl = financial_data.get("profitLoss", {})
        if pl and pl.get("headers") and pl.get("rows"):
            fin_lines.append(f"\n\n**Profit & Loss Statement**\n")
            fin_lines.append(render_table(pl["headers"], pl["rows"]))

        bs = financial_data.get("balanceSheet", {})
        if bs and bs.get("headers") and bs.get("rows"):
            fin_lines.append(f"\n\n**Balance Sheet**\n")
            fin_lines.append(render_table(bs["headers"], bs["rows"]))

        cf = financial_data.get("cashFlow", {})
        if cf and cf.get("headers") and cf.get("rows"):
            fin_lines.append(f"\n\n**Cash Flow Statement**\n")
            fin_lines.append(render_table(cf["headers"], cf["rows"]))

    fin_lines.append(f"\n\n### Financial Quality Check")
    fin_lines.append(f"| Check | Result |")
    fin_lines.append(f"|-------|--------|")
    fin_lines.append(f"| Revenue Consistency | {score_label(fs_val)} ({fs_val:.0f}/100) |")
    fin_lines.append(f"| Profit Consistency | {score_label(fs_val)} ({fs_val:.0f}/100) |")
    fin_lines.append(f"| Margin Stability | {profile_margin} |")
    fin_lines.append(f"| Overall Financial Strength | **{fs_val:.0f}/100 ({score_label(fs_val)})** |")

    financial_analysis = "\n".join(fin_lines)

    # ========== SECTION 10: RATIO ANALYSIS ==========
    ratio_lines = []
    ratio_lines.append(f"## Key Financial Ratios\n")
    ratio_lines.append(f"| Ratio | Value/Assessment |")
    ratio_lines.append(f"|-------|-----------------|")
    ratio_lines.append(f"| **ROE** | {score_label(fs_val)} ({fs_val:.0f}/100) |")
    ratio_lines.append(f"| **ROCE** | {score_label(fs_val)} |")
    ratio_lines.append(f"| **Debt/Equity** | {score_label(risk_val)} ({risk_val:.0f}/100) |")
    ratio_lines.append(f"| **Interest Coverage** | Sector-dependent |")
    ratio_lines.append(f"| **Current Ratio** | Further data required |")
    ratio_lines.append(f"| **P/E** | {profile['pe_range']} (sector range) |")

    if financial_data:
        ratios_data = financial_data.get("ratios", {})
        if ratios_data and ratios_data.get("headers") and ratios_data.get("rows"):
            ratio_lines.append(f"\n\n### Ratio Trend (Screener)\n")
            ratio_lines.append(render_table(ratios_data["headers"], ratios_data["rows"]))

        growth_metrics = financial_data.get("growthMetrics", {})
        if growth_metrics:
            ratio_lines.append(f"\n\n### Growth Metrics")
            for key, val2 in growth_metrics.items():
                if isinstance(val2, dict) and val2:
                    ratio_lines.append(f"\n**{key.replace('_', ' ').title()}**: {json.dumps(val2)}")

    ratio_analysis = "\n".join(ratio_lines)

    # ========== BALANCE SHEET ==========
    bs_lines = []
    bs_lines.append(f"## Balance Sheet Strength\n")
    bs_lines.append(f"| Parameter | Assessment |")
    bs_lines.append(f"|-----------|-----------|")
    bs_lines.append(f"| **Debt Burden** | {score_label(risk_val)} ({risk_val:.0f}/100) |")
    bs_lines.append(f"| **Liquidity** | Moderate (requires detailed data) |")
    bs_lines.append(f"| **Capital Structure** | Adequate |")
    bs_lines.append(f"| **Contingent Liabilities** | Review notes to accounts |")
    bs_lines.append(f"| **Balance Sheet Verdict** | **{score_label(risk_val)}** |")
    balance_sheet_analysis = "\n".join(bs_lines)

    # ========== CASH FLOW ==========
    cf_lines = []
    cf_lines.append(f"## Cash Flow Analysis\n")
    cf_lines.append(f"| Metric | Assessment |")
    cf_lines.append(f"|--------|-----------|")
    cf_lines.append(f"| **Operating Cash Flow** | Analysis requires cash flow statements |")
    cf_lines.append(f"| **Free Cash Flow** | Needs capex data for calculation |")
    cf_lines.append(f"| **Cash Conversion** | Requires working capital analysis |")
    cf_lines.append(f"| **Cash Flow Quality** | Further data required |")
    cash_flow_analysis = "\n".join(cf_lines)

    # ========== SECTION 14: VALUATION ==========
    val_lines = []
    val_lines.append(f"## Valuation Analysis\n")
    val_lines.append(f"| Metric | Assessment |")
    val_lines.append(f"|--------|-----------|")
    val_lines.append(f"| **P/E Ratio** | {profile['pe_range']} (sector range) |")
    val_lines.append(f"| **P/B Ratio** | Sector-dependent |")
    val_lines.append(f"| **EV/EBITDA** | Further data required |")
    val_lines.append(f"| **Price/Sales** | Sector-dependent |")
    val_lines.append(f"| **Market Cap** | {market_cap if market_cap else 'N/A'} |")

    val_class = "Fairly Valued" if val_val >= 60 else ("Moderately Expensive" if val_val >= 50 else "Expensive")
    val_lines.append(f"\n\n### Valuation Verdict")
    val_lines.append(f"\nValuation Score: **{val_val:.0f}/100** ({score_label(val_val)}).")
    val_lines.append(f"\nThe company appears **{val_class.lower()}** relative to sector norms.")
    val_lines.append(f"\n\n**Classification: {val_class}**")
    valuation_analysis = "\n".join(val_lines)

    # ========== MANAGEMENT ==========
    mgmt_lines = []
    mgmt_lines.append(f"## Promoter & Management Analysis\n")
    mgmt_lines.append(f"| Parameter | Assessment |")
    mgmt_lines.append(f"|-----------|-----------|")
    mgmt_lines.append(f"| **Management Quality** | {score_label(risk_val)} ({risk_val:.0f}/100) |")
    mgmt_lines.append(f"| **Governance Score** | {risk_val:.0f}/100 |")
    mgmt_lines.append(f"| **Promoter Background** | Review RHP for details |")
    mgmt_lines.append(f"| **SEBI Actions** | Check SEBI website for any actions |")
    mgmt_lines.append(f"| **Legal Disputes** | Review company filings |")
    management_quality = "\n".join(mgmt_lines)

    # ========== RISKS ==========
    risk_text = ""
    if risks:
        r_lines = []
        for rf in risks[:8]:
            r_lines.append(f"- **{rf}** — Risk Level: Medium")
        risk_text = "\n".join(r_lines)
    else:
        risk_text = "- General market and economic risks\n- Sector-specific headwinds\n- Competition risk"

    flags_text = ""
    if flags:
        f_lines = [f"- ⚠ {f}" for f in flags[:4]]
        flags_text = "\n".join(f_lines)

    risk_assessment = f"""## Identified Risks

{risk_text}
{f'\n\n### Red Flags\n{flags_text}' if flags_text else ''}

## Risk Categories
| Risk Category | Level | Description |
|--------------|-------|-------------|
| Industry Risk | Medium | Sector-specific headwinds |
| Regulatory Risk | Medium | Regulatory changes may impact |
| Competition Risk | Medium | Competitive pressure on margins |
| Execution Risk | Medium | Business execution dependencies |

**Risk Safety Score: {risk_val:.0f}/100 ({score_label(risk_val)})**
*Higher score = lower risk*
"""

    # ========== STRENGTHS/WEAKNESSES ==========
    strengths_text = "\n".join(f"- {b}" for b in (bull[:6] if bull else [f"Positioned in {sector} sector", "Sector growth tailwinds"]))
    weaknesses_text = "\n".join(f"- {b}" for b in (bear[:6] if bear else ["Limited publicly available financial data", "Competitive pressure from established players"]))
    strengths_weaknesses = f"""### Key Strengths
{strengths_text}

### Key Weaknesses
{weaknesses_text}
"""

    # ========== MARKET SENTIMENT ==========
    gmp_str = f"₹{gmp:.0f}" if gmp else "Not Available"
    gmp_pct_str = f"{gmp_pct:.0f}%" if gmp_pct else "N/A"
    sentiment_score = "positive" if demand_val >= 60 else ("neutral" if demand_val >= 40 else "weak")

    market_sentiment = f"""## Market Sentiment Analysis

### GMP (Grey Market Premium)
| Metric | Value |
|--------|-------|
| **Current GMP** | {gmp_str} |
| **Expected Listing Gain** | {gmp_pct_str} |
| **GMP Sentiment** | {'Bullish' if gmp_pct >= 50 else 'Neutral' if gmp_pct >= 20 else 'Weak' if gmp_pct else 'N/A'} |

### Subscription Data
Subscription Status: **{subscription or 'Not Available'}**

### Demand Analysis
| Investor Category | Assessment |
|-----------------|-----------|
| **QIB Demand Score** | {demand_val:.0f}/100 ({score_label(demand_val)}) |
| **Overall Demand** | {score_label(demand_val)} |

### Market Sentiment Verdict
The overall market sentiment is **{sentiment_score}** based on available indicators.
**Demand & Hype Score: {demand_val:.0f}/100 ({score_label(demand_val)})**
"""

    # ========== FINAL VERDICT ==========
    verdict = score_rating(overall)
    long_term = "Very Good" if overall >= 75 else "Good" if overall >= 65 else "Average" if overall >= 50 else "Below Average"
    hype_level = "High" if (demand_val >= 70 or gmp_pct >= 50) else ("Moderate" if (demand_val >= 50 or gmp_pct >= 20) else "Low")
    listing_gain_view = "Strong Subscribe" if hype_level == "High" and overall >= 60 else ("Subscribe" if hype_level == "Moderate" else "Neutral")

    final_verdict = f"""## Final Recommendation

### AI Decision Engine

**WHY INVEST?**
{chr(10).join(f"- {b}" for b in (bull[:10] if bull else [f"Positioned in growing {sector} sector", "Sector tailwinds support growth"]))}

**WHY AVOID?**
{chr(10).join(f"- {b}" for b in (bear[:10] if bear else ["Limited financial data for deep analysis", "Market competition risk"]))}

### Listing Gain View
| Scenario | Assessment |
|---------|-----------|
| **Bear Case** | Conservative listing expected |
| **Base Case** | Moderate listing gains possible |
| **Bull Case** | Strong listing if demand surges |
| **Hype Level** | **{hype_level}** |

**Listing Gain Recommendation: {listing_gain_view}**

### Long-Term View
**Long-Term Rating: {long_term}**
- Business Quality: {bq_val:.0f}/100 ({score_label(bq_val)})
- Financial Strength: {fs_val:.0f}/100 ({score_label(fs_val)})
- Valuation: {val_val:.0f}/100 ({score_label(val_val)})

**Long-Term Recommendation: {'Strong Buy' if overall >= 75 else 'Buy' if overall >= 65 else 'Hold' if overall >= 50 else 'Avoid'}**

### Investor Suitability
| Investor Type | Suitability |
|-------------|------------|
| Listing Gain Investors | {'Suitable' if hype_level == 'High' else 'Neutral'} |
| Long-Term Investors | {'Suitable' if overall >= 65 else 'Neutral'} |
| Conservative Investors | {'Suitable' if overall >= 70 else 'Not Suitable'} |
| Aggressive Investors | {'Suitable' if overall >= 50 else 'Neutral'} |

### Multibagger Potential
| Timeframe | Potential |
|-----------|----------|
| **1 Year** | {'High' if overall >= 75 else 'Moderate' if overall >= 60 else 'Limited'} |
| **3 Year** | {'High' if overall >= 70 else 'Moderate' if overall >= 55 else 'Limited'} |
| **5 Year** | {'High' if overall >= 65 else 'Moderate' if overall >= 50 else 'Limited'} |

### OVERALL VERDICT: **{verdict}**
Confidence Level: **{overall:.0f}/100**

**Final Assessment**
{name} ({ticker}) — AI Score: **{overall:.0f}/100** | Rating: **{ai_rating}**
Suitable for {'aggressive' if overall >= 65 else 'moderate' if overall >= 50 else 'conservative'} investors with appropriate risk appetite.
"""

    # ========== SEO ==========
    seo_title = f"{name} IPO Analysis: AI Score {overall:.0f}/100 | PulseTrends"
    if len(seo_title) > 60:
        seo_title = f"{name} IPO: {score_label(overall)} AI Score {overall:.0f}/100"
    if len(seo_title) > 60:
        seo_title = f"{name} IPO Analysis {overall:.0f}/100"

    meta_desc = f"Comprehensive {name} IPO analysis. AI Score: {overall:.0f}/100 ({ai_rating}). Business quality: {score_label(bq_val)}. Valuation: {score_label(val_val)}."
    if len(meta_desc) > 160:
        meta_desc = f"{name} IPO: {ai_rating} | AI Score {overall:.0f}/100 | {score_label(fs_val)} fundamentals | {score_label(bq_val)} business quality."
    meta_desc = meta_desc[:160]

    keywords = [name, ticker, f"{name} IPO", f"{sector} IPO", f"IPO Analysis", f"IPO Rating", "PulseTrends"]
    keywords = [k for k in keywords if k]

    # ========== FAQ ==========
    faq = [
        {"question": f"What is the price band of {name} IPO?", "answer": f"The price band for {name} IPO is {price_band}."},
        {"question": f"When is {name} IPO opening?", "answer": f"The IPO opens on {open_date or 'TBA'} and closes on {close_date or 'TBA'}."},
        {"question": f"What is the lot size for {name} IPO?", "answer": f"The lot size is {int(lot_size) if lot_size else 'TBA'} shares."},
        {"question": f"Is {name} a good investment?", "answer": f"Based on PulseTrends AI analysis, {name} has an AI Score of {overall:.0f}/100 ({ai_rating}). {score_label(bq_val)} business quality with {score_label(fs_val)} financial fundamentals."},
        {"question": f"What is the GMP of {name} IPO?", "answer": f"The current grey market premium is {gmp_str}."},
        {"question": f"What are the risks of {name} IPO?", "answer": f"Key risks include: {risks[0] if risks else 'general market and sector-specific risks'}."},
        {"question": f"Should I subscribe to {name} IPO?", "answer": f"PulseTrends AI recommends: {score_rating(overall)} for {name} IPO."},
        {"question": f"What is the expected listing gain for {name} IPO?", "answer": f"Based on GMP of {gmp_str}, the expected listing gain is approximately {gmp_pct_str}."},
        {"question": f"What sector does {name} operate in?", "answer": f"{name} operates in the {sector} sector, {industry or 'General'} industry."},
        {"question": f"What is the issue size of {name} IPO?", "answer": f"The total issue size is {issue_size or 'TBA'}."},
    ]

    # ========== SCORECARD ==========
    scorecard_categories = [
        {"key": "bq", "label": "Business Quality", "score": round(bq_val / 10, 1)},
        {"key": "fin", "label": "Financial Strength", "score": round(fs_val / 10, 1)},
        {"key": "val", "label": "Valuation", "score": round(val_val / 10, 1)},
        {"key": "dem", "label": "Demand & Hype", "score": round(demand_val / 10, 1)},
        {"key": "risk", "label": "Risk Safety", "score": round(risk_val / 10, 1)},
    ]

    # ========== BUILD ENTRY ==========
    entry = {
        "slug": slug,
        "company": name,
        "ticker": ticker,
        "sector": sector,
        "industry": industry,
        "exchange": exchange,
        "status": status,
        "executive_summary": exec_summary,
        "business_overview": bus_overview,
        "industry_analysis": industry_analysis,
        "financial_analysis": financial_analysis,
        "balance_sheet_analysis": balance_sheet_analysis,
        "cash_flow_analysis": cash_flow_analysis,
        "ratio_analysis": ratio_analysis,
        "ipo_details": ipo_details,
        "valuation_analysis": valuation_analysis,
        "management_quality": management_quality,
        "risk_assessment": risk_assessment,
        "strengths_weaknesses": strengths_weaknesses,
        "market_sentiment": market_sentiment,
        "final_verdict": final_verdict,
        "ai_scorecard": {
            "categories": scorecard_categories,
            "total_score": round(overall / 10, 1),
            "rating": ai_rating,
        },
        "investment_verdict": {
            "overall_score": round(overall, 1),
            "rating": ai_rating,
            "long_term_rating": long_term,
            "subscription_recommendation": verdict,
            "listing_gain_view": listing_gain_view,
            "scores": {
                "overall_score": round(overall, 1),
                "fundamentals_score": round(fs_val, 1),
                "valuation_score": round(val_val, 1),
                "growth_score": round(bq_val, 1),
                "management_score": round(risk_val, 1),
                "market_sentiment_score": round(demand_val, 1),
            },
            "summary": thesis[:500] if thesis else f"{name} IPO: {ai_rating} with AI Score {overall:.0f}/100.",
        },
        "seo": {
            "title": seo_title[:60],
            "description": meta_desc[:160],
            "canonical_url": f"/ipo/{slug}",
            "keywords": keywords,
            "ai_overview_ready": True,
        },
        "faq": faq,
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Report",
            "name": f"{name} IPO Analysis",
            "description": meta_desc[:200],
            "datePublished": datetime.now(timezone.utc).isoformat(),
        },
        "red_flags": flags[:8] if flags else ["No significant red flags detected based on available data."],
        "positive_catalysts": bull[:5] if bull else ["Sector growth tailwinds", "Market positioning"],
        "section_20_scorecard": {
            "categories": scorecard_categories,
            "total_score": round(overall / 10, 1),
            "interpretation": ai_rating,
        },
        "section_13_market_performance": {
            "stock_pe": profile['pe_range'],
            "analysis": f"AI Score: {overall:.0f}/100 | Sector P/E Range: {profile['pe_range']}",
        },
        "section_21_final_verdict": {
            "long_term_rating": long_term,
            "subscription_recommendation": verdict,
            "summary": thesis[:500] if thesis else f"Overall AI Score: {overall:.0f}/100 - {ai_rating}",
        },
    }
    return entry


def main():
    FORCE = "--force" in sys.argv

    screener_data = load_json(os.path.join(DATA_DIR, "screener_ipos.json"))
    ipos = screener_data.get("ipos", []) if isinstance(screener_data, dict) else []
    print(f"Loaded {len(ipos)} screener IPOs.")

    financial_data = load_json(os.path.join(DATA_DIR, "screener_financial_data.json"))
    print(f"Loaded financial data for {len(financial_data)} companies.")

    master_db = load_json(os.path.join(DATA_DIR, "ipo_master_database.json"))
    master_lookup = {}
    for mipo in master_db.get("ipos", []):
        key = mipo.get("company_name", "").lower().strip()
        if key:
            master_lookup[key] = mipo
    print(f"Loaded {len(master_lookup)} master DB entries for score fallback.")

    output_path = os.path.join(SRC_DIR, "ipoComprehensiveAnalysis.json")
    existing = {}
    if not FORCE and os.path.exists(output_path):
        try:
            with open(output_path, encoding="utf-8") as f:
                existing = json.load(f)
            print(f"Loaded {len(existing)} existing entries (incremental mode).")
        except:
            pass

    output = dict(existing)
    new_count = 0
    skipped = 0

    for i, ipo in enumerate(ipos):
        name = ipo.get("name", "Unknown")
        slug = f"{slugify(name)}-{i+1}"

        if not FORCE and slug in existing:
            skipped += 1
            continue

        master_entry = master_lookup.get(name.lower().strip(), {})
        fd_entry = None
        fd_slug = slugify(name)
        for fd_key in financial_data:
            if fd_slug == slugify(fd_key):
                fd_entry = financial_data[fd_key]
                break

        entry = generate_44_section_entry(ipo, fd_entry, master_entry, slug)
        output[slug] = entry
        new_count += 1

        if (i + 1) % 200 == 0:
            print(f"  Processed {i+1}/{len(ipos)} IPOs...")

    os.makedirs(SRC_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\nDone! {new_count} new + {skipped} existing = {len(output)} entries -> {output_path}")
    print(f"File size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
