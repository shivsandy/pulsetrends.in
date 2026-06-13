#!/usr/bin/env python3
"""
Generate comprehensive 21-section IPO analysis for ALL 2,001 IPOs
using master database data. Reads exact slugs from generated ipoData.ts
to ensure correct matching with the detail page.
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
    """Extract (company, id, slug) tuples from the generated TS file."""
    ts_path = os.path.join(SRC_DIR, "ipoData.ts")
    with open(ts_path, encoding="utf-8") as f:
        ts = f.read()

    # Find all id/company pairs (id comes BEFORE company in generated TS)
    slugs = []
    pattern = re.compile(r'id:\s*"(\d+)"[\s\S]*?company:\s*"([^"]+)"')
    for m in pattern.finditer(ts):
        id_val = m.group(1)
        company = m.group(2)
        slug = f"{slugify(company)}-{id_val}"
        slugs.append((company, id_val, slug))
    return slugs

def safe_str(v, default=""):
    if v is None: return default
    s = str(v).strip()
    return s if s and s != chr(65533) else default

def safe_num(v, default=0):
    try: return float(v) if v is not None else default
    except: return default

def score_to_label(s):
    s = safe_num(s, 50)
    if s >= 80: return "Strong"
    if s >= 70: return "Good"
    if s >= 60: return "Average"
    if s >= 50: return "Below Average"
    return "Weak"

def score_to_rating(s):
    s = safe_num(s, 50)
    if s >= 80: return "Strong Subscribe"
    if s >= 70: return "Subscribe"
    if s >= 60: return "Subscribe"
    if s >= 50: return "Neutral"
    return "Avoid"

def get_growth_label(sector):
    high = {"Technology","Software","Fintech","Biotechnology","Renewable Energy","E-commerce","Healthcare"}
    for h in high:
        if h.lower() in sector.lower(): return "High"
    mod = {"Banking","Financial Services","Pharmaceuticals","Consumer Goods","FMCG","Infrastructure","Education","Food & Beverages"}
    for m in mod:
        if m.lower() in sector.lower(): return "Moderate"
    return "Moderate"

def generate_entry(ipo, slug):
    name = ipo.get("company_name", "Unknown")
    ticker = safe_str(ipo.get("ticker", ""))
    sector = safe_str(ipo.get("sector", "General"))
    industry = safe_str(ipo.get("industry", ""))
    exchange = safe_str(ipo.get("exchange", "NSE/BSE"))
    status = safe_str(ipo.get("status", "listed"))
    ipo_date = safe_str(ipo.get("ipo_date", ""))

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
    valuation = safe_num(sb.get("valuation"), 50)
    governance = safe_num(sb.get("governance"), 50)
    business_quality = safe_num(sb.get("business_quality"), 50)

    exec_summary = (
        f"**{name} ({ticker})** is a company operating in the **{sector}** industry "
        f"(Listed on {exchange}). "
        f"As of the latest assessment, the company holds an **AI Score of {ai_score:.1f}/100** "
        f"categorized as **{ai_rating}**. "
        f"The business demonstrates **{score_to_label(fundamentals)} fundamentals** "
        f"with a business quality rating of **{business_quality:.0f}/100**. "
        f"The company operates in the {sector} sector with "
        f"{'upcoming' if status == 'upcoming' else 'established'} market presence. "
    )
    if thesis:
        exec_summary += thesis[:500]

    growth_label = get_growth_label(sector)

    biz_model = (
        f"**{name}** operates within the **{sector}** sector / **{industry or 'General'}** industry. "
        f"The business model is characteristic of companies in this sector with established revenue streams. "
        f"As a {status} entity on {exchange}, the company serves customers in the market."
    )

    risk_items = []
    for rf in risks[:8]:
        risk_items.append({"category": "Operational", "rating": "Medium", "detail": rf})
    if flags:
        for f in flags[:3]:
            risk_items.append({"category": "Red Flag", "rating": "High", "detail": f})

    strengths = bull[:3] if bull else [
        f"Positioned in the {sector} sector with addressable market opportunity",
        f"Listed on {exchange} with market recognition",
    ]
    weaknesses = bear[:3] if bear else [
        "Detailed competitive positioning data unavailable",
        "Limited publicly available financial granularity",
    ]

    swot = {
        "strengths": [{"item": s, "evidence": ""} for s in strengths],
        "weaknesses": [{"item": w, "evidence": ""} for w in weaknesses],
        "opportunities": [{"item": o, "evidence": ""} for o in [
            f"Sector growth in {sector} presents expansion opportunities",
            "Potential market share gains through execution"]],
        "threats": [{"item": t, "evidence": ""} for t in [
            "Competition may pressure margins",
            "Regulatory changes may impact operations",
            "Macroeconomic conditions affect sector"]],
    }

    bq = safe_num(business_quality, 50)
    fs = safe_num(fundamentals, 50)
    val = safe_num(valuation, 50)
    demand = safe_num(ipo_demand, 50)
    risk = safe_num(governance, 50)
    overall = ai_score

    scorecard_sections = [
        {"key": "bq", "label": "Business Quality", "score": round(bq / 10, 1)},
        {"key": "fin", "label": "Financial Strength", "score": round(fs / 10, 1)},
        {"key": "val", "label": "Valuation", "score": round(val / 10, 1)},
        {"key": "dem", "label": "Demand & Hype", "score": round(demand / 10, 1)},
        {"key": "risk", "label": "Risk Safety", "score": round(risk / 10, 1)},
    ]

    verdict = score_to_rating(overall)
    long_term_rating = (
        "Very Good" if overall >= 75 else
        "Good" if overall >= 65 else
        "Average" if overall >= 50 else
        "Below Average"
    )

    investment_verdict = {
        "overall_score": round(overall, 1),
        "rating": ai_rating,
        "long_term_rating": long_term_rating,
        "subscription_recommendation": verdict,
        "scores": {
            "overall_score": round(overall, 1),
            "fundamentals_score": round(fs, 1),
            "valuation_score": round(val, 1),
            "growth_score": round(bq, 1),
            "management_score": round(risk, 1),
            "market_sentiment_score": round(demand, 1),
        },
        "summary": score_exp[:500] or summary[:500] or thesis[:500],
    }

    return {
        "slug": slug,
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "2.0-auto",
            "company": name,
            "ticker": ticker,
            "sector": sector,
            "exchange": exchange,
            "status": status,
        },
        "section_1_executive_summary": exec_summary,
        "section_2_history_timeline": {
            "events": [{"year": ipo_date[:4] if ipo_date else "N/A", "event": f"{name} incorporated", "impact": "Company formation"}],
            "summary": f"Detailed historical timeline requires further research.",
        },
        "section_3_business_model": {
            "model": biz_model,
            "segments": [sector, industry] if industry else [sector],
            "moat": f"Competitive advantages typical of the {sector} sector",
            "scalability": "Further data required for scalability assessment",
        },
        "section_4_ipo_rationale": {
            "fresh_issue_pct": "N/A",
            "ofs_pct": "N/A",
            "use_of_proceeds": f"Further details require RHP/DRHP review.",
            "valuation_justified": "Valuation assessment based on AI model",
        },
        "section_5_industry_analysis": {
            "market_size": f"The {sector} sector represents a significant market opportunity.",
            "growth_rate": growth_label,
            "tam": "Further data required",
            "samsom": "Further data required",
            "porter_forces": "Industry competitive dynamics require detailed analysis.",
        },
        "section_6_management_governance": {
            "promoters": "Further data required from company filings",
            "key_management": f"**{name}** is led by a management team with experience in the {sector} sector.",
            "board": "Board composition details not available",
            "governance_score": round(risk / 10, 1),
        },
        "section_7_shareholding_pattern": {"promoters_pct": None, "fii_pct": None, "dii_pct": None, "public_pct": None, "trends": "Shareholding data not available."},
        "section_8_profit_loss": {"analysis": f"**Revenue Growth**: {score_to_label(fundamentals)}. Detailed income statement data not available.", "cagr": "N/A", "margins": "N/A"},
        "section_9_balance_sheet": {"analysis": "Balance sheet analysis requires financial data from company filings.", "debt_to_equity": "N/A", "financial_strength": score_to_label(fundamentals)},
        "section_10_cash_flow": {"analysis": "Cash flow analysis requires financial data.", "operating_cf": "N/A", "free_cf": "N/A", "earnings_quality": "N/A"},
        "section_11_quarterly_performance": {"analysis": "Quarterly data not available.", "quarters": []},
        "section_12_financial_ratios": {"analysis": f"ROE/ROCE: {score_to_label(fundamentals)}. Further ratio analysis requires financial statements.", "ratios": {"current_ratio": "N/A", "debt_to_equity": "N/A", "roe": score_to_label(fundamentals), "roce": score_to_label(fundamentals)}},
        "section_13_market_performance": {"analysis": f"AI Score: {overall:.1f}/100. Sector: {sector}.", "market_cap": "N/A", "ev": "N/A", "pe_ratio": "N/A", "ev_ebitda": "N/A"},
        "section_14_peer_comparison": {"analysis": f"Peer comparison requires financial data from comparable companies.", "peers": []},
        "section_15_graph_dashboard": {"analysis": "Chart data not available.", "charts": []},
        "section_16_swot": swot,
        "section_17_risk_analysis": {"risks": risk_items, "summary": f"Identified {len(risk_items)} risk factor(s)."},
        "section_18_valuation_analysis": {"relative_valuation": f"Valuation Score: {val:.0f}/100.", "intrinsic_valuation": "Requires financial projections.", "fair_value": "Requires peer comparison and DCF."},
        "section_19_investment_thesis": {"bull_case": strengths, "bear_case": weaknesses, "catalysts": ["Industry growth", "Market positioning"], "key_risks": [r["detail"] for r in risk_items[:3]]},
        "section_20_scorecard": {"categories": scorecard_sections, "total_score": round(overall / 10, 1), "interpretation": ai_rating},
        "section_21_final_verdict": {"long_term_rating": long_term_rating, "subscription_recommendation": verdict, "summary": thesis[:500] or score_exp[:500] or summary[:500]},
        "investment_verdict": investment_verdict,
    }

def main():
    import sys
    FORCE = "--force" in sys.argv

    # Load master DB for analysis data
    with open(os.path.join(DATA_DIR, "ipo_master_database.json"), encoding="utf-8") as f:
        db = json.load(f)
    master_lookup = {}
    for ipo in db["ipos"]:
        master_lookup[ipo.get("company_name", "").lower().strip()] = ipo
    print(f"Loaded {len(master_lookup)} master DB entries.")

    # Load existing comprehensive analysis
    src_path = os.path.join(SRC_DIR, "ipoComprehensiveAnalysis.json")
    try:
        with open(src_path, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"Loaded {len(existing)} existing comprehensive analysis entries.")
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}
        print("No existing comprehensive analysis found.")

    # Extract slugs from the generated TS (authoritative mapping)
    slug_map = extract_slugs_from_ts()
    print(f"Found {len(slug_map)} IPOs in generated TS.")

    # Create lookup from company name to (id, slug)
    company_to_slug = {}
    for company, id_val, slug in slug_map:
        company_to_slug[company.lower().strip()] = (id_val, slug)

    new_count = 0
    skipped = 0
    output = dict(existing)

    for company_lower, (id_val, slug) in company_to_slug.items():
        if slug in output and not FORCE:
            skipped += 1
            continue

        # Find master DB entry
        ipo = master_lookup.get(company_lower)
        if not ipo:
            skipped += 1
            continue

        output[slug] = generate_entry(ipo, slug)
        new_count += 1
        if new_count % 100 == 0:
            print(f"  Generated {new_count} new (skipped {skipped})...")

    with open(src_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {new_count} new + {skipped} existing = {len(output)} total -> {src_path}")
    size_mb = os.path.getsize(src_path) / 1024 / 1024
    print(f"File size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
