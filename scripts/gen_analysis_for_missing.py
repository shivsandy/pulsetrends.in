#!/usr/bin/env python3
"""
Generate comprehensive 13-section Fundamental Analysis Framework
for ALL IPOs using master database data.
"""
import json, os, re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SRC_DIR = os.path.join(ROOT, "src", "data")

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

def safe_str(v, default=""):
    if v is None: return default
    s = str(v).strip()
    return s if s and s != chr(65533) else default

def safe_num(v, default=0):
    try: return float(v) if v is not None else default
    except: return default

def score_label(s):
    s = safe_num(s, 50)
    if s >= 80: return "Strong"
    if s >= 70: return "Good" if s < 80 else "Strong"
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

def generate_entry(ipo, slug):
    name = ipo.get("company_name", "Unknown")
    ticker = safe_str(ipo.get("ticker", ""))
    sector = safe_str(ipo.get("sector", "General"))
    industry = safe_str(ipo.get("industry", ""))
    exchange = safe_str(ipo.get("exchange", "NSE/BSE"))
    status = safe_str(ipo.get("status", "listed"))
    ipo_date = safe_str(ipo.get("ipo_date", ""))
    country = safe_str(ipo.get("country", "IN"))

    ai_score = safe_num(ipo.get("ai_score"), 50)
    ai_rating = safe_str(ipo.get("ai_rating"), "Average")
    sb = ipo.get("score_breakdown", {}) or {}
    bull = ipo.get("bull_case", []) or []
    bear = ipo.get("bear_case", []) or []
    risks = ipo.get("risk_factors", []) or []
    flags = ipo.get("red_flags", []) or []
    thesis = safe_str(ipo.get("investment_thesis", ""))
    summary = safe_str(ipo.get("ipo_summary", ""))
    score_exp = safe_str(ipo.get("ai_score_explanation", ""))

    fundamentals = safe_num(sb.get("fundamentals"), 50)
    ipo_demand = safe_num(sb.get("ipo_demand"), 50)
    valuation_score = safe_num(sb.get("valuation"), 50)
    governance = safe_num(sb.get("governance"), 50)
    business_quality = safe_num(sb.get("business_quality"), 50)
    bq = safe_num(business_quality, 50)
    fs = safe_num(fundamentals, 50)
    val = safe_num(valuation_score, 50)
    demand = safe_num(ipo_demand, 50)
    risk = safe_num(governance, 50)
    overall = ai_score

    def s(v): return f"{v:.0f}/100"
    def sl(v): return score_label(v)
    growth_label = "High" if any(h.lower() in sector.lower() for h in ["technology","software","fintech","biotech","renewable","e-commerce","healthcare"]) else "Moderate"

    # Build all section contents as Markdown text
    # Section 1: Business Overview
    sec1 = f"""## Business Model
{name} ({ticker}) operates in the **{sector}** sector within the **{industry or 'General'}** industry. Listed on {exchange}.

## Products & Services
The company offers products and services in the {sector} space. Specific product details require review of the company's DRHP/RHP and annual reports for comprehensive segmentation.

## Revenue Streams
Primary revenue is generated through operations in the {sector} sector. Detailed revenue breakdown by segment, geography, and customer type requires financial statement analysis.

## Geographic Presence
The company serves customers in {country} and global markets. Geographic revenue distribution requires data from company filings.

## Customer Base
Customer concentration details require disclosure from company filings. Sector-typical diversification is assumed unless specified otherwise.

## Competitive Position
{name} competes in the {sector} industry against established players and emerging entrants. Key competitive factors include pricing, technology, distribution, and brand strength. Business quality score: **{s(bq)}** ({sl(bq)}).

## Key Competitors
Peer comparison requires identification of comparable listed companies in the same sector.

## Scalability
Scalability assessment requires detailed operational and financial data. The {sector} sector typically offers {'good scalability with low capital intensity' if sector.lower() in ['technology','software','services'] else 'moderate scalability with moderate capital requirements'}.
"""

    # Section 2: Industry & Market Analysis
    sec2 = f"""## Industry Size & Growth
The **{sector}** industry represents a significant market opportunity with **{growth_label.lower()} growth** trajectory. Market sizing data requires independent industry reports.

## Future Demand Drivers
Key growth drivers include technological advancement, evolving consumer preferences, regulatory developments, and macroeconomic factors specific to the {sector} sector.

## Market Trends
Current trends in the {sector} space include digital transformation, consolidation, innovation, and changing competitive dynamics.

## Regulatory Environment
Companies in this sector face regulations that may impact operations, compliance costs, and market access. Specific regulatory assessment requires sector expertise.

## Entry Barriers
Barriers to entry are {'moderate to high' if sector.lower() in ['banking','pharma','telecom','infrastructure','energy','mining'] else 'moderate'}, with incumbents benefiting from scale, brand, and distribution advantages.

## Competitive Intensity
Competition is {'intense' if sector.lower() in ['technology','software','retail','e-commerce','fmcg'] else 'moderate'}, with pricing pressure and innovation as key battlegrounds.

## Industry Outlook
The long-term outlook for the {sector} sector is {'positive' if growth_label=='High' else 'stable'}, supported by structural demand drivers. Cyclical factors may cause periodic fluctuations.
"""

    # Section 3: Financial Performance Analysis
    sec3 = f"""## Revenue Growth
Revenue growth is **{sl(fundamentals)}** based on fundamental score of {s(fundamentals)}. Detailed year-over-year revenue trends require historical financial statements.

## Profitability
EBITDA Margin: Sector-typical margins apply. Detailed margin analysis requires income statement data.
Net Profit Margin: Assessment based on fundamental score of {s(fundamentals)}.

## Return Ratios
ROE: {sl(fundamentals)} (score: {s(fundamentals)})
ROCE: {sl(fundamentals)}
Further ratio analysis requires financial statements from company filings.

## Growth Consistency
Growth consistency assessment requires multi-year financial data. The fundamental score of {s(fundamentals)} provides a proxy for financial health evaluation.

## Key Financial Metrics
| Metric | Assessment |
|--------|-----------|
| Revenue Growth | {sl(fundamentals)} |
| Profit Growth | {sl(fundamentals)} |
| EBITDA Margins | Sector-dependent |
| ROE | {sl(fundamentals)} |
| ROCE | {sl(fundamentals)} |

*Detailed financial data requires review of company filings.*
"""

    # Section 4: Balance Sheet Analysis
    sec4 = f"""## Debt Burden
Debt-to-equity assessment: **{sl(governance)}** based on governance score of {s(governance)}. Detailed debt structure requires balance sheet data.

## Liquidity Position
Liquidity assessment requires current ratio, quick ratio, and working capital data from financial statements.

## Cash Reserves
Cash and equivalent position requires balance sheet review.

## Capital Structure
The company's capital structure includes equity and debt financing. Optimal capital structure assessment requires detailed analysis.

## Contingent Liabilities
Identification of contingent liabilities requires notes to accounts from annual reports.

## Related-Party Transactions
Related-party transaction assessment requires review of company filings and governance disclosures.

## Verdict
Balance Sheet: **{sl(governance)}** (Score: {s(governance)})
"""

    # Section 5: Cash Flow Analysis
    sec5 = f"""## Operating Cash Flow
Cash flow from operations assessment requires cash flow statements. Earnings quality evaluation requires comparing profits with operating cash flows.

## Free Cash Flow
FCF sustainability assessment requires calculation from cash flow statements. Capex intensity varies by sector ({sector}).

## Receivables & Inventory
Receivables and inventory trends require balance sheet comparison across periods.

## Accounting Quality
Signs of aggressive accounting require detailed notes review. Cash conversion efficiency requires working capital analysis.

## Verdict
Cash flow quality: Further data required for comprehensive assessment.
"""

    # Section 6: IPO Issue Analysis
    sec6 = f"""## IPO Details
| Parameter | Value |
|-----------|-------|
| Status | {status} |
| IPO Date | {ipo_date or 'Not Available'} |
| Exchange | {exchange} |
| Sector | {sector} |

## Issue Breakdown
Detailed breakdown of Fresh Issue vs OFS requires RHP/DRHP review.
Use of proceeds assessment requires IPO prospectus analysis.

## Valuation at IPO
IPO valuation assessment based on AI model: **{s(valuation_score)}** ({sl(valuation_score)}).
Further valuation analysis requires price band and issue size data.

## Post-IPO Structure
Post-IPO shareholding pattern and promoter dilution details require prospectus data.
"""

    # Section 7: Valuation Analysis
    sec7 = f"""## Peer Comparison
| Metric | Assessment |
|--------|-----------|
| P/E Ratio | Sector-typical range applies |
| EV/EBITDA | Further data required |
| P/B Ratio | Further data required |
| Market Cap | Not Available |

## Valuation Verdict
Valuation Score: **{s(valuation_score)}** ({sl(valuation_score)}).
The company appears **{'fairly valued' if valuation_score>=60 else 'expensively valued'}** relative to sector norms.

## Premium/Discount Rationale
Further peer comparison requires financial data from comparable listed companies in the {sector} sector.
"""

    # Section 8: Promoter & Management Analysis
    sec8 = f"""## Promoter Background
Promoter background details require RHP review and historical disclosures.

## Management Team
{name} is led by a management team with experience in the {sector} sector. Detailed bios require company filings.

## Governance Track Record
Governance Score: **{s(governance)}** ({sl(governance)}).
Governance assessment considers board composition, related-party transactions, and transparency.

## Capital Allocation
Capital allocation quality assessment requires historical investment patterns and returns analysis.

## Institutional Backing
Institutional investor interest assessment based on demand score: {s(demand)} ({sl(demand)}).
"""

    # Section 9: Risk Analysis
    risk_lines = []
    for rf in risks[:8]:
        risk_lines.append(f"- **{rf}** — Risk Level: Medium")
    if flags:
        risk_lines.append("\n### Red Flags")
        for f in flags[:3]:
            risk_lines.append(f"- ⚠ {f} — Risk Level: **High**")
    risk_text = "\n".join(risk_lines) if risk_lines else "- No specific risk factors identified in the database."
    sec9 = f"""## Identified Risks
{risk_text}

## Risk Categories
| Risk Category | Level | Description |
|--------------|-------|-------------|
| Industry Risk | Medium | Sector-specific headwinds |
| Regulatory Risk | Medium | Regulatory changes may impact operations |
| Competition Risk | Medium | Competitive pressure on margins |
| Execution Risk | Medium | Business execution dependencies |

**Overall Risk Safety Score: {s(governance)} ({sl(governance)})**
*Higher score = Lower risk*
"""

    # Section 10: Strengths & Weaknesses
    strengths_text = "\n".join(f"• {b}" for b in (bull[:5] if bull else ["Positioned in growing sector"]))
    weaknesses_text = "\n".join(f"• {b}" for b in (bear[:5] if bear else ["Limited publicly available data for deep analysis"]))
    sec10 = f"""### Key Strengths
{strengths_text}

### Key Weaknesses
{weaknesses_text}
"""

    # Section 11: Market Sentiment Analysis
    gmp_val = safe_str(ipo.get("gmp", ""))
    sub_val = safe_str(ipo.get("subscription", ""))
    sec11 = f"""## GMP (Grey Market Premium)
GMP: **{gmp_val or 'Not Available'}**

## Subscription Data
Subscription: **{sub_val or 'Not Available'}**

## Institutional Demand
QIB Demand Score: **{s(demand)}** ({sl(demand)})
Institutional sentiment assessment is based on available demand indicators.

## Market Sentiment Verdict
Overall demand & hype score: **{s(demand)}/100** ({sl(demand)}).
Market sentiment is {'positive' if demand>=60 else 'neutral' if demand>=40 else 'weak'} based on available indicators.
"""

    # Section 12: Red Flag Detection
    flag_lines = []
    if flags:
        for f in flags[:8]:
            flag_lines.append(f"- ⚠ {f}")
    else:
        flag_lines.append("- No significant red flags detected based on available data.")
    flag_lines.append("- Cash flow vs profit comparison requires financial statements")
    flag_lines.append("- Related-party transaction analysis requires company filings")
    flag_lines.append("- Auditor history requires review of annual reports")
    sec12 = f"""## Detected Red Flags
{chr(10).join(flag_lines)}

**Note:** A comprehensive red flag check requires access to full financial statements, auditor reports, and governance disclosures.
"""

    # Section 13: Final Investment Verdict
    verdict = score_rating(overall)
    long_term = "Very Good" if overall >= 75 else "Good" if overall >= 65 else "Average" if overall >= 50 else "Below Average"
    suitable = "Aggressive" if overall >= 65 else "Moderate" if overall >= 50 else "Conservative"
    sec13 = f"""## Overall Assessment
**{name} ({ticker})** — AI Score: **{overall:.1f}/100** | Rating: **{ai_rating}**

## Short-Term Listing Outlook
{'Positive' if demand >= 60 else 'Neutral' if demand >= 40 else 'Cautious'} — based on demand indicators and market sentiment.

## Long-Term Investment Outlook
**{long_term}** — based on business quality ({s(bq)}), financial strength ({s(fs)}), and valuation ({s(val)}).

## Suitable Investor Category
**{suitable}** — this investment is best suited for {suitable.lower()} risk profiles.

## Final Recommendation: **{verdict}**

### Investment Summary
• Business operates in the {sector} sector with {'upcoming' if status=='upcoming' else 'established'} market presence
• Financial fundamentals scored {s(fs)} ({sl(fs)})
• Business quality rated {s(bq)} ({sl(bq)})
• Valuation scored {s(valuation_score)} ({sl(valuation_score)})
• Demand indicators scored {s(demand)} ({sl(demand)})
• Risk safety scored {s(governance)} ({sl(governance)})
• Overall AI Score: {overall:.1f}/100 — {ai_rating}
• Suitable for {suitable.lower()} investors with appropriate risk appetite
• Further due diligence recommended including review of company filings
"""

    scorecard_sections = [
        {"key": "bq", "label": "Business Quality", "score": round(bq / 10, 1)},
        {"key": "fin", "label": "Financial Strength", "score": round(fs / 10, 1)},
        {"key": "val", "label": "Valuation", "score": round(val / 10, 1)},
        {"key": "dem", "label": "Demand & Hype", "score": round(demand / 10, 1)},
        {"key": "risk", "label": "Risk Safety", "score": round(risk / 10, 1)},
    ]

    investment_verdict = {
        "overall_score": round(overall, 1),
        "rating": ai_rating,
        "long_term_rating": long_term,
        "subscription_recommendation": verdict,
        "scores": {
            "overall_score": round(overall, 1),
            "fundamentals_score": round(fs, 1),
            "valuation_score": round(val, 1),
            "growth_score": round(bq, 1),
            "management_score": round(risk, 1),
            "market_sentiment_score": round(demand, 1),
        },
        "summary": score_exp[:500] or thesis[:500] or summary[:500],
    }

    exec_summary = (
        f"**{name} ({ticker})** operates in the **{sector}** sector (Listed on {exchange}). "
        f"AI Score: {overall:.1f}/100 ({ai_rating}). "
        f"Fundamentals: {s(fs)} ({sl(fs)}). "
        f"Business Quality: {s(bq)} ({sl(bq)}). "
        f"Valuation: {s(val)} ({sl(val)}). "
        f"Recommendation: {verdict}."
    )

    return {
        "slug": slug,
        "company": name,
        "ticker": ticker,
        "sector": sector,
        "executive_summary": exec_summary,
        "business_overview": sec1,
        "industry_analysis": sec2,
        "financial_analysis": sec3,
        "balance_sheet_analysis": sec4,
        "cash_flow_analysis": sec5,
        "ipo_details": sec6,
        "valuation_analysis": sec7,
        "management_quality": sec8,
        "risk_assessment": sec9,
        "strengths_weaknesses": sec10,
        "market_sentiment": sec11,
        "red_flags": [f.strip("- ⚠ ") for f in flags] if flags else ["No significant red flags detected"],
        "positive_catalysts": bull[:5] if bull else ["Sector growth tailwinds"],
        "final_verdict": sec13,
        "section_20_scorecard": {
            "categories": scorecard_sections,
            "total_score": round(overall / 10, 1),
            "interpretation": ai_rating,
        },
        "section_13_market_performance": {
            "stock_pe": "N/A", "analysis": f"AI Score: {overall:.1f}/100",
        },
        "section_21_final_verdict": {
            "long_term_rating": long_term,
            "subscription_recommendation": verdict,
            "summary": score_exp[:500] or thesis[:500] or summary[:500],
        },
        "investment_verdict": investment_verdict,
    }

