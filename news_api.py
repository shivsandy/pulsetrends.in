import atexit
import json
import os
import random
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

NEWS_CACHE: List[dict] = []
CACHE_LOCK = threading.Lock()
DATA_DIR = Path(__file__).resolve().parent / "data"
NEWS_CACHE_FILE = DATA_DIR / "news_cache.json"

OPENROUTER_KEYS = []
for i in range(1, 5):
    val = os.environ.get(f"OPENROUTER_API_KEY_{i}")
    if val:
        OPENROUTER_KEYS.append({"key": val, "index": i})

NVIDIA_KEYS = []
for i in range(1, 2):
    val = os.environ.get(f"NVIDIA_API_KEY_{i}")
    if val:
        NVIDIA_KEYS.append({"key": val, "index": i})

GOOGLE_KEYS = []
for i in range(1, 3):
    val = os.environ.get(f"GOOGLE_AI_API_KEY_{i}")
    if val:
        GOOGLE_KEYS.append({"key": val, "index": i})

FINNHUB_KEYS = []
for i in range(1, 5):
    val = os.environ.get(f"FINNHUB_API_KEY_{i}")
    if val:
        FINNHUB_KEYS.append({"key": val, "index": i})

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
UNSPLASH_KEYS = []
for i in range(1, 4):
    val = os.environ.get(f"UNSPLASH_ACCESS_KEY_{i}")
    if val:
        UNSPLASH_KEYS.append(val)

USED_IMAGES_FILE = DATA_DIR / "used_news_images.json"


class ModelHealth:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def healthy_models(self, models: List[str]) -> List[str]:
        now = time.time()
        with self.lock:
            healthy = []
            for m in models:
                h = self.data.get(m)
                if h and h.get("cooldown", 0) > now:
                    continue
                healthy.append(m)
            random.shuffle(healthy)
            return healthy

    def record_failure(self, model: str, code: Optional[int] = None):
        with self.lock:
            h = self.data.get(model, {"failures": 0, "cooldown": 0})
            h["failures"] = h.get("failures", 0) + 1
            now = time.time()
            if code == 429:
                h["cooldown"] = now + 300
            elif code and 500 <= code < 600:
                h["cooldown"] = now + 180
            else:
                h["cooldown"] = now + 120
            self.data[model] = h

    def record_success(self, model: str):
        with self.lock:
            h = self.data.get(model, {"failures": 0, "cooldown": 0})
            h["failures"] = 0
            h["cooldown"] = 0
            self.data[model] = h


model_health = ModelHealth()

FALLBACK_FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-32b:free",
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-chat:free",
    "microsoft/phi-4:free",
]

OPENROUTER_FALLBACK_NVIDIA_MODELS = [
    "meta/llama-3.1-70b-instruct",
    "mistralai/mistral-large",
    "google/gemma-2-27b-it",
]

GOOGLE_FREE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemma-3-27b-it",
]

_DISCOVERED_FREE_MODELS: Optional[List[str]] = None


def discover_free_models(api_keys: List[dict]) -> List[str]:
    """Discover currently free models from OpenRouter's /v1/models endpoint.

    Filters by pricing.prompt == "0" (truly free tier).
    Caches result in module-level _DISCOVERED_FREE_MODELS for reuse.
    """
    global _DISCOVERED_FREE_MODELS
    if _DISCOVERED_FREE_MODELS is not None:
        return _DISCOVERED_FREE_MODELS

    discovered: set = set()
    for entry in api_keys:
        try:
            resp = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {entry['key']}"},
                timeout=15,
            )
            if resp.status_code == 200:
                for m in resp.json().get("data", []):
                    pricing = m.get("pricing", {})
                    try:
                        if float(pricing.get("prompt", "1")) == 0.0:
                            mid = m.get("id", "")
                            if mid and not mid.endswith(":free"):
                                mid = mid + ":free"
                            if mid:
                                discovered.add(mid)
                    except (ValueError, TypeError):
                        pass
        except Exception as e:
            print(f"[NewsAPI] Model discovery probe failed for key {entry['index']}: {e}")
        if discovered:
            break

    if discovered:
        sorted_models = sorted(discovered)
        print(f"[NewsAPI] Discovered {len(sorted_models)} free models from OpenRouter")
        _DISCOVERED_FREE_MODELS = sorted_models
        return sorted_models
    print(f"[NewsAPI] Model discovery failed, using {len(FALLBACK_FREE_MODELS)} fallback models")
    _DISCOVERED_FREE_MODELS = list(FALLBACK_FREE_MODELS)
    return _DISCOVERED_FREE_MODELS


def reset_model_discovery() -> None:
    """Clear the cached discovered model list (for testing)."""
    global _DISCOVERED_FREE_MODELS
    _DISCOVERED_FREE_MODELS = None


def get_free_models() -> List[str]:
    """Get the current free model list, discovering on first call."""
    if OPENROUTER_KEYS:
        return discover_free_models(OPENROUTER_KEYS)
    return list(FALLBACK_FREE_MODELS)

RSS_URLS = [
    "https://news.google.com/rss/search?q=cryptocurrency+bitcoin+ethereum&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=crypto+market+bitcoin+ethereum+ETF&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=IPO+stock+market+listing&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=India+IPO+NSE+BSE+GMP+subscription&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=Indian+stock+market+Sensex+Nifty+RBI&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=US+stocks+Nasdaq+S%26P+500+earnings&hl=en-US&gl=US&ceid=US:en",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://cointelegraph.com/rss",
    "https://coindesk.com/feed",
    "https://finance.yahoo.com/news/rss/index",
    "https://www.livemint.com/rss/markets",
    "https://www.livemint.com/rss/companies",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://www.moneycontrol.com/rss/business.xml",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
]

