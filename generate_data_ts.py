import json
import os
import re
from datetime import datetime, timezone

import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "data")


ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "news")


def load_news_articles_from_artifacts() -> list:
    """Load all news articles from artifacts/news/*.json files."""
    if not os.path.isdir(ARTIFACTS_DIR):
        return []
    all_articles = []
    seen_ids = set()
    try:
        for fname in sorted(os.listdir(ARTIFACTS_DIR)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(ARTIFACTS_DIR, fname)
            try:
                with open(fpath, encoding="utf-8") as f:
                    batch = json.load(f)
                if not isinstance(batch, list):
                    continue
                for art in batch:
                    if not isinstance(art, dict):
                        continue
                    aid = art.get("id", "")
                    if aid and aid not in seen_ids:
                        seen_ids.add(aid)
                        all_articles.append(art)
            except Exception:
                continue
    except Exception:
        pass
    print(f"[DataGen] Loaded {len(all_articles)} articles from artifacts")
    return all_articles


def prune_old_articles(articles: list, max_days: int = 70) -> list:
    """Remove articles older than max_days from the list."""
    if not isinstance(articles, list):
        return []
    cutoff = datetime.now(timezone.utc).timestamp() - max_days * 24 * 3600
    kept = []
    for art in articles:
        if not isinstance(art, dict):
            continue
        try:
            pub = art.get("publishedAt", "")
            if pub:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                if dt.timestamp() < cutoff:
                    continue
            kept.append(art)
        except Exception:
            kept.append(art)
    pruned = len(articles) - len(kept)
    if pruned:
        print(f"[DataGen] Pruned {pruned} articles older than {max_days} days")
    return kept

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def esc(s):
    if s is None:
        return ""
    if isinstance(s, (int, float)):
        return str(s)
    if not isinstance(s, str):
        return str(s)
    val = json.dumps(s, ensure_ascii=False)[1:-1]
    # Escape single quotes used in TS strings
    val = val.replace("\\'", "'").replace("'", "\\'")
    return val


def search_news_for_ipo(company: str, ticker: str) -> str:
    if not NEWSAPI_KEY:
        return ""
    try:
        query = f"{company} IPO {ticker}"
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "pageSize": 5, "language": "en", "sortBy": "relevancy", "apiKey": NEWSAPI_KEY},
            timeout=10,
        )
        if resp.status_code == 200:
            articles = resp.json().get("articles", [])
            if not articles:
                resp2 = requests.get(
                    "https://newsapi.org/v2/everything",
                    params={"q": f"{ticker} stock", "pageSize": 3, "language": "en", "sortBy": "relevancy", "apiKey": NEWSAPI_KEY},
                    timeout=10,
                )
                articles = resp2.json().get("articles", []) if resp2.status_code == 200 else []

            snippets = []
            for a in articles[:5]:
                title = a.get("title", "")
                desc = a.get("description", "")
                src = a.get("source", {}).get("name", "")
                url = a.get("url", "")
                if title:
                    snippets.append(f"- {title} ({src})")
                    if desc:
                        snippets.append(f"  {desc[:200]}")
            if snippets:
                return "Recent News:\n" + "\n".join(snippets)
    except Exception:
        pass
    return ""


def _slugify_company(name):
    import re as _re
    import unicodedata as _ud
    s = (name or '').strip()
    s = _ud.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = s.replace('&', ' and ')
    s = _re.sub(r'[^a-z0-9]+', '-', s)
    s = _re.sub(r'^-+|-+$', '', s)
    return s[:80]



def _extract_comp_analysis(comp_entry: dict) -> dict:
    """Extract detailed analysis fields from comprehensive analysis entry."""
    if not isinstance(comp_entry, dict):
        return {}
    return {
        "executive_summary": comp_entry.get("executive_summary", ""),
        "business_overview": comp_entry.get("business_overview", ""),
        "industry_analysis": comp_entry.get("industry_analysis", ""),
        "financial_analysis": comp_entry.get("financial_analysis", ""),
        "balance_sheet_analysis": comp_entry.get("balance_sheet_analysis", ""),
        "cash_flow_analysis": comp_entry.get("cash_flow_analysis", ""),
        "ipo_details": comp_entry.get("ipo_details", ""),
        "valuation_analysis": comp_entry.get("valuation_analysis", ""),
        "management_quality": comp_entry.get("management_quality", ""),
        "risk_assessment": comp_entry.get("risk_assessment", ""),
        "strengths_weaknesses": comp_entry.get("strengths_weaknesses", ""),
        "market_sentiment": comp_entry.get("market_sentiment", ""),
        "final_verdict": comp_entry.get("final_verdict", ""),
        "red_flags": comp_entry.get("red_flags", []),
        "positive_catalysts": comp_entry.get("positive_catalysts", []),
        "long_term_rating": comp_entry.get("long_term_rating", ""),
        "subscription_recommendation": comp_entry.get("subscription_recommendation", ""),
        "scorecard_categories": comp_entry.get("section_20_scorecard", {}).get("categories", []),
        "scorecard_total": comp_entry.get("section_20_scorecard", {}).get("total_score", 0),
        "scorecard_interpretation": comp_entry.get("section_20_scorecard", {}).get("interpretation", ""),
    }

