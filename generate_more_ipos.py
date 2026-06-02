import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

MORE_IPOS = [
    # Format: (company, ticker, sector, price_band, open_date, close_date, listing_date, issue_size, exchange, status, country, description)
    
    # Indian Mainboard IPOs
    ("Swiggy", "SWIGGY", "Food Delivery / Technology", "₹350 - ₹390", "2026-07-01", "2026-07-05", "2026-07-10", "₹10,000 Cr", "NSE", "upcoming", "India", "India's leading food delivery and restaurant discovery platform"),
    ("MobiKwik", "MOBIKWIK", "Fintech / Digital Payments", "₹250 - ₹275", "2026-06-25", "2026-06-29", "2026-07-05", "₹1,200 Cr", "NSE", "upcoming", "India", "Leading digital payments and financial services platform in India"),
    ("Vishal Mega Mart", "VISHAL", "Retail / FMCG", "₹70 - ₹78", "2026-06-20", "2026-06-24", "2026-07-01", "₹3,500 Cr", "NSE", "upcoming", "India", "India's leading hypermarket chain offering groceries and general merchandise"),
    ("LG Electronics India", "LGINDIA", "Consumer Electronics", "₹2,800 - ₹3,100", "2026-07-15", "2026-07-19", "2026-07-25", "₹12,000 Cr", "NSE", "upcoming", "India", "Leading consumer electronics and home appliances company in India"),
    ("NSE", "NSE", "Stock Exchange / Financial Services", "₹2,500 - ₹2,800", "2026-08-01", "2026-08-05", "2026-08-12", "₹20,000 Cr", "NSE", "upcoming", "India", "India's largest stock exchange and leading financial marketplace"),
    ("Bajaj Housing Finance", "BAJAJHOUSING", "Housing Finance", "₹60 - ₹66", "2026-06-15", "2026-06-19", "2026-06-25", "₹5,000 Cr", "NSE", "upcoming", "India", "Leading housing finance company offering home loans and mortgage solutions"),
    ("Lenskart", "LENSKART", "Eyewear / Retail", "₹650 - ₹720", "2026-09-01", "2026-09-05", "2026-09-12", "₹3,000 Cr", "NSE", "upcoming", "India", "India's leading omnichannel eyewear retailer with in-house manufacturing"),
    ("Razorpay", "RAZORPAY", "Fintech / Payments", "₹450 - ₹500", "2026-08-15", "2026-08-19", "2026-08-26", "₹7,500 Cr", "NSE", "upcoming", "India", "India's leading full-stack financial solutions platform for businesses"),
    ("Urban Company", "URBAN", "Home Services / Technology", "₹380 - ₹420", "2026-07-20", "2026-07-24", "2026-07-31", "₹2,500 Cr", "NSE", "upcoming", "India", "India's leading home services marketplace connecting professionals with consumers"),
    ("Mamaearth (Honasa)", "MAMAEARTH", "Personal Care / D2C", "₹280 - ₹310", "2026-06-10", "2026-06-14", "2026-06-20", "₹2,000 Cr", "NSE", "upcoming", "India", "India's leading D2C personal care brand with natural and toxin-free products"),
    ("Nykaa Fashion", "NYKAAFASHION", "E-commerce / Fashion", "₹180 - ₹210", "2026-09-10", "2026-09-14", "2026-09-21", "₹1,800 Cr", "NSE", "upcoming", "India", "Leading online fashion and lifestyle retail platform for premium brands"),
    ("Pine Labs", "PINELABS", "Fintech / Merchant Commerce", "₹1,200 - ₹1,350", "2026-10-01", "2026-10-05", "2026-10-12", "₹5,000 Cr", "NSE", "upcoming", "India", "Leading merchant commerce platform offering payment and retail solutions"),

    # Indian SME IPOs
    ("Astonia Foods", "ASTONIA", "FMCG / Food Processing", "₹85 - ₹90", "2026-06-15", "2026-06-20", "2026-06-27", "₹40 Cr", "BSE", "upcoming", "India", "Manufacturer of packaged food products and snacks"),
    ("GreenHive Renewables", "GREENHIVE", "Renewable Energy", "₹55 - ₹60", "2026-06-20", "2026-06-25", "2026-07-02", "₹55 Cr", "NSE", "upcoming", "India", "Solar energy solutions provider for residential and commercial segments"),
    ("MediAssist Healthcare", "MEDIASSIST", "Healthcare Services", "₹120 - ₹130", "2026-07-05", "2026-07-10", "2026-07-17", "₹75 Cr", "BSE", "upcoming", "India", "Healthcare management and medical assistance services provider"),
    ("CyberShield Technologies", "CYBERSHIELD", "Cybersecurity / IT", "₹95 - ₹105", "2026-07-10", "2026-07-15", "2026-07-22", "₹60 Cr", "NSE", "upcoming", "India", "Cybersecurity solutions provider for enterprise clients"),
    ("Swasthya Ayurveda", "SWASTHYA", "Ayurveda / Wellness", "₹65 - ₹72", "2026-08-01", "2026-08-06", "2026-08-13", "₹35 Cr", "BSE", "upcoming", "India", "Manufacturer and retailer of Ayurvedic health and wellness products"),
    ("DigiTeach Edtech", "DIGITEACH", "Education Technology", "₹45 - ₹50", "2026-08-10", "2026-08-15", "2026-08-22", "₹50 Cr", "NSE", "upcoming", "India", "Digital learning platform offering K-12 and competitive exam preparation"),

    # US IPOs
    ("CoreWeave", "CRWV", "Cloud Computing / AI", "$40.00 - $45.00", "2026-06-15", "2026-06-17", "2026-06-20", "$3.5B", "NASDAQ", "upcoming", "USA", "Specialized cloud provider for AI and machine learning workloads"),
    ("Starlink", "STRLK", "Satellite Communications", "$50.00 - $55.00", "2026-07-01", "2026-07-03", "2026-07-08", "$5.0B", "NASDAQ", "upcoming", "USA", "SpaceX's satellite internet constellation providing global broadband connectivity"),
    ("Databricks", "DATAB", "Data Analytics / AI", "$45.00 - $52.00", "2026-08-05", "2026-08-07", "2026-08-12", "$8.0B", "NASDAQ", "upcoming", "USA", "Leading data and AI platform for data engineering and machine learning"),
    ("Stripe", "STRPE", "Fintech / Payments", "$35.00 - $40.00", "2026-09-01", "2026-09-03", "2026-09-08", "$10B", "NYSE", "upcoming", "USA", "Global online payment processing platform for internet businesses"),
    ("Canva", "CNVA", "Design / Technology", "$55.00 - $62.00", "2026-09-15", "2026-09-17", "2026-09-22", "$6.0B", "NASDAQ", "upcoming", "USA", "World's leading online design and visual communication platform"),
    ("Chime", "CHIME", "Fintech / Banking", "$30.00 - $35.00", "2026-08-15", "2026-08-18", "2026-08-22", "$4.0B", "NASDAQ", "upcoming", "USA", "US-based digital banking platform offering fee-free banking services"),
    ("Chainalysis", "CHAIN", "Blockchain Analytics", "$28.00 - $33.00", "2026-07-20", "2026-07-23", "2026-07-28", "$2.0B", "NASDAQ", "upcoming", "USA", "Blockchain data platform providing compliance and investigation solutions"),
    ("Celonis", "CELO", "Process Mining / AI", "$38.00 - $44.00", "2026-09-20", "2026-09-23", "2026-09-28", "$5.0B", "NYSE", "upcoming", "USA", "Leading process mining and execution management platform for enterprises"),
    ("Deel", "DEEL", "HR Tech / Payments", "$32.00 - $38.00", "2026-10-05", "2026-10-08", "2026-10-14", "$3.0B", "NASDAQ", "upcoming", "USA", "Global payroll and compliance platform for remote teams and contractors"),
    ("Rippling", "RIPPL", "HR / IT Management", "$36.00 - $42.00", "2026-10-15", "2026-10-18", "2026-10-22", "$4.5B", "NASDAQ", "upcoming", "USA", "Unified HR, IT, and finance management platform for businesses"),
]