NEWSAPI_QUERIES = [
    "cryptocurrency OR bitcoin OR ethereum",
    "crypto ETF OR blockchain OR defi",
    "IPO OR initial public offering OR stock listing",
    "India IPO OR NSE IPO OR BSE IPO OR grey market premium",
    "Indian stock market OR Sensex OR Nifty OR RBI",
    "stock market earnings OR Nasdaq OR S&P 500",
]

MARKET_TERMS = [
    "ipo", "initial public", "listing", "stock", "stocks", "market", "markets",
    "nse", "bse", "nifty", "sensex", "rbi", "earnings", "nasdaq", "s&p",
    "crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain", "defi",
    "token", "coin", "etf", "funding", "valuation", "shares",
]

BLOCKED_TERMS = ["trump", "election", "sports", "weather", "celebrity", "movie", "cricket"]


def fetch_rss() -> List[dict]:
    items = []
    for url in RSS_URLS:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if resp.status_code != 200:
                continue
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.content)
            for item in root.iter("item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                pubdate = item.findtext("pubDate", "")
                if title and len(title) > 20:
                    items.append({"title": title.strip(), "url": link.strip(), "summary": desc.strip()[:500] if desc else "", "published": pubdate.strip(), "source": url.split("/")[2] if "//" in url else url})
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                link = link_el.get("href", "") if link_el is not None else ""
                summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", "")
                published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")
                if title and len(title) > 20:
                    items.append({"title": title.strip(), "url": link.strip(), "summary": summary.strip()[:500] if summary else "", "published": published.strip(), "source": url.split("/")[2] if "//" in url else url})
        except Exception:
            pass
    print(f"[NewsAPI] RSS: {len(items)} raw items")
    return items


def fetch_newsapi() -> List[dict]:
    if not NEWSAPI_KEY:
        return []
    items = []
    for q in NEWSAPI_QUERIES:
        try:
            resp = requests.get("https://newsapi.org/v2/everything", params={"q": q, "pageSize": 10, "language": "en", "sortBy": "popularity", "apiKey": NEWSAPI_KEY}, timeout=15)
            if resp.status_code == 200:
                for article in resp.json().get("articles", []):
                    title = (article.get("title") or "").strip()
                    if title and len(title) > 20:
                        items.append({"title": title, "url": article.get("url", ""), "summary": (article.get("description") or "")[:500], "published": article.get("publishedAt", ""), "source": article.get("source", {}).get("name", "newsapi")})
        except Exception:
            pass
    print(f"[NewsAPI] NewsAPI: {len(items)} items")
    return items


def fetch_finnhub() -> List[dict]:
    if not FINNHUB_KEYS:
        return []
    items: List[dict] = []
    today = datetime.now(timezone.utc)
    week_ago = today.fromtimestamp(today.timestamp() - 7 * 24 * 3600, tz=timezone.utc)
    from_str = week_ago.strftime("%Y-%m-%d")
    to_str = today.strftime("%Y-%m-%d")

    key_index = 0
    for category in ["general", "forex", "crypto"]:
        if key_index >= len(FINNHUB_KEYS):
            key_index = 0
        key = FINNHUB_KEYS[key_index]["key"]
        try:
            resp = requests.get(
                "https://finnhub.io/api/v1/news",
                params={"category": category, "token": key, "minId": 0},
                timeout=15,
            )
            if resp.status_code == 200:
                for article in resp.json()[:15]:
                    title = (article.get("headline") or "").strip()
                    url = article.get("url", "")
                    summary = (article.get("summary") or "")[:500]
                    image = article.get("image", "")
                    source = article.get("source", "finnhub")
                    published_ts = article.get("datetime")
                    published = ""
                    if published_ts:
                        try:
                            published = datetime.fromtimestamp(published_ts, tz=timezone.utc).isoformat()
                        except Exception:
                            pass
                    if title and len(title) > 20 and url:
                        items.append({
                            "title": title,
                            "url": url,
                            "summary": summary,
                            "published": published,
                            "source": source,
                            "image": image,
                        })
        except Exception as e:
            print(f"[NewsAPI] Finnhub {category} fetch error: {e}")
        key_index += 1

    print(f"[NewsAPI] Finnhub: {len(items)} items")
    return items


def is_market_relevant(item: dict) -> bool:
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    if any(term in text for term in BLOCKED_TERMS):
        return False
    return any(term in text for term in MARKET_TERMS)


def deduplicate(items: List[dict]) -> List[dict]:
    seen_titles = set()
    seen_urls = set()
    result = []
    for item in items:
        t = item["title"].lower().strip()
        url = item.get("url", "").strip()
        if not is_market_relevant(item) or url in seen_urls:
            continue
        is_dup = False
        for seen in seen_titles:
            from difflib import SequenceMatcher
            if SequenceMatcher(None, t, seen).ratio() > 0.7:
                is_dup = True
                break
        if not is_dup:
            seen_titles.add(t)
            if url:
                seen_urls.add(url)
            result.append(item)
    return result


def load_cached_news() -> List[dict]:
    try:
        if NEWS_CACHE_FILE.exists():
            with NEWS_CACHE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                print(f"[NewsAPI] Loaded {len(data)} cached articles from disk")
                return data
    except Exception as e:
        print(f"[NewsAPI] Cache load failed: {e}")
    return []


def save_cached_news(articles: List[dict]) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with NEWS_CACHE_FILE.open("w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[NewsAPI] Cache save failed: {e}")


def load_used_image_ids() -> set:
    try:
        if USED_IMAGES_FILE.exists():
            with USED_IMAGES_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return set(data)
    except Exception as e:
        print(f"[NewsAPI] Used-images load failed: {e}")
    return set()


def save_used_image_ids(ids: set) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with USED_IMAGES_FILE.open("w", encoding="utf-8") as f:
            json.dump(sorted(ids), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[NewsAPI] Used-images save failed: {e}")


def scrape_article(url: str) -> Optional[dict]:
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        og_title = ""
        og_desc = ""
        og_image = ""
        author = ""
        pub_date = ""
        content_text = ""

        og_title_el = soup.select_one("meta[property='og:title'], meta[name='twitter:title']")
        if og_title_el:
            og_title = og_title_el.get("content", "")

        og_desc_el = soup.select_one("meta[property='og:description'], meta[name='description'], meta[name='twitter:description']")
        if og_desc_el:
            og_desc = og_desc_el.get("content", "")

        og_image_el = soup.select_one("meta[property='og:image'], meta[name='twitter:image']")
        if og_image_el:
            og_image = og_image_el.get("content", "")

        author_el = soup.select_one("meta[name='author'], meta[property='article:author']")
        if author_el:
            author = author_el.get("content", "")

        date_el = soup.select_one("meta[property='article:published_time'], meta[name='pubdate'], time")
        if date_el:
            pub_date = date_el.get("content", "") or date_el.get("datetime", "")

        article_el = soup.select_one("article, .article-body, .post-content, .entry-content, .story-body, .article-content, [itemprop='articleBody']")
        if article_el:
            for tag in article_el.select("script, style, nav, footer, aside, .ad, .advertisement, .social-share"):
                tag.decompose()
            content_text = article_el.get_text(separator="\n", strip=True)[:3000]
        else:
            body = soup.find("body")
            if body:
                for tag in body.select("script, style, nav, footer, aside, .ad, .advertisement, .sidebar, .comments, .social-share"):
                    tag.decompose()
                content_text = body.get_text(separator="\n", strip=True)[:2000]

        if not content_text or len(content_text) < 100:
            return None

        return {"title": og_title, "description": og_desc, "image": og_image, "author": author, "date": pub_date, "content": content_text}
    except Exception:
        return None


CATEGORY_QUERY_MAP: dict = {
    "crypto": [
        "cryptocurrency bitcoin ethereum",
        "blockchain digital assets defi",
        "crypto trading exchange",
        "bitcoin ethereum price chart",
    ],
    "ipo": [
        "ipo stock market listing",
        "initial public offering trading",
        "wall street trading floor",
        "financial documents earnings report",
    ],
    "india": [
        "mumbai stock exchange sensex nifty",
        "indian financial district bse nse",
        "india business economy market",
        "rupee indian currency banking",
    ],
    "stocks": [
        "nasdaq stock market charts",
        "wall street trading screen",
        "equity portfolio finance",
        "global stock market trading",
    ],
}


TOPIC_KEYWORDS: dict = {
    "crypto": ["bitcoin", "crypto", "ethereum", "blockchain", "defi", "nft", "token", "coin", "altcoin", "web3", "stablecoin"],
    "ipo": ["ipo", "initial public", "listing", "offer", "subscription", "grey market", "gmp", "drhp", "anchor"],
    "india": ["india", "indian", "nse", "bse", "nifty", "sensex", "rbi", "rupee", "mumbai", "sebi"],
    "stocks": ["stock", "stocks", "equity", "shares", "dividend", "earnings", "nasdaq", "s&p", "dow jones"],
}


def detect_category(text: str) -> str:
    text_lower = (text or "").lower()
    scores: dict = {}
    for cat, keywords in TOPIC_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in text_lower)
    if not any(scores.values()):
        return "stocks"
    india_score = scores.get("india", 0)
    if india_score >= 2 and india_score >= scores.get("ipo", 0) and india_score >= scores.get("crypto", 0) and india_score >= scores.get("stocks", 0):
        return "india"
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "stocks"


def _validate_image_url(url: str, timeout: int = 5) -> bool:
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        if resp.status_code == 200 and "image" in resp.headers.get("Content-Type", "").lower():
            return True
        resp = requests.get(url, stream=True, timeout=timeout)
        return resp.status_code == 200 and "image" in resp.headers.get("Content-Type", "").lower()
    except Exception:
        return False


def fetch_images(title: str, count: int = 4, category: Optional[str] = None) -> List[dict]:
    if not UNSPLASH_KEYS:
        return []

    category = category or detect_category(title)
    query_pool = CATEGORY_QUERY_MAP.get(category, CATEGORY_QUERY_MAP["stocks"])
    base_words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', '', title).split() if len(w) > 3][:3]
    if base_words:
        query_pool = [" ".join(base_words)] + query_pool

    used_ids = load_used_image_ids()
    results: List[dict] = []
    seen_photo_ids: set = set()

    for q in query_pool:
        if len(results) >= count:
            break
        for uk in UNSPLASH_KEYS:
            try:
                resp = requests.get(
                    "https://api.unsplash.com/search/photos",
                    params={"query": q, "per_page": 10, "orientation": "landscape", "content_filter": "high"},
                    headers={"Authorization": f"Client-ID {uk}"},
                    timeout=10,
                )
                if resp.status_code != 200:
                    continue
                hits = resp.json().get("results", [])
                for hit in hits:
                    photo_id = hit.get("id")
                    if not photo_id or photo_id in seen_photo_ids or photo_id in used_ids:
                        continue
                    url = hit.get("urls", {}).get("regular", "")
                    if not url:
                        continue
                    if not _validate_image_url(url):
                        continue
                    user = hit.get("user", {}) or {}
                    user_name = user.get("name", "Unsplash")
                    user_link = user.get("links", {}).get("html", "https://unsplash.com")
                    alt_desc = (hit.get("alt_description") or title).strip()
                    results.append({
                        "url": url,
                        "alt": alt_desc,
                        "title": alt_desc[:80],
                        "caption": f"{alt_desc} (via Unsplash)",
                        "attribution": f"Photo by {user_name} on Unsplash",
                        "sourceUrl": f"{user_link}?utm_source=pulsetrends&utm_medium=referral",
                        "photoId": photo_id,
                        "category": category,
                    })
                    seen_photo_ids.add(photo_id)
                    break
                if len(results) >= count:
                    break
            except Exception:
                continue
        if len(results) >= count:
            break

    if results:
        used_ids.update(r["photoId"] for r in results if "photoId" in r)
        if len(used_ids) > 500:
            used_ids = set(sorted(used_ids)[-500:])
        save_used_image_ids(used_ids)

    return results


# ----- LLM Prompts -----

SYSTEM_PROMPT = """You are an Elite Financial Research Analyst at PulseTrends, an institutional-grade financial intelligence platform covering cryptocurrency, IPOs, Indian equities, and global stock markets. You combine the roles of senior financial journalist, crypto researcher, IPO analyst, equity market analyst, technical SEO expert, GEO (Generative Engine Optimization) expert, digital journalist, Google Search Quality expert, AdSense compliance specialist, and content strategist.

OBJECTIVE: Produce content that ranks in Google Search, appears in Google AI Overviews, ChatGPT Search, Gemini, Perplexity, builds topical authority, passes Google AdSense review, gets indexed quickly, and generates long-term organic traffic.

=== ABSOLUTE RULES ===

NEVER:
- Copy content from any source
- Rewrite articles line-by-line
- Spin content
- Generate low-value content or generic AI filler
- Fabricate statistics, expert quotes, or data
- Publish unsupported claims
- Use legal, tax, or guaranteed-return claims
- Reproduce source article wording, sentence structure, or long quoted passages

ALWAYS:
- Research multiple trusted sources from the source material
- Extract facts only
- Build a completely original article with original analysis
- Add unique value beyond any single source
- Attribute factual claims to source names concisely
- Use professional tone similar to Bloomberg, Reuters, Financial Times
- Use short paragraphs, tables, and bullet points where useful
- Explain complex financial concepts clearly
- Prioritize India-relevant context when the story involves NSE, BSE, Sensex, Nifty, RBI, Indian IPOs, GMP, or Indian investors
- Include search-friendly but natural language for crypto, IPO, stock market, and India market readers
- Target 900-1500 words

=== GEO (GENERATIVE ENGINE OPTIMIZATION) ===

Optimize for Google AI Overviews, ChatGPT, Gemini, Claude, Perplexity, future AI Search Engines.
Primary goal: become a trusted citation source. Optimize for knowledge depth, not just keywords.
- Cover the full question space for the topic
- Build strong entity relationships (companies, tokens, exchanges, founders, regulators, products, technologies)
- Provide information gain beyond what any single source offers
- Demonstrate topic completeness
- Satisfy user intent (informational, transactional, navigational)
- Maximize AI citation potential through clear, factual, well-structured prose

=== E-E-A-T (EXPERIENCE, EXPERTISE, AUTHORITATIVENESS, TRUSTWORTHINESS) ===

Demonstrate:
- Verified facts only
- Industry context
- Balanced viewpoints (bull, bear, neutral cases)
- Risk disclosure
- Data-backed conclusions
- No promotional or hyped language

=== ARTICLE STRUCTURE ===

Generate the article body using this exact structure (in markdown-style sections within each JSON field):

1. EXECUTIVE SUMMARY (TL;DR for AI Overview snippets)
2. QUICK ANSWER (1-2 sentence direct answer for featured snippets)
3. WHAT HAPPENED (factual news reporting)
4. BACKGROUND CONTEXT
5. CURRENT MARKET SITUATION
6. KEY DEVELOPMENTS
7. DETAILED ANALYSIS with sub-sections:
   - Bullish Factors
   - Bearish Factors
   - Risk Analysis
   - Expert Perspective
   - Historical Comparison
   - Market Impact
8. INVESTOR TAKEAWAYS
9. FUTURE OUTLOOK
10. FREQUENTLY ASKED QUESTIONS (5-8 questions with concise answers)
11. CONCLUSION

=== CRYPTO-SPECIFIC REQUIREMENTS ===

For crypto articles, the "detailedAnalysis" or a dedicated "cryptoDetails" field should cover:
- Project Overview
- Token Utility
- Tokenomics
- Vesting Analysis
- Team Analysis
- Funding Analysis
- Ecosystem Analysis
- Airdrop Potential
- Security Risks
- Regulatory Risks
- Market Risks

=== IPO-SPECIFIC REQUIREMENTS ===

For IPO articles, the "detailedAnalysis" or a dedicated "ipoDetails" field should cover:
- Company Overview
- Financial Performance
- Revenue Trends
- Profitability
- GMP Analysis
- Valuation Analysis
- Industry Comparison
- Strengths
- Weaknesses
- Risks
- Subscription Analysis
- Listing Potential
- VERDICT: one of "Avoid", "Neutral", "Consider", "Strong Consider" with reasoning

=== STOCK-SPECIFIC REQUIREMENTS ===

For stock articles:
- Company Overview
- Business Model
- Revenue Analysis
- Profit Analysis
- Growth Drivers
- Risk Factors
- Technical View
- Fundamental View
- Industry Outlook
- Valuation Analysis
- Long-Term Potential
- Bull Case / Bear Case / Neutral Case

=== ENTITY OPTIMIZATION ===

Identify and weave in entities: companies, tokens, exchanges, founders, CEOs, investors, products, technologies, governments, regulators. Explain relationships between entities to strengthen knowledge graph relevance.

=== SEO METADATA ===

Generate these fields for every article:
- seoTitle: SEO-optimized title (50-60 chars, includes primary keyword)
- metaTitle: HTML <title> variant (50-60 chars)
- metaDescription: under 160 chars, includes primary keyword naturally
- slug: lowercase, hyphenated, keyword-rich URL slug
- focusKeyword: main target keyword
- secondaryKeywords: 3-7 related keywords
- relatedEntities: list of related entities for internal linking
- tags: 5-10 short tags
- categories: list of category names

=== INDEXING OPTIMIZATION ===

Ensure article: has single H1, proper H2/H3 structure, internal linking opportunities, crawl-friendly, index-friendly, sitemap-ready, canonical-friendly.
- indexingNotes: object with primaryKeyword, searchIntent, category, tags, entityCoverage fields

=== SCHEMA RECOMMENDATIONS ===

Generate recommendations for:
- schemaArticle: Article schema fields to include
- schemaFAQ: FAQPage schema with the FAQ Q&A pairs
- schemaBreadcrumb: BreadcrumbList path

=== TRAFFIC OPTIMIZATION ===

Generate:
- seoHeadlines: 5 SEO-optimized title variants
- ctrHeadlines: 5 high CTR / curiosity-driven variants
- socialHeadlines: 5 social-media optimized variants
- peopleAlsoAsk: 5-8 PAA questions relevant to the topic
- relatedSearches: 6-10 related search queries
- longTailKeywords: 5-8 long-tail keyword phrases

=== QUALITY SCORES ===

Generate honest quality scores 1-10 for:
- searchConsoleReadiness: how suitable for indexing
- adsenseReadiness: how well it passes AdSense review
- seoScore: technical SEO quality
- geoScore: generative engine optimization potential
- authorityScore: E-E-A-T strength
- aiCitationPotential: likelihood of being cited by AI search

=== IMAGE RULES ===

Every article must have:
- featuredImagePrompt: detailed image generation prompt (high quality, unique, topic-relevant, no stock-photo cliches)
- imageFilename: unique SEO-friendly filename
- imageAltText: descriptive alt text including primary keyword
- imageCaption: engaging caption
- imageTitle: image title attribute

=== OUTPUT FORMAT ===

Return ONLY valid JSON. No markdown code blocks. No text before or after. Structure:

{
  "headline": "SEO-optimized headline (50-70 chars)",
  "subheadline": "One-sentence summary",
  "keyHighlights": ["3-5 bullet points summarizing key facts"],
  "executiveSummary": "2-3 paragraph executive summary with Quick Answer embedded",
  "quickAnswer": "1-2 sentence direct answer for featured snippets",
  "marketBackground": "Market context and background",
  "detailedAnalysis": "In-depth analysis covering bullish factors, bearish factors, risk analysis, expert perspective, historical comparison, market impact. Use markdown-style ## for sub-headings within the text.",
  "financialMetrics": {
    "tableCaption": "string",
    "headers": ["col1", "col2", "col3"],
    "rows": [["val1", "val2", "val3"]]
  },
  "expertInsights": "Expert commentary and perspectives",
  "risks": ["List of 3-6 key risks"],
  "opportunities": ["List of 3-6 opportunities"],
  "outlook": "Future outlook and predictions",
  "conclusion": "Concluding analysis",
  "frequentlyAskedQuestions": [
    {"question": "...", "answer": "..."}
  ],
  "investorTakeaways": ["3-5 key takeaways for investors"],
  "sourcesReferenced": ["Source Name - URL or Source Name"],
  "aiAnalysis": {
    "bullCase": "Bullish thesis",
    "bearCase": "Bearish thesis",
    "neutralCase": "Neutral perspective",
    "probabilityWeightedOutlook": "Weighted probability forecast",
    "potentialCatalysts": ["Catalyst 1", "Catalyst 2"],
    "keyRisks": ["Risk 1", "Risk 2"]
  },
  "category": "crypto | ipo | stocks | india",
  "sentiment": "bullish | bearish | neutral",
  "impact": "high | medium | low",
  "relatedCoins": ["BTC", "ETH"],
  "relatedStocks": ["AAPL"],
  "relatedEntities": ["Company X", "Regulator Y"],
  "primaryKeyword": "main seo keyword",
  "secondaryKeywords": ["kw1", "kw2", "kw3"],
  "tags": ["tag1", "tag2"],
  "seoTitle": "SEO title 50-60 chars",
  "metaTitle": "Meta title 50-60 chars",
  "metaDescription": "Under 160 chars SEO meta",
  "slug": "keyword-rich-url-slug",
  "focusKeyword": "main target keyword",
  "categories": ["Category 1"],
  "seoHeadlines": ["5 SEO title variants"],
  "ctrHeadlines": ["5 high CTR variants"],
  "socialHeadlines": ["5 social variants"],
  "peopleAlsoAsk": ["5-8 PAA questions"],
  "relatedSearches": ["6-10 related queries"],
  "longTailKeywords": ["5-8 long-tail phrases"],
  "indexingNotes": {
    "primaryKeyword": "main keyword",
    "searchIntent": "informational | transactional | navigational | commercial",
    "category": "main category",
    "tags": ["tag list"],
    "entityCoverage": ["entities covered"]
  },
  "schemaArticle": {"type": "NewsArticle", "headline": "...", "author": "PulseTrends", "publisher": "PulseTrends"},
  "schemaFAQ": [{"question": "...", "answer": "..."}],
  "schemaBreadcrumb": [{"name": "Home", "url": "/"}, {"name": "News", "url": "/news"}, {"name": "Article", "url": "/news/slug"}],
  "searchConsoleReadiness": 8,
  "adsenseReadiness": 9,
  "seoScore": 9,
  "geoScore": 9,
  "authorityScore": 8,
  "aiCitationPotential": 9,
  "featuredImagePrompt": "Detailed Unsplash/DALL-E style prompt for unique hero image",
  "imageFilename": "unique-seo-friendly-filename.jpg",
  "imageAltText": "Descriptive alt with primary keyword",
  "imageCaption": "Engaging caption",
  "imageTitle": "Image title attribute",
  "ipoDetails": { ... },  // ONLY for IPO articles
  "cryptoDetails": { ... }  // ONLY for crypto articles
}

For IPO articles, include this ADDITIONAL top-level field:
"ipoDetails": {
  "companyOverview": "Company description",
  "ipoSize": "IPO size",
  "valuation": "Valuation",
  "offerPrice": "Price range",
  "subscriptionStatus": "Oversubscribed/undersubscribed",
  "greyMarketPremium": "GMP if available",
  "institutionalParticipation": "Institutional investor details",
  "revenueAnalysis": "Revenue and profitability analysis",
  "industryComparison": "Comparison with peers",
  "growthProspects": "Growth outlook",
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "risksDisclosed": ["Risk 1", "Risk 2"],
  "verdict": "Avoid | Neutral | Consider | Strong Consider",
  "verdictReasoning": "1-2 sentence reasoning"
}

For crypto articles, include this ADDITIONAL top-level field:
"cryptoDetails": {
  "tokenOverview": "Token description",
  "tokenUtility": "What the token is used for",
  "tokenomics": "Supply, distribution, inflation",
  "vestingAnalysis": "Vesting schedule and unlock risks",
  "teamAnalysis": "Team background and credibility",
  "fundingAnalysis": "Funding rounds and investors",
  "ecosystemAnalysis": "Ecosystem and partnerships",
  "airdropPotential": "Likelihood of airdrop",
  "marketCap": "Market cap figure",
  "tradingVolume": "24h volume",
  "priceMovement": "Price analysis",
  "onChainMetrics": "On-chain data",
  "whaleActivity": "Whale wallet movements",
  "institutionalAdoption": "Institutional interest",
  "regulatoryDevelopments": "Regulatory status",
  "ecosystemGrowth": "Ecosystem developments",
  "securityRisks": ["Security risk 1"],
  "regulatoryRisks": ["Regulatory risk 1"],
  "marketRisks": ["Market risk 1"]
}

=== INTERNAL LINKING ===
Suggest 3-5 related articles (by topic) that this article should link to internally. Use generic slugs like "/news/slug-of-related-article".

=== QUALITY CONTROL VERIFICATION ===
Before returning, verify:
✓ Originality > 95% (no copied phrasing)
✓ Factual accuracy (no fabricated stats)
✓ Entity coverage
✓ E-E-A-T compliance
✓ SEO/GEO optimization
✓ AdSense friendly
✓ No misleading claims
✓ All required JSON fields populated

Return ONLY the JSON object. No other text before or after."""


NVIDIA_FREE_MODELS = [
    "meta/llama-3.1-70b-instruct",
    "mistralai/mistral-large",
    "google/gemma-2-27b-it",
    "qwen/qwen3-32b",
    "meta/llama-3.3-70b-instruct",
]


def _call_openrouter(key: str, model: str, messages: List[dict], timeout: int = 180) -> Optional[str]:
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 16384},
            timeout=timeout,
        )
        if resp.status_code != 200:
            body = resp.text[:200] if resp.text else ""
            print(f"[NewsAPI] HTTP {resp.status_code} from OpenRouter/{model}: {body}")
            return None
        data = resp.json()
        if "choices" not in data or not data["choices"]:
            print(f"[NewsAPI] OpenRouter/{model} returned no choices: {str(data)[:200]}")
            return None
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[NewsAPI] OpenRouter/{model} exception: {e}")
        return None


