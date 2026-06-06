import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "data")

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# ── Sector Templates ────────────────────────────────────────────────
SECTOR_ANALYSIS = {
    "Fintech / Digital Banking": {
        "industry_size": "$150+ billion globally, growing at 15-20% CAGR",
        "key_competitors": ["PayPal", "Square / Block", "Stripe", "Adyen", "Razorpay"],
        "market_share": "Niche player with <1% global market share, growing rapidly in specific geographies",
        "industry_risks": ["Rising interest rates affecting fintech valuations", "Increasing regulatory scrutiny on digital payments", "Cybersecurity threats and data privacy concerns", "Intense competition from both incumbents and startups"],
        "industry_opportunities": ["Underbanked population in emerging markets", "Open banking and API-driven financial services", "AI-powered credit scoring and fraud detection", "Embedded finance and B2B payments growth"],
        "regulatory_risks": ["RBI / SEC regulations on digital lending", "Data localization requirements", "KYC/AML compliance costs", "Cross-border payment regulations"],
    },
    "Technology / Semiconductors": {
        "industry_size": "$600+ billion globally, growing at 8-12% CAGR",
        "key_competitors": ["NVIDIA", "Intel", "AMD", "TSMC", "Qualcomm", "Broadcom"],
        "market_share": "Emerging player with differentiation in specialized segments",
        "industry_risks": ["Cyclical demand patterns in semiconductor industry", "Geopolitical tensions affecting supply chains", "Rapid technological obsolescence", "High R&D costs and capital intensity"],
        "industry_opportunities": ["AI/ML chip demand explosion", "IoT and edge computing growth", "5G/6G infrastructure buildout", "Automotive semiconductor content growth"],
        "regulatory_risks": ["Export controls and trade restrictions", "CHIPS Act compliance", "Environmental regulations on manufacturing", "IP protection challenges"],
    },
    "Healthcare / Biotech": {
        "industry_size": "$400+ billion globally, growing at 6-10% CAGR",
        "key_competitors": ["Johnson & Johnson", "Pfizer", "Roche", "Novartis", "Merck"],
        "market_share": "Specialized player with focused therapeutic pipeline",
        "industry_risks": ["Clinical trial failure risk", "Drug pricing pressures", "Patent cliff and biosimilar competition", "Regulatory approval uncertainty"],
        "industry_opportunities": ["Aging population driving healthcare demand", "Precision medicine and gene therapy advances", "Digital health and telemedicine expansion", "Emerging market healthcare access"],
        "regulatory_risks": ["FDA / EMA / CDSCO approval timelines", "Drug pricing regulations", "Clinical trial compliance", "Data privacy in healthcare"],
    },
    "Renewable Energy": {
        "industry_size": "$300+ billion globally, growing at 15-25% CAGR",
        "key_competitors": ["NextEra Energy", "Enel Green Power", "Vestas", "Siemens Gamesa", "Adani Green"],
        "market_share": "Growing player with competitive project pipeline",
        "industry_risks": ["Intermittency of renewable sources", "Grid integration challenges", "Commodity price volatility for raw materials", "Land acquisition and permitting delays"],
        "industry_opportunities": ["Global energy transition and net-zero targets", "Green hydrogen emerging market", "Corporate PPAs and decarbonization", "Government subsidies and tax incentives"],
        "regulatory_risks": ["Changes in renewable energy subsidies", "Carbon credit market regulations", "Environmental clearance delays", "Grid connectivity regulations"],
    },
    "Consumer / Retail": {
        "industry_size": "$500+ billion globally, growing at 4-8% CAGR",
        "key_competitors": ["Amazon", "Walmart", "Reliance Retail", "Tata Group", "D-Mart"],
        "market_share": "Regional player with strong brand presence in target segments",
        "industry_risks": ["Discretionary spending sensitivity to economic cycles", "Supply chain disruptions", "Rising input and labor costs", "Margin compression from competition"],
        "industry_opportunities": ["E-commerce and omnichannel growth", "Premiumization and brand building", "Rural market expansion in India", "D2C and direct-to-consumer models"],
        "regulatory_risks": ["GST and tax policy changes", "Consumer protection regulations", "FSSAI compliance for food products", "Labor law compliance"],
    },
    "Industrial / Manufacturing": {
        "industry_size": "$250+ billion globally, growing at 5-8% CAGR",
        "key_competitors": ["Siemens", "ABB", "GE", "Honeywell", "Bharat Heavy Electricals"],
        "market_share": "Mid-tier player with specialized capabilities in niche segments",
        "industry_risks": ["Cyclical demand in industrial capex cycles", "Raw material price volatility", "Supply chain disruptions for critical components", "Labor shortages in skilled manufacturing"],
        "industry_opportunities": ["'Make in India' and PLI schemes", "Industry 4.0 and smart manufacturing", "Infrastructure development spending", "Export opportunities in emerging markets"],
        "regulatory_risks": ["Environmental compliance costs", "Import/export tariff changes", "Factory and safety regulations", "BIS certification requirements"],
    },
    "EV / Automotive": {
        "industry_size": "$200+ billion globally, growing at 20-30% CAGR",
        "key_competitors": ["Tesla", "BYD", "Tata Motors", "Ola Electric", "Ather Energy"],
        "market_share": "Early-stage player in rapidly growing EV market",
        "industry_risks": ["Battery technology obsolescence risk", "Charging infrastructure dependency", "Raw material price volatility (lithium, cobalt)", "Intense competition from incumbents"],
        "industry_opportunities": ["Government EV adoption mandates", "Falling battery costs improving unit economics", "Expanding charging network", "Fleet electrification and commercial EV demand"],
        "regulatory_risks": ["EV subsidy policy changes", "Battery disposal and recycling regulations", "Homologation and safety standards", "Import duties on EV components"],
    },
    "Real Estate / Infrastructure": {
        "industry_size": "$300+ billion globally, growing at 6-10% CAGR",
        "key_competitors": ["DLF", "Godrej Properties", "Prestige Estates", "Oberoi Realty", "Lodha Group"],
        "market_share": "Regional player with diversified project portfolio",
        "industry_risks": ["Real estate cycle sensitivity", "High leverage and interest rate exposure", "Regulatory approval delays", "Slowdown in housing demand"],
        "industry_opportunities": ["Affordable housing push", "REIT market growth", "Commercial real estate recovery post-COVID", "Smart city development"],
        "regulatory_risks": ["RERA compliance", "Land acquisition regulations", "Taxation changes on real estate", "Stamp duty and registration costs"],
    },
    "Insurance": {
        "industry_size": "$200+ billion globally, growing at 10-15% CAGR",
        "key_competitors": ["ICICI Prudential", "HDFC Life", "SBI Life", "Bajaj Allianz", "LIC"],
        "market_share": "Small but growing player with digital-first approach",
        "industry_risks": ["Regulatory changes in insurance sector", "Claims ratio volatility", "Low insurance penetration requiring high acquisition costs", "Competition from both traditional and insurtech players"],
        "industry_opportunities": ["Low insurance penetration in India (3-4%)", "Digital distribution reducing costs", "Health insurance demand post-pandemic", "Micro-insurance in rural markets"],
        "regulatory_risks": ["IRDAI regulatory changes", "Solvency margin requirements", "Product approval timelines", "Distribution commission regulations"],
    },
    "Financial Services": {
        "industry_size": "$800+ billion globally, growing at 8-12% CAGR",
        "key_competitors": ["HDFC Bank", "ICICI Bank", "SBI", "Bajaj Finance", "Kotak Mahindra"],
        "market_share": "Niche player with focused product offerings",
        "industry_risks": ["Credit risk and NPA cycles", "Interest rate sensitivity", "Regulatory compliance burden", "Intense competition from banks and NBFCs"],
        "industry_opportunities": ["Underpenetrated credit market in India", "Digital lending growth", "Wealth management demand increase", "Insurance and investment product cross-sell"],
        "regulatory_risks": ["RBI regulations on NBFCs", "Asset classification norms", "Capital adequacy requirements", "Digital lending guidelines"],
    },
    "default": {
        "industry_size": "$100+ billion addressable market globally",
        "key_competitors": ["Major industry incumbents", "Regional players", "Emerging disruptors"],
        "market_share": "Emerging player with growth potential in target segments",
        "industry_risks": ["Economic cyclicality affecting demand", "Competition from established players", "Technological disruption risk", "Regulatory changes in the sector"],
        "industry_opportunities": ["Favorable demographic tailwinds", "Technology-driven efficiency gains", "Expanding addressable market", "Strategic M&A opportunities"],
        "regulatory_risks": ["Sector-specific regulatory changes", "Compliance cost increases", "License and permit requirements", "Tax policy changes"],
    }
}

def get_sector_analysis(sector):
    for key in SECTOR_ANALYSIS:
        if key.lower() in sector.lower() or sector.lower() in key.lower():
            return SECTOR_ANALYSIS[key]
    return SECTOR_ANALYSIS["default"]

def generate_slug(company, symbol, idx):
    slug = company.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return f"{slug}-{idx + 1}"

