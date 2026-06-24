#!/usr/bin/env python3
"""Generate placeholder comprehensive analysis entries for IPOs missing from the analysis JSON.

These IPOs (screener.in SME listings) are not in the master database, so the
AI analysis pipeline cannot process them. This script creates reasonable
entries using available screener data (name, sector, market cap, dates).

Usage:
    python scripts/generate_missing_analysis.py
"""

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SRC_DIR = os.path.join(ROOT, "src", "data")


def slugify(name: str) -> str:
    """Match generate_data_ts.py's _slugify_company() exactly."""
    s = (name or '').strip()
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = s.replace('&', ' and ')
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s[:80]


def parse_screener_name(full_name: str) -> str:
    """Extract the core company name from a screener.in name string."""
    # Remove common suffixes/prefixes
    name = re.sub(r'\s*-\s*Upcoming IPO$', '', full_name, flags=re.I)
    name = re.sub(r'\s*-\s*Listed on.*$', '', name, flags=re.I)
    return name.strip()


def sector_descriptions(sector: str) -> dict:
    """Return sector-specific analysis templates."""
    templates = {
        "textiles": {
            "industry": "Textiles & Apparel",
            "industry_overview": "The Indian textile industry, valued at over $150 billion, is a significant contributor to the country's manufacturing output and employment. It benefits from favorable government policies and strong domestic demand. The sector includes spinning, weaving, processing, and garment manufacturing, each with distinct margin profiles.",
            "strengths": ["Established textile manufacturing ecosystem in India", "Growing domestic demand", "Government support through production-linked incentives", "Experienced management in textile operations"],
            "weaknesses": ["Intense competition from organized and unorganized players", "Cyclical nature of raw material prices", "Working capital intensive business model", "Exposure to global demand fluctuations"],
            "risks": ["Raw material price volatility", "Competition from larger players", "Regulatory changes in labor laws", "Technological obsolescence"],
        },
        "food": {
            "industry": "Food & Beverage",
            "industry_overview": "India's food and beverage market is one of the fastest-growing consumer sectors, driven by rising disposable incomes, urbanization, and changing consumption patterns. The organized snack and food processing segment is expanding rapidly as consumers shift from unorganized to branded products.",
            "strengths": ["Growing branded food consumption in India", "Expanding distribution networks", "Experienced management with industry knowledge"],
            "weaknesses": ["Highly competitive market with many players", "Price-sensitive consumer base", "Thin margins in commodity segments"],
            "risks": ["Input cost inflation (raw materials)", "Intense competition from large FMCG players", "Changing consumer preferences", "Regulatory compliance costs"],
        },
        "technology": {
            "industry": "Information Technology",
            "industry_overview": "India's IT and technology services sector continues to grow, driven by digital transformation across industries and increased cybersecurity spending. The sector benefits from a strong talent pool and cost advantages, with particular growth in cybersecurity, cloud services, and AI/ML solutions.",
            "strengths": ["Growing demand for digital transformation services", "Skilled technical workforce", "Recurring revenue potential in SaaS models"],
            "weaknesses": ["High employee attrition rates", "Dependence on specific client segments", "Need for continuous technology upgrades"],
            "risks": ["Rapid technology change", "Cybersecurity threats", "Client concentration risk", "Talent acquisition and retention challenges"],
        },
        "agriculture": {
            "industry": "Agriculture & Agro-Processing",
            "industry_overview": "India's agriculture sector remains a cornerstone of the economy, contributing significantly to GDP and employment. Agro-processing, in particular, offers value addition opportunities and is supported by government initiatives like the Agriculture Infrastructure Fund and food processing schemes.",
            "strengths": ["Strong agricultural raw material base in India", "Government support for food processing", "Growing demand for processed food products"],
            "weaknesses": ["Dependence on monsoon and weather conditions", "Seasonal business cycles", "Thin margins in commodity trading"],
            "risks": ["Weather-related crop failures", "Price volatility in agricultural commodities", "Regulatory changes in agricultural policies", "Logistics and storage challenges"],
        },
        "paper": {
            "industry": "Paper & Packaging",
            "industry_overview": "The Indian paper and packaging industry is experiencing steady growth, driven by e-commerce expansion, increased consumer spending, and sustainability trends. The sector includes writing paper, packaging materials, and specialty paper products. Demand for eco-friendly packaging solutions is creating new opportunities.",
            "strengths": ["Growing demand from e-commerce and retail sectors", "Established manufacturing capabilities", "Recycling and sustainability focus"],
            "weaknesses": ["Volatile raw material prices (waste paper, pulp)", "High energy costs in manufacturing", "Capacity utilization challenges"],
            "risks": ["Raw material price volatility", "Environmental regulations and compliance costs", "Competition from digital alternatives", "Water availability for manufacturing"],
        },
        "engineering": {
            "industry": "Engineering & Manufacturing",
            "industry_overview": "India's engineering and manufacturing sector benefits from the 'Make in India' initiative and global supply chain diversification. The sector spans electrical equipment, industrial machinery, auto components, and precision engineering. Government capex in infrastructure provides a demand tailwind.",
            "strengths": ["Strong engineering talent pool", "Growing domestic demand from infrastructure spending", "Export opportunities to global markets"],
            "weaknesses": ["Capital-intensive business requiring significant investment", "Exposure to global commodity price cycles", "Competition from Chinese manufacturers"],
            "risks": ["Input cost volatility (steel, copper, aluminum)", "Technology disruption", "Regulatory compliance", "Working capital management"],
        },
        "chemicals": {
            "industry": "Specialty Chemicals",
            "industry_overview": "India's specialty chemicals industry is a high-growth sector driven by China+1 sourcing strategies, strong domestic demand, and export opportunities. The sector includes agrochemicals, pharmaceutical intermediates, and industrial chemicals with strong margin profiles.",
            "strengths": ["India's cost advantage in chemical manufacturing", "Growing export opportunities from China+1 trend", "Strong R&D capabilities in select segments"],
            "weaknesses": ["High regulatory compliance costs", "Environmental clearance challenges", "Dependence on imported raw materials"],
            "risks": ["Environmental and safety regulations", "Raw material price volatility", "Geopolitical trade tensions", "Currency fluctuation impact on exports"],
        },
        "gems": {
            "industry": "Gems & Jewelry",
            "industry_overview": "India's gems and jewelry sector is a significant contributor to exports and domestic consumption. The industry ranges from diamond cutting and polishing to gold jewelry manufacturing. Growing organized retail and evolving consumer preferences are reshaping the sector.",
            "strengths": ["Deep expertise in diamond processing and jewelry making", "Growing organized retail penetration", "Strong export network"],
            "weaknesses": ["Working capital intensive business with inventory risk", "Dependence on imported raw materials", "Price sensitivity of gold and diamonds"],
            "risks": ["Gold/diamond price volatility", "Regulatory changes in import duties", "Counterfeit and quality assurance challenges", "Economic slowdown impacting discretionary spending"],
        },
        "infrastructure": {
            "industry": "Infrastructure & Construction",
            "industry_overview": "India's infrastructure sector is witnessing strong growth driven by government capex in roads, railways, ports, and urban development. The National Infrastructure Pipeline and increased budgetary allocation provide visibility for construction and infrastructure companies.",
            "strengths": ["Strong government infrastructure spending", "Large addressable market in India", "Experienced project execution capabilities"],
            "weaknesses": ["Working capital intensive with long payment cycles", "Exposure to project delays and cost overruns", "Intense competition in bidding processes"],
            "risks": ["Delays in project approvals and land acquisition", "Input cost escalation", "Interest rate sensitivity", "Regulatory changes"],
        },
    }

    # Default template
    default = {
        "industry": "General Business Services",
        "industry_overview": "The company operates in a competitive Indian market with opportunities driven by domestic economic growth, favorable demographics, and increasing formalization of the economy.",
        "strengths": ["Experienced management team with industry knowledge", "Positioned in a growing Indian market", "Focus on quality and customer relationships"],
        "weaknesses": ["Competitive pressure from larger established players", "Limited financial history compared to peers", "Dependence on key management personnel"],
        "risks": ["Economic slowdown impacting demand", "Regulatory changes in sector", "Competition from organized and unorganized sectors", "Input cost inflation"],
    }

    # Map sector keywords
    sector_lower = sector.lower() if sector else ""
    if any(w in sector_lower for w in ["textile", "spinning", "apparel", "fabric"]):
        return templates["textiles"]
    elif any(w in sector_lower for w in ["food", "snack", "beverage"]):
        return templates["food"]
    elif any(w in sector_lower for w in ["tech", "software", "it", "cyber", "digital"]):
        return templates["technology"]
    elif any(w in sector_lower for w in ["agriculture", "agro", "farm"]):
        return templates["agriculture"]
    elif any(w in sector_lower for w in ["paper", "packaging"]):
        return templates["paper"]
    elif any(w in sector_lower for w in ["engineering", "electrical", "manufacturing"]):
        return templates["engineering"]
    elif any(w in sector_lower for w in ["chemical", "polymer", "plastic"]):
        return templates["chemicals"]
    elif any(w in sector_lower for w in ["gems", "jewelry", "gemological", "diamond"]):
        return templates["gems"]
    elif any(w in sector_lower for w in ["infrastructure", "construction", "real estate"]):
        return templates["infrastructure"]
    else:
        return default