def _call_nvidia(key: str, model: str, messages: List[dict], timeout: int = 180) -> Optional[str]:
    try:
        resp = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"},
            json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 16384, "stream": False},
            timeout=timeout,
        )
        if resp.status_code != 200:
            body = resp.text[:200] if resp.text else ""
            print(f"[NewsAPI] HTTP {resp.status_code} from NVIDIA/{model}: {body}")
            return None
        data = resp.json()
        if "choices" not in data or not data["choices"]:
            print(f"[NewsAPI] NVIDIA/{model} returned no choices: {str(data)[:200]}")
            return None
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[NewsAPI] NVIDIA/{model} exception: {e}")
        return None


def _call_google(key: str, model: str, messages: List[dict], timeout: int = 180) -> Optional[str]:
    try:
        system_text = ""
        user_text = ""
        for m in messages:
            if m.get("role") == "system":
                system_text = m.get("content", "")
            elif m.get("role") == "user":
                user_text = m.get("content", "")
        combined = f"{system_text}\n\n{user_text}" if system_text else user_text
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"role": "user", "parts": [{"text": combined}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 16384},
            },
            timeout=timeout,
        )
        if resp.status_code != 200:
            body = resp.text[:200] if resp.text else ""
            print(f"[NewsAPI] HTTP {resp.status_code} from Google/{model}: {body}")
            return None
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            print(f"[NewsAPI] Google/{model} returned no candidates: {str(data)[:200]}")
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        return text if text else None
    except Exception as e:
        print(f"[NewsAPI] Google/{model} exception: {e}")
        return None