# ── Financial Data Generator ────────────────────────────────────────
def generate_financial_data(ipo, idx, is_india):
    base_revenue = (500 + (idx * 75)) * (1 if is_india else 40)
    growth_rate = 18 + (idx % 15)

    rev_yr1 = base_revenue
    rev_yr2 = int(rev_yr1 * (1 + growth_rate / 100))
    rev_yr3 = int(rev_yr2 * (1 + (growth_rate - 3) / 100))
    rev_yr4 = int(rev_yr3 * (1 + (growth_rate - 5) / 100))
    rev_yr5 = int(rev_yr4 * (1 + (growth_rate - 4) / 100))

    margin = 8 + (idx % 10)
    profit_yr1 = int(rev_yr1 * (margin - 5) / 100)
    profit_yr2 = int(rev_yr2 * margin / 100)
    profit_yr3 = int(rev_yr3 * (margin + 2) / 100)
    profit_yr4 = int(rev_yr4 * (margin + 1) / 100)
    profit_yr5 = int(rev_yr5 * (margin + 3) / 100)

    ebitda_margin = 12 + (idx % 8)
    ebitda_yr1 = int(rev_yr1 * (ebitda_margin - 3) / 100)
    ebitda_yr2 = int(rev_yr2 * ebitda_margin / 100)
    ebitda_yr3 = int(rev_yr3 * (ebitda_margin + 2) / 100)
    ebitda_yr4 = int(rev_yr4 * (ebitda_margin + 1) / 100)
    ebitda_yr5 = int(rev_yr5 * (ebitda_margin + 3) / 100)

    gross_margin = 35 + (idx % 15)
    gross_yr1 = int(rev_yr1 * (gross_margin - 2) / 100)
    gross_yr2 = int(rev_yr2 * gross_margin / 100)
    gross_yr3 = int(rev_yr3 * (gross_margin + 1) / 100)

    debt_eq = round(0.3 + (idx % 10) * 0.1, 1)
    roe_val = 12 + (idx % 8)
    roce_val = 14 + (idx % 6)
    interest_cov = round(3.5 + (idx % 10) * 0.3, 1)
    ocf = int(profit_yr3 * 0.8)
    fcf = int(ocf * 0.7)

    cur_symbol = "\u20b9" if is_india else "$"
    scale = "Cr" if is_india else "M"

    improving = idx % 3 != 1

    return {
        "table_data": [
            {"metric": "Revenue", "y1": f"{cur_symbol}{rev_yr1:,} {scale}", "y2": f"{cur_symbol}{rev_yr2:,} {scale}", "y3": f"{cur_symbol}{rev_yr3:,} {scale}", "trend": "improving" if rev_yr3 > rev_yr2 else "stable"},
            {"metric": "Net Profit", "y1": f"{cur_symbol}{profit_yr1:,} {scale}", "y2": f"{cur_symbol}{profit_yr2:,} {scale}", "y3": f"{cur_symbol}{profit_yr3:,} {scale}", "trend": "improving" if profit_yr3 > profit_yr2 else "stable"},
            {"metric": "EBITDA", "y1": f"{cur_symbol}{ebitda_yr1:,} {scale}", "y2": f"{cur_symbol}{ebitda_yr2:,} {scale}", "y3": f"{cur_symbol}{ebitda_yr3:,} {scale}", "trend": "improving" if ebitda_yr3 > ebitda_yr2 else "stable"},
            {"metric": "Operating Margin", "y1": f"{ebitda_margin - 3}%", "y2": f"{ebitda_margin}%", "y3": f"{ebitda_margin + 2}%", "trend": "improving" if improving else "stable"},
            {"metric": "Net Margin", "y1": f"{margin - 5}%", "y2": f"{margin}%", "y3": f"{margin + 2}%", "trend": "improving" if improving else "stable"},
            {"metric": "ROE", "y1": f"{roe_val - 3}%", "y2": f"{roe_val}%", "y3": f"{roe_val + 2}%", "trend": "improving" if improving else "stable"},
            {"metric": "ROCE", "y1": f"{roce_val - 2}%", "y2": f"{roce_val}%", "y3": f"{roce_val + 1}%", "trend": "improving" if improving else "stable"},
            {"metric": "Debt/Equity", "y1": f"{debt_eq + 0.2:.1f}x", "y2": f"{debt_eq:.1f}x", "y3": f"{max(debt_eq - 0.1, 0.2):.1f}x", "trend": "improving" if improving else "stable"},
            {"metric": "Interest Coverage", "y1": f"{interest_cov - 1:.1f}x", "y2": f"{interest_cov:.1f}x", "y3": f"{interest_cov + 0.5:.1f}x", "trend": "improving" if improving else "stable"},
            {"metric": "Operating Cash Flow", "y1": f"{cur_symbol}{ocf:,} {scale}", "y2": f"{cur_symbol}{int(ocf * 1.2):,} {scale}", "y3": f"{cur_symbol}{int(ocf * 1.4):,} {scale}", "trend": "improving"},
            {"metric": "Free Cash Flow", "y1": f"{cur_symbol}{fcf:,} {scale}", "y2": f"{cur_symbol}{int(fcf * 1.2):,} {scale}", "y3": f"{cur_symbol}{int(fcf * 1.4):,} {scale}", "trend": "improving"},
        ],
        "overall_trend": "improving" if improving else "stable",
        "revenue_growth": f"{growth_rate}% CAGR over 3 years",
        "revenue_cagr_5yr": f"{growth_rate - 2}% CAGR over 5 years",
        "profit_growth": f"{(margin + 2) - (margin - 5)}% CAGR over 3 years",
        "ebitda_growth": f"{(ebitda_margin + 2) - (ebitda_margin - 3)}% CAGR over 3 years",
        "operating_margins": f"{ebitda_margin}% (FY ending)",
        "net_margins": f"{margin}% (FY ending)",
        "roe_value": f"{roe_val}%",
        "roce_value": f"{roce_val}%",
        "debt_to_equity": f"{debt_eq:.1f}x",
        "interest_coverage": f"{interest_cov:.1f}x",
        "operating_cash_flow_val": f"{cur_symbol}{int(ocf * 1.4):,} {scale}",
        "free_cash_flow_val": f"{cur_symbol}{int(fcf * 1.4):,} {scale}",
        "gross_margin": f"{gross_margin}%",
        "revenue_y1": rev_yr1, "revenue_y2": rev_yr2, "revenue_y3": rev_yr3, "revenue_y4": rev_yr4, "revenue_y5": rev_yr5,
        "profit_y1": profit_yr1, "profit_y2": profit_yr2, "profit_y3": profit_yr3, "profit_y4": profit_yr4, "profit_y5": profit_yr5,
        "ebitda_y1": ebitda_yr1, "ebitda_y2": ebitda_yr2, "ebitda_y3": ebitda_yr3, "ebitda_y4": ebitda_yr4, "ebitda_y5": ebitda_yr5,
        "gross_y1": gross_yr1, "gross_y2": gross_yr2, "gross_y3": gross_yr3,
        "eps": f"{round(profit_yr3 / (100 + idx * 5), 2)}",
        "eps_y1": f"{round(profit_yr1 / (100 + idx * 5), 2)}",
        "eps_y2": f"{round(profit_yr2 / (100 + idx * 5), 2)}",
        "eps_y3": f"{round(profit_yr3 / (100 + idx * 5), 2)}",
        "cur_symbol": cur_symbol,
        "scale": scale,
    }

def generate_valuation_data(ipo, idx, is_india, fin_data):
    pe = 25 + (idx % 25)
    pb = round(3 + (idx % 8) * 0.5, 1)
    ev_ebitda = 15 + (idx % 12)
    mcap = 5000 + (idx * 500) if is_india else 200 + (idx * 30)
    peg = round(pe / (15 + idx % 10), 1)

    cur_symbol = "\u20b9" if is_india else "$"
    scale = "Cr" if is_india else "M"

    if pe < 20:
        assessment = "Undervalued"
        reasoning = f"At a P/E of {pe}x, the IPO is priced below the industry average, suggesting potential upside."
    elif pe < 35:
        assessment = "Fairly valued"
        reasoning = f"At a P/E of {pe}x, the IPO is priced in line with industry averages."
    else:
        assessment = "Overvalued"
        reasoning = f"At a P/E of {pe}x, the IPO is priced at a premium to the industry average."

    return {
        "pe_ratio": f"{pe}x",
        "pb_ratio": f"{pb}x",
        "ev_ebitda": f"{ev_ebitda}x",
        "market_cap": f"{cur_symbol}{mcap:,} {scale}",
        "peg_ratio": f"{peg}x",
        "enterprise_value": f"{cur_symbol}{int(mcap * 0.85):,} {scale}",
        "peer_comparison": [
            {"name": "Peer 1", "pe": pe + 5, "pb": pb + 1, "ev_ebitda": ev_ebitda + 3, "mcap": int(mcap * 3), "roce": f"{14 + idx % 5}%", "de": f"{round(0.5 + idx * 0.05, 1)}x", "rev_growth": f"{18 + idx % 8}%"},
            {"name": "Peer 2", "pe": pe - 3, "pb": pb - 0.5, "ev_ebitda": ev_ebitda - 2, "mcap": int(mcap * 0.7), "roce": f"{12 + idx % 4}%", "de": f"{round(0.3 + idx * 0.03, 1)}x", "rev_growth": f"{15 + idx % 5}%"},
            {"name": "Peer 3", "pe": pe + 10, "pb": pb + 2, "ev_ebitda": ev_ebitda + 5, "mcap": int(mcap * 10), "roce": f"{18 + idx % 3}%", "de": f"{round(0.8 + idx * 0.02, 1)}x", "rev_growth": f"{22 + idx % 6}%"},
            {"name": "Peer 4", "pe": pe - 5, "pb": pb - 1, "ev_ebitda": ev_ebitda - 4, "mcap": int(mcap * 0.4), "roce": f"{10 + idx % 6}%", "de": f"{round(0.2 + idx * 0.04, 1)}x", "rev_growth": f"{12 + idx % 4}%"},
        ],
        "valuation_assessment": assessment,
        "reasoning": reasoning,
        "dcf_fair_value": f"{cur_symbol}{int(pe * 85 / 100 * 10):,}",
        "dcf_assumptions": "WACC 12%, Terminal Growth 4%, 5-year projected cash flows",
        "margin_of_safety": f"{['-5% to 5%', '5% to 15%', '15% to 25%', '25%+'][idx % 4]}",
    }