def generate_ipo_data():
    new_path = os.path.join(DATA_DIR, "ipo_data.json")
    legacy_path = os.path.join(DATA_DIR, "ipos.json")
    if os.path.exists(new_path):
        ipos_data = load_json(new_path)
        print(f"[DataGen] Using new ipo_data.json ({len(ipos_data.get('ipos', []))} IPOs)")
    else:
        ipos_data = load_json(legacy_path)
        print(f"[DataGen] Using legacy ipos.json ({len(ipos_data.get('ipos', []))} IPOs)")
    analysis_data = load_json(os.path.join(DATA_DIR, "ipo_analysis.json"))
    ipos = ipos_data.get("ipos", [])

    # Load master database for fallback analysis (covers all 2001 IPOs)
    master_db = load_json(os.path.join(DATA_DIR, "ipo_master_database.json"))
    master_lookup = {}
    for mipo in master_db.get("ipos", []):
        key = mipo.get("company_name", "").lower().strip()
        if key:
            master_lookup[key] = mipo
    print(f"[DataGen] Loaded {len(master_lookup)} master DB entries for fallback analysis")

    # Load comprehensive analysis JSON for per-IPO scores
    comp_analysis = load_json(os.path.join(DATA_DIR, "..", "src", "data", "ipoComprehensiveAnalysis.json"))
    print(f"[DataGen] Loaded {len(comp_analysis)} comprehensive analysis entries")

    # Build company-name-based lookup for comp analysis
    comp_by_name = {}
    for ckey, centry in comp_analysis.items():
        # Extract company name from key by removing trailing -{number}
        cname_key = re.sub(r'-\d+$', '', ckey).strip()
        if cname_key and isinstance(centry, dict) and centry.get('business_overview'):
            if cname_key not in comp_by_name:
                comp_by_name[cname_key] = centry
    print(f"[DataGen] Built name-based lookup: {len(comp_by_name)} entries")

    print(f"[DataGen] Loading {len(ipos)} IPOs, fetching web news...")

    lines = []
    lines.append('export interface IPOStock {')
    lines.append('  id: string;')
    lines.append('  company: string;')
    lines.append('  ticker: string;')
    lines.append('  sector: string;')
    lines.append('  industry?: string;')
    lines.append('  description: string;')
    lines.append('  about?: string;')
    lines.append('  founded: string;')
    lines.append('  headquarters: string;')
    lines.append('  employees: string;')
    lines.append('  ceo: string;')
    lines.append('  expectedDate: string;')
    lines.append('  openDate?: string;')
    lines.append('  closeDate?: string;')
    lines.append('  listingDate?: string;')
    lines.append('  priceRange: string;')
    lines.append('  priceBandHigh?: number;')
    lines.append('  priceBandLow?: number;')
    lines.append('  lotSize: number;')
    lines.append('  issueSize: string;')
    lines.append('  listingExchange: string;')
    lines.append('  ipoType: string;')
    lines.append('  registrar: string;')
    lines.append("  status: 'upcoming' | 'open' | 'listed' | 'subscribed' | 'closed';")
    lines.append('  gmp?: number;')
    lines.append('  gmpPercent?: number;')
    lines.append('  subscriptionStatus?: string;')
    lines.append('  anchorInvestors?: string[];')
    lines.append('  rhpDate?: string;')
    lines.append('  allotmentDate?: string;')
    lines.append('  refundDate?: string;')
    lines.append('  drhpUrl?: string;')
    lines.append('  rhpUrl?: string;')
    lines.append('  source?: string;')
    lines.append('  currentPrice?: number;')
    lines.append('  percentChange?: number;')
    lines.append('  marketCap?: number;')
    lines.append('  revenue: string;')
    lines.append('  revenueGrowth: string;')
    lines.append('  netIncome: string;')
    lines.append('  profitMargin: string;')
    lines.append('  debt: string;')
    lines.append('  roce: string;')
    lines.append('  eps: string;')
    lines.append('  peRatio: string;')
    lines.append('  strengths: string[];')
    lines.append('  risks: { text: string; indicator: string }[];')
    lines.append('  aiScores: {')
    lines.append('    overall: number;')
    lines.append('    fundamentals: number;')
    lines.append('    valuation: number;')
    lines.append('    growth: number;')
    lines.append('    management: number;')
    lines.append('    marketSentiment: number;')
    lines.append('  };')
    lines.append('  aiAnalysis: string;')
    lines.append('  aiVerdict: string;')
    lines.append('  aiRating?: string;')
    lines.append('  aiRatingScore?: number;')
    lines.append('  executiveSummary?: string;')
    lines.append('  businessOverview?: string;')
    lines.append('  industryAnalysis?: string;')
    lines.append('  financialAnalysis?: string;')
    lines.append('  balanceSheetAnalysis?: string;')
    lines.append('  cashFlowAnalysis?: string;')
    lines.append('  ipoDetails?: string;')
    lines.append('  valuationAnalysis?: string;')
    lines.append('  managementQuality?: string;')
    lines.append('  riskAssessment?: string;')
    lines.append('  strengthsWeaknesses?: string;')
    lines.append('  marketSentiment?: string;')
    lines.append('  finalVerdict?: string;')
    lines.append('  redFlags?: string[];')
    lines.append('  positiveCatalysts?: string[];')
    lines.append('  scorecardCategories?: { key: string; label: string; score: number }[];')
    lines.append('  scorecardTotalScore?: number;')
    lines.append('  scorecardInterpretation?: string;')
    lines.append('  longTermRating?: string;')
    lines.append('  subscriptionRecommendation?: string;')
    lines.append('}')
    lines.append('')
    lines.append('export const ipoStocks: IPOStock[] = [')

    for i, ipo in enumerate(ipos):
        name = ipo.get("name") or ipo.get("company_name", "")
        symbol = ipo.get("ticker") or ipo.get("symbol", "")
        country = ipo.get("headquarters") or ipo.get("country", "Global")
        exchange = ipo.get("exchange") or ipo.get("listingExchange", "NSE/BSE")
        status = ipo.get("status", "upcoming")
        if status not in ("upcoming", "open", "listed", "subscribed", "closed"):
            status = "closed" if status in ("rights",) else "upcoming"
        industry = ipo.get("industry", "")
        sector = ipo.get("sector", "") or industry or "mainboard"
        price_band_high = ipo.get("priceBandHigh", 0) or 0
        price_band_low = ipo.get("priceBandLow", 0) or 0
        if price_band_high and price_band_low:
            price = f"Rs.{price_band_low} - Rs.{price_band_high}"
        else:
            price = ipo.get("priceRange") or ipo.get("price_band", "")
        open_date = ipo.get("openDate", "") or ipo.get("open_date", "")
        close_date = ipo.get("closeDate", "") or ipo.get("close_date", "")
        listing_date = ipo.get("listingDate", "") or ipo.get("listing_date", "")
        # For listed IPOs, set expected_date to empty so UI shows "Listed"
        # For upcoming/open IPOs, use real dates
        if status == "listed":
            expected_date = listing_date or ""
        else:
            expected_date = open_date or ""
        issue_size = ipo.get("issueSize", "") or ipo.get("issue_size", "")
        lot_size = ipo.get("lotSize", 0) or ipo.get("lot_size", 0)
        ipo_type = ipo.get("ipoType", "") or ipo.get("ipo_type", "mainboard")
        gmp = ipo.get("gmp", 0) or 0
        gmp_pct = ipo.get("gmpPercent", 0) or 0
        subscription_status = ipo.get("subscriptionStatus", "") or ""
        anchor_investors = ipo.get("anchorInvestors", []) or []
        rhp_date = ipo.get("rhpDate", "") or ""
        allotment_date = ipo.get("allotmentDate", "") or ""
        refund_date = ipo.get("refundDate", "") or ""
        drhp_url = ipo.get("drhpUrl", "") or ""
        rhp_url = ipo.get("rhpUrl", "") or ""
        source = ipo.get("source", "") or ""
        fm = ipo.get("fiscalMetrics", {}) or {}
        if not isinstance(fm, dict):
            fm = {}
        current_price = fm.get("currentPrice", ipo.get("currentPrice", 0)) or 0
        pct_change = fm.get("percentChange", ipo.get("percentChange", 0)) or 0
        mcap = fm.get("ipoMcap", ipo.get("marketCap", 0)) or 0
        about = ipo.get("about", "") or ipo.get("description", "")
        description = about or name

        akey_raw = ipo.get("id", "") or ""
        if akey_raw:
            akey = akey_raw
        else:
            akey = f"{symbol}-{country}" if symbol else f"{name.lower().replace(' ', '-')[:20]}-{country}"
        akey_lookup = akey if akey.startswith("ipo:") else akey
        analysis = analysis_data.get(akey_lookup) or analysis_data.get(akey) or {}

        strengths_raw = analysis.get("strengths", []) or analysis.get("key_drivers", [])
        risks_raw = analysis.get("risks", [])
        scores = analysis.get("scores", {})
        ai_analysis_text = analysis.get("aiAnalysis", "") or analysis.get("summary", "")
        ai_verdict_text = analysis.get("aiVerdict", "") or analysis.get("verdict", "")
        ai_rating = analysis.get("final_rating", "") or analysis.get("aiRating", "")
        ai_rating_score = analysis.get("final_rating_score") or analysis.get("aiRatingScore")

        # Fallback: use master database data when no ipo_analysis.json entry exists
        if not ai_analysis_text:
            mipo = master_lookup.get(name.lower().strip()) or master_lookup.get(symbol.lower().strip())
            if mipo:
                summary_text = mipo.get("ipo_summary", "")
                thesis_text = mipo.get("investment_thesis", "")
                score_exp_text = mipo.get("ai_score_explanation", "")
                ai_analysis_text = (score_exp_text or thesis_text or summary_text)
                if not ai_verdict_text:
                    ai_verdict_text = mipo.get("ai_rating", "")
                if not ai_rating:
                    ai_rating = mipo.get("ai_rating", "")
                if ai_rating_score is None:
                    ai_rating_score = mipo.get("ai_score")

        if not strengths_raw and analysis:
            swot = analysis.get("swot", {}) or {}
            strengths_raw = swot.get("strengths", []) or []

        news_snippet = ""
        if not os.environ.get("SKIP_NEWS_FETCH"):
            try:
                news_snippet = search_news_for_ipo(name, symbol)
            except Exception:
                news_snippet = ""
        if news_snippet:
            combined = (ai_analysis_text + "\n\n" + news_snippet) if ai_analysis_text else news_snippet
            enriched_analysis = esc(combined)
        else:
            enriched_analysis = esc(ai_analysis_text) if ai_analysis_text else ""

        strengths_list = strengths_raw if isinstance(strengths_raw, list) else []
        strengths_str = ', '.join([f'"{esc(s)}"' for s in strengths_list[:5]]) if strengths_list else ''

        lines.append('  {')
        lines.append(f'    id: "{i + 1}",')
        lines.append(f'    company: "{esc(name)}",')
        lines.append(f'    ticker: "{esc(symbol)}",')
        lines.append(f'    sector: "{esc(sector)}",')
        if industry:
            lines.append(f'    industry: "{esc(industry)}",')
        lines.append(f'    description: "{esc(description)}",')
        if about and about != name:
            lines.append(f'    about: "{esc(about)}",')
        lines.append(f'    founded: "",')
        lines.append(f'    headquarters: "{esc(country)}",')
        lines.append(f'    employees: "",')
        lines.append(f'    ceo: "",')
        lines.append(f'    expectedDate: "{esc(expected_date)}",')
        if open_date:
            lines.append(f'    openDate: "{esc(open_date)}",')
        if close_date:
            lines.append(f'    closeDate: "{esc(close_date)}",')
        if listing_date:
            lines.append(f'    listingDate: "{esc(listing_date)}",')
        lines.append(f'    priceRange: "{esc(price)}",')
        if price_band_high:
            lines.append(f'    priceBandHigh: {price_band_high},')
        if price_band_low:
            lines.append(f'    priceBandLow: {price_band_low},')
        try:
            lot_int = int(float(str(lot_size).replace(",", ""))) if lot_size else 0
        except (ValueError, TypeError):
            lot_int = 0
        lines.append(f'    lotSize: {lot_int},')
        lines.append(f'    issueSize: "{esc(str(issue_size))}",')
        lines.append(f'    listingExchange: "{esc(exchange)}",')
        lines.append(f'    ipoType: "{esc(ipo_type)}",')
        lines.append(f'    registrar: "",')
        lines.append(f'    status: "{esc(status)}" as const,')
        if gmp:
            lines.append(f'    gmp: {gmp},')
        if gmp_pct:
            lines.append(f'    gmpPercent: {gmp_pct},')
        if subscription_status:
            lines.append(f'    subscriptionStatus: "{esc(subscription_status)}",')
        if anchor_investors:
            anchor_str = ', '.join([f'"{esc(a)}"' for a in anchor_investors[:20]])
            lines.append(f'    anchorInvestors: [{anchor_str}],')
        if rhp_date:
            lines.append(f'    rhpDate: "{esc(rhp_date)}",')
        if allotment_date:
            lines.append(f'    allotmentDate: "{esc(allotment_date)}",')
        if refund_date:
            lines.append(f'    refundDate: "{esc(refund_date)}",')
        if drhp_url:
            lines.append(f'    drhpUrl: "{esc(drhp_url)}",')
        if rhp_url:
            lines.append(f'    rhpUrl: "{esc(rhp_url)}",')
        if source:
            lines.append(f'    source: "{esc(source)}",')
        if current_price:
            lines.append(f'    currentPrice: {current_price},')
        if pct_change:
            lines.append(f'    percentChange: {pct_change},')
        if mcap:
            lines.append(f'    marketCap: {mcap},')
        lines.append(f'    revenue: "",')
        lines.append(f'    revenueGrowth: "",')
        lines.append(f'    netIncome: "",')
        lines.append(f'    profitMargin: "",')
        lines.append(f'    debt: "",')
        lines.append(f'    roce: "",')
        lines.append(f'    eps: "",')
        lines.append(f'    peRatio: "",')
        lines.append(f'    strengths: [{strengths_str}],')
        risks_list = risks_raw if isinstance(risks_raw, list) else []
        lines.append('    risks: [')
        for r in risks_list[:5]:
            rtext = esc(r["text"]) if isinstance(r, dict) else esc(r)
            rind = esc(r["indicator"]) if isinstance(r, dict) else '"🟡"'
            lines.append(f'      {{ text: "{rtext}", indicator: "{rind}" }},')
        lines.append('    ],')
        # Try comprehensive analysis scores first, fall back to ipo_analysis.json
        comp_slug = f"{_slugify_company(name)}-{i + 1}"
        comp_entry = comp_analysis.get(comp_slug, {})
        if not comp_entry or not comp_entry.get('business_overview'):
            # Fallback: try matching by company name slug (handles index mismatch)
            name_slug = _slugify_company(name)
            comp_entry = comp_by_name.get(name_slug, {})
        comp_entry_data = _extract_comp_analysis(comp_entry) if isinstance(comp_entry, dict) else {}
        comp_scores = comp_entry.get('investment_verdict', {}).get('scores', {}) if isinstance(comp_entry, dict) else {}

        if comp_scores and isinstance(comp_scores, dict):
            overall_val = int(comp_scores.get('overall_score', 50))
            fundamentals_val = int(comp_scores.get('fundamentals_score') or comp_scores.get('financial_strength', 50))
            valuation_val = int(comp_scores.get('valuation_score') or comp_scores.get('valuation_attractiveness', 50))
            growth_val = int(comp_scores.get('growth_score') or comp_scores.get('business_quality', 50))
            management_val = int(comp_scores.get('management_score') or comp_scores.get('management_quality', 50))
            sentiment_val = int(comp_scores.get('market_sentiment_score') or comp_scores.get('industry_outlook', 50))
        else:
            # Try master database scores first, fall back to ipo_analysis or hardcoded
            m_sb = mipo.get("score_breakdown", {}) if mipo else {}
            if m_sb:
                overall_val = int(mipo.get("ai_score", 50))
                fundamentals_val = int(m_sb.get("fundamentals", 50))
                valuation_val = int(m_sb.get("valuation", 50))
                growth_val = int(m_sb.get("business_quality", 50))
                management_val = int(m_sb.get("governance", 50))
                sentiment_val = int(m_sb.get("ipo_demand", 50))
            else:
                overall_val = scores.get("attractiveness", scores.get("overall", 75))
                fundamentals_val = scores.get("financial_health", 70)
                valuation_val = scores.get("risk", 65)
                growth_val = scores.get("growth_potential", 75)
                management_val = 70
                sentiment_val = scores.get("attractiveness", 72)

        lines.append('    aiScores: {')
        lines.append(f'      overall: {overall_val},')
        lines.append(f'      fundamentals: {fundamentals_val},')
        lines.append(f'      valuation: {valuation_val},')
        lines.append(f'      growth: {growth_val},')
        lines.append(f'      management: {management_val},')
        lines.append(f'      marketSentiment: {sentiment_val},')
        lines.append('    },')
        lines.append(f'    aiAnalysis: "{enriched_analysis}",')
        lines.append(f'    aiVerdict: "{esc(ai_verdict_text)}",')
        if ai_rating:
            lines.append(f'    aiRating: "{esc(ai_rating)}",')
        if ai_rating_score:
            try:
                lines.append(f'    aiRatingScore: {float(ai_rating_score)},')
            except (ValueError, TypeError):
                pass

        # Write comprehensive analysis detail fields if available
        if comp_entry_data.get('executive_summary'):
            lines.append(f'    executiveSummary: "{esc(comp_entry_data["executive_summary"])}",')
        if comp_entry_data.get('business_overview'):
            lines.append(f'    businessOverview: "{esc(comp_entry_data["business_overview"])}",')
        if comp_entry_data.get('industry_analysis'):
            lines.append(f'    industryAnalysis: "{esc(comp_entry_data["industry_analysis"])}",')
        if comp_entry_data.get('financial_analysis'):
            lines.append(f'    financialAnalysis: "{esc(comp_entry_data["financial_analysis"])}",')
        if comp_entry_data.get('balance_sheet_analysis'):
            lines.append(f'    balanceSheetAnalysis: "{esc(comp_entry_data["balance_sheet_analysis"])}",')
        if comp_entry_data.get('cash_flow_analysis'):
            lines.append(f'    cashFlowAnalysis: "{esc(comp_entry_data["cash_flow_analysis"])}",')
        if comp_entry_data.get('ipo_details'):
            lines.append(f'    ipoDetails: "{esc(comp_entry_data["ipo_details"])}",')
        if comp_entry_data.get('valuation_analysis'):
            lines.append(f'    valuationAnalysis: "{esc(comp_entry_data["valuation_analysis"])}",')
        if comp_entry_data.get('management_quality'):
            lines.append(f'    managementQuality: "{esc(comp_entry_data["management_quality"])}",')
        if comp_entry_data.get('risk_assessment'):
            lines.append(f'    riskAssessment: "{esc(comp_entry_data["risk_assessment"])}",')
        if comp_entry_data.get('strengths_weaknesses'):
            lines.append(f'    strengthsWeaknesses: "{esc(comp_entry_data["strengths_weaknesses"])}",')
        if comp_entry_data.get('market_sentiment'):
            lines.append(f'    marketSentiment: "{esc(comp_entry_data["market_sentiment"])}",')
        if comp_entry_data.get('final_verdict'):
            lines.append(f'    finalVerdict: "{esc(comp_entry_data["final_verdict"])}",')
        rf_list = comp_entry_data.get('red_flags', [])
        if rf_list:
            rf_str = ', '.join([f'"{esc(r)}"' for r in rf_list[:10]])
            lines.append(f'    redFlags: [{rf_str}],')
        pc_list = comp_entry_data.get('positive_catalysts', [])
        if pc_list:
            pc_str = ', '.join([f'"{esc(p)}"' for p in pc_list[:10]])
            lines.append(f'    positiveCatalysts: [{pc_str}],')
        if comp_entry_data.get('long_term_rating'):
            lines.append(f'    longTermRating: "{esc(comp_entry_data["long_term_rating"])}",')
        if comp_entry_data.get('subscription_recommendation'):
            lines.append(f'    subscriptionRecommendation: "{esc(comp_entry_data["subscription_recommendation"])}",')
        if comp_entry_data.get('scorecard_categories'):
            cats = comp_entry_data['scorecard_categories']
            cat_lines = []
            for cat in cats[:6]:
                if isinstance(cat, dict):
                    cat_lines.append(f'{{key: "{esc(cat.get("key",""))}", label: "{esc(cat.get("label",""))}", score: {cat.get("score",0)}}}')
            if cat_lines:
                cats_str = ', '.join(cat_lines)
                lines.append(f'    scorecardCategories: [{cats_str}],')
        if comp_entry_data.get('scorecard_total'):
            lines.append(f'    scorecardTotalScore: {comp_entry_data["scorecard_total"]},')
        if comp_entry_data.get('scorecard_interpretation'):
            lines.append(f'    scorecardInterpretation: "{esc(comp_entry_data["scorecard_interpretation"])}",')

        lines.append('  },')

        if (i + 1) % 20 == 0:
            print(f"[DataGen] Processed {i + 1}/{len(ipos)} IPOs")

    lines.append('];')
    lines.append('')

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "ipoData.ts"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[DataGen] Wrote {len(ipos)} IPOs to ipoData.ts")