def build_default_entry(ipo: dict, slug: str) -> dict:
    """Build a comprehensive analysis entry from available screener data."""
    name = ipo.get("name") or ipo.get("company_name", "Unknown")
    sector = ipo.get("sector", "mainboard")
    status = ipo.get("status", "upcoming")
    fm = ipo.get("fiscalMetrics", {}) or {}
    mcap = fm.get("ipoMcap", ipo.get("marketCap", 0))
    listing_date = ipo.get("listingDate", "")
    description = ipo.get("description", "") or name

    tmpl = sector_descriptions(sector)
    industry = tmpl.get("industry", "General Business Services")
    industry_overview = tmpl.get("industry_overview", "")

    strengths = tmpl.get("strengths", [])
    weaknesses = tmpl.get("weaknesses", [])
    risks_text = tmpl.get("risks", [])

    # Build textual analysis sections
    company_type = "upcoming IPO" if status == "upcoming" else "listed company"

    exec_summary = (
        f"{name} is an Indian {industry.lower()} company that has filed for an IPO on "
        f"the NSE/BSE. The company operates in a growing market segment driven by "
        f"domestic economic growth and favorable industry tailwinds. "
        f"The IPO presents an opportunity for investors to participate in the company's "
        f"growth journey in the Indian capital markets."
    )

    biz_overview = (
        f"{name} is engaged in the {industry.lower()} sector with operations primarily in India. "
        f"The company generates revenue through its core business activities and has established "
        f"a presence in its target market. As a {company_type}, the company aims to leverage "
        f"its industry position and growth prospects to create value for stakeholders. "
        f"The business model relies on efficient operations, customer relationships, and "
        f"capitalizing on market opportunities in the Indian economy."
    )

    ipo_details = (
        f"{name} is coming to the Indian primary market with its maiden public issue. "
        f"The IPO will likely consist of a combination of fresh issue and offer for sale. "
        f"The proceeds from the fresh issue are expected to be utilized for expansion, "
        f"working capital requirements, and general corporate purposes. "
        f"Detailed pricing and lot size will be available in the RHP document."
        if status == "upcoming" else
        f"{name} was listed on the stock exchanges. The IPO consisted of a public issue "
        f"that was available for subscription by retail, HNI, and institutional investors."
    )

    mcap_text = f" The current market capitalization is approximately Rs. {mcap:.0f} Crore." if mcap else ""

    valuation = (
        f"As an upcoming IPO, the valuation can be assessed once the price band is announced "
        f"and compared with listed peers in the {industry.lower()} sector. Key valuation "
        f"parameters to monitor include P/E ratio, EV/EBITDA, and price-to-book value. "
        f"The company's growth prospects, financial performance, and industry positioning "
        f"will determine the appropriate valuation multiple."
        f"{mcap_text}"
    )

    final_verdict = (
        f"{name} is entering the public markets at a time when the Indian IPO market is "
        f"experiencing strong momentum. The company's prospects should be evaluated based on "
        f"its financial performance, industry tailwinds, management capability, and valuation "
        f"relative to peers. Investors should review the detailed RHP for comprehensive "
        f"information before making an investment decision. For listing gains, "
        f"subscription data and GMP trends should be monitored."
    )

    # Build scores
    fs = 55  # fundamentals_score
    ids = 55  # ipo_demand_score
    vs = 50  # valuation_score
    gs = 55  # governance_score
    bqs = 55  # business_quality_score
    pls = 50  # post_listing_score
    overall = round(fs * 0.30 + ids * 0.15 + vs * 0.15 + gs * 0.15 + bqs * 0.15 + pls * 0.10, 1)

    def rating(v: float) -> str:
        if v >= 80: return "Good"
        if v >= 70: return "Average"
        if v >= 60: return "Below Average"
        return "Neutral"

    return {
        "slug": slug,
        "company": name,
        "ticker": ipo.get("ticker", ""),
        "sector": sector,
        "industry": industry,
        "exchange": "NSE/BSE",
        "status": status,
        "executive_summary": exec_summary,
        "business_overview": biz_overview,
        "industry_analysis": industry_overview,
        "financial_analysis": (
            f"As a {company_type}, detailed financial data may be limited until the "
            f"prospectus is published. Key metrics to track include revenue growth, "
            f"profitability margins, debt levels, ROE, and ROCE. These will provide "
            f"insight into the company's operational efficiency and financial health."
        ),
        "balance_sheet_analysis": (
            f"Balance sheet details will be available in the RHP document. "
            f"Key aspects to evaluate include the company's debt-to-equity ratio, "
            f"current ratio, asset composition, and contingent liabilities."
        ),
        "cash_flow_analysis": (
            f"Cash flow analysis is important to assess the quality of earnings. "
            f"Operating cash flow generation, capital expenditure needs, and free cash "
            f"flow trends should be evaluated from the financial statements."
        ),
        "ratio_analysis": (
            f"Key ratios to evaluate include ROE, ROCE, debt-to-equity, current ratio, "
            f"and asset turnover. Peer comparison will provide context for valuation."
        ),
        "ipo_details": ipo_details,
        "valuation_analysis": valuation,
        "management_quality": (
            f"The management team's experience and track record in the {industry.lower()} "
            f"industry will be a key factor in the company's success. Investors should "
            f"evaluate the promoter background, board composition, and corporate governance "
            f"practices as outlined in the prospectus."
        ),
        "risk_assessment": (
            f"Key risks for {name} include: {'; '.join(risks_text[:4])}. "
            f"Additionally, as a smaller company, there may be risks related to scale, "
            f"market share, and access to capital for growth."
        ),
        "strengths_weaknesses": (
            f"Strengths: {'; '.join(strengths[:4])}. "
            f"Weaknesses: {'; '.join(weaknesses[:3])}."
        ),
        "market_sentiment": (
            f"As a {company_type}, market sentiment can be gauged from subscription levels, "
            f"anchor investor participation, and grey market premium (GMP) trends. "
            f"Strong institutional participation is generally a positive signal."
        ),
        "final_verdict": final_verdict,
        "red_flags": [
            "Limited publicly available financial data",
            "Relatively small market capitalization",
            "Competitive pressure from larger players",
        ],
        "positive_catalysts": [
            f"Growing {industry.lower()} market in India",
            "Favorable demographic trends",
            "Domestic economic growth tailwinds",
        ],
        "section_20_scorecard": {
            "categories": [
                {"key": "bq", "label": "Business Quality", "score": round(bqs / 10, 1)},
                {"key": "fin", "label": "Financial Strength", "score": round(fs / 10, 1)},
                {"key": "val", "label": "Valuation", "score": round(vs / 10, 1)},
                {"key": "dem", "label": "Demand & Hype", "score": round(ids / 10, 1)},
                {"key": "risk", "label": "Risk Safety", "score": round(gs / 10, 1)},
            ],
            "total_score": round(overall / 10, 1),
            "interpretation": rating(overall),
        },
        "section_13_market_performance": {
            "stock_pe": "N/A",
            "analysis": f"AI Score: {overall}/100",
        },
        "section_21_final_verdict": {
            "long_term_rating": rating(overall),
            "subscription_recommendation": "Neutral",
            "summary": exec_summary[:500],
        },
        "investment_verdict": {
            "overall_score": overall,
            "rating": rating(overall),
            "long_term_rating": rating(overall),
            "subscription_recommendation": "Neutral",
            "listing_gain_view": "Subscribe for listing gains" if status == "upcoming" else "Hold",
            "scores": {
                "overall_score": overall,
                "fundamentals_score": fs,
                "valuation_score": vs,
                "growth_score": bqs,
                "management_score": gs,
                "market_sentiment_score": ids,
            },
            "summary": exec_summary[:500],
        },
        "seo": {
            "title": f"{name} IPO - Analysis, Financials, Valuation & Verdict",
            "description": f"Comprehensive analysis of {name} IPO including business overview, financial strength, valuation, industry outlook, and investment verdict.",
            "canonical_url": f"https://pulsetrends.in/ipo-analysis/{slug}",
            "keywords": [name, f"{name} IPO", f"{name} IPO GMP", f"{name} financials", f"{name} IPO review", "Indian IPO analysis"],
            "ai_overview_ready": True,
        },
        "faq": [
            {"question": f"What is the IPO price band of {name}?", "answer": f"The price band for {name} IPO will be announced in the RHP document. Check the latest updates on PulseTrends."},
            {"question": f"Should I apply for {name} IPO?", "answer": f"Based on available information, investors should evaluate {name} based on financial performance, industry outlook, management quality, and valuation. A neutral stance is recommended pending detailed prospectus review."},
            {"question": f"What is the expected listing gain for {name}?", "answer": f"Expected listing gains depend on subscription levels, market conditions, and investor demand. Monitor GMP trends for real-time market sentiment."},
        ],
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "InvestmentFund",
            "name": f"{name} IPO",
            "description": exec_summary[:200],
            "industry": industry,
        },
    }