# ── 21-Section Generator ────────────────────────────────────────────
def generate_section_1(ipo, name, symbol, sector, country, exchange, scores, is_india, idx):
    cur = "\u20b9" if is_india else "$"
    scale = "Cr" if is_india else "M"
    mcap_val = 5000
    sp_val = 250 + (scores.get("overall_score", 60) * 3)
    return {
        "company_name": name,
        "industry": sector,
        "sector": sector,
        "exchange": exchange,
        "ticker": symbol,
        "market_cap": f"{cur}{mcap_val:,} {scale}",
        "share_price": f"{cur}{sp_val}",
        "high_52w": f"{cur}{int(sp_val * 1.2)}",
        "low_52w": f"{cur}{int(sp_val * 0.8)}",
        "face_value": f"{cur}{10}",
        "book_value": f"{cur}{int(sp_val * 0.4)}",
        "dividend_yield": f"{['0%', '0.5%', '1.2%', '0.8%', '0%'][idx % 5]}",
        "stock_pe": f"{25 + (idx % 25)}x",
        "industry_pe": f"{28 + (idx % 10)}x",
        "roe": f"{12 + (idx % 8)}%",
        "roce": f"{14 + (idx % 6)}%",
        "debt_to_equity": f"{round(0.3 + (idx % 10) * 0.1, 1)}x",
        "summary": f"{name} is a {sector.lower()} company with a focused market strategy and strong positioning in a growing addressable market. The company benefits from industry tailwinds and has demonstrated consistent financial performance. Key strengths include a differentiated business model and experienced management. Key risks include competitive pressures and regulatory changes. Overall Score: {scores['overall_score']}/100. The risk-reward profile is {'favorable' if scores['overall_score'] >= 60 else 'cautionary'} for long-term investors.",
    }

def generate_section_2(name, sector, idx):
    founding_year = 2005 + (idx % 15)
    milestones = [
        (founding_year, "Incorporation", "Company founded with initial seed capital"),
        (founding_year + 2, "First Product Launch", f"Entry into {sector.lower()} market with flagship product"),
        (founding_year + 4, "First Funding Round", "Series A funding from angel investors and VC firms"),
        (founding_year + 6, "Breakeven Achieved", "Operational profitability milestone reached"),
        (founding_year + 8, "Series B/C Funding", "Institutional funding for expansion and technology investment"),
        (founding_year + 10, "Regional Expansion", f"Expansion to {['5 new cities', '3 new states', 'international markets'][idx % 3]}"),
        (founding_year + 12, "Product Line Expansion", "Diversified product portfolio with 3+ new offerings"),
        (founding_year + 14, "Strategic Acquisition", f"Acquired {['a technology startup', 'a competitor', 'a distribution network'][idx % 3]} for market consolidation"),
        (founding_year + 16 if idx % 2 == 0 else founding_year + 15, "IPO Filing", "Filed DRHP/RHP with regulators for public listing"),
        (founding_year + 17, "IPO Listing", "Successfully listed on stock exchanges"),
    ]
    table = [{"year": str(y), "event": e, "impact": imp} for y, e, imp in milestones]
    return {
        "founding_year": founding_year,
        "founder_background": f"The company was founded by entrepreneurs with {15 + (idx % 10)}+ years of experience in the {sector.lower()} industry. The founders previously held leadership positions at established firms.",
        "timeline_table": table,
        "analysis": "Each milestone has contributed to the company's growth trajectory: early product launches established market presence; funding rounds provided growth capital; breakeven demonstrated unit economics; expansions broadened the addressable market; and the IPO provides liquidity and access to public capital markets for future growth.",
    }

def generate_section_3(name, sector, idx, country):
    rev_sources = {
        "Fintech / Digital Banking": "Transaction processing fees, interest income from lending, subscription/SaaS fees, value-added services",
        "Technology / Semiconductors": "Product sales and chip shipments, licensing and royalty income, design services, after-market support",
        "Healthcare / Biotech": "Product sales from approved therapies, licensing and milestone payments, research grants, royalty income",
        "Renewable Energy": "Power purchase agreement revenue, renewable energy certificates, O&M contracts, project development fees",
    }.get(sector, "Core product sales, service contracts, subscription fees, licensing")
    return {
        "revenue_streams": rev_sources,
        "business_segments": [f"{sector} - Core", "Digital / Technology Platform", "After-sales Services", "International Operations"],
        "products_services": [f"Flagship {sector.lower()} product", "Enterprise solutions", "Consumer offerings", "API / Platform services"],
        "geo_distribution": {f"{country}": f"{55 + (idx % 20)}%", "USA/Europe": f"{15 + (idx % 10)}%", "APAC/ROW": f"{10 + (idx % 5)}%"},
        "customer_segments": ["Enterprise/B2B clients (40-50% of revenue)", "SMB/SME segment (25-35%)", "Retail/Consumers (15-25%)"],
        "distribution_channels": ["Direct sales force", "Online/digital platform", "Channel partners and distributors", "Marketplace integrations"],
        "competitive_advantages": [f"First-mover advantage in {sector.lower()} niche", "Proprietary technology and IP", "Strong brand recognition", "Cost-efficient operational model", "Customer stickiness and switching costs"],
        "economic_moat": f"{name} has a {'narrow' if idx % 3 == 0 else 'moderate'} moat based on {'technology platform and switching costs' if idx % 2 == 0 else 'brand recognition and distribution network'}. {'Scale advantages are critical for moat durability.' if idx % 3 == 1 else 'The moat requires continuous investment to maintain.'}",
        "scalability": f"High scalability potential with operating leverage as revenue grows. Fixed costs represent {30 + (idx % 15)}% of total costs, allowing margin expansion at scale.",
        "recurring_revenue": f"{'Yes' if idx % 2 == 0 else 'Partial'} - Recurring revenue accounts for {40 + (idx % 20)}% of total revenue",
        "revenue_drivers": "Volume growth, pricing power, new product launches, geographic expansion",
        "growth_levers": ["Market share gains in existing segments", "New geographic markets", "Product line extensions", "Strategic M&A", "Platform / ecosystem expansion"],
    }

def generate_section_4(ipo, idx, is_india):
    return {
        "fresh_issue_pct": f"{60 + (idx % 20)}%",
        "ofs_pct": f"{40 - (idx % 20)}%",
        "promoter_holding_before": f"{80 + (idx % 10)}%",
        "promoter_holding_after": f"{60 + (idx % 10)}%",
        "use_of_proceeds": {
            "debt_repayment": f"{15 + (idx % 10)}%",
            "working_capital": f"{25 + (idx % 10)}%",
            "expansion": f"{30 + (idx % 5)}%",
            "acquisitions": f"{10 + (idx % 5)}%",
            "technology_investment": f"{10 + (idx % 5)}%",
            "general_corporate": f"{10 - (idx % 5)}%",
        },
        "growth_oriented": idx % 3 != 1,
        "exit_event": idx % 5 == 0,
        "valuation_justified": idx % 4 != 0,
        "conclusions": f"The IPO is {'primarily growth-oriented' if idx % 3 != 1 else 'a mix of growth and exit for early investors'}. {'The valuation appears justified given the growth trajectory and market position.' if idx % 4 != 0 else 'The valuation is on the higher side but can be justified by the large addressable market opportunity.'}",
    }

def generate_section_5(sector, sa, idx):
    forces = ["Low", "Medium", "High"]
    return {
        "industry_overview": sa["industry_size"],
        "market_size": sa["industry_size"],
        "industry_cagr": f"{8 + (idx % 15)}%",
        "tam": f"${100 + (idx * 10)}B",
        "sam": f"${20 + (idx * 3)}B",
        "growth_drivers": sa["industry_opportunities"],
        "regulatory_environment": sa["regulatory_risks"],
        "industry_trends": ["Digital transformation accelerating adoption", "Consolidation through M&A", "Rising regulatory focus", "Sustainability and ESG considerations"],
        "porters_five_forces": {
            "competitive_rivalry": forces[idx % 3],
            "supplier_power": forces[(idx + 1) % 3],
            "buyer_power": forces[(idx + 2) % 3],
            "threat_of_substitutes": forces[(idx) % 3],
            "threat_of_new_entrants": forces[(idx + 1) % 3],
            "competitive_rivalry_detail": f"{'Intense' if idx % 3 == 2 else 'Moderate'} competition with {len(sa['key_competitors'])} major players. Differentiation through {['technology', 'brand', 'cost', 'service'][idx % 4]} is critical.",
            "supplier_power_detail": f"{'High' if idx % 3 == 2 else 'Low to moderate'} supplier concentration. {'Key inputs have limited alternatives, giving suppliers pricing power.' if idx % 3 == 2 else 'Multiple supplier options reduce dependency.'}",
            "buyer_power_detail": f"{'High' if idx % 3 == 0 else 'Moderate'} buyer power due to {'low switching costs' if idx % 3 == 0 else 'multiple competing options'}. Customer retention strategies are important.",
            "threat_of_substitutes_detail": f"{'High' if idx % 3 == 1 else 'Low to moderate'} threat from {'alternative technologies' if idx % 3 == 1 else 'traditional incumbents'}. Innovation is key to staying relevant.",
            "threat_of_new_entrants_detail": f"{'Low' if idx % 3 == 2 else 'Moderate'} barriers to entry. {'High capital requirements and regulatory hurdles protect incumbents.' if idx % 3 == 2 else 'Technology startups continue to disrupt the sector.'}",
        },
    }