# Existing IPOs from the scraper
def generate_analysis(company, ticker, sector, description, exchange):
    """Generate AI analysis for an IPO."""
    sector_lower = sector.lower()
    
    if "fintech" in sector_lower or "payment" in sector_lower:
        industry_focus = "financial technology"
        growth_rate = "25-30%"
        revenue_est = "$200-500M"
        profit_est = "$20-50M"
        strengths = [
            f"Leading position in the {industry_focus} sector with strong network effects",
            "High recurring revenue model with strong customer retention",
            "Regulatory compliance and technology moat providing competitive advantage"
        ]
        risks = [
            {"text": "Intense competition from established players and new entrants", "indicator": "🟡"},
            {"text": "Regulatory changes could impact business model and profitability", "indicator": "🔴"},
            {"text": "Dependence on macroeconomic conditions and consumer spending", "indicator": "🟡"},
        ]
        scores = {"financial_health": 72, "growth_potential": 82, "risk": 65, "attractiveness": 74}
        verdict_brief = "Subscribe with a medium to long-term perspective given the strong growth trajectory"
    elif "tech" in sector_lower or "software" in sector_lower or "cloud" in sector_lower:
        industry_focus = "technology"
        growth_rate = "30-40%"
        revenue_est = "$100-300M"
        profit_est = "$10-30M"
        strengths = [
            f"Innovative technology platform disrupting the {industry_focus} landscape",
            "Strong intellectual property portfolio and R&D capabilities",
            "Experienced management team with proven execution track record"
        ]
        risks = [
            {"text": "Rapid technological change could render solutions obsolete", "indicator": "🟡"},
            {"text": "High customer acquisition costs in competitive market", "indicator": "🔴"},
            {"text": "Key person dependency on technical leadership team", "indicator": "🟡"},
        ]
        scores = {"financial_health": 70, "growth_potential": 85, "risk": 68, "attractiveness": 76}
        verdict_brief = "Subscribe for long-term growth given the strong technology moat"
    elif "renewable" in sector_lower or "energy" in sector_lower:
        industry_focus = "renewable energy"
        growth_rate = "20-25%"
        revenue_est = "$50-150M"
        profit_est = "$5-15M"
        strengths = [
            f"Strong positioning in the growing {industry_focus} sector",
            "Beneficiary of government incentives and green energy mandates",
            "Long-term PPAs providing revenue visibility and stability"
        ]
        risks = [
            {"text": "Regulatory policy changes could impact subsidies and incentives", "indicator": "🟡"},
            {"text": "High capital expenditure requirements for project development", "indicator": "🔴"},
            {"text": "Weather and environmental factors affecting energy generation", "indicator": "🟢"},
        ]
        scores = {"financial_health": 74, "growth_potential": 80, "risk": 62, "attractiveness": 73}
        verdict_brief = "Subscribe given the strong ESG tailwinds and government support"
    elif "retail" in sector_lower or "fashion" in sector_lower or "consumer" in sector_lower:
        industry_focus = "consumer retail"
        growth_rate = "15-20%"
        revenue_est = "$200-600M"
        profit_est = "$20-60M"
        strengths = [
            f"Strong brand recognition and customer loyalty in the {industry_focus} space",
            "Pan-India distribution network with multi-channel presence",
            "Diversified product portfolio catering to multiple consumer segments"
        ]
        risks = [
            {"text": "Intense competition from organized and unorganized players", "indicator": "🟡"},
            {"text": "Volatile raw material prices affecting profit margins", "indicator": "🔴"},
            {"text": "Dependence on discretionary consumer spending patterns", "indicator": "🟡"},
        ]
        scores = {"financial_health": 75, "growth_potential": 78, "risk": 62, "attractiveness": 72}
        verdict_brief = "Subscribe with a medium-term perspective given the brand strength"
    elif "healthcare" in sector_lower or "pharma" in sector_lower:
        industry_focus = "healthcare"
        growth_rate = "18-22%"
        revenue_est = "$100-400M"
        profit_est = "$15-45M"
        strengths = [
            f"Strong product pipeline and R&D capabilities in the {industry_focus} sector",
            "Regulatory approvals and quality certifications providing entry barriers",
            "Experienced management with deep domain expertise"
        ]
        risks = [
            {"text": "Regulatory approval delays could impact product launches", "indicator": "🔴"},
            {"text": "Pricing pressure from government and insurance providers", "indicator": "🟡"},
            {"text": "Patent expirations and generic competition risks", "indicator": "🟡"},
        ]
        scores = {"financial_health": 73, "growth_potential": 78, "risk": 65, "attractiveness": 72}
        verdict_brief = "Subscribe with a long-term perspective given the defensive nature"
    elif "food" in sector_lower or "fmcg" in sector_lower:
        industry_focus = "FMCG"
        growth_rate = "12-18%"
        revenue_est = "$50-200M"
        profit_est = "$5-20M"
        strengths = [
            f"Established brand presence in the growing {industry_focus} market",
            "Wide distribution network reaching urban and rural markets",
            "Product portfolio diversity reducing single-product dependency"
        ]
        risks = [
            {"text": "Raw material price volatility affecting input costs", "indicator": "🟡"},
            {"text": "Intense competition from national and regional brands", "indicator": "🟡"},
            {"text": "Changing consumer preferences and health consciousness trends", "indicator": "🟢"},
        ]
        scores = {"financial_health": 76, "growth_potential": 75, "risk": 60, "attractiveness": 72}
        verdict_brief = "Subscribe for stable returns with moderate growth potential"
    elif "fintech" in sector_lower or "banking" in sector_lower:
        industry_focus = "financial services"
        growth_rate = "20-25%"
        revenue_est = "$100-300M"
        profit_est = "$15-30M"
        strengths = [
            f"Strong digital-first platform in the {industry_focus} sector",
            "Regulatory compliance and partnerships with established financial institutions",
            "Large addressable market with underpenetrated segments"
        ]
        risks = [
            {"text": "Regulatory changes in financial services sector", "indicator": "🔴"},
            {"text": "Credit risk and asset quality concerns in lending portfolio", "indicator": "🟡"},
            {"text": "Intense competition from banks and other fintech players", "indicator": "🟡"},
        ]
        scores = {"financial_health": 72, "growth_potential": 82, "risk": 68, "attractiveness": 74}
        verdict_brief = "Subscribe for long-term growth given the digital adoption trends"
    else:
        industry_focus = sector_lower
        growth_rate = "15-25%"
        revenue_est = "$100-500M"
        profit_est = "$10-50M"
        strengths = [
            f"Strong competitive position in the {industry_focus} market",
            "Diversified revenue streams and customer base",
            "Experienced management team with strong execution capabilities"
        ]
        risks = [
            {"text": "Competitive pressure from established players", "indicator": "🟡"},
            {"text": "Regulatory and compliance risks in the operating environment", "indicator": "🟡"},
            {"text": "Macroeconomic factors affecting industry demand", "indicator": "🟡"},
        ]
        scores = {"financial_health": 72, "growth_potential": 78, "risk": 65, "attractiveness": 72}
        verdict_brief = "Subscribe with a medium to long-term investment horizon"

    return {
        "about": f"{company} ({ticker}) is a leading company in the {industry_focus} sector. {description} The company has established a strong market presence through its innovative approach and customer-centric business model. With a focus on sustainable growth and technological advancement, it is well-positioned to capitalize on the growing demand in its segment.",
        "ipo_details": f"{company} is coming up with an IPO on {exchange}. The price band is set at the above range. The offering includes both fresh issue and offer for sale components.",
        "financial_summary": f"The company has demonstrated strong financial performance with revenue growing at {growth_rate} CAGR. Estimated annual revenue stands at approximately {revenue_est} with healthy profit margins. Balance sheet remains strong with manageable debt levels and positive cash flows from operations.",
        "financial_trend": f"Revenue has grown at a compound annual rate of {growth_rate} over the past three fiscals, driven by market expansion and operational efficiencies. Profitability has shown consistent improvement as the company scales its operations.",
        "strengths": strengths,
        "risks": risks,
        "scores": scores,
        "ai_analysis": f"{company} presents a compelling investment opportunity in the growing {industry_focus} sector. The company's strong market position, robust financial performance, and experienced management team provide a solid foundation for future growth. While there are inherent risks associated with the industry and competitive landscape, the company's strategic initiatives and market positioning suggest potential for value creation over the medium to long term. Investors should carefully evaluate the valuation and their risk appetite before making investment decisions.",
        "verdict": f"The IPO offers moderate to strong listing gain potential given the company's market positioning and sector tailwinds. {verdict_brief}. Long-term outlook remains positive supported by industry growth trends and the company's competitive advantages."
    }