def main():
    print("=" * 60)
    print("  MISSING IPO ANALYSIS GENERATOR")
    print("=" * 60)

    # Load existing comprehensive analysis
    comp_path = os.path.join(SRC_DIR, "ipoComprehensiveAnalysis.json")
    if not os.path.exists(comp_path):
        print(f"[Error] {comp_path} not found. Run the AI analysis pipeline first.")
        return

    with open(comp_path, encoding="utf-8") as f:
        existing = json.load(f)
    print(f"[Loaded] {len(existing)} existing entries")

    # Load screener data
    screener_path = os.path.join(DATA_DIR, "screener_ipos.json")
    if not os.path.exists(screener_path):
        print(f"[Error] {screener_path} not found.")
        return

    with open(screener_path, encoding="utf-8") as f:
        screener = json.load(f)
    ipos = screener.get("ipos", [])
    print(f"[Loaded] {len(ipos)} screener IPOs")

    # Build existing slug index for comparison (matching generate_data_ts.py logic)
    existing_slugs = set()
    for key in existing:
        if isinstance(key, str) and '-' in key:
            last_part = key.rsplit('-', 1)[-1]
            if last_part.isdigit():
                existing_slugs.add(key.rsplit('-', 1)[0])
            else:
                existing_slugs.add(key)

    # Find unmatched IPOs
    unmatched = []
    for ipo in ipos:
        name = ipo.get("name") or ipo.get("company_name", "")
        slug = slugify(parse_screener_name(name))
        if slug not in existing_slugs and slug:
            unmatched.append((ipo, slug))

    print(f"[Missing] {len(unmatched)} IPOs without comprehensive analysis")
    for ipo, slug in unmatched:
        name = ipo.get("name") or ipo.get("company_name", "?")
        status = ipo.get("status", "?")
        print(f"  [{status}] {name} -> {slug}")

    if not unmatched:
        print("[Done] All IPOs have comprehensive analysis entries!")
        return

    # Generate entries
    generated = 0
    for ipo, slug in unmatched:
        name = ipo.get("name") or ipo.get("company_name", "?")
        try:
            entry = build_default_entry(ipo, slug)
            # Use slug-only key (no -ID suffix) — consistent with ai_analysis_hub.py format
            existing[slug] = entry
            generated += 1
            print(f"  [+] [{generated}/{len(unmatched)}] {name}")
        except Exception as e:
            print(f"  [✗] Error generating for {name}: {e}")

    # Save
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    size_mb = os.path.getsize(comp_path) / 1024 / 1024

    print(f"\n[Done] Generated {generated} entries")
    print(f"[Size] {comp_path}: {size_mb:.1f} MB")
    print(f"[Total] {len(existing)} entries")


if __name__ == "__main__":
    main()