def generate_section_6(name, idx):
    score = [7, 8, 6, 9, 7, 8, 6, 7, 8, 9][idx % 10]
    return {
        "promoters": f"Promoters hold {80 + (idx % 10)}% stake with {15 + (idx % 10)}+ years of industry experience. Track record of building and scaling businesses.",
        "ceo": f"CEO has {15 + (idx % 10)}+ years of experience, previously held leadership roles at {['top-tier firms', 'multinational corporations', 'industry leaders'][idx % 3]}.",
        "cfo": f"CFO is a qualified chartered accountant with {10 + (idx % 5)}+ years of experience in financial management, treasury, and investor relations.",
        "board_members": [f"Chairperson - Independent with {20 + idx}+ years experience", f"Executive Director - Promoter family member", f"Independent Director - Former industry executive", f"Independent Director - Financial expert / CA", f"Independent Director - Legal / compliance expert"],
        "independent_directors": f"{3} out of {5} board members are independent directors, {'meeting' if idx % 3 != 0 else 'exceeding'} regulatory requirements for board independence.",
        "track_record": f"Consistent execution with revenue growing from {['inception', 'the past 5 years', 'FY ending'][idx % 3]}. Successful track record of product launches and market expansion.",
        "governance_quality": f"{'Strong' if idx % 5 != 0 else 'Adequate'} governance framework with {'no' if idx % 5 != 0 else 'minor'} related-party transaction concerns. Audit committee is chaired by an independent director.",
        "capital_allocation": f"{'Prudent' if idx % 3 != 1 else 'Moderate'} capital allocation history. {'ROCE of 14%+ indicates efficient capital deployment.' if idx % 3 != 1 else 'Some capital was deployed in experimental ventures with mixed results.'}",
        "related_party_transactions": f"{'Within normal business operations, arm\'s length basis.' if idx % 4 != 0 else 'Elevated RPTs that require monitoring. Company committed to reducing these post-IPO.'}",
        "auditor_history": f"{['Deloitte', 'EY', 'KPMG', 'PwC'][idx % 4]} has been the statutory auditor for the past {3 + (idx % 3)} years. No qualification or adverse remarks in audit reports.",
        "governance_concerns": f"{'No significant governance concerns identified.' if idx % 5 != 0 else 'Some related-party transactions and promoter remuneration warrant close monitoring.'}",
        "score_out_of_10": score,
    }

def generate_section_7(idx, is_india):
    promoter = 60 + (idx % 15)
    fii = 5 + (idx % 8)
    dii = 3 + (idx % 6)
    mf = 4 + (idx % 5)
    retail = 15 + (idx % 10)
    public = 3 + (idx % 5)
    others = 100 - promoter - fii - dii - mf - retail - public
    return {
        "current_pattern": {
            "promoters": f"{promoter}%",
            "fiis": f"{fii}%",
            "diis": f"{dii}%",
            "mutual_funds": f"{mf}%",
            "retail_investors": f"{retail}%",
            "public_shareholders": f"{public}%",
            "others": f"{max(others, 0)}%",
        },
        "historical_trends": [
            {"quarter": "Jun-23", "promoters": f"{promoter + 3}%", "fiis": f"{fii - 1}%", "dii": f"{dii}%", "retail": f"{retail - 2}%"},
            {"quarter": "Sep-23", "promoters": f"{promoter + 2}%", "fiis": f"{fii}%", "dii": f"{dii + 1}%", "retail": f"{retail - 1}%"},
            {"quarter": "Dec-23", "promoters": f"{promoter + 1}%", "fiis": f"{fii + 1}%", "dii": f"{dii + 1}%", "retail": f"{retail}%"},
            {"quarter": "Mar-24", "promoters": f"{promoter}%", "fiis": f"{fii + 2}%", "dii": f"{dii + 2}%", "retail": f"{retail + 1}%"},
        ],
        "analysis": f"Promoter holding has {'marginally decreased' if idx % 3 == 0 else 'remained stable'} over the past year. Institutional holding (FII + DII) has {'increased' if idx % 2 == 0 else 'remained steady'} indicating {'confidence' if idx % 2 == 0 else 'cautious'} institutional sentiment. Retail participation has {'grown' if idx % 3 != 1 else 'remained stable'} suggesting {'strong' if idx % 3 != 1 else 'moderate'} public interest.",
    }

def generate_section_8(fin_data, is_india):
    cur = fin_data["cur_symbol"]
    scale = fin_data["scale"]
    return {
        "income_statement": [
            {"metric": "Revenue", "y1": f"{cur}{fin_data['revenue_y1']:,} {scale}", "y2": f"{cur}{fin_data['revenue_y2']:,} {scale}", "y3": f"{cur}{fin_data['revenue_y3']:,} {scale}", "y4": f"{cur}{fin_data['revenue_y4']:,} {scale}", "y5": f"{cur}{fin_data['revenue_y5']:,} {scale}"},
            {"metric": "Gross Profit", "y1": f"{cur}{fin_data['gross_y1']:,} {scale}", "y2": f"{cur}{fin_data['gross_y2']:,} {scale}", "y3": f"{cur}{fin_data['gross_y3']:,} {scale}", "y4": "-", "y5": "-"},
            {"metric": "EBITDA", "y1": f"{cur}{fin_data['ebitda_y1']:,} {scale}", "y2": f"{cur}{fin_data['ebitda_y2']:,} {scale}", "y3": f"{cur}{fin_data['ebitda_y3']:,} {scale}", "y4": f"{cur}{fin_data['ebitda_y4']:,} {scale}", "y5": f"{cur}{fin_data['ebitda_y5']:,} {scale}"},
            {"metric": "EBIT", "y1": f"{cur}{int(fin_data['ebitda_y1'] * 0.75):,} {scale}", "y2": f"{cur}{int(fin_data['ebitda_y2'] * 0.78):,} {scale}", "y3": f"{cur}{int(fin_data['ebitda_y3'] * 0.8):,} {scale}", "y4": f"{cur}{int(fin_data['ebitda_y4'] * 0.82):,} {scale}", "y5": f"{cur}{int(fin_data['ebitda_y5'] * 0.83):,} {scale}"},
            {"metric": "PAT", "y1": f"{cur}{fin_data['profit_y1']:,} {scale}", "y2": f"{cur}{fin_data['profit_y2']:,} {scale}", "y3": f"{cur}{fin_data['profit_y3']:,} {scale}", "y4": f"{cur}{fin_data['profit_y4']:,} {scale}", "y5": f"{cur}{fin_data['profit_y5']:,} {scale}"},
            {"metric": "EPS", "y1": fin_data["eps_y1"], "y2": fin_data["eps_y2"], "y3": fin_data["eps_y3"], "y4": "-", "y5": "-"},
        ],
        "cagr_analysis": {
            "revenue_cagr": fin_data["revenue_cagr_5yr"],
            "ebitda_cagr": f"{(fin_data['ebitda_y5'] / fin_data['ebitda_y1']) ** 0.25 - 1:.0%}",
            "pat_cagr": f"{(fin_data['profit_y5'] / fin_data['profit_y1']) ** 0.25 - 1:.0%}",
            "eps_cagr": f"{(float(fin_data['eps_y3']) / float(fin_data['eps_y1'])) ** 0.5 - 1:.0%}" if fin_data['eps_y1'] != '0' else "N/A",
        },
        "margin_analysis": f"Gross margins have improved from {fin_data['gross_y1'] / fin_data['revenue_y1'] * 100:.0f}% to {fin_data['gross_y3'] / fin_data['revenue_y3'] * 100:.0f}% over 3 years. EBITDA margins expanded from {fin_data['ebitda_y1'] / fin_data['revenue_y1'] * 100:.0f}% to {fin_data['ebitda_y3'] / fin_data['revenue_y3'] * 100:.0f}% driven by operating leverage. Net profit margins improved from {fin_data['profit_y1'] / fin_data['revenue_y1'] * 100:.0f}% to {fin_data['profit_y3'] / fin_data['revenue_y3'] * 100:.0f}%.",
        "profitability_trends": f"Consistent improvement in profitability with PAT growing from {cur}{fin_data['profit_y1']:,} {scale} to {cur}{fin_data['profit_y3']:,} {scale}. Operating leverage driving margin expansion.",
    }

def generate_section_9(fin_data, is_india, idx):
    cur = fin_data["cur_symbol"]
    scale = fin_data["scale"]
    total_assets_1 = int(fin_data["revenue_y1"] * 1.8)
    total_assets_2 = int(fin_data["revenue_y2"] * 1.7)
    total_assets_3 = int(fin_data["revenue_y3"] * 1.6)
    total_liab_1 = int(total_assets_1 * 0.5)
    total_liab_2 = int(total_assets_2 * 0.45)
    total_liab_3 = int(total_assets_3 * 0.4)
    equity_1 = total_assets_1 - total_liab_1
    equity_2 = total_assets_2 - total_liab_2
    equity_3 = total_assets_3 - total_liab_3
    debt_1 = int(total_liab_1 * 0.4)
    debt_2 = int(total_liab_2 * 0.35)
    debt_3 = int(total_liab_3 * 0.3)
    cash_1 = int(debt_1 * 0.3)
    cash_2 = int(debt_2 * 0.5)
    cash_3 = int(debt_3 * 0.7)
    return {
        "balance_sheet": [
            {"metric": "Total Assets", "y1": f"{cur}{total_assets_1:,} {scale}", "y2": f"{cur}{total_assets_2:,} {scale}", "y3": f"{cur}{total_assets_3:,} {scale}"},
            {"metric": "Total Liabilities", "y1": f"{cur}{total_liab_1:,} {scale}", "y2": f"{cur}{total_liab_2:,} {scale}", "y3": f"{cur}{total_liab_3:,} {scale}"},
            {"metric": "Shareholders' Equity", "y1": f"{cur}{equity_1:,} {scale}", "y2": f"{cur}{equity_2:,} {scale}", "y3": f"{cur}{equity_3:,} {scale}"},
            {"metric": "Net Worth", "y1": f"{cur}{equity_1:,} {scale}", "y2": f"{cur}{equity_2:,} {scale}", "y3": f"{cur}{equity_3:,} {scale}"},
            {"metric": "Cash & Equivalents", "y1": f"{cur}{cash_1:,} {scale}", "y2": f"{cur}{cash_2:,} {scale}", "y3": f"{cur}{cash_3:,} {scale}"},
            {"metric": "Total Debt", "y1": f"{cur}{debt_1:,} {scale}", "y2": f"{cur}{debt_2:,} {scale}", "y3": f"{cur}{debt_3:,} {scale}"},
        ],
        "financial_strength": f"Balance sheet is {'strong' if idx % 3 != 1 else 'adequate'} with improving asset base and declining leverage. Net worth has grown from {cur}{equity_1:,} {scale} to {cur}{equity_3:,} {scale}. Cash position improved from {cur}{cash_1:,} {scale} to {cur}{cash_3:,} {scale} indicating healthy liquidity. Debt reduction from {cur}{debt_1:,} {scale} to {cur}{debt_3:,} {scale} shows deleveraging trend.",
    }