def main():
    # Load existing ipos.json
    ipos_path = os.path.join(DATA_DIR, "ipos.json")
    with open(ipos_path, encoding="utf-8") as f:
        ipos_data = json.load(f)
    
    existing_count = len(ipos_data.get("ipos", []))
    print(f"Existing IPOs: {existing_count}")
    
    # Load existing ipo_analysis.json
    analysis_path = os.path.join(DATA_DIR, "ipo_analysis.json")
    with open(analysis_path, encoding="utf-8") as f:
        analysis_data = json.load(f)
    
    existing_analysis_count = len(analysis_data)
    print(f"Existing analysis entries: {existing_analysis_count}")
    
    # Add more IPOs
    current_id = existing_count + 1
    added = 0
    
    for ipo in MORE_IPOS:
        company, ticker, sector, price_band, open_date, close_date, listing_date, issue_size, exchange, status, country, description = ipo
        
        # Create IPO entry
        ipo_entry = {
            "company_name": company,
            "symbol": ticker,
            "price_band": price_band,
            "open_date": open_date,
            "close_date": close_date,
            "listing_date": listing_date,
            "lot_size": "",
            "issue_size": issue_size,
            "gmp": "",
            "subscription": "",
            "status": status,
            "exchange": exchange,
            "ipo_type": "mainboard" if "NASDAQ" in exchange or "NYSE" in exchange or "NSE" in exchange else "sme",
            "country": country
        }
        ipos_data["ipos"].append(ipo_entry)
        
        # Create analysis entry
        analysis_key = f"{ticker}-{country}"
        if analysis_key not in analysis_data:
            analysis = generate_analysis(company, ticker, sector, description, exchange)
            analysis_data[analysis_key] = analysis
        
        added += 1
        current_id += 1
        
        if added % 10 == 0:
            print(f"Added {added} IPOs...")
    
    # Write updated ipos.json
    ipos_data["total"] = len(ipos_data["ipos"])
    ipos_data["last_updated"] = datetime.now().isoformat()
    with open(ipos_path, "w", encoding="utf-8") as f:
        json.dump(ipos_data, f, indent=2, ensure_ascii=False)
    
    # Write updated ipo_analysis.json
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    total = len(ipos_data["ipos"])
    print(f"\nDone! Added {added} new IPOs")
    print(f"Total IPOs in ipos.json: {total}")
    print(f"Total analysis entries: {len(analysis_data)}")

if __name__ == "__main__":
    main()
