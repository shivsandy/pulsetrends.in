import json
import os
import re
from datetime import datetime, timezone

import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "data")

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
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")
    return s


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
    ipos_data = load_json(os.path.join(DATA_DIR, "ipos.json"))
    analysis_data = load_json(os.path.join(DATA_DIR, "ipo_analysis.json"))
    ipos = ipos_data.get("ipos", [])

    print(f"[DataGen] Loading {len(ipos)} IPOs, fetching web news...")

    lines = []
    lines.append('export interface IPOStock {')
    lines.append('  id: string;')
    lines.append('  company: string;')
    lines.append('  ticker: string;')
    lines.append('  sector: string;')
    lines.append('  description: string;')
    lines.append('  founded: string;')
    lines.append('  headquarters: string;')
    lines.append('  employees: string;')
    lines.append('  ceo: string;')
    lines.append('  expectedDate: string;')
    lines.append('  priceRange: string;')
    lines.append('  lotSize: number;')
    lines.append('  issueSize: string;')
    lines.append('  listingExchange: string;')
    lines.append('  ipoType: string;')
    lines.append('  registrar: string;')
    lines.append("  status: 'upcoming' | 'open' | 'listed';")
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
    lines.append('}')
    lines.append('')
    lines.append('export const ipoStocks: IPOStock[] = [')

    for i, ipo in enumerate(ipos):
        name = ipo.get("company_name", "")
        symbol = ipo.get("symbol", "")
        country = ipo.get("country", "Global")
        exchange = ipo.get("exchange", "")
        status = ipo.get("status", "upcoming")
        price = ipo.get("price_band", "")
        listing_date = ipo.get("listing_date", "")
        open_date = ipo.get("open_date", "")
        issue_size = ipo.get("issue_size", "")
        lot_size = ipo.get("lot_size", "")
        ipo_type = ipo.get("ipo_type", "mainboard")

        akey = f"{symbol}-{country}" if symbol else f"{name.lower().replace(' ', '-')[:20]}-{country}"
        analysis = analysis_data.get(akey, {})

        about_raw = analysis.get("about", "")
        about = esc(about_raw) if isinstance(about_raw, str) else ""
        strengths_raw = analysis.get("strengths", [])
        risks_raw = analysis.get("risks", [])
        scores = analysis.get("scores", {})
        ai_analysis = esc(analysis.get("ai_analysis", ""))
        verdict = esc(analysis.get("verdict", ""))

        news_snippet = search_news_for_ipo(name, symbol)
        if news_snippet:
            enriched_analysis = ai_analysis + "\n\n" + esc(news_snippet) if ai_analysis else esc(news_snippet)
        else:
            enriched_analysis = ai_analysis

        strengths_list = strengths_raw if isinstance(strengths_raw, list) else []
        strengths_str = ', '.join([f'"{esc(s)}"' for s in strengths_list[:5]]) if strengths_list else ''

        lines.append('  {')
        lines.append(f'    id: "{i + 1}",')
        lines.append(f'    company: "{esc(name)}",')
        lines.append(f'    ticker: "{esc(symbol)}",')
        lines.append(f'    sector: "{esc(ipo_type)}",')
        lines.append(f'    description: "{esc(about or name)}",')
        lines.append(f'    founded: "",')
        lines.append(f'    headquarters: "{esc(country)}",')
        lines.append(f'    employees: "",')
        lines.append(f'    ceo: "",')
        lines.append(f'    expectedDate: "{esc(listing_date or open_date)}",')
        lines.append(f'    priceRange: "{esc(price)}",')
        lines.append(f'    lotSize: {int(float(lot_size)) if lot_size.replace(",","").replace(".","").isdigit() else 0},')
        lines.append(f'    issueSize: "{esc(issue_size)}",')
        lines.append(f'    listingExchange: "{esc(exchange)}",')
        lines.append(f'    ipoType: "{esc(ipo_type)}",')
        lines.append(f'    registrar: "",')
        lines.append(f'    status: "{esc(status)}" as const,')
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
        lines.append(f'    aiVerdict: "{verdict}",')
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
    lines.append('  aiAnalysis?: {')
    lines.append('    summary: string;')
    lines.append("    sentiment: 'bullish' | 'bearish' | 'neutral';")
    lines.append('    convictionScore: number;')
    lines.append('    keyDrivers: string[];')
    lines.append('    risks: string[];')
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
        price = esc(proj.get("price", ""))
        market_cap = esc(proj.get("market_cap", ""))
        volume = esc(proj.get("volume_24h", ""))
        est_value = esc(proj.get("estimated_value", ""))
        eligibility = esc(proj.get("eligibility", ""))
        farming_guide = esc(proj.get("farming_guide", ""))
        tge_date = esc(proj.get("tge_date", ""))

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

        has_ai = analysis and (ai_summary or verdict)
        if has_ai:
            drivers_str = ', '.join([f'"{esc(d)}"' for d in key_drivers[:5]])
            risks_str = ', '.join([f'"{esc(r)}"' for r in risks[:5]])
            lines.append('    aiAnalysis: {')
            lines.append(f'      summary: "{ai_summary}",')
            lines.append(f'      sentiment: "{sentiment}" as const,')
            lines.append(f'      convictionScore: {conviction},')
            lines.append(f'      keyDrivers: [{drivers_str}],')
            lines.append(f'      risks: [{risks_str}],')
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


if __name__ == "__main__":
    generate_ipo_data()
    generate_crypto_data()
    print("[DataGen] Done")