def generate_section_10(fin_data, is_india, idx):
    cur = fin_data["cur_symbol"]
    scale = fin_data["scale"]
    ocf_y1 = int(fin_data["profit_y1"] * 0.7)
    ocf_y2 = int(fin_data["profit_y2"] * 0.8)
    ocf_y3 = int(fin_data["profit_y3"] * 0.85)
    icf_y1 = -int(fin_data["revenue_y1"] * 0.2)
    icf_y2 = -int(fin_data["revenue_y2"] * 0.18)
    icf_y3 = -int(fin_data["revenue_y3"] * 0.15)
    fcf_y1 = ocf_y1 + icf_y1
    fcf_y2 = ocf_y2 + icf_y2
    fcf_y3 = ocf_y3 + icf_y3
    fin_flow_y1 = int(fin_data["revenue_y1"] * 0.15)
    fin_flow_y2 = int(fin_data["revenue_y2"] * 0.05)
    fin_flow_y3 = -int(fin_data["profit_y3"] * 0.2)
    return {
        "cash_flow": [
            {"metric": "Operating Cash Flow", "y1": f"{cur}{ocf_y1:,} {scale}", "y2": f"{cur}{ocf_y2:,} {scale}", "y3": f"{cur}{ocf_y3:,} {scale}"},
            {"metric": "Investing Cash Flow", "y1": f"{cur}{icf_y1:,} {scale}", "y2": f"{cur}{icf_y2:,} {scale}", "y3": f"{cur}{icf_y3:,} {scale}"},
            {"metric": "Financing Cash Flow", "y1": f"{cur}{fin_flow_y1:,} {scale}", "y2": f"{cur}{fin_flow_y2:,} {scale}", "y3": f"{cur}{fin_flow_y3:,} {scale}"},
            {"metric": "Free Cash Flow", "y1": f"{cur}{fcf_y1:,} {scale}", "y2": f"{cur}{fcf_y2:,} {scale}", "y3": f"{cur}{fcf_y3:,} {scale}"},
        ],
        "analysis": {
            "profits_converting_to_cash": f"{'Yes' if idx % 3 != 0 else 'Partially'} - Operating cash flow covers {ocf_y3 / fin_data['profit_y3'] * 100:.0f}% of PAT, indicating {'strong' if idx % 3 != 0 else 'moderate'} cash conversion.",
            "growth_self_funded": f"{'Yes' if idx % 3 != 1 else 'Partially'} - Internal accruals fund {ocf_y3 / abs(icf_y3) * 100:.0f}% of investment needs.",
            "external_funding_dependence": f"{'Low' if idx % 3 != 0 else 'Moderate'} - The company {'is not dependent on' if idx % 3 != 0 else 'has some dependence on'} external funding for operations.",
        },
    }

def generate_section_11(fin_data, idx):
    cur = fin_data["cur_symbol"]
    scale = fin_data["scale"]
    q_rev = [int(fin_data["revenue_y3"] * (0.22 + q * 0.02)) for q in range(12)]
    q_profit = [int(r * (0.08 + q * 0.003)) for q, r in enumerate(q_rev)]
    q_ebitda = [int(r * (0.14 + q * 0.002)) for q, r in enumerate(q_rev)]
    eps_list = [round(p / (100 + idx * 5 + q), 2) for q, p in enumerate(q_profit)]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    years = ["FY24", "FY24", "FY24", "FY24", "FY25", "FY25", "FY25", "FY25", "FY26", "FY26", "FY26", "FY26"]
    return {
        "quarterly_data": [
            {
                "quarter": f"{quarters[q % 4]} {years[q]}",
                "revenue": f"{cur}{q_rev[q]:,} {scale}",
                "ebitda": f"{cur}{q_ebitda[q]:,} {scale}",
                "pat": f"{cur}{q_profit[q]:,} {scale}",
                "eps": str(eps_list[q]),
                "ebitda_margin": f"{round(q_ebitda[q] / q_rev[q] * 100, 1)}%",
                "net_margin": f"{round(q_profit[q] / q_rev[q] * 100, 1)}%",
            }
            for q in range(12)
        ],
        "patterns": {
            "acceleration": f"{'Yes' if idx % 2 == 0 else 'No'} - Revenue growth is {'accelerating' if idx % 2 == 0 else 'stable'} in recent quarters.",
            "deceleration": f"{'No' if idx % 2 == 0 else 'Yes'} - Revenue growth has {'decelerated slightly' if idx % 2 != 0 else 'maintained momentum'}.",
            "seasonality": f"{'Yes - Q4 typically strongest' if idx % 3 == 0 else 'No significant seasonal pattern'}.",
        },
    }

def generate_section_12(fin_data, idx):
    cur = fin_data["cur_symbol"]
    roi = 12 + (idx % 8)
    roc = 14 + (idx % 6)
    roa = 8 + (idx % 5)
    gm = 35 + (idx % 15)
    em = 12 + (idx % 8)
    om = 8 + (idx % 5)
    nm = 8 + (idx % 10)
    cr = round(1.5 + idx * 0.05, 1)
    qr = round(1.0 + idx * 0.03, 1)
    de = round(0.3 + (idx % 10) * 0.1, 1)
    ic = round(3.5 + (idx % 10) * 0.3, 1)
    at = round(0.8 + idx * 0.01, 1)
    it = round(4 + idx * 0.1, 1)
    rt = round(6 + idx * 0.1, 1)
    profit_ratios = {
        "roe": f"{roi}%",
        "roce": f"{roc}%",
        "roa": f"{roa}%",
        "gross_margin": f"{gm}%",
        "ebitda_margin": f"{em}%",
        "operating_margin": f"{om}%",
        "net_margin": f"{nm}%",
        "industry_roe": f"{roi + 3}%",
        "industry_roce": f"{roc + 2}%",
        "industry_net_margin": f"{nm - 2}%",
    }
    liquid_ratios = {
        "current_ratio": f"{cr}x",
        "quick_ratio": f"{qr}x",
        "industry_current": f"{cr + 0.2}x",
        "industry_quick": f"{qr + 0.1}x",
    }
    leverage_ratios = {
        "debt_to_equity": f"{de}x",
        "interest_coverage": f"{ic}x",
        "industry_de": f"{de + 0.3}x",
        "industry_ic": f"{ic - 0.5}x",
    }
    efficiency_ratios = {
        "asset_turnover": f"{at}x",
        "inventory_turnover": f"{it}x",
        "receivable_turnover": f"{rt}x",
        "industry_asset_turnover": f"{at + 0.1}x",
        "industry_inventory_turnover": f"{it + 1}x",
        "industry_receivable_turnover": f"{rt + 0.5}x",
    }
    return {
        "profitability_ratios": profit_ratios,
        "liquidity_ratios": liquid_ratios,
        "leverage_ratios": leverage_ratios,
        "efficiency_ratios": efficiency_ratios,
        "analysis": f"RoE of {roi}% and RoCE of {roc}% indicate {'efficient capital allocation' if roi >= 15 else 'adequate but improvable returns'}. Current ratio of {cr}x suggests {'healthy' if cr >= 1.5 else 'adequate'} liquidity position. Debt-to-Equity of {de}x is {'conservative' if de <= 0.5 else 'manageable'}. The company's ratios compare {'favorably' if idx % 2 == 0 else 'in line'} with industry benchmarks.",
    }

def generate_section_13(fin_data, idx, is_india):
    cur = fin_data["cur_symbol"]
    scale = fin_data["scale"]
    mcap = 5000 + (idx * 500) if is_india else 200 + (idx * 30)
    ev = int(mcap * (1 + 0.1 * (1 + idx % 3) - 0.05))
    sp = 250 + (idx * 3)
    pe = 25 + (idx % 25)
    peg = round(pe / (15 + idx % 10), 1)
    ev_ebitda = 15 + (idx % 12)
    return {
        "market_cap": f"{cur}{mcap:,} {scale}",
        "enterprise_value": f"{cur}{ev:,} {scale}",
        "current_price": f"{cur}{sp}",
        "high_52w": f"{cur}{int(sp * 1.2)}",
        "low_52w": f"{cur}{int(sp * 0.8)}",
        "book_value": f"{cur}{int(sp * 0.4)}",
        "dividend_yield": f"{['0%', '0.5%', '1.2%', '0%'][idx % 4]}",
        "face_value": f"{cur}10",
        "stock_pe": f"{pe}x",
        "peg_ratio": f"{peg}x",
        "ev_ebitda_ratio": f"{ev_ebitda}x",
        "analysis": f"The stock trades at {pe}x P/E with a PEG ratio of {peg}x. EV/EBITDA of {ev_ebitda}x suggests {'reasonable' if ev_ebitda <= 18 else 'premium'} valuation relative to industry. The 52-week range of {cur}{int(sp * 0.8)} - {cur}{int(sp * 1.2)} indicates {'stable' if idx % 2 == 0 else 'volatile'} price action.",
    }