def generate_crypto_data():
    crypto_data = load_json(os.path.join(DATA_DIR, "crypto_data.json"))
    analysis_data = load_json(os.path.join(DATA_DIR, "crypto_analysis.json"))
    projects = crypto_data.get("projects", [])

    print(f"[DataGen] Loading {len(projects)} crypto projects...")

    lines = []
    lines.append('export interface CryptoProject {')
    lines.append('  id: string;')
    lines.append('  name: string;')
    lines.append('  ticker: string;')
    lines.append('  chain: string;')
    lines.append('  category: string;')
    lines.append('  description: string;')
    lines.append("  status: 'active' | 'upcoming' | 'ended';")
    lines.append('  price: string;')
    lines.append('  marketCap: string;')
    lines.append('  volume24h: string;')
    lines.append('  estimatedValue: string;')
    lines.append('  eligibility: string;')
    lines.append('  farmingGuide: string;')
    lines.append('  tgeDate: string;')
    lines.append('  website: string;')
    lines.append('  socialLinks: { twitter: string; discord: string; telegram: string; website: string };')
    lines.append('  steps: string[];')
    lines.append('  availableFrom: string;')
    lines.append('  aiAnalysis?: {')
    lines.append('    summary: string;')
    lines.append("    sentiment: 'bullish' | 'bearish' | 'neutral';")
    lines.append('    convictionScore: number;')
    lines.append('    keyDrivers: string[];')
    lines.append('    risks: string[];')
    lines.append('    riskAssessment: {')
    lines.append("      overallRisk: 'low' | 'medium' | 'high';")
    lines.append("      smartContractRisk: 'low' | 'medium' | 'high';")
    lines.append("      teamRisk: 'low' | 'medium' | 'high';")
    lines.append("      marketRisk: 'low' | 'medium' | 'high';")
    lines.append("      regulatoryRisk: 'low' | 'medium' | 'high';")
    lines.append("      rugPullPotential: 'low' | 'medium' | 'high';")
    lines.append("      liquidityRisk: 'low' | 'medium' | 'high';")
    lines.append("      dilutionRisk: 'low' | 'medium' | 'high';")
    lines.append('    };')
    lines.append('    verdict: string;')
    lines.append('  };')
    lines.append('}')
    lines.append('')
    lines.append('export const cryptoProjects: CryptoProject[] = [')

    for i, proj in enumerate(projects):
        pid = proj.get("id", "")
        name = proj.get("name", "")
        ticker = proj.get("ticker", "")
        chain = proj.get("chain", "")
        category = proj.get("category", "coin")
        description = esc(proj.get("description", ""))
        status = proj.get("status", "active")
        if status not in ("upcoming", "active", "ended"):
            status_map = {
                "confirmed": "upcoming",
                "ongoing": "active",
                "live": "active",
                "closed": "ended",
                "expired": "ended",
                "completed": "ended",
            }
            status = status_map.get(status.lower(), "active")
        price = esc(proj.get("price", ""))
        market_cap = esc(proj.get("market_cap", ""))
        volume = esc(proj.get("volume_24h", ""))
        est_value = esc(proj.get("estimated_value", ""))
        eligibility = esc(proj.get("eligibility", ""))
        farming_guide = esc(proj.get("farming_guide", ""))
        tge_date = esc(proj.get("tge_date", ""))
        website = esc(proj.get("website", ""))
        social_links = proj.get("social_links", {})
        if not isinstance(social_links, dict):
            social_links = {}
        steps = proj.get("steps", [])
        if not isinstance(steps, list):
            steps = []
        available_from = esc(proj.get("available_from", ""))

        akey = pid.lower() if pid else ticker.upper()
        analysis = analysis_data.get(akey, {})

        ai_summary = esc(analysis.get("summary", ""))
        sentiment = analysis.get("sentiment", "neutral")
        conviction = analysis.get("conviction_score", 50)
        key_drivers = analysis.get("key_drivers", [])
        risks = analysis.get("risks", [])
        verdict = esc(analysis.get("verdict", ""))

        lines.append('  {')
        lines.append(f'    id: "{i + 1}",')
        lines.append(f'    name: "{esc(name)}",')
        lines.append(f'    ticker: "{esc(ticker)}",')
        lines.append(f'    chain: "{esc(chain)}",')
        lines.append(f'    category: "{esc(category)}",')
        lines.append(f'    description: "{description}",')
        lines.append(f'    status: "{esc(status)}" as const,')
        lines.append(f'    price: "{price}",')
        lines.append(f'    marketCap: "{market_cap}",')
        lines.append(f'    volume24h: "{volume}",')
        lines.append(f'    estimatedValue: "{est_value}",')
        lines.append(f'    eligibility: "{eligibility}",')
        lines.append(f'    farmingGuide: "{farming_guide}",')
        lines.append(f'    tgeDate: "{tge_date}",')
        lines.append(f'    website: "{website}",')
        sl_tw = esc(social_links.get("twitter", ""))
        sl_dc = esc(social_links.get("discord", ""))
        sl_tg = esc(social_links.get("telegram", ""))
        sl_ws = esc(social_links.get("website", ""))
        lines.append(f'    socialLinks: {{ twitter: "{sl_tw}", discord: "{sl_dc}", telegram: "{sl_tg}", website: "{sl_ws}" }},')
        steps_str = ', '.join([f'"{esc(s)}"' for s in steps[:10]])
        lines.append(f'    steps: [{steps_str}],')
        lines.append(f'    availableFrom: "{available_from}",')

        has_ai = analysis and (ai_summary or verdict)
        if has_ai:
            drivers_str = ', '.join([f'"{esc(d)}"' for d in key_drivers[:5]])
            risks_str = ', '.join([f'"{esc(r)}"' for r in risks[:5]])
            ra = analysis.get("risk_assessment", {})
            lines.append('    aiAnalysis: {')
            lines.append(f'      summary: "{ai_summary}",')
            lines.append(f'      sentiment: "{sentiment}" as const,')
            lines.append(f'      convictionScore: {conviction},')
            lines.append(f'      keyDrivers: [{drivers_str}],')
            lines.append(f'      risks: [{risks_str}],')
            lines.append('      riskAssessment: {')
            lines.append(f'        overallRisk: "{ra.get("overall_risk", "medium")}" as const,')
            lines.append(f'        smartContractRisk: "{ra.get("smart_contract_risk", "medium")}" as const,')
            lines.append(f'        teamRisk: "{ra.get("team_risk", "medium")}" as const,')
            lines.append(f'        marketRisk: "{ra.get("market_risk", "medium")}" as const,')
            lines.append(f'        regulatoryRisk: "{ra.get("regulatory_risk", "medium")}" as const,')
            lines.append(f'        rugPullPotential: "{ra.get("rug_pull_potential", "medium")}" as const,')
            lines.append(f'        liquidityRisk: "{ra.get("liquidity_risk", "medium")}" as const,')
            lines.append(f'        dilutionRisk: "{ra.get("dilution_risk", "medium")}" as const,')
            lines.append('      },')
            lines.append(f'      verdict: "{verdict}",')
            lines.append('    },')
        else:
            lines.append('    aiAnalysis: undefined,')

        lines.append('  },')

    lines.append('];')
    lines.append('')

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "cryptoData.ts"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[DataGen] Wrote {len(projects)} crypto projects to cryptoData.ts")