def _try_llm_providers(messages: List[dict]) -> Optional[dict]:
    openrouter_models = get_free_models() if OPENROUTER_KEYS else []
    nvidia_models = list(NVIDIA_FREE_MODELS) if NVIDIA_KEYS else []
    google_models = list(GOOGLE_FREE_MODELS) if GOOGLE_KEYS else []

    openrouter_healthy = model_health.healthy_models(openrouter_models) if openrouter_models else []
    nvidia_healthy = model_health.healthy_models(nvidia_models) if nvidia_models else []
    google_healthy = model_health.healthy_models(google_models) if google_models else []

    print(f"[NewsAPI] Pool: OpenRouter={len(openrouter_healthy)} healthy of {len(openrouter_models)}; NVIDIA={len(nvidia_healthy)} of {len(nvidia_models)}; Google={len(google_healthy)} of {len(google_models)}")

    now = time.time()
    or_all_cooled = bool(openrouter_healthy) and all(model_health.data.get(m, {}).get("cooldown", 0) > now for m in openrouter_healthy)
    nvidia_all_cooled = bool(nvidia_healthy) and all(model_health.data.get(m, {}).get("cooldown", 0) > now for m in nvidia_healthy)
    google_all_cooled = bool(google_healthy) and all(model_health.data.get(m, {}).get("cooldown", 0) > now for m in google_healthy)

    total_attempts = (
        (len(OPENROUTER_KEYS) * len(openrouter_healthy)) +
        (len(NVIDIA_KEYS) * len(nvidia_healthy)) +
        (len(GOOGLE_KEYS) * len(google_healthy))
    )
    if total_attempts == 0:
        print(f"[NewsAPI] No LLM attempts possible (OR cooled={or_all_cooled}, NVIDIA cooled={nvidia_all_cooled}, Google cooled={google_all_cooled})")
        return None

    for key_entry in OPENROUTER_KEYS:
        for model in openrouter_healthy:
            start = time.time()
            text = _call_openrouter(key_entry["key"], model, messages)
            if text:
                model_health.record_success(model)
                print(f"[NewsAPI] Generated article in {time.time() - start:.0f}s via OpenRouter/{model} (key {key_entry['index']})")
                return {"text": text, "provider": "openrouter", "model": model}
            model_health.record_failure(model)

    for key_entry in NVIDIA_KEYS:
        for model in nvidia_healthy:
            start = time.time()
            text = _call_nvidia(key_entry["key"], model, messages)
            if text:
                model_health.record_success(model)
                print(f"[NewsAPI] Generated article in {time.time() - start:.0f}s via NVIDIA/{model} (key {key_entry['index']})")
                return {"text": text, "provider": "nvidia", "model": model}
            model_health.record_failure(model)

    for key_entry in GOOGLE_KEYS:
        for model in google_healthy:
            start = time.time()
            text = _call_google(key_entry["key"], model, messages)
            if text:
                model_health.record_success(model)
                print(f"[NewsAPI] Generated article in {time.time() - start:.0f}s via Google/{model} (key {key_entry['index']})")
                return {"text": text, "provider": "google", "model": model}
            model_health.record_failure(model)

    return None