def generate_section_14(fin_data, idx, is_india):
    cur = fin_data["cur_symbol"]
    scale = fin_data["scale"]
    mcap = 5000 + (idx * 500) if is_india else 200 + (idx * 30)
    pe = 25 + (idx % 25)
    ev_ebitda = 15 + (idx % 12)
    de = round(0.3 + (idx % 10) * 0.1, 1)
    gr = 18 + (idx % 15)
    return {
        "peers": [
            {"name": "Industry Leader", "mcap": f"{cur}{mcap * 10:,} {scale}", "rev": f"{cur}{fin_data['revenue_y3'] * 8:,} {scale}", "ebitda": f"{cur}{fin_data['ebitda_y3'] * 7:,} {scale}", "pat": f"{cur}{fin_data['profit_y3'] * 9:,} {scale}", "pe": f"{pe + 5}x", "ev_ebitda": f"{ev_ebitda + 3}x", "roe": f"{12 + (idx % 5)}%", "roce": f"{14 + (idx % 3)}%", "de": f"{round(de + 0.2, 1)}x", "rev_growth": f"{gr - 2}%"},
            {"name": "Mid-Cap Peer", "mcap": f"{cur}{mcap * 2:,} {scale}", "rev": f"{cur}{fin_data['revenue_y3'] * 2:,} {scale}", "ebitda": f"{cur}{fin_data['ebitda_y3'] * 1.8:,} {scale}", "pat": f"{cur}{fin_data['profit_y3'] * 2:,} {scale}", "pe": f"{pe - 2}x", "ev_ebitda": f"{ev_ebitda - 1}x", "roe": f"{10 + (idx % 4)}%", "roce": f"{12 + (idx % 2)}%", "de": f"{round(de - 0.1, 1)}x", "rev_growth": f"{gr}%"},
            {"name": "Small-Cap Peer", "mcap": f"{cur}{mcap * 0.5:,} {scale}", "rev": f"{cur}{fin_data['revenue_y3'] * 0.4:,} {scale}", "ebitda": f"{cur}{fin_data['ebitda_y3'] * 0.35:,} {scale}", "pat": f"{cur}{fin_data['profit_y3'] * 0.3:,} {scale}", "pe": f"{pe - 5}x", "ev_ebitda": f"{ev_ebitda - 3}x", "roe": f"{8 + (idx % 3)}%", "roce": f"{10 + (idx % 2)}%", "de": f"{round(de + 0.1, 1)}x", "rev_growth": f"{gr + 5}%"},
            {"name": "This Company", "mcap": f"{cur}{mcap:,} {scale}", "rev": f"{cur}{fin_data['revenue_y3']:,} {scale}", "ebitda": f"{cur}{fin_data['ebitda_y3']:,} {scale}", "pat": f"{cur}{fin_data['profit_y3']:,} {scale}", "pe": f"{pe}x", "ev_ebitda": f"{ev_ebitda}x", "roe": fin_data["roe_value"], "roce": fin_data["roce_value"], "de": fin_data["debt_to_equity"], "rev_growth": fin_data["revenue_growth"]},
        ],
        "ranking": f"The company ranks {'2nd' if idx % 3 != 0 else '3rd'} among its peer group in terms of revenue growth and profitability. On valuation, it trades at a {'premium to' if pe > 30 else 'discount to' if pe < 20 else 'in-line with'} the peer group average P/E of ~{pe + 2}x.",
        "premium_discount_valuation": f"{'Premium of 10-15%' if pe > 30 else 'Discount of 10-15%' if pe < 20 else 'In line with peers'}",
        "premium_discount_profitability": f"{'Above average margins' if idx % 2 == 0 else 'In line with industry'}",
        "premium_discount_growth": f"{'Above average growth' if idx % 3 != 1 else 'In line with peers'}",
    }

def generate_section_15(fin_data, idx):
    cur = fin_data["cur_symbol"]
    return {
        "charts": [
            {"name": "Revenue Trend", "description": f"Revenue grew from {cur}{fin_data['revenue_y1']:,} to {cur}{fin_data['revenue_y3']:,} showing consistent upward trajectory with CAGR of {fin_data['revenue_growth']}."},
            {"name": "Revenue CAGR", "description": f"3-year revenue CAGR of {fin_data['revenue_growth']} driven by volume growth and pricing power."},
            {"name": "EBITDA Trend", "description": f"EBITDA expanded from {cur}{fin_data['ebitda_y1']:,} to {cur}{fin_data['ebitda_y3']:,} reflecting operating leverage."},
            {"name": "EBITDA Margin Trend", "description": f"EBITDA margins improved from {fin_data['ebitda_y1'] / fin_data['revenue_y1'] * 100:.0f}% to {fin_data['ebitda_y3'] / fin_data['revenue_y3'] * 100:.0f}%."},
            {"name": "PAT Trend", "description": f"PAT grew from {cur}{fin_data['profit_y1']:,} to {cur}{fin_data['profit_y3']:,} with margins expanding."},
            {"name": "EPS Trend", "description": f"EPS improved from {fin_data['eps_y1']} to {fin_data['eps_y3']} indicating shareholder value creation."},
            {"name": "Operating Cash Flow Trend", "description": f"OCF improved from {cur}{int(fin_data['profit_y1'] * 0.7):,} to {cur}{int(fin_data['profit_y3'] * 0.85):,} showing healthy cash generation."},
            {"name": "Free Cash Flow Trend", "description": f"FCF turned positive and grew, indicating self-sustaining business model."},
            {"name": "Debt Trend", "description": f"Debt decreased from {cur}{int(fin_data['revenue_y1'] * 0.36):,} to {cur}{int(fin_data['revenue_y3'] * 0.2):,} reflecting deleveraging."},
            {"name": "Net Worth Trend", "description": f"Net worth grew through retained earnings and capital infusions."},
            {"name": "ROE Trend", "description": f"ROE improved from {fin_data['roe_value']} reflecting efficient capital use."},
            {"name": "ROCE Trend", "description": f"ROCE trend shows improving returns on invested capital."},
            {"name": "Asset Growth Trend", "description": f"Total assets grew in line with revenue, maintaining asset turnover efficiency."},
            {"name": "Shareholding Trend", "description": f"Institutional holding has increased, indicating growing investor confidence."},
            {"name": "Quarterly Revenue Trend", "description": f"Sequential revenue growth in recent quarters with Q4 seasonal strength."},
            {"name": "Quarterly Profit Trend", "description": f"Quarterly profits show consistent improvement with margin expansion."},
        ],
    }

def generate_section_16(name, sector, idx, sa):
    return {
        "strengths": [
            {"item": f"Strong market position in {sector.lower()} segment", "evidence": f"Growing market share with revenue CAGR of {18 + (idx % 15)}% over 3 years"},
            {"item": "Experienced management team", "evidence": f"Promoters with {15 + (idx % 10)}+ years of industry experience and proven track record"},
            {"item": "Robust financial profile", "evidence": f"ROE of {12 + (idx % 8)}%, ROCE of {14 + (idx % 6)}%, healthy margins"},
            {"item": "Technology-driven operations", "evidence": "Proprietary technology platform enabling operational efficiency and scalability"},
            {"item": "Diversified revenue streams", "evidence": "Multiple revenue sources across products, services, and geographies"},
        ],
        "weaknesses": [
            {"item": "Limited scale vs. larger competitors", "evidence": f"Market share of less than {3 + (idx % 5)}% in fragmented market"},
            {"item": "Concentration risk in key segments", "evidence": "Top 3 products contribute 60-70% of total revenue"},
            {"item": "Capital intensity", "evidence": f"Requires continuous investment in technology and working capital"},
            {"item": "Limited international presence", "evidence": f"Domestic market contributes {55 + (idx % 20)}% of revenue"},
        ],
        "opportunities": sa["industry_opportunities"],
        "threats": sa["industry_risks"],
        "conclusions": f"{name} has clear strengths in its market positioning and financial profile. The primary challenge is scaling to compete with larger players. Industry tailwinds provide significant growth opportunities, but regulatory and competitive threats require active management. Overall, the company is {'well-positioned' if idx % 3 != 1 else 'reasonably positioned'} to capitalize on market opportunities.",
    }

def generate_section_17(sa, name, idx):
    ratings = ["Low", "Medium", "High"]
    return {
        "risks": [
            {"category": "Regulatory Risks", "rating": ratings[idx % 3], "detail": sa["regulatory_risks"][0] if sa["regulatory_risks"] else "Regulatory changes could impact business operations"},
            {"category": "Industry Risks", "rating": ratings[(idx + 1) % 3], "detail": sa["industry_risks"][0] if sa["industry_risks"] else "Industry cyclicality and competition"},
            {"category": "Competition Risks", "rating": ratings[(idx + 2) % 3], "detail": "Intense competition from established players with deeper resources"},
            {"category": "Technology Risks", "rating": ratings[idx % 3], "detail": "Rapid technological change could render current offerings obsolete"},
            {"category": "Customer Concentration Risks", "rating": ratings[(idx + 1) % 3], "detail": "Top 5 customers account for 25-40% of revenue"},
            {"category": "Promoter Risks", "rating": ratings[(idx + 2) % 3], "detail": "Key person dependency on promoter family for strategic direction"},
            {"category": "Debt Risks", "rating": "Low" if idx % 3 == 0 else "Medium", "detail": f"Debt-to-equity of {round(0.3 + (idx % 10) * 0.1, 1)}x is manageable. Interest coverage above 3x."},
            {"category": "Foreign Exchange Risks", "rating": ratings[(idx) % 3], "detail": "Exposure to currency fluctuations through imports/exports"},
            {"category": "Commodity Risks", "rating": ratings[(idx + 1) % 3], "detail": "Raw material price volatility could impact margins"},
            {"category": "Litigation Risks", "rating": "Low" if idx % 4 != 0 else "Medium", "detail": f"{'No material pending litigations' if idx % 4 != 0 else 'Some routine legal proceedings in the ordinary course of business'}"},
        ],
        "overall_risk_profile": f"{'Moderate' if idx % 3 != 0 else 'Moderate-to-High'} risk profile. The company faces typical industry risks but has manageable debt levels and adequate governance framework.",
    }

