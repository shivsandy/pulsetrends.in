import json
import os
import re
from datetime import datetime, timezone

import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "data")


def prune_old_articles(articles: list, max_days: int = 60) -> list:
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
    return json.dumps(s, ensure_ascii=False)[1:-1]


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
    lines.append("  status: 'upcoming' | 'open' | 'listed' | 'subscribed';")
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
    lines.append('}')
    lines.append('')
    lines.append('export const ipoStocks: IPOStock[] = [')

    for i, ipo in enumerate(ipos):
        name = ipo.get("name") or ipo.get("company_name", "")
        symbol = ipo.get("ticker") or ipo.get("symbol", "")
        country = ipo.get("headquarters") or ipo.get("country", "Global")
        exchange = ipo.get("exchange") or ipo.get("listingExchange", "NSE/BSE")
        status = ipo.get("status", "upcoming")
        if status not in ("upcoming", "open", "listed", "subscribed"):
            status = "upcoming"
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
        expected_date = listing_date or open_date
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
        lines.append('    aiScores: {')
        lines.append(f'      overall: {scores.get("attractiveness", scores.get("overall", 75))},')
        lines.append(f'      fundamentals: {scores.get("financial_health", 70)},')
        lines.append(f'      valuation: {scores.get("risk", 65)},')
        lines.append(f'      growth: {scores.get("growth_potential", 75)},')
        lines.append(f'      management: 70,')
        lines.append(f'      marketSentiment: {scores.get("attractiveness", 72)},')
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
    articles = load_json(news_cache_path)
    if not isinstance(articles, list):
        articles = []

    # Enforce 60-day retention
    articles = prune_old_articles(articles)

    print(f"[DataGen] Loading {len(articles)} news articles from cache...")

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


if __name__ == "__main__":
    generate_ipo_data()
    generate_crypto_data()
    generate_news_data()
    print("[DataGen] Done")