def generate_article(source_items: List[dict]) -> Optional[dict]:
    source_text = ""
    for item in source_items:
        source_text += f"\n---\nTitle: {item.get('title', '')}\nSource: {item.get('source', '')}\nSummary: {item.get('summary', '')}\n"
        if item.get("scraped_content"):
            source_text += f"Full Article Content: {item['scraped_content'][:2000]}\n"

    title = source_items[0].get("title", "") if source_items else ""
    combined_text = " ".join(
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
        for item in source_items
    ).lower()
    is_crypto = any(kw in combined_text for kw in ["bitcoin", "crypto", "ethereum", "blockchain", "defi", "nft", "token", "coin", "altcoin", "web3"])
    is_ipo = any(kw in combined_text for kw in ["ipo", "initial public", "listing", "offer", "subscription", "grey market", "gmp"])
    is_india = any(kw in combined_text for kw in ["india", "indian", "nse", "bse", "nifty", "sensex", "rbi", "rupee"])

    category_hint = "crypto" if is_crypto else ("ipo" if is_ipo else "stocks")
    market_hint = "India-focused" if is_india else "global"

    user_prompt = f"""Write a premium financial news article based on these sources. This is a {market_hint} {category_hint}-related story for PulseTrends readers.

Sources:
{source_text}

Generate the complete JSON article as specified in the system prompt."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
    llm_response = _try_llm_providers(messages)
    if not llm_response:
        return None

    text = llm_response["text"]
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        return None

    try:
        result = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        print(f"[NewsAPI] JSON parse failed: {e}")
        return None

    final_category = result.get("category") or category_hint
    if final_category == "stocks" and is_india:
        final_category = "india"
    final_category = final_category if final_category in CATEGORY_QUERY_MAP else category_hint

    og_image_url = ""
    og_image_alt = ""
    for item in source_items:
        if item.get("image"):
            og_image_url = item["image"]
            og_image_alt = item.get("title", title)
            break

    images: List[dict] = []
    if og_image_url and _validate_image_url(og_image_url):
        images.append({
            "url": og_image_url,
            "alt": og_image_alt or title,
            "title": (og_image_alt or title)[:80],
            "caption": (og_image_alt or title) + " (Source article image)",
            "attribution": item.get("source", "Source") if isinstance(item, dict) else "Source",
            "category": final_category,
            "source": "og-image",
        })

    if len(images) < 4:
        fetched = fetch_images(result.get("headline", title), count=4 - len(images), category=final_category)
        existing_urls = {i["url"] for i in images}
        for img in fetched:
            if img["url"] not in existing_urls:
                images.append(img)
                if len(images) >= 4:
                    break

    result["images"] = images
    result["category"] = final_category
    result["id"] = f"news-{int(time.time())}-{random.randint(1000, 9999)}"
    result["publishedAt"] = datetime.now(timezone.utc).isoformat()
    if not result.get("headline"):
        result["headline"] = title
    if not result.get("metaDescription"):
        result["metaDescription"] = (result.get("subheadline") or title)[:160]
    return result


def refresh_news():
    print("[NewsAPI] Refreshing news cache...")
    items = fetch_rss()
    items += fetch_newsapi()
    items += fetch_finnhub()
    items = deduplicate(items)
    print(f"[NewsAPI] {len(items)} relevant items after filtering")

    # Scrape full content for top articles
    enriched = []
    for item in items[:24]:
        scraped = scrape_article(item["url"])
        if scraped:
            item["scraped_content"] = scraped.get("content", "")
            if scraped.get("image") and not item.get("image"):
                item["image"] = scraped["image"]
            if scraped.get("author"):
                item["author"] = scraped["author"]
        enriched.append(item)

    print(f"[NewsAPI] {len(enriched)} enriched items, generating articles...")

    new_articles = []
    batch_size = 3
    for i in range(0, min(len(enriched), 18), batch_size):
        batch = enriched[i:i + batch_size]
        article = generate_article(batch)
        if article:
            new_articles.append(article)

    with CACHE_LOCK:
        if new_articles:
            NEWS_CACHE.clear()
            NEWS_CACHE.extend(new_articles)
            save_cached_news(new_articles)
    print(f"[NewsAPI] Cache updated with {len(new_articles)} articles")


@app.route("/api/news")
def get_news():
    with CACHE_LOCK:
        return jsonify(NEWS_CACHE)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "articles": len(NEWS_CACHE)})


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_news, "interval", hours=24, next_run_time=None)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))


def validate_env():
    checks = [
        ("OPENROUTER_API_KEY_1", bool(os.environ.get("OPENROUTER_API_KEY_1"))),
        ("OPENROUTER_API_KEY_2", bool(os.environ.get("OPENROUTER_API_KEY_2"))),
        ("OPENROUTER_API_KEY_3", bool(os.environ.get("OPENROUTER_API_KEY_3"))),
        ("OPENROUTER_API_KEY_4", bool(os.environ.get("OPENROUTER_API_KEY_4"))),
        ("NVIDIA_API_KEY_1", bool(os.environ.get("NVIDIA_API_KEY_1"))),
        ("GOOGLE_AI_API_KEY_1", bool(os.environ.get("GOOGLE_AI_API_KEY_1"))),
        ("GOOGLE_AI_API_KEY_2", bool(os.environ.get("GOOGLE_AI_API_KEY_2"))),
        ("FINNHUB_API_KEY_1", bool(os.environ.get("FINNHUB_API_KEY_1"))),
        ("FINNHUB_API_KEY_2", bool(os.environ.get("FINNHUB_API_KEY_2"))),
        ("FINNHUB_API_KEY_3", bool(os.environ.get("FINNHUB_API_KEY_3"))),
        ("FINNHUB_API_KEY_4", bool(os.environ.get("FINNHUB_API_KEY_4"))),
        ("NEWSAPI_KEY", bool(os.environ.get("NEWSAPI_KEY"))),
        ("UNSPLASH_ACCESS_KEY_1", bool(os.environ.get("UNSPLASH_ACCESS_KEY_1"))),
        ("UNSPLASH_ACCESS_KEY_2", bool(os.environ.get("UNSPLASH_ACCESS_KEY_2"))),
        ("UNSPLASH_ACCESS_KEY_3", bool(os.environ.get("UNSPLASH_ACCESS_KEY_3"))),
    ]
    print("[NewsAPI] Env validation:")
    for name, present in checks:
        print(f"  {name}: {'YES' if present else 'MISSING'}")


if __name__ == "__main__":
    print("[NewsAPI] Initializing...")
    validate_env()
    cached_articles = load_cached_news()
    if cached_articles:
        with CACHE_LOCK:
            NEWS_CACHE.extend(cached_articles)
    refresh_news()
    start_scheduler()
    print("[NewsAPI] Server starting on http://0.0.0.0:5000")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