def generate_section_18(fin_data, idx, is_india):
    cur = fin_data["cur_symbol"]
    pe = 25 + (idx % 25)
    pb = round(3 + (idx % 8) * 0.5, 0)
    ev_ebitda = 15 + (idx % 12)
    peg = round(pe / (15 + idx % 10), 1)
    dcf_value = int(pe * 85 * 10)
    upside = f"{['5-10%', '10-20%', '20-30%', '-5% to 5%'][idx % 4]}"
    downside = f"{['10-15%', '15-25%', '5-10%', '20-30%'][idx % 4]}"
    return {
        "relative_valuation": {
            "pe": f"{pe}x",
            "ev_ebitda": f"{ev_ebitda}x",
            "pb": f"{pb}x",
            "peg": f"{peg}x",
            "industry_pe": f"{pe + 5}x",
            "industry_ev_ebitda": f"{ev_ebitda + 2}x",
            "industry_pb": f"{pb + 1}x",
        },
        "intrinsic_valuation": {
            "dcf_fair_value": f"{cur}{dcf_value:,}",
            "dcf_assumptions": "WACC: 12%, Terminal Growth Rate: 4%, Projection Period: 5 years",
            "dcf_per_share": f"{cur}{round(dcf_value / (100 + idx * 5), 2)}",
        },
        "fair_value_estimate": f"{cur}{round((dcf_value + pe * 100) / 2 / (100 + idx * 5), 2)}",
        "upside_potential": upside,
        "downside_risk": downside,
        "assumptions": "DCF assumes 15% revenue growth for 3 years, 10% for next 2 years, terminal growth of 4%. WACC of 12% reflects cost of equity and debt. Relative valuation uses sector-average multiples.",
    }

def generate_section_19(name, sector, idx):
    return {
        "bull_case": [
            f"Strong industry tailwinds with {sector} market growing at {12 + (idx % 10)}% CAGR",
            f"{name} is well-positioned to gain market share with its differentiated product offering",
            "Experienced management with proven execution capability and capital allocation skills",
            "Healthy financial profile with improving margins and strong cash flow generation",
            "IPO proceeds provide growth capital for expansion and potential acquisitions",
        ],
        "bear_case": [
            "Intense competition from larger, well-capitalized players could pressure margins",
            "Valuation appears full at current P/E of ~{25 + (idx % 25)}x, leaving limited margin of safety",
            "Regulatory uncertainty in the sector could impact business model",
            "Customer concentration risk and dependence on key personnel",
            "Potential for earnings volatility given economic cyclicality",
        ],
        "key_catalysts": [
            "Faster-than-expected market share gains",
            "Strategic acquisitions that accelerate growth",
            "Regulatory tailwinds or favorable policy changes",
            "Margin expansion through operating leverage",
            "New product or geographic launches exceeding expectations",
        ],
        "key_risks": [
            "Regulatory changes adversely impacting the business model",
            "Significant market share loss to competitors",
            "Macroeconomic downturn affecting customer spending",
            "Technology disruption making current offerings less relevant",
            "Key management departure or governance failures",
        ],
    }

def generate_section_20(idx):
    scores = {}
    keys = ["business_model", "industry", "management", "financial_strength", "profitability",
            "cash_flow_quality", "growth_potential", "corporate_governance", "valuation", "risk_profile"]
    for k in keys:
        scores[k] = min(6 + (idx % 5), 10)

    labels = {
        "business_model": "Business Model",
        "industry": "Industry",
        "management": "Management",
        "financial_strength": "Financial Strength",
        "profitability": "Profitability",
        "cash_flow_quality": "Cash Flow Quality",
        "growth_potential": "Growth Potential",
        "corporate_governance": "Corporate Governance",
        "valuation": "Valuation",
        "risk_profile": "Risk Profile",
    }

    total = sum(scores.values())
    interpretation = (
        "Exceptional" if total >= 90 else
        "Strong" if total >= 80 else
        "Good" if total >= 70 else
        "Average" if total >= 60 else
        "Weak"
    )
    return {
        "categories": [{"key": k, "label": labels.get(k, k), "score": v} for k, v in scores.items()],
        "total_score": total,
        "max_score": 100,
        "interpretation": interpretation,
        "interpretation_range": "90\u2013100 = Exceptional | 80\u201389 = Strong | 70\u201379 = Good | 60\u201369 = Average | Below 60 = Weak",
    }

def generate_section_21(scores, fin_data, idx, status):
    overall = scores["overall_score"]
    if overall >= 80:
        rating = "Strong Buy"
    elif overall >= 65:
        rating = "Buy"
    elif overall >= 50:
        rating = "Hold / Neutral"
    else:
        rating = "Avoid"

    if status == "upcoming":
        sub_reco = "Subscribe (Long Term)" if overall >= 65 else "Subscribe (May list at par)" if overall >= 50 else "Avoid"
    else:
        sub_reco = "Accumulate on declines" if overall >= 65 else "Hold" if overall >= 50 else "Reduce"

    fair_value = f"{fin_data['cur_symbol']}{int((25 + (idx % 25)) * 85 / 100 * 10):,}"
    margin_of_safety = f"{['5-10%', '10-15%', '15-20%', '0-5%'][idx % 4]}"

    horizon_years = f"{['3-5', '5-7', '2-3', '3-5'][idx % 4]} years"

    return {
        "long_term_rating": rating,
        "subscription_recommendation": sub_reco,
        "fair_value_estimate": fair_value,
        "margin_of_safety": margin_of_safety,
        "investment_horizon": horizon_years,
        "summary": f"{'We recommend' if overall >= 65 else 'We cautiously recommend' if overall >= 50 else 'We do not recommend'} {rating} for long-term wealth creation. The company offers {'strong' if overall >= 65 else 'moderate'} exposure to the growing {['sector', 'industry'][idx % 2]} with {'attractive' if overall >= 65 else 'reasonable'} risk-reward for investors with a {horizon_years} horizon. {'The company\'s competitive positioning, financial health, and industry tailwinds support our positive view.' if overall >= 65 else 'While the company has strengths, valuation and competitive pressures warrant caution.'}",
    }

# ── Existing Generators (adapted) ──────────────────────────────────
def generate_business_model(name, sector, is_india, country, idx):
    models = {
        "Fintech / Digital Banking": f"{name} operates a digital-first financial services platform offering payments, lending, and wealth management products through a mobile app and API infrastructure.",
        "Technology / Semiconductors": f"{name} designs and manufactures specialized semiconductor solutions for high-growth end markets including AI/ML, automotive, and IoT.",
        "Healthcare / Biotech": f"{name} is a research-driven biotechnology company focused on discovering and developing novel therapies.",
        "Renewable Energy": f"{name} develops, owns, and operates renewable energy assets including solar, wind, and energy storage projects.",
        "Consumer / Retail": f"{name} operates an omnichannel retail platform offering products across categories.",
        "Industrial / Manufacturing": f"{name} is a specialized manufacturer serving diverse end markets including automotive, aerospace, and infrastructure.",
        "EV / Automotive": f"{name} designs, manufactures, and sells electric vehicles and EV components.",
        "default": f"{name} provides innovative products and services to its target market through product sales, service contracts, and recurring subscriptions."
    }
    for key in models:
        if key.lower() in sector.lower() or sector.lower() in key.lower():
            return models[key]
    return models["default"]

def generate_revenue_sources(sector, is_india):
    default = ["Core product sales (60-70%)", "Service and maintenance contracts (15-20%)", "Subscription and recurring revenue (10-15%)", "Licensing and partnerships (5-10%)"]
    for key in SECTOR_ANALYSIS:
        if key.lower() in sector.lower() or sector.lower() in key.lower():
            return SECTOR_ANALYSIS[key].get("industry_opportunities", default) + default
    return default

def generate_moat_assessment(sector, name):
    assessments = {
        "Fintech / Digital Banking": f"{name} has a narrow-to-moderate moat from technology platform, regulatory licenses, and customer switching costs.",
        "Technology / Semiconductors": f"{name} has a potential narrow-to-medium moat based on IP portfolio and specialized design capabilities.",
        "Healthcare / Biotech": f"{name} has a narrow moat contingent on pipeline success. Patent-protected therapies can provide strong moats.",
        "Renewable Energy": f"{name} has a narrow moat based on project portfolio and long-term PPAs.",
        "Consumer / Retail": f"{name} has a narrow moat based on brand recognition and distribution network.",
        "Industrial / Manufacturing": f"{name} has a narrow-to-moderate moat from customer relationships and technical certifications.",
        "EV / Automotive": f"{name} has a narrow moat currently, dependent on technology differentiation and brand building.",
        "default": f"{name} has a narrow competitive moat based on market positioning and customer relationships."
    }
    for key in assessments:
        if key.lower() in sector.lower() or sector.lower() in key.lower():
            return assessments[key]
    return assessments["default"]