def generate_news_data():
    news_cache_path = os.path.join(DATA_DIR, "news_cache.json")
    current = load_json(news_cache_path)
    if not isinstance(current, list):
        current = []

    daily_cache_path = os.path.join(DATA_DIR, "daily_news_cache.json")
    daily_articles = load_json(daily_cache_path)
    if not isinstance(daily_articles, list):
        daily_articles = []

    # Load archived articles from artifacts
    archived = load_news_articles_from_artifacts()

    # Merge: daily cache (most recent), then news cache, then archived (deduped by ID)
    seen_ids = set()
    merged = []
    for art in daily_articles:
        if isinstance(art, dict):
            aid = art.get("id", "")
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                merged.append(art)
    for art in current:
        if isinstance(art, dict):
            aid = art.get("id", "")
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                merged.append(art)
    for art in archived:
        if isinstance(art, dict):
            aid = art.get("id", "")
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                merged.append(art)

    # Enforce 70-day retention
    articles = prune_old_articles(merged)

    print(f"[DataGen] Loaded {len(daily_articles)} from daily cache + {len(current)} from cache + {len(archived)} from artifacts = {len(merged)} merged, "
          f"{len(articles)} after 70-day pruning")
    if len(articles) == 0:
        print("[DataGen] WARNING: 0 articles after merge — newsData.ts will be empty!")
        print("[DataGen] If this is unexpected, check generate_news_cache.py output")

    lines = []
    lines.append('export interface ArticleImage {')
    lines.append('  url: string;')
    lines.append('  alt: string;')
    lines.append('  attribution: string;')
    lines.append('  title?: string;')
    lines.append('  caption?: string;')
    lines.append('  category?: string;')
    lines.append('  sourceUrl?: string;')
    lines.append('  source?: string;')
    lines.append('  photoId?: string;')
    lines.append('}')
    lines.append('')
    lines.append('export interface FinancialMetrics {')
    lines.append('  tableCaption: string;')
    lines.append('  headers: string[];')
    lines.append('  rows: string[][];')
    lines.append('}')
    lines.append('')
    lines.append('export interface AiAnalysis {')
    lines.append('  bullCase: string;')
    lines.append('  bearCase: string;')
    lines.append('  neutralCase: string;')
    lines.append('  probabilityWeightedOutlook: string;')
    lines.append('  potentialCatalysts: string[];')
    lines.append('  keyRisks: string[];')
    lines.append('}')
    lines.append('')
    lines.append('export interface NewsArticle {')
    lines.append('  id: string;')
    lines.append('  headline: string;')
    lines.append('  subheadline: string;')
    lines.append('  keyHighlights: string[];')
    lines.append('  executiveSummary: string;')
    lines.append('  quickAnswer?: string;')
    lines.append('  marketBackground: string;')
    lines.append('  detailedAnalysis: string;')
    lines.append('  expertInsights: string;')
    lines.append('  financialMetrics: FinancialMetrics;')
    lines.append('  risks: string[];')
    lines.append('  opportunities: string[];')
    lines.append('  outlook: string;')
    lines.append('  conclusion: string;')
    lines.append('  frequentlyAskedQuestions?: { question: string; answer: string }[];')
    lines.append('  investorTakeaways?: string[];')
    lines.append('  sourcesReferenced: string[];')
    lines.append('  aiAnalysis: AiAnalysis | null;')
    lines.append('  images: ArticleImage[];')
    lines.append('  ipoDetails?: { [key: string]: string };')
    lines.append('  cryptoDetails?: { [key: string]: string };')
    lines.append('  category: string;')
    lines.append('  sentiment: string;')
    lines.append('  impact: string;')
    lines.append('  relatedCoins: string[];')
    lines.append('  relatedStocks: string[];')
    lines.append('  relatedEntities?: string[];')
    lines.append('  primaryKeyword: string;')
    lines.append('  secondaryKeywords: string[];')
    lines.append('  tags?: string[];')
    lines.append('  seoTitle?: string;')
    lines.append('  metaTitle?: string;')
    lines.append('  metaDescription: string;')
    lines.append('  author?: string;')
    lines.append('  authorAvatar?: string;')
    lines.append('  telegram?: string;')
    lines.append('  slug?: string;')
    lines.append('  focusKeyword?: string;')
    lines.append('  categories?: string[];')
    lines.append('  seoHeadlines?: string[];')
    lines.append('  ctrHeadlines?: string[];')
    lines.append('  socialHeadlines?: string[];')
    lines.append('  peopleAlsoAsk?: string[];')
    lines.append('  relatedSearches?: string[];')
    lines.append('  longTailKeywords?: string[];')
    lines.append('  indexingNotes?: { primaryKeyword: string; searchIntent: string; category: string; tags: string[]; entityCoverage: string[] };')
    lines.append('  searchConsoleReadiness?: number;')
    lines.append('  adsenseReadiness?: number;')
    lines.append('  seoScore?: number;')
    lines.append('  geoScore?: number;')
    lines.append('  authorityScore?: number;')
    lines.append('  aiCitationPotential?: number;')
    lines.append('  featuredImagePrompt?: string;')
    lines.append('  imageFilename?: string;')
    lines.append('  imageAltText?: string;')
    lines.append('  imageCaption?: string;')
    lines.append('  imageTitle?: string;')
    lines.append('  publishedAt: string;')
    lines.append('}')
    lines.append('')
    lines.append('export const newsArticles: NewsArticle[] = [')

    for i, art in enumerate(articles):
        if not isinstance(art, dict):
            continue
        images_raw = art.get("images", [])
        if not isinstance(images_raw, list):
            images_raw = []
        images = [img for img in images_raw if isinstance(img, dict) and img.get("url")]

        financial_metrics = art.get("financialMetrics", {})
        if not isinstance(financial_metrics, dict):
            financial_metrics = {}
        fm_headers = financial_metrics.get("headers", [])
        fm_rows = financial_metrics.get("rows", [])
        if not isinstance(fm_headers, list):
            fm_headers = []
        if not isinstance(fm_rows, list):
            fm_rows = []

        ai_analysis = art.get("aiAnalysis")
        if not isinstance(ai_analysis, dict):
            ai_analysis = None

        ipo_details = art.get("ipoDetails")
        if ipo_details is not None and not isinstance(ipo_details, dict):
            ipo_details = None

        crypto_details = art.get("cryptoDetails")
        if crypto_details is not None and not isinstance(crypto_details, dict):
            crypto_details = None

        lines.append('  {')
        lines.append(f'    id: "{esc(art.get("id", f"news-{i}"))}",')
        lines.append(f'    headline: "{esc(art.get("headline", ""))}",')
        lines.append(f'    author: "Shiva Sandeep",')
        lines.append(f'    authorAvatar: "/author-avatar.jpg",')
        lines.append(f'    telegram: "its_terabyte",')
        lines.append(f'    subheadline: "{esc(art.get("subheadline", ""))}",')
        kh = art.get("keyHighlights", [])
        kh = kh if isinstance(kh, list) else []
        kh_str = ', '.join([f'"{esc(k)}"' for k in kh[:8]])
        lines.append(f'    keyHighlights: [{kh_str}],')
        lines.append(f'    executiveSummary: "{esc(art.get("executiveSummary", ""))}",')
        lines.append(f'    marketBackground: "{esc(art.get("marketBackground", ""))}",')
        lines.append(f'    detailedAnalysis: "{esc(art.get("detailedAnalysis", ""))}",')
        lines.append(f'    expertInsights: "{esc(art.get("expertInsights", ""))}",')
        lines.append('    financialMetrics: {')
        lines.append(f'      tableCaption: "{esc(financial_metrics.get("tableCaption", ""))}",')
        headers_str = ', '.join([f'"{esc(h)}"' for h in fm_headers])
        lines.append(f'      headers: [{headers_str}],')
        rows_lines = []
        for row in fm_rows:
            if not isinstance(row, list):
                continue
            cells_str = ', '.join([f'"{esc(c)}"' for c in row])
            rows_lines.append(f'        [{cells_str}]')
        rows_block = ',\n'.join(rows_lines)
        if rows_block:
            lines.append(f'      rows: [\n{rows_block}\n      ],')
        else:
            lines.append('      rows: [],')
        lines.append('    },')
        risks = art.get("risks", [])
        risks = risks if isinstance(risks, list) else []
        lines.append('    risks: [' + ', '.join([f'"{esc(r)}"' for r in risks[:6]]) + '],')
        opps = art.get("opportunities", [])
        opps = opps if isinstance(opps, list) else []
        lines.append('    opportunities: [' + ', '.join([f'"{esc(o)}"' for o in opps[:6]]) + '],')
        lines.append(f'    outlook: "{esc(art.get("outlook", ""))}",')
        lines.append(f'    conclusion: "{esc(art.get("conclusion", ""))}",')
        sources = art.get("sourcesReferenced", [])
        sources = sources if isinstance(sources, list) else []
        lines.append('    sourcesReferenced: [' + ', '.join([f'"{esc(s)}"' for s in sources[:8]]) + '],')

        if ai_analysis:
            lines.append('    aiAnalysis: {')
            lines.append(f'      bullCase: "{esc(ai_analysis.get("bullCase", ""))}",')
            lines.append(f'      bearCase: "{esc(ai_analysis.get("bearCase", ""))}",')
            lines.append(f'      neutralCase: "{esc(ai_analysis.get("neutralCase", ""))}",')
            lines.append(f'      probabilityWeightedOutlook: "{esc(ai_analysis.get("probabilityWeightedOutlook", ""))}",')
            cats = ai_analysis.get("potentialCatalysts", [])
            cats = cats if isinstance(cats, list) else []
            lines.append('      potentialCatalysts: [' + ', '.join([f'"{esc(c)}"' for c in cats[:6]]) + '],')
            krs = ai_analysis.get("keyRisks", [])
            krs = krs if isinstance(krs, list) else []
            lines.append('      keyRisks: [' + ', '.join([f'"{esc(r)}"' for r in krs[:6]]) + '],')
            lines.append('    },')
        else:
            lines.append('    aiAnalysis: null,')

        lines.append('    images: [')
        for img in images[:4]:
            lines.append('      {')
            lines.append(f'        url: "{esc(img.get("url", ""))}",')
            lines.append(f'        alt: "{esc(img.get("alt", ""))}",')
            lines.append(f'        attribution: "{esc(img.get("attribution", "Photo via Unsplash"))}",')
            if img.get("title"):
                lines.append(f'        title: "{esc(img.get("title", ""))}",')
            if img.get("caption"):
                lines.append(f'        caption: "{esc(img.get("caption", ""))}",')
            if img.get("category"):
                lines.append(f'        category: "{esc(img.get("category", ""))}",')
            if img.get("sourceUrl"):
                lines.append(f'        sourceUrl: "{esc(img.get("sourceUrl", ""))}",')
            if img.get("source"):
                lines.append(f'        source: "{esc(img.get("source", ""))}",')
            if img.get("photoId"):
                lines.append(f'        photoId: "{esc(img.get("photoId", ""))}",')
            lines.append('      },')
        lines.append('    ],')

        if ipo_details:
            lines.append('    ipoDetails: {')
            for k, v in ipo_details.items():
                if isinstance(v, (str, int, float)):
                    lines.append(f'      {k}: "{esc(v)}",')
            lines.append('    },')
        if crypto_details:
            lines.append('    cryptoDetails: {')
            for k, v in crypto_details.items():
                if isinstance(v, (str, int, float)):
                    lines.append(f'      {k}: "{esc(v)}",')
            lines.append('    },')

        lines.append(f'    category: "{esc(art.get("category", "stocks"))}",')
        lines.append(f'    sentiment: "{esc(art.get("sentiment", "neutral"))}",')
        lines.append(f'    impact: "{esc(art.get("impact", "medium"))}",')
        rc = art.get("relatedCoins", [])
        rc = rc if isinstance(rc, list) else []
        lines.append('    relatedCoins: [' + ', '.join([f'"{esc(c)}"' for c in rc[:6]]) + '],')
        rs = art.get("relatedStocks", [])
        rs = rs if isinstance(rs, list) else []
        lines.append('    relatedStocks: [' + ', '.join([f'"{esc(s)}"' for s in rs[:6]]) + '],')
        lines.append(f'    primaryKeyword: "{esc(art.get("primaryKeyword", ""))}",')
        sk = art.get("secondaryKeywords", [])
        sk = sk if isinstance(sk, list) else []
        lines.append('    secondaryKeywords: [' + ', '.join([f'"{esc(k)}"' for k in sk[:5]]) + '],')
        tags = art.get("tags", [])
        tags = tags if isinstance(tags, list) else []
        if tags:
            lines.append('    tags: [' + ', '.join([f'"{esc(t)}"' for t in tags[:10]]) + '],')
        if art.get("seoTitle"):
            lines.append(f'    seoTitle: "{esc(art.get("seoTitle", ""))}",')
        if art.get("metaTitle"):
            lines.append(f'    metaTitle: "{esc(art.get("metaTitle", ""))}",')
        lines.append(f'    metaDescription: "{esc(art.get("metaDescription", ""))}",')
        if art.get("slug"):
            lines.append(f'    slug: "{esc(art.get("slug", ""))}",')
        if art.get("focusKeyword"):
            lines.append(f'    focusKeyword: "{esc(art.get("focusKeyword", ""))}",')
        cats = art.get("categories", [])
        cats = cats if isinstance(cats, list) else []
        if cats:
            lines.append('    categories: [' + ', '.join([f'"{esc(c)}"' for c in cats[:5]]) + '],')
        rel_ents = art.get("relatedEntities", [])
        rel_ents = rel_ents if isinstance(rel_ents, list) else []
        if rel_ents:
            lines.append('    relatedEntities: [' + ', '.join([f'"{esc(e)}"' for e in rel_ents[:8]]) + '],')
        if art.get("quickAnswer"):
            lines.append(f'    quickAnswer: "{esc(art.get("quickAnswer", ""))}",')
        faq = art.get("frequentlyAskedQuestions", [])
        if isinstance(faq, list) and faq:
            lines.append('    frequentlyAskedQuestions: [')
            for item in faq[:8]:
                if isinstance(item, dict):
                    lines.append(f'      {{ question: "{esc(item.get("question", ""))}", answer: "{esc(item.get("answer", ""))}" }},')
            lines.append('    ],')
        takeaways = art.get("investorTakeaways", [])
        takeaways = takeaways if isinstance(takeaways, list) else []
        if takeaways:
            lines.append('    investorTakeaways: [' + ', '.join([f'"{esc(t)}"' for t in takeaways[:6]]) + '],')
        seo_h = art.get("seoHeadlines", [])
        if isinstance(seo_h, list) and seo_h:
            lines.append('    seoHeadlines: [' + ', '.join([f'"{esc(h)}"' for h in seo_h[:5]]) + '],')
        ctr_h = art.get("ctrHeadlines", [])
        if isinstance(ctr_h, list) and ctr_h:
            lines.append('    ctrHeadlines: [' + ', '.join([f'"{esc(h)}"' for h in ctr_h[:5]]) + '],')
        soc_h = art.get("socialHeadlines", [])
        if isinstance(soc_h, list) and soc_h:
            lines.append('    socialHeadlines: [' + ', '.join([f'"{esc(h)}"' for h in soc_h[:5]]) + '],')
        paa = art.get("peopleAlsoAsk", [])
        if isinstance(paa, list) and paa:
            lines.append('    peopleAlsoAsk: [' + ', '.join([f'"{esc(q)}"' for q in paa[:8]]) + '],')
        rs_searches = art.get("relatedSearches", [])
        if isinstance(rs_searches, list) and rs_searches:
            lines.append('    relatedSearches: [' + ', '.join([f'"{esc(q)}"' for q in rs_searches[:10]]) + '],')
        ltk = art.get("longTailKeywords", [])
        if isinstance(ltk, list) and ltk:
            lines.append('    longTailKeywords: [' + ', '.join([f'"{esc(q)}"' for q in ltk[:8]]) + '],')
        idx_notes = art.get("indexingNotes")
        if isinstance(idx_notes, dict):
            ent_cov = idx_notes.get("entityCoverage", [])
            ent_cov = ent_cov if isinstance(ent_cov, list) else []
            idx_tags = idx_notes.get("tags", [])
            idx_tags = idx_tags if isinstance(idx_tags, list) else []
            lines.append('    indexingNotes: {')
            lines.append(f'      primaryKeyword: "{esc(idx_notes.get("primaryKeyword", ""))}",')
            lines.append(f'      searchIntent: "{esc(idx_notes.get("searchIntent", "informational"))}",')
            lines.append(f'      category: "{esc(idx_notes.get("category", ""))}",')
            lines.append('      tags: [' + ', '.join([f'"{esc(t)}"' for t in idx_tags[:8]]) + '],')
            lines.append('      entityCoverage: [' + ', '.join([f'"{esc(e)}"' for e in ent_cov[:8]]) + '],')
            lines.append('    },')
        for score_field, score_key in [
            ("searchConsoleReadiness", "searchConsoleReadiness"),
            ("adsenseReadiness", "adsenseReadiness"),
            ("seoScore", "seoScore"),
            ("geoScore", "geoScore"),
            ("authorityScore", "authorityScore"),
            ("aiCitationPotential", "aiCitationPotential"),
        ]:
            v = art.get(score_key)
            if isinstance(v, (int, float)):
                lines.append(f'    {score_field}: {int(v)},')
        if art.get("featuredImagePrompt"):
            lines.append(f'    featuredImagePrompt: "{esc(art.get("featuredImagePrompt", ""))}",')
        if art.get("imageFilename"):
            lines.append(f'    imageFilename: "{esc(art.get("imageFilename", ""))}",')
        if art.get("imageAltText"):
            lines.append(f'    imageAltText: "{esc(art.get("imageAltText", ""))}",')
        if art.get("imageCaption"):
            lines.append(f'    imageCaption: "{esc(art.get("imageCaption", ""))}",')
        if art.get("imageTitle"):
            lines.append(f'    imageTitle: "{esc(art.get("imageTitle", ""))}",')
        lines.append(f'    publishedAt: "{esc(art.get("publishedAt", ""))}",')
        lines.append('  },')

    lines.append('];')
    lines.append('')

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "newsData.ts")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[DataGen] Wrote {len(articles)} news articles to newsData.ts")