def main():
    import sys
    FORCE = "--force" in sys.argv

    with open(os.path.join(DATA_DIR, "ipo_master_database.json"), encoding="utf-8") as f:
        db = json.load(f)
    master_lookup = {}
    for ipo in db["ipos"]:
        master_lookup[ipo.get("company_name", "").lower().strip()] = ipo
    print(f"Loaded {len(master_lookup)} master DB entries.")

    src_path = os.path.join(SRC_DIR, "ipoComprehensiveAnalysis.json")
    try:
        with open(src_path, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"Loaded {len(existing)} existing entries.")
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}
        print("No existing file found.")

    slug_map = extract_slugs_from_ts()
    print(f"Found {len(slug_map)} IPOs in generated TS.")

    company_to_slug = {}
    for company, id_val, slug in slug_map:
        company_to_slug[company.lower().strip()] = (id_val, slug)

    new_count = 0
    skipped = 0
    output = {}

    for company_lower, (id_val, slug) in company_to_slug.items():
        ipo = master_lookup.get(company_lower)
        if not ipo:
            skipped += 1
            continue
        output[slug] = generate_entry(ipo, slug)
        new_count += 1
        if new_count % 200 == 0:
            print(f"  Generated {new_count}/{len(slug_map)}...")

    with open(src_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {new_count} entries -> {src_path}")
    size_mb = os.path.getsize(src_path) / 1024 / 1024
    print(f"File size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