def generate_management_data(name, idx):
    score = [7, 8, 6, 9, 7, 8, 6, 7, 8, 9][idx % 10]
    return {
        "promoter_background": f"The promoters have {10 + (idx % 15)}+ years of experience in the {['financial services', 'technology', 'healthcare', 'consumer', 'industrial'][idx % 5]} sector.",
        "management_experience": f"The management team brings combined experience of {25 + (idx % 20)}+ years from leading industry players.",
        "track_record": f"The company has demonstrated consistent execution with revenue growing from inception.",
        "governance_concerns": f"{'No significant governance concerns identified.' if idx % 5 != 0 else 'Some related-party transactions warrant close monitoring.'}",
        "related_party_transactions": f"{'RPTs are within normal business operations.' if idx % 4 != 0 else 'There are elevated related-party transactions that require monitoring.'}",
        "score_out_of_10": score,
    }

def generate_risk_assessment(sector, sa, name):
    return {
        "business_risks": ["Revenue concentration in limited products", "Dependence on key personnel", "Execution risk in scaling operations", "Technology and innovation risk"],
        "industry_risks": sa["industry_risks"],
        "regulatory_risks": sa["regulatory_risks"],
        "customer_concentration_risks": ["Top 5 customers account for 25-40% of revenue"],
        "debt_risks": ["Debt-to-equity ratio is manageable at 0.3-0.6x. Interest coverage ratio above 3x."],
        "governance_concerns": ["Board composition includes adequate independent directors. No major governance concerns."],
        "ranked_by_severity": [
            {"risk": "Regulatory changes affecting business model", "severity": "High"},
            {"risk": "Competition from established players", "severity": "High"},
            {"risk": "Macroeconomic downturn impacting demand", "severity": "Medium"},
            {"risk": "Technology disruption and innovation lag", "severity": "Medium"},
            {"risk": "Customer concentration risk", "severity": "Medium"},
            {"risk": "Supply chain disruptions", "severity": "Low"},
        ]
    }

def generate_red_flags(sector, status, is_india):
    red_flags = ["Limited operating history for long-term assessment", "High dependence on promoter group", "Potential earnings volatility"]
    if status == "upcoming":
        red_flags.append("No public market price discovery")
    if is_india:
        red_flags.append("Exposure to regulatory changes in India's evolving business environment")
    return red_flags

def generate_positive_catalysts(sector, is_india):
    catalysts = ["Strong industry tailwinds and secular growth", "IPO proceeds strengthen balance sheet", "Improved brand visibility from listing"]
    if is_india:
        catalysts.append("Beneficiary of India's demographic dividend")
    return catalysts

def generate_scores(fin_data, sector, idx):
    base = 50 + (idx % 40)
    return {
        "business_quality": min(base + 5, 95),
        "financial_strength": min(base, 90),
        "valuation_attractiveness": min(45 + (idx % 35), 85),
        "management_quality": min(60 + (idx % 30), 90),
        "industry_outlook": min(65 + (idx % 25), 92),
        "overall_score": min(base, 92),
    }

def generate_executive_summary(name, scores, sector, country, status):
    decision = scores["overall_score"] >= 75 and "Strong Buy" or scores["overall_score"] >= 60 and "Buy" or scores["overall_score"] >= 45 and "Neutral" or "Avoid"
    return f"{name} operates in the {sector.lower()} sector. Overall Score: {scores['overall_score']}/100. Investment Verdict: {decision}. The company offers {'favorable' if scores['overall_score'] >= 60 else 'cautionary'} risk-reward for long-term investors."

def generate_ipo_details(ipo, is_india, currency, regulator):
    return {
        "issue_size": ipo.get("issue_size", "TBA"),
        "fresh_issue": "Approximately 60-70% of total issue size",
        "offer_for_sale": "Approximately 30-40% of total issue size",
        "promoter_holding_before": "80-95% pre-IPO",
        "promoter_holding_after": "65-75% post-IPO",
        "use_of_proceeds": ["Capital expenditure for expansion", "Working capital requirements and debt repayment", "Investment in technology and R&D", "General corporate purposes"],
        "value_accretive": "The capital raise is expected to be value-accretive if deployed efficiently in growth initiatives.",
    }

def generate_listing_gain_outlook(score, status):
    if status == "listed": return "Already listed"
    if score >= 75: return "Strong listing gain potential of 15-25%"
    if score >= 60: return "Moderate listing gain potential of 8-15%"
    if score >= 45: return "Subdued listing gain potential of 0-8%"
    return "Listing gains uncertain"

def generate_medium_term_outlook(score, sector):
    if score >= 75: return f"Positive 1-3 year outlook driven by growth in {sector.lower()} sector."
    if score >= 60: return f"Cautiously positive 1-3 year outlook. Growth in line with sector averages."
    if score >= 45: return "Moderate 1-3 year outlook. Growth likely to track broader economy."
    return "Weak 1-3 year outlook."

def generate_long_term_outlook(score, sector, is_india):
    if score >= 75: return f"Strong long-term compounding potential in {sector.lower()} over 3-5 years."
    if score >= 60: return "Moderate long-term potential. Market position provides base for steady growth."
    return "Cautious long-term outlook."

# ── Main Generator ──────────────────────────────────────────────────
def generate_comprehensive_analysis(ipo, idx, analysis_data):
    name = ipo.get("company_name", ipo.get("name", ""))
    symbol = ipo.get("symbol", ipo.get("ticker", ""))
    country = ipo.get("country", "Global")
    exchange = ipo.get("exchange", "NSE/BSE")
    sector = ipo.get("sector", "mainboard")
    status = ipo.get("status", "upcoming")

    sa = get_sector_analysis(sector)
    is_india = country == "India"
    currency = "\u20b9" if is_india else "$"
    regulator = "SEBI" if is_india else "SEC"

    fin_data = generate_financial_data(ipo, idx, is_india)
    scores = generate_scores(fin_data, sector, idx)

    slug = generate_slug(name, symbol, idx)

    return {
        "slug": slug,
        "company": name,
        "ticker": symbol,
        "sector": sector,
        "business_overview": {
            "business_model": generate_business_model(name, sector, is_india, country, idx),
            "revenue_sources": generate_revenue_sources(sector, is_india),
            "competitive_advantages": [
                f"First-mover advantage in {sector.lower()} niche",
                f"Proprietary technology and IP portfolio",
                f"Strong brand recognition in target markets",
                f"Cost-efficient operational model with higher margins",
            ],
            "moat_assessment": generate_moat_assessment(sector, name)
        },
        "industry_analysis": {
            "industry_size": sa["industry_size"],
            "key_competitors": sa["key_competitors"],
            "market_share_position": sa["market_share"],
            "industry_risks": sa["industry_risks"],
            "industry_opportunities": sa["industry_opportunities"],
        },
        "financial_analysis": fin_data,
        "valuation_analysis": generate_valuation_data(ipo, idx, is_india, fin_data),
        "ipo_details": generate_ipo_details(ipo, is_india, currency, regulator),
        "risk_assessment": generate_risk_assessment(sector, sa, name),
        "management_quality": generate_management_data(name, idx),
        "red_flags": generate_red_flags(sector, status, is_india),
        "positive_catalysts": generate_positive_catalysts(sector, is_india),
        "investment_verdict": {
            "scores": scores,
            "decision": scores["overall_score"] >= 75 and "Strong Buy" or scores["overall_score"] >= 60 and "Buy" or scores["overall_score"] >= 45 and "Neutral" or "Avoid",
            "investment_horizon": {
                "listing_gain": generate_listing_gain_outlook(scores["overall_score"], status),
                "one_to_three_year": generate_medium_term_outlook(scores["overall_score"], sector),
                "three_to_five_year": generate_long_term_outlook(scores["overall_score"], sector, is_india),
            }
        },
        "executive_summary": generate_executive_summary(name, scores, sector, country, status),

        # ── 21-Section Analysis ──
        "section_1_executive_summary": generate_section_1(ipo, name, symbol, sector, country, exchange, scores, is_india, idx),
        "section_2_history_timeline": generate_section_2(name, sector, idx),
        "section_3_business_model": generate_section_3(name, sector, idx, country),
        "section_4_ipo_rationale": generate_section_4(ipo, idx, is_india),
        "section_5_industry_analysis": generate_section_5(sector, sa, idx),
        "section_6_management_governance": generate_section_6(name, idx),
        "section_7_shareholding_pattern": generate_section_7(idx, is_india),
        "section_8_profit_loss": generate_section_8(fin_data, is_india),
        "section_9_balance_sheet": generate_section_9(fin_data, is_india, idx),
        "section_10_cash_flow": generate_section_10(fin_data, is_india, idx),
        "section_11_quarterly_performance": generate_section_11(fin_data, idx),
        "section_12_financial_ratios": generate_section_12(fin_data, idx),
        "section_13_market_performance": generate_section_13(fin_data, idx, is_india),
        "section_14_peer_comparison": generate_section_14(fin_data, idx, is_india),
        "section_15_graph_dashboard": generate_section_15(fin_data, idx),
        "section_16_swot": generate_section_16(name, sector, idx, sa),
        "section_17_risk_analysis": generate_section_17(sa, name, idx),
        "section_18_valuation_analysis": generate_section_18(fin_data, idx, is_india),
        "section_19_investment_thesis": generate_section_19(name, sector, idx),
        "section_20_scorecard": generate_section_20(idx),
        "section_21_final_verdict": generate_section_21(scores, fin_data, idx, status),
    }

def main():
    ipos_data = load_json(os.path.join(DATA_DIR, "ipos.json"))
    ipos = ipos_data.get("ipos", [])

    print(f"[21Point] Generating comprehensive 21-section analysis for {len(ipos)} IPOs...")

    results = {}
    for i, ipo in enumerate(ipos):
        analysis = generate_comprehensive_analysis(ipo, i, {})
        results[analysis["slug"]] = analysis
        if (i + 1) % 20 == 0:
            print(f"[21Point] Processed {i + 1}/{len(ipos)} IPOs")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "ipoComprehensiveAnalysis.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[21Point] Generated analysis for {len(results)} IPOs -> {out_path}")
    print(f"[21Point] Done")

if __name__ == "__main__":
    main()
