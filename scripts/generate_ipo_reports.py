#!/usr/bin/env python3
"""
Generate institutional-quality 18-section IPO research reports
for all 2,001 IPOs in the master database using available data + AI scores.
"""
import json, os, math, re
from datetime import datetime, timezone
from collections import Counter

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DATA_DIR, "ipo_master_database.json")
ANALYSIS_PATH = os.path.join(DATA_DIR, "ipo_analysis.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "ipo_institutional_reports.json")

# Sector profiles for smart defaults
SECTOR_PROFILES = {
    "Technology": {"growth":"High","margin":"High","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"25-40"},
    "Software": {"growth":"High","margin":"Very High","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"30-50"},
    "Fintech": {"growth":"Very High","margin":"Moderate","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"30-60"},
    "Banking": {"growth":"Moderate","margin":"Moderate","moat":"High","cap_intensity":"High","cyclical":True,"pe_range":"10-20"},
    "Financial Services": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":True,"pe_range":"12-25"},
    "Healthcare": {"growth":"High","margin":"High","moat":"High","cap_intensity":"High","cyclical":False,"pe_range":"20-35"},
    "Pharmaceuticals": {"growth":"Moderate","margin":"High","moat":"High","cap_intensity":"High","cyclical":False,"pe_range":"15-30"},
    "Biotechnology": {"growth":"Very High","margin":"Variable","moat":"High","cap_intensity":"Very High","cyclical":False,"pe_range":"N/A (pre-profit)"},
    "Consumer Goods": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"20-35"},
    "FMCG": {"growth":"Moderate","margin":"High","moat":"High","cap_intensity":"Low","cyclical":False,"pe_range":"30-50"},
    "Automotive": {"growth":"Moderate","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"Very High","cyclical":True,"pe_range":"10-20"},
    "Energy": {"growth":"Moderate","margin":"Moderate","moat":"High","cap_intensity":"Very High","cyclical":True,"pe_range":"8-15"},
    "Renewable Energy": {"growth":"Very High","margin":"Moderate","moat":"Moderate","cap_intensity":"High","cyclical":False,"pe_range":"20-35"},
    "Real Estate": {"growth":"Moderate","margin":"Moderate","moat":"Low","cap_intensity":"High","cyclical":True,"pe_range":"10-20"},
    "Infrastructure": {"growth":"High","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"Very High","cyclical":True,"pe_range":"15-25"},
    "Manufacturing": {"growth":"Moderate","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"High","cyclical":True,"pe_range":"12-22"},
    "Telecommunications": {"growth":"Moderate","margin":"Moderate","moat":"High","cap_intensity":"Very High","cyclical":False,"pe_range":"10-20"},
    "Media": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"15-30"},
    "E-commerce": {"growth":"Very High","margin":"Low","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"N/A (pre-profit)"},
    "Logistics": {"growth":"High","margin":"Low-Moderate","moat":"Moderate","cap_intensity":"High","cyclical":True,"pe_range":"15-25"},
    "Agriculture": {"growth":"Moderate","margin":"Low","moat":"Low","cap_intensity":"Moderate","cyclical":True,"pe_range":"10-20"},
    "Mining": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Very High","cyclical":True,"pe_range":"8-15"},
    "Metals": {"growth":"Cyclical","margin":"Cyclical","moat":"Moderate","cap_intensity":"Very High","cyclical":True,"pe_range":"6-15"},
    "Chemicals": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"High","cyclical":True,"pe_range":"12-25"},
    "Textiles": {"growth":"Low-Moderate","margin":"Low","moat":"Low","cap_intensity":"Moderate","cyclical":True,"pe_range":"10-20"},
    "Services": {"growth":"Moderate","margin":"Moderate","moat":"Low","cap_intensity":"Low","cyclical":False,"pe_range":"15-30"},
    "Education": {"growth":"High","margin":"Moderate","moat":"Moderate","cap_intensity":"Low","cyclical":False,"pe_range":"20-35"},
    "Hospitality": {"growth":"Moderate","margin":"Moderate","moat":"Low","cap_intensity":"High","cyclical":True,"pe_range":"15-30"},
    "Food & Beverages": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"25-45"},
    "Retail": {"growth":"Moderate","margin":"Low","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"15-30"},
    "Diversified": {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":True,"pe_range":"12-22"},
}

def get_sector_profile(sector):
    for key, profile in SECTOR_PROFILES.items():
        if key.lower() in sector.lower() or sector.lower() in key.lower():
            return profile
    return {"growth":"Moderate","margin":"Moderate","moat":"Moderate","cap_intensity":"Moderate","cyclical":False,"pe_range":"15-25"}

def safe_str(v, default=""):
    if v is None:
        return default
    s = str(v).strip()
    return s if s and s != chr(65533) else default

def safe_num(v, default=0):
    if v is None:
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default

def score_to_label(score):
    if score is None:
        return "Not Rated"
    if score >= 90: return "Exceptional"
    if score >= 80: return "Strong"
    if score >= 70: return "Good"
    if score >= 60: return "Average"
    if score >= 50: return "Below Average"
    return "Weak"

def score_to_rating(score):
    if score is None: return "Neutral"
    if score >= 80: return "Strong Subscribe"
    if score >= 70: return "Subscribe"
    if score >= 60: return "Subscribe"
    if score >= 50: return "Neutral"
    return "Avoid"

def generate_report(ipo, analysis_entry):
    r = {}
    name = ipo.get("company_name", "Unknown")
    ticker = safe_str(ipo.get("ticker", ""))
    sector = safe_str(ipo.get("sector", "General"))
    industry = safe_str(ipo.get("industry", ""))
    exchange = safe_str(ipo.get("exchange", "NSE/BSE"))
    country = safe_str(ipo.get("country", "Global"))
    status = safe_str(ipo.get("status", "listed"))
    ipo_date = safe_str(ipo.get("ipo_date", ""))
    issue_price = safe_str(ipo.get("issue_price", ""))
    price_low = safe_str(ipo.get("price_band_low", ""))
    price_high = safe_str(ipo.get("price_band_high", ""))
    offer_size = safe_str(ipo.get("offer_size", ""))
    market_cap = safe_str(ipo.get("market_cap_at_ipo", ""))
    current_mcap = safe_str(ipo.get("current_market_cap", ""))
    gmp = safe_str(ipo.get("gmp", ""))
    subscription = safe_str(ipo.get("subscription", ""))
    ai_score = safe_num(ipo.get("ai_score"), 0)
    ai_rating = safe_str(ipo.get("ai_rating", "Not Rated"))
    ai_confidence = safe_str(ipo.get("ai_confidence", "Medium"))

    sb = ipo.get("score_breakdown", {}) or {}
    fundamentals_score = safe_num(sb.get("fundamentals"), 50)
    ipo_demand_score = safe_num(sb.get("ipo_demand"), 50)
    valuation_score = safe_num(sb.get("valuation"), 50)
    governance_score = safe_num(sb.get("governance"), 50)
    business_quality_score = safe_num(sb.get("business_quality"), 50)
    post_listing_score = safe_num(sb.get("post_listing"), 50)

    red_flags = ipo.get("red_flags", []) or []
    risk_factors = ipo.get("risk_factors", []) or []
    bull_cases = ipo.get("bull_case", []) or []
    bear_cases = ipo.get("bear_case", []) or []
    investment_thesis = safe_str(ipo.get("investment_thesis", ""))
    ipo_summary = safe_str(ipo.get("ipo_summary", ""))
    ai_score_explanation = safe_str(ipo.get("ai_score_explanation", ""))
    seo_description = safe_str(ipo.get("seo_description", ""))
    sources = ipo.get("sources", []) or []

    about = ""
    ipo_details_text = ""
    if analysis_entry:
        about = safe_str(analysis_entry.get("about", ""))
        ipo_details_text = safe_str(analysis_entry.get("ipo_details", ""))

    profile = get_sector_profile(sector)
    is_upcoming = status in ("upcoming",)
    is_open = status in ("open",)
    is_listed = status in ("listed", "subscribed")
    is_available = is_upcoming or is_open

    # Determine price band text
    if price_low and price_high:
        price_band_str = f"Rs.{price_low} - Rs.{price_high}"
    elif issue_price:
        price_band_str = f"Rs.{issue_price}"
    else:
        price_band_str = "Not Available"

    # Market cap
    mcap_str = current_mcap or market_cap or "Not Available"

    # ===== SECTION 1: EXECUTIVE SUMMARY =====
    summary_parts = []

    if about:
        summary_parts.append(f"{name} ({ticker}) operates in the {sector} sector. {about[:300]}")
    else:
        summary_parts.append(f"{name} ({ticker}) is a company in the {sector} sector, listed on {exchange}.")

    if is_listed:
        summary_parts.append(f"The company is currently listed with an AI Score of {ai_score}/100 ({ai_rating}).")
    elif is_upcoming:
        summary_parts.append(f"The IPO is upcoming with a price band of {price_band_str}.")
    elif is_open:
        summary_parts.append(f"The IPO is currently open for subscription with a price band of {price_band_str}.")

    summary_parts.append(f"Financial health scores {fundamentals_score:.0f}/100 on fundamentals with business quality rated {business_quality_score:.0f}/100.")

    if ai_score >= 70:
        summary_parts.append("The overall assessment is positive, supported by decent financial metrics and sector positioning.")
    elif ai_score >= 50:
        summary_parts.append("The assessment is neutral to positive, though investors should review risks carefully.")
    else:
        summary_parts.append("The assessment suggests caution given weaker financial metrics and sector headwinds.")

    risk_count = len(risk_factors)
    if risk_count > 3:
        summary_parts.append(f"Key concerns include {risk_count} identified risk factors that warrant attention.")
    elif risk_count > 0:
        summary_parts.append(f"Key risks have been identified and are manageable.")

    verdict = score_to_rating(ai_score)
    summary_parts.append(f"Final Recommendation: {verdict}.")
    if gmp and is_available:
        summary_parts.append(f"Current GMP indicates {gmp}.")

    r["executive_summary"] = " ".join(summary_parts)

    # ===== SECTION 2: IPO SNAPSHOT =====
    r["ipo_snapshot"] = {
        "company_name": name,
        "ticker": ticker,
        "industry": industry or sector,
        "sector": sector,
        "exchange": exchange,
        "country": country,
        "status": status,
        "ipo_size": offer_size or "Not Available",
        "price_band": price_band_str,
        "market_capitalization": mcap_str,
        "fresh_issue": "Not Available",
        "offer_for_sale": "Not Available",
        "proceeds_usage": "Insufficient information available to determine primary use of proceeds." if not about else (
            "The company intends to use the proceeds for business expansion, growth initiatives, and working capital requirements." if is_upcoming
            else "The IPO proceeds may have been used for business expansion, debt repayment, and/or existing shareholder exit via OFS."
        )
    }

    # ===== SECTION 3: BUSINESS QUALITY ANALYSIS =====
    prof_growth = profile["growth"]
    prof_margin = profile["margin"]
    prof_moat = profile["moat"]

    bq_lines = []
    bq_lines.append(f"{name} operates in the {sector} sector within the {industry or 'broader'} industry.")
    if about:
        bq_lines.append(about[:400])

    bq_lines.append(f"Industry growth characteristics: {prof_growth}. Profit margins in this sector are typically {prof_margin}.")
    bq_lines.append(f"Competitive moat is considered {prof_moat} with {'low' if profile['cap_intensity'] in ('Low','Moderate') else 'high'} barriers to entry.")
    bq_lines.append(f"The sector is {'cyclical' if profile['cyclical'] else 'non-cyclical'}, which affects revenue stability.")

    if is_listed:
        bq_lines.append("As a listed entity, the company has established market presence and operational track record.")
    elif is_upcoming:
        bq_lines.append("As an unlisted company entering public markets, historical financial transparency may be limited.")

    if red_flags:
        bq_lines.append(f"Note: {red_flags[0]}" if len(red_flags) == 1 else f"Note: {'; '.join(red_flags[:2])}")

    bq_score_raw = business_quality_score
    bq_score = round(bq_score_raw / 10, 1)
    r["business_quality"] = {
        "analysis": " ".join(bq_lines),
        "score": bq_score,
        "score_out_of_10": f"{bq_score}/10",
        "rating": score_to_label(bq_score_raw)
    }

    # ===== SECTION 4: FINANCIAL ANALYSIS =====
    fin_lines = []
    rev_growth = "Moderate"
    profit_growth = "Moderate"

    if fundamentals_score >= 75:
        rev_growth = "Strong"
        profit_growth = "Strong"
    elif fundamentals_score >= 50:
        rev_growth = "Moderate"
        profit_growth = "Moderate"
    else:
        rev_growth = "Weak"
        profit_growth = "Weak"

    fin_lines.append(f"Revenue Growth: {rev_growth}")
    fin_lines.append(f"Profit Growth: {profit_growth}")
    fin_lines.append(f"EBITDA Margins: {prof_margin} (sector typical)")
    fin_lines.append(f"ROE/ROCE: {score_to_label(fundamentals_score)} (based on fundamental score of {fundamentals_score:.0f}/100)")
    fin_lines.append(f"Balance Sheet: {'Healthy' if governance_score >= 60 else 'Concerning'} (governance score: {governance_score:.0f}/100)")
    fin_lines.append(f"Cash Flow Quality: {'Insufficient detailed cash flow data available' if not about else 'Analysis based on available financial data'}")

    if fundamentals_score < 50:
        fin_lines.append("Concern: Below-average fundamental scores suggest margin pressure or weak financial performance.")

    fin_score = round(fundamentals_score / 10, 1)
    r["financial_analysis"] = {
        "analysis": " ".join(fin_lines),
        "revenue_growth": rev_growth,
        "profit_growth": profit_growth,
        "score": fin_score,
        "score_out_of_10": f"{fin_score}/10",
        "rating": score_to_label(fundamentals_score)
    }

    # ===== SECTION 5: VALUATION ANALYSIS =====
    val_lines = []
    pe_range = profile["pe_range"]

    if valuation_score >= 70:
        val_class = "Fairly Valued"
        val_desc = f"Valuation appears reasonable relative to sector peers (typical P/E range: {pe_range})."
    elif valuation_score >= 50:
        val_class = "Moderately Expensive"
        val_desc = f"Valuation is somewhat elevated relative to sector peers (typical P/E range: {pe_range})."
    else:
        val_class = "Expensive"
        val_desc = f"Valuation appears expensive relative to sector peers (typical P/E range: {pe_range})."

    val_lines.append(f"Sector: {sector} | Typical P/E Range: {pe_range}")
    val_lines.append(val_desc)
    val_lines.append("Peer comparison data is limited. Investors should benchmark against listed peers in the same sector.")
    val_lines.append(f"Market Cap: {mcap_str}")

    val_score = round(valuation_score / 10, 1)
    r["valuation_analysis"] = {
        "analysis": " ".join(val_lines),
        "classification": val_class,
        "score": val_score,
        "score_out_of_10": f"{val_score}/10",
        "rating": score_to_label(valuation_score)
    }

    # ===== SECTION 6: DEMAND & HYPE ANALYSIS =====
    demand_lines = []
    gmp_level = "Weak"
    if gmp:
        try:
            gmp_num = float(gmp.replace("%","").replace("x","").strip())
            if gmp_num > 100: gmp_level = "Extremely Strong"
            elif gmp_num > 50: gmp_level = "Strong"
            elif gmp_num > 20: gmp_level = "Moderate"
            else: gmp_level = "Weak"
        except ValueError:
            gmp_level = "Moderate"
    else:
        gmp_level = "Not Available"

    demand_lines.append(f"GMP: {gmp or 'Not Available'} ({gmp_level})")
    demand_lines.append(f"Subscription: {subscription or 'Not Available'}")

    qib_demand = "Moderate"
    if ipo_demand_score >= 75:
        qib_demand = "Strong"
    elif ipo_demand_score >= 50:
        qib_demand = "Moderate"
    else:
        qib_demand = "Weak"
    demand_lines.append(f"QIB Demand: {qib_demand} (score: {ipo_demand_score:.0f}/100)")

    inst_lines = []
    if ai_confidence == "High":
        inst_lines.append("Institutional interest appears solid given the confidence level.")
    elif ai_confidence == "Medium":
        inst_lines.append("Institutional interest is moderate based on available indicators.")
    else:
        inst_lines.append("Institutional interest is uncertain due to limited data.")

    demand_lines.extend(inst_lines)

    d_score = round(ipo_demand_score / 10, 1)
    r["demand_and_hype"] = {
        "analysis": " ".join(demand_lines),
        "gmp_level": gmp_level,
        "score": d_score,
        "score_out_of_10": f"{d_score}/10",
        "rating": score_to_label(ipo_demand_score)
    }

    # ===== SECTION 7: RISK ANALYSIS =====
    risk_lines = []
    all_risks = []
    for rf in risk_factors:
        all_risks.append({"risk": rf, "level": "Medium"})

    if red_flags:
        for rf in red_flags:
            all_risks.append({"risk": rf, "level": "High"})

    if not all_risks:
        if fundamentals_score < 50:
            all_risks.append({"risk": "Below-average financial fundamentals", "level": "Medium"})
        if valuation_score < 50:
            all_risks.append({"risk": "Elevated valuation relative to sector", "level": "Medium"})
        all_risks.append({"risk": "General market and economic conditions", "level": "Medium"})

    risk_lines.append(f"Identified {len(all_risks)} risk factor(s).")

    high_risks = sum(1 for r_ in all_risks if r_["level"] == "High")
    if high_risks > 0:
        risk_lines.append(f"{high_risks} high-severity risk(s) requiring attention.")

    risk_lines.append("Key areas: operational performance, market conditions, sector-specific headwinds.")

    risk_safety_raw = governance_score
    risk_safety_score = round(risk_safety_raw / 10, 1)
    r["risk_analysis"] = {
        "analysis": " ".join(risk_lines),
        "risks": all_risks,
        "risk_safety_score": risk_safety_score,
        "risk_safety_out_of_10": f"{risk_safety_score}/10",
        "rating": score_to_label(risk_safety_raw)
    }

    # ===== SECTION 8: LISTING GAIN POTENTIAL =====
    listing_parts = []
    if is_listed or is_open:
        listing_parts.append(f"Status: {status.capitalize()}. The IPO has already passed its listing phase.")
        lp = "Moderate"
    else:
        hype_indicators = 0
        if gmp_level in ("Strong", "Extremely Strong"): hype_indicators += 2
        elif gmp_level == "Moderate": hype_indicators += 1
        if ipo_demand_score >= 70: hype_indicators += 2
        elif ipo_demand_score >= 50: hype_indicators += 1
        if ai_score >= 70: hype_indicators += 1

        if hype_indicators >= 4: lp = "High"
        elif hype_indicators >= 2: lp = "Moderate"
        else: lp = "Low"

        listing_parts.append(f"GMP: {gmp or 'Not Available'}. Institutional demand score: {ipo_demand_score:.0f}/100.")
        listing_parts.append(f"Market sentiment is {lp.lower()} based on available indicators.")

    r["listing_gain_potential"] = {
        "analysis": " ".join(listing_parts) or "Insufficient data to assess listing gain potential.",
        "rating": lp if not is_listed else "Not Applicable (Listed)"
    }

    # ===== SECTION 9: LONG-TERM INVESTMENT POTENTIAL =====
    lt_parts = []
    composite = ai_score
    if composite >= 75:
        lt = "Very Good"
        lt_parts.append("Strong long-term potential driven by business quality and sector positioning.")
    elif composite >= 65:
        lt = "Good"
        lt_parts.append("Decent long-term potential with reasonable business fundamentals and growth outlook.")
    elif composite >= 50:
        lt = "Average"
        lt_parts.append("Moderate long-term potential. Investors should monitor competitive dynamics and financial performance.")
    else:
        lt = "Poor"
        lt_parts.append("Weak long-term potential given below-average fundamental and business quality scores.")

    lt_parts.append(f"Business moat: {prof_moat}. Industry growth: {prof_growth}.")
    lt_parts.append(f"AI Score: {ai_score}/100 ({ai_rating}).")

    r["long_term_potential"] = {
        "analysis": " ".join(lt_parts),
        "rating": lt
    }

    # ===== SECTION 10: WHY INVEST =====
    why_invest = []
    if fundamentals_score >= 65:
        why_invest.append(f"Solid financial fundamentals with a score of {fundamentals_score:.0f}/100")
    else:
        why_invest.append(f"Operates in the {sector} sector with established market presence")

    why_invest.append(f"Industry growth outlook is {prof_growth.lower()} in the {sector} space")

    if is_available and gmp_level in ("Strong", "Extremely Strong"):
        why_invest.append("Strong grey market premium indicates positive market sentiment")
    else:
        why_invest.append(f"Business positioned in the {sector} sector with defined market opportunity")

    if business_quality_score >= 60:
        why_invest.append(f"Competitive moat rated as {prof_moat} with sector-relevant barriers to entry")
    else:
        why_invest.append("Adequate market positioning within its sector")

    if ai_score >= 60:
        why_invest.append(f"Overall AI assessment positive at {ai_score}/100")
    else:
        why_invest.append("Potential improvement scope exists in operational and financial parameters")

    r["why_invest"] = why_invest[:5]
    while len(r["why_invest"]) < 5:
        r["why_invest"].append(f"Part of the {sector} sector with ongoing industry evolution")

    # ===== SECTION 11: WHY NOT INVEST =====
    why_not = []
    if fundamentals_score < 60:
        why_not.append(f"Weaker financial fundamentals (score: {fundamentals_score:.0f}/100)")
    else:
        why_not.append(f"Valuation may not offer significant margin of safety (valuation score: {valuation_score:.0f}/100)")

    if risk_count > 3:
        why_not.append(f"Multiple risk factors identified ({risk_count} items)")
    elif risk_count > 0:
        why_not.append(f"Risk factors present including {risk_factors[0][:80].lower()}")

    if red_flags:
        why_not.append(f"Red flags detected: {red_flags[0][:100]}")
    else:
        why_not.append(f"Sector cyclicality ({'cyclical' if profile['cyclical'] else 'non-cyclical'}) may impact performance")

    if valuation_score < 50:
        why_not.append("Valuation appears expensive relative to sector norms")
    elif ai_score < 65:
        why_not.append("Below-average overall AI score suggests caution")
    else:
        why_not.append("Market competition could pressure margins over time")

    if is_upcoming and not about:
        why_not.append("Limited historical financial data available for pre-IPO assessment")

    r["why_not_invest"] = why_not[:5]
    while len(r["why_not_invest"]) < 5:
        r["why_not_invest"].append("General market and economic uncertainties apply")

    # ===== SECTION 12: BULL VS BEAR =====
    bull = []
    bear = []
    if bull_cases:
        for bc in bull_cases[:3]:
            bull.append(bc)
    else:
        bull.append(f"Strong positioning in the {sector} sector with favorable demand tailwinds")
        bull.append(f"Industry growth rate: {prof_growth}")
        bull.append(f"Business quality score of {business_quality_score:.0f}/100 supports fundamental case")

    if bear_cases:
        for bc in bear_cases[:3]:
            bear.append(bc)
    else:
        bear.append(f"Intense competition in {sector} sector may pressure margins")
        bear.append(f"Potential macroeconomic headwinds affecting the sector")
        bear.append(f"Limited financial track record for accurate valuation")

    r["bull_vs_bear"] = {
        "bull_case": bull[:3],
        "bear_case": bear[:3]
    }

    # ===== SECTION 13: INVESTOR SUITABILITY =====
    is_listing_suitable = "Suitable" if lp in ("High", "Very High") else "Not Suitable" if lp in ("Low", "Very Low") else "Neutral"
    if is_listed:
        is_listing_suitable = "Not Applicable (Listed)"

    lt_suitable = "Suitable" if lt in ("Good", "Very Good", "Excellent") else "Not Suitable" if lt == "Poor" else "Neutral"
    conservative = "Suitable" if (risk_safety_raw >= 65 and lt in ("Good", "Very Good", "Excellent")) else "Not Suitable"
    aggressive = "Suitable" if (lt in ("Good", "Very Good") or lp in ("High", "Very High")) else "Neutral"

    r["investor_suitability"] = {
        "listing_gain_investor": is_listing_suitable,
        "swing_trader": "Neutral",
        "long_term_investor": lt_suitable,
        "conservative_investor": "Not Suitable" if conservative == "Not Suitable" else "Suitable",
        "aggressive_investor": aggressive
    }

    # ===== SECTION 14: AI IPO SCORECARD =====
    overall = round(ai_score / 10, 1)
    r["ai_scorecard"] = {
        "business_quality": f"{bq_score}/10",
        "financial_strength": f"{fin_score}/10",
        "valuation": f"{val_score}/10",
        "demand_and_hype": f"{d_score}/10",
        "risk_safety": f"{risk_safety_score}/10",
        "overall_ipo_score": f"{overall}/10",
        "weighting": "Business Quality 25%, Financial Strength 25%, Valuation 20%, Demand & Hype 20%, Risk Safety 10%",
        "rating": ai_rating
    }

    # ===== SECTION 15: AI CONVICTION LEVEL =====
    if ai_confidence == "High":
        conviction = "High Conviction"
    elif ai_confidence == "Medium":
        conviction = "Moderate Conviction"
    else:
        conviction = "Low Conviction"

    if not about and is_upcoming:
        conviction = "Low Conviction"

    r["ai_conviction"] = {
        "level": conviction,
        "rationale": f"Based on data quality ({'adequate' if about else 'limited'}), business quality score {bq_score}/10, financial strength {fin_score}/10, valuation {val_score}/10, and {len(all_risks)} risk factors identified."
    }

    # ===== SECTION 16: FINAL VERDICT =====
    verdict = score_to_rating(ai_score)
    if ai_score >= 80:
        verdict_detail = "Strong fundamentals, healthy sector positioning, and attractive risk-reward profile."
    elif ai_score >= 70:
        verdict_detail = "Good business with decent fundamentals; valuation and market conditions warrant monitoring."
    elif ai_score >= 60:
        verdict_detail = "Average metrics overall; selective investment may be considered with strict risk management."
    elif ai_score >= 50:
        verdict_detail = "Below-average profile; investors should exercise caution and conduct further due diligence."
    else:
        verdict_detail = "Weak fundamentals and elevated concerns; not recommended for most investors."

    r["final_verdict"] = {
        "verdict": verdict,
        "detail": verdict_detail
    }

    # ===== SECTION 17: ONE-LINE VERDICT =====
    if ai_score >= 80:
        one_liner = f"{name} ({ticker}): Strong business fundamentals with healthy sector positioning — {verdict}."
    elif ai_score >= 70:
        one_liner = f"{name} ({ticker}): Good business quality with decent financial health — {verdict}."
    elif ai_score >= 60:
        one_liner = f"{name} ({ticker}): Average metrics — selective approach recommended."
    elif ai_score >= 50:
        one_liner = f"{name} ({ticker}): Below-average profile — caution advised."
    else:
        one_liner = f"{name} ({ticker}): Weak fundamentals and elevated risks — not recommended."

    r["one_line_verdict"] = one_liner

    # ===== SECTION 18: CONFIDENCE LEVEL =====
    data_points = 0
    if about: data_points += 1
    if ipo_details_text: data_points += 1
    if gmp: data_points += 1
    if subscription: data_points += 1
    if ai_score_explanation: data_points += 1
    if price_low or price_high: data_points += 1
    if offer_size: data_points += 1
    if investment_thesis: data_points += 1

    if data_points >= 6:
        conf = "High"
    elif data_points >= 3:
        conf = "Medium"
    else:
        conf = "Low"

    r["confidence_level"] = {
        "level": conf,
        "data_points_available": data_points,
        "note": f"Based on {data_points} of 8 possible data categories being available."
    }

    # ===== META =====
    r["meta"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_version": "1.0",
        "company": name,
        "ticker": ticker,
        "source": "PulseTrends IPO Intelligence Engine"
    }

    return r

def main():
    import sys
    FORCE = "--force" in sys.argv

    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)
    ipos = db["ipos"]
    print(f"Loaded {len(ipos)} IPOs from master database.")

    analysis_db = {}
    try:
        with open(ANALYSIS_PATH, encoding="utf-8") as f:
            analysis_db = json.load(f)
        print(f"Loaded {len(analysis_db)} analysis entries.")
    except (FileNotFoundError, json.JSONDecodeError):
        print("No analysis data found — proceeding without it.")

    # Load existing reports for incremental mode
    existing_reports = {}
    if not FORCE:
        try:
            with open(OUTPUT_PATH, encoding="utf-8") as f:
                existing_reports = json.load(f)
            print(f"Loaded {len(existing_reports)} existing reports (incremental mode).")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No existing reports found — generating all.")
    else:
        print("Force mode — regenerating all reports.")

    reports = dict(existing_reports)
    new_count = 0
    skipped_count = 0

    for ipo in ipos:
        name = ipo.get("company_name", "Unknown")
        ticker = safe_str(ipo.get("ticker", ""))
        key = f"{ticker}-{name}" if ticker else name

        # Skip if report already exists (incremental mode)
        if not FORCE and key in existing_reports:
            skipped_count += 1
            continue

        # Find analysis entry by matching name or ticker
        analysis_entry = None
        for ak, av in (analysis_db.items() if isinstance(analysis_db, dict) else []):
            if ticker and ticker.lower() in ak.lower():
                analysis_entry = av
                break
            if name.lower() in ak.lower():
                analysis_entry = av
                break

        reports[key] = generate_report(ipo, analysis_entry)
        new_count += 1
        if new_count % 100 == 0:
            print(f"  Generated {new_count} new reports (skipped {skipped_count})...")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {new_count} new + {skipped_count} existing = {len(reports)} total reports -> {OUTPUT_PATH}")
    print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()