# ── Airdrop Data Generator ────────────────────────────────────

def generate_airdrop_data():
    """Generate src/data/airdropData.ts from data/airdrops_data.json + data/airdrop_analysis.json"""
    import hashlib  # for deterministic scoring
    airdrops_data = load_json(os.path.join(DATA_DIR, "airdrops_data.json"))
    analysis_data = load_json(os.path.join(DATA_DIR, "airdrop_analysis.json"))
    airdrops = airdrops_data.get("airdrops", [])

    print(f"[DataGen] Loading {len(airdrops)} airdrops for TypeScript generation...")
    if not airdrops:
        print("[DataGen] No airdrops data found, skipping")
        return

    lines = []
    # ── Write types ──
    lines.append('// ──────────────────────────────────────────────────────────────')
    lines.append('// Airdrop Intelligence Platform — Auto-generated from scraped data')
    lines.append('// ──────────────────────────────────────────────────────────────')
    lines.append('')
    lines.append('export interface ParticipationGuide {')
    lines.append('  steps: string[];')
    lines.append('  estimatedTime: string;')
    lines.append('  estimatedCost: string;')
    lines.append("  difficulty: 'Easy' | 'Medium' | 'Hard';")
    lines.append('}')
    lines.append('')
    lines.append('export interface AboutInfo {')
    lines.append('  aboutProject: string;')
    lines.append('  projectOverview: string;')
    lines.append('  productDescription: string;')
    lines.append('  ecosystemDescription: string;')
    lines.append('  useCases: string[];')
    lines.append('  teamInfo: string;')
    lines.append('  fundingInfo: string;')
    lines.append('  investors: string[];')
    lines.append('  tokenInfo: string;')
    lines.append('  reviewSummary: string;')
    lines.append('}')
    lines.append('')
    lines.append('export interface AiAnalysis {')
    lines.append('  summary: string;')
    lines.append('  bullCase: string;')
    lines.append('  bearCase: string;')
    lines.append('  competitiveAnalysis: string;')
    lines.append('  marketOpportunity: string;')
    lines.append('  airdropAttractiveness: {')
    lines.append('    rewardPotential: string;')
    lines.append('    effortRequired: string;')
    lines.append('    costRequired: string;')
    lines.append('    expectedROI: string;')
    lines.append('  };')
    lines.append('}')
    lines.append('')
    lines.append('export interface AirdropScores {')
    lines.append('  team: number;')
    lines.append('  investors: number;')
    lines.append('  product: number;')
    lines.append('  market: number;')
    lines.append('  community: number;')
    lines.append('  token: number;')
    lines.append('  airdrop: number;')
    lines.append('  overall: number;')
    lines.append('}')
    lines.append('')
    lines.append('export type AirdropStatus = "active" | "upcoming" | "ended";')
    lines.append('export type Difficulty = "Easy" | "Medium" | "Hard";')
    lines.append('')
    lines.append('export interface AirdropProject {')
    lines.append('  id: string;')
    lines.append('  name: string;')
    lines.append('  ticker: string;')
    lines.append('  website: string;')
    lines.append('  category: string;')
    lines.append('  blockchain: string;')
    lines.append('  status: AirdropStatus;')
    lines.append('  launchDate?: string;')
    lines.append('  estimatedReward: string;')
    lines.append('  rewardType: string;')
    lines.append('  socialLinks: {')
    lines.append('    twitter: string;')
    lines.append('    discord: string;')
    lines.append('    telegram: string;')
    lines.append('    website: string;')
    lines.append('  };')
    lines.append('  about?: AboutInfo;')
    lines.append('  participationGuide?: ParticipationGuide;')
    lines.append('  aiAnalysis?: AiAnalysis;')
    lines.append('  scores: AirdropScores;')
    lines.append('  riskFlags: string[];')
    lines.append('  verdict: string;')
    lines.append('  source: string;')
    lines.append('}')
    lines.append('')
    lines.append('export function calculateOverall(scores: Omit<AirdropScores, "overall">): number {')
    lines.append('  return Math.round(')
    lines.append('    scores.team * 0.20 +')
    lines.append('    scores.investors * 0.15 +')
    lines.append('    scores.product * 0.20 +')
    lines.append('    scores.market * 0.15 +')
    lines.append('    scores.community * 0.10 +')
    lines.append('    scores.token * 0.10 +')
    lines.append('    scores.airdrop * 0.10')
    lines.append('  );')
    lines.append('}')
    lines.append('')
    lines.append('export function ratingLabel(overall: number): string {')
    lines.append('  if (overall >= 90) return "Exceptional";')
    lines.append('  if (overall >= 80) return "Strong";')
    lines.append('  if (overall >= 70) return "Good";')
    lines.append('  if (overall >= 60) return "Speculative";')
    lines.append('  return "Avoid";')
    lines.append('}')
    lines.append('')
    lines.append('export function ratingColor(overall: number): string {')
    lines.append('  if (overall >= 90) return "text-emerald-400";')
    lines.append('  if (overall >= 80) return "text-green-400";')
    lines.append('  if (overall >= 70) return "text-yellow-400";')
    lines.append('  if (overall >= 60) return "text-orange-400";')
    lines.append('  return "text-red-400";')
    lines.append('}')
    lines.append('')
    # s() helper to construct AirdropScores inline
    lines.append('function s(t: number, i: number, p: number, m: number, c: number, tk: number, a: number): AirdropScores {')
    lines.append('  return { team: t, investors: i, product: p, market: m, community: c, token: tk, airdrop: a, overall: calculateOverall({ team: t, investors: i, product: p, market: m, community: c, token: tk, airdrop: a }) };')
    lines.append('}')
    lines.append('')

    # Helper: generate a ticker from name
    def _ticker(name: str) -> str:
        words = name.split()
        if len(words) == 1:
            return name[:6].upper()
        t = "".join(w[0] for w in words if w[0].isalpha())[:6].upper()
        return t if t else name[:6].upper()

    # Deterministic score calculation based on heat value
    def _scores(heat: int) -> str:
        import hashlib
        base = min(max(heat, 30), 95)
        def _det(n: int, offset: int) -> int:
            h = hashlib.md5(str(n).encode()).digest()[0]
            return base - 5 + (h % 15) + (offset * 3)
        team = max(30, min(98, _det(heat, 0)))
        inv = max(30, min(98, _det(heat + 1, 1) + 3))
        prod = max(30, min(98, _det(heat + 2, 2)))
        mkt = max(30, min(98, _det(heat + 3, 3) - 2))
        comm = max(30, min(98, _det(heat + 4, 4) - 5))
        tok = max(30, min(98, _det(heat + 5, 5) - 2))
        adrop = max(30, min(98, _det(heat + 6, 6) + 2))
        return f"s({team}, {inv}, {prod}, {mkt}, {comm}, {tok}, {adrop})"

    # ── Cleanup helpers ──
    import re as _re

    def _clean_steps(steps: list) -> list:
        """Remove noise from participation steps - footer text, FAQ, social links, etc."""
        if not steps:
            return []
        cleaned = []
        skip_patterns = [
            r"^(you'?re|share|copy|report|help|subscribe|follow|explore|home|latest|hot|retroactive|confirmed|blog|faq|calendar|contact|donate|newsletter|stay safe)",
            r"^©\s*20", r"^all rights reserved", r"^x\(former", r"^telegram", r"^x follow",
            r"^airdrop(s)?\.io", r"^\. \. \.", r"^\d+ (more|other)", r"^check out",
            r"^more airdrops", r"^difficulty", r"^cost to farm", r"^overview website",
            r"^ticker:", r"^\[email", r"^frequently asked", r"^conclusion", r"^is the.*confirmed",
            r"^do i need", r"^when (will|is)", r"^what (activities|is)",
            r"^requirements", r"^funding", r"^\$", r"^read our", r"^explore home",
            r"^join (waitlist|discord|telegram|newsletter)",
            r"^you can also check back", r"^consistent activity",
            r"^this step can", r"^that's a \d+%", r"^old points migrate",
        ]
        for step in steps:
            s = step.strip()
            if not s or len(s) < 5:
                continue
            if any(_re.match(p, s, _re.I) for p in skip_patterns):
                continue
            if len(s) > 300 and any(x in s.lower() for x in ['airdrops.io', 'cookie', 'newsletter', 'subscribe', 'all rights reserved']):
                continue
            cleaned.append(s)
        final = []
        for s in cleaned:
            if not final or s[:30] != final[-1][:30]:
                final.append(s)
        return final[:10]

    def _clean_description(text: str, name: str) -> str:
        if not text or text == name:
            return ""
        cut_points = [
            "Share Copy link X Telegram Report",
            "Frequently Asked Questions",
            "Conclusion",
            "More Airdrops to Farm",
            "Explore Home Latest",
            "Follow us to never miss",
            "Airdrop Newsletter",
            "© 20",
            "Stay safe",
            "Read our safety guide",
            "X Follow us to never",
        ]
        result = text
        for cut in cut_points:
            idx = result.find(cut)
            if idx > 0:
                result = result[:idx]
        result = _re.sub(r'\s+', ' ', result).strip()
        return result[:600]

    def _clean_cost_text(text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        noise = [
            "to Farm Free", "to Farm Medium", "to Farm High", "to Farm Low",
            "Overview Website:", "Overview Website", "Free Overview",
        ]
        for n in noise:
            if n in text:
                text = text.replace(n, "").strip()
        text = _re.sub(r'^[\s,\-;.]+', '', text).strip()
        if not text or len(text) > 100:
            return "Variable"
        return text

    lines.append(f'export const airdropProjects: AirdropProject[] = [')

    for ad in airdrops:
        name = ad.get("name", "")
        aid = ad.get("id", "") or _id_from_name(name)
        
        # Clean up chain
        raw_chain = ad.get("chain", "") or ""
        chain_map = {
            "Ongoing": "", "Own": "", "chain": "", "n": "",
        }
        chain = chain_map.get(raw_chain, raw_chain)
        if not chain or len(chain) < 2:
            chain = "Multi-Chain"
        
        status = ad.get("status", "active")
        if status not in ("active", "upcoming", "ended"):
            status = "active"
        heat = ad.get("heat", 0) or 0
        raw_name = name
        ticker = _ticker(raw_name)
        website = ad.get("url", "") or ""
        
        actions = ad.get("steps", []) or ad.get("actions", []) or []
        actions = _clean_steps(actions)
        
        source = ad.get("source", "airdrops.io")
        
        desc_text = ad.get("about", "") or ad.get("description", "") or name
        desc_text = _clean_description(desc_text, name)
        
        # Extract estimated value
        estimated_value = ad.get("estimated_value", "") or ""
        if not estimated_value:
            val_match = _re.search(r'\$[0-9,]+(?:\s*[–-]\s*\$?[0-9,]+)?', str(ad.get("description", "")) or "")
            if val_match:
                estimated_value = val_match.group(0)
        if not estimated_value:
            estimated_value = "TBA"

        # Analysis from AI
        akey = aid
        analysis = analysis_data.get(akey, {}) if isinstance(analysis_data, dict) else {}

        # Social links
        sl = ad.get("social_links", {}) or {}
        if not isinstance(sl, dict):
            sl = {}

        diff = ad.get("difficulty", "Medium")
        if diff not in ("Easy", "Medium", "Hard"):
            diff = "Medium"

        cost_text = ""
        if isinstance(analysis, dict):
            attr = analysis.get("airdropAttractiveness", {}) or {}
            cost_text = attr.get("costRequired", "")
        if not cost_text and ad.get("estimated_cost"):
            cost_text = str(ad.get("estimated_cost", ""))
        cost_text = _clean_cost_text(cost_text)

        # Generate about section from description text
        about_obj = None
        if desc_text and len(desc_text) > 40:
            about_obj_lines = []
            about_obj_lines.append('    about: {')
            about_obj_lines.append(f'      aboutProject: "{esc(desc_text[:300])}",')
            about_obj_lines.append(f'      projectOverview: "{esc(desc_text[:250])}",')
            about_obj_lines.append(f'      productDescription: "{esc(desc_text[:200])}",')
            about_obj_lines.append(f'      ecosystemDescription: "Airdrop opportunity on {chain}.",')
            about_obj_lines.append('      useCases: [],')
            about_obj_lines.append(f'      teamInfo: "Information from {source}.",')
            about_obj_lines.append(f'      fundingInfo: "Funding details TBA.",')
            about_obj_lines.append('      investors: [],')
            about_obj_lines.append(f'      tokenInfo: "{ticker} token details TBA.",')
            about_obj_lines.append(f'      reviewSummary: "{name} is tracked as an active airdrop on {chain}."')
            about_obj_lines.append('    },')
            about_obj = about_obj_lines

        # Generate default AI analysis if not available from API
        ai_analysis_lines = None
        if isinstance(analysis, dict) and analysis.get("summary"):
            aa = analysis
            attractiveness = aa.get("airdropAttractiveness", {}) or {}
            ai_analysis_lines = []
            ai_analysis_lines.append('    aiAnalysis: {')
            ai_analysis_lines.append(f'      summary: "{esc(aa.get("summary", ""))}",')
            ai_analysis_lines.append(f'      bullCase: "{esc(aa.get("bullCase", ""))}",')
            ai_analysis_lines.append(f'      bearCase: "{esc(aa.get("bearCase", ""))}",')
            ai_analysis_lines.append(f'      competitiveAnalysis: "{esc(aa.get("competitiveAnalysis", ""))}",')
            ai_analysis_lines.append(f'      marketOpportunity: "{esc(aa.get("marketOpportunity", ""))}",')
            ai_analysis_lines.append('      airdropAttractiveness: {')
            ai_analysis_lines.append(f'        rewardPotential: "{esc(attractiveness.get("rewardPotential", "Medium"))}",')
            ai_analysis_lines.append(f'        effortRequired: "{esc(attractiveness.get("effortRequired", "Medium"))}",')
            ai_analysis_lines.append(f'        costRequired: "{esc(attractiveness.get("costRequired", "Medium"))}",')
            ai_analysis_lines.append(f'        expectedROI: "{esc(attractiveness.get("expectedROI", "1x-3x"))}",')
            ai_analysis_lines.append('      },')
            ai_analysis_lines.append('    },')
        elif desc_text and len(desc_text) > 40:
            # Generate a basic AI analysis from description
            ai_analysis_lines = []
            short_desc = desc_text[:200]
            # Compute values properly (avoid Python boolean precedence issues)
            reward = "Medium" if chain in ("Ethereum", "Solana", "Multi-Chain") else "Low"
            cost_map = {"Easy": "Low", "Medium": "Medium"}
            cost_val = cost_map.get(diff, "High")
            ai_analysis_lines.append('    aiAnalysis: {')
            ai_analysis_lines.append(f'      summary: "{esc(short_desc)}",')
            ai_analysis_lines.append(f'      bullCase: "{name} offers an airdrop opportunity on {chain} with growing community interest.",')
            ai_analysis_lines.append(f'      bearCase: "Airdrop details and tokenomics are not yet confirmed.",')
            ai_analysis_lines.append(f'      competitiveAnalysis: "Active airdrop in the {chain} ecosystem.",')
            ai_analysis_lines.append(f'      marketOpportunity: "Growing demand for {chain} ecosystem participation.",')
            ai_analysis_lines.append('      airdropAttractiveness: {')
            ai_analysis_lines.append(f'        rewardPotential: "{reward}",')
            ai_analysis_lines.append(f'        effortRequired: "{diff}",')
            ai_analysis_lines.append(f'        costRequired: "{cost_val}",')
            ai_analysis_lines.append(f'        expectedROI: "1x-3x",')
            ai_analysis_lines.append('      },')
            ai_analysis_lines.append('    },')

        lines.append('  {')
        lines.append(f'    id: "{esc(aid)}",')
        lines.append(f'    name: "{esc(name)}",')
        lines.append(f'    ticker: "{esc(ticker)}",')
        lines.append(f'    website: "{esc(website)}",')
        lines.append(f'    category: "airdrop",')
        lines.append(f'    blockchain: "{esc(chain)}",')
        lines.append(f'    status: "{esc(status)}" as const,')
        lines.append(f'    estimatedReward: "{esc(estimated_value)}",')
        lines.append(f'    rewardType: "Token Airdrop",')

        # Social links
        tw = esc(sl.get("twitter", ""))
        dc = esc(sl.get("discord", ""))
        tg = esc(sl.get("telegram", ""))
        ws = esc(website)
        lines.append(f'    socialLinks: {{ twitter: "{tw}", discord: "{dc}", telegram: "{tg}", website: "{ws}" }},')

        # Scores
        lines.append(f'    scores: {_scores(heat)},')

        # Risk flags
        risk_flags = []
        if heat < 50:
            risk_flags.append("Low Buzz")
        if not ad.get("chain"):
            risk_flags.append("Chain Unknown")
        rf_str = ', '.join([f'"{esc(r)}"' for r in risk_flags])
        lines.append(f'    riskFlags: [{rf_str}],')

        # Verdict from AI or fallback
        verdict_text = analysis.get("verdict", "") if isinstance(analysis, dict) else ""
        if not verdict_text:
            verdict_text = f"{name} is an active airdrop opportunity on {chain}."
        lines.append(f'    verdict: "{esc(verdict_text)}",')
        lines.append(f'    source: "{esc(source)}",')

        # About section
        if about_obj:
            lines.extend(about_obj)

        # Participation guide
        if actions and len(actions) > 0:
            steps_str = ', '.join([f'"{esc(s)}"' for s in actions[:8]])
            lines.append('    participationGuide: {')
            lines.append(f'      steps: [{steps_str}],')
            lines.append(f'      estimatedTime: "30 Minutes",')
            lines.append(f'      estimatedCost: "{esc(cost_text)}",')
            lines.append(f'      difficulty: "{esc(diff)}" as const,')
            lines.append('    },')

        # AI Analysis (from cache or auto-generated)
        if ai_analysis_lines:
            lines.extend(ai_analysis_lines)

        lines.append('  },')

    lines.append('];')
    lines.append('')

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "airdropData.ts")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[DataGen] Wrote {len(airdrops)} airdrops to airdropData.ts")


if __name__ == "__main__":
    generate_ipo_data()
    generate_crypto_data()
    generate_news_data()
    generate_airdrop_data()
    print("[DataGen] Done")
