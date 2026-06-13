#!/usr/bin/env python3
"""
Daily News Generator for PulseTrends — CONSOLIDATED PIPELINE
=============================================================
Runs once daily and generates 11 articles total:
  - 3 Crypto articles (trending crypto/blockchain keywords)
  - 3 IPO articles (trending IPO/stock-market keywords)
  - 5 Hot-topic articles (general trending topics from across the web)

Pipeline:
  1. Fetch 25+ RSS feeds from news, finance, sports, entertainment sources
  2. Use an LLM to discover & rank 11 trending keywords (3 crypto, 3 IPO, 5 general)
  3. Check existing newsData.ts for duplicate topics
  4. Generate all 11 articles using LLM providers
  5. Fetch Unsplash images for each article
  6. Prepend articles to src/data/newsData.ts (newest first)

Run: python scripts/generate-daily-news.py

Environment variables (GitHub Secrets):
  GROQ_API, MISTRAL_API, GOOGLE_AI_API_KEY_1/2, COHERE_API  — LLM providers
  UNSPLASH_ACCESS_KEY_1/2/3                                   — Unsplash images
"""

import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "data"
NEWS_DATA_FILE = DATA_DIR / "newsData.ts"
CACHE_DIR = REPO_ROOT / "data"
USED_IMAGES_FILE = CACHE_DIR / "used_news_images.json"
MAX_RETRIES = 3
TIMEOUT_SEC = 90

# ── RSS Feed Sources for Trend Discovery ──────────────────────────

TREND_RSS_FEEDS = [
    # Global news
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    # Finance & Markets
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    # Crypto & Tech
    "https://cointelegraph.com/rss",
    "https://coindesk.com/feed",
    # Sports
    "https://feeds.bbci.co.uk/sport/rss.xml",
    "https://www.cricbuzz.com/cricket-feed/news",
    # Entertainment
    "https://variety.com/feed",
    "https://www.hollywoodreporter.com/feed",
    # India-specific
    "https://www.livemint.com/rss/markets",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://timesofindia.indiatimes.com/rssfeeds/1967008.cms",
]

# ── Unsplash image queries per category ───────────────────────────

UNSPLASH_QUERY_MAP = {
    "crypto": [
        "cryptocurrency bitcoin ethereum",
        "blockchain digital assets defi",
        "crypto trading exchange",
        "bitcoin ethereum price chart",
        "digital finance crypto wallet",
        "blockchain technology network",
    ],
    "ipo": [
        "ipo stock market listing",
        "initial public offering trading",
        "wall street trading floor",
        "stock exchange building",
        "investment banking finance",
        "financial documents earnings report",
    ],
    "stocks": [
        "stock market charts data",
        "wall street trading screen",
        "financial charts data analytics",
        "trading desk monitors",
    ],
    "breaking": [
        "breaking news live update",
        "global news event",
        "news conference press",
    ],
    "sports": [
        "sports stadium action",
        "football cricket match",
        "athlete competition sport",
    ],
    "entertainment": [
        "movie premiere red carpet",
        "concert music festival",
        "celebrity event stage",
    ],
    "technology": [
        "ai artificial intelligence tech",
        "robot future technology",
        "computer code screen",
    ],
    "economy": [
        "stock market trading",
        "global economy finance",
        "money business growth",
    ],
    "general": [
        "world news global",
        "people city street",
        "current events today",
    ],
}

# ── Author attribution ────────────────────────────────────────────

AUTHOR_BLOCK = "\n\n---\n\nAuthor: Shiva Sandeep\n\nTelegram: @its_terabyte\n\nWhatsApp:\n\n*Default WhatsApp profile image placeholder*\n\nPublished by PulseTrends\n\n---"

# ── Helpers ───────────────────────────────────────────────────────

def esc(s):
    if s is None:
        return ""
    if isinstance(s, (int, float)):
        return str(s)
    if not isinstance(s, str):
        return str(s)
    return (s
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t"))

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')[:80]

def make_id():
    ts = int(time.time() * 1000)
    r = random.randint(1000, 9999)
    return f"news-{ts}-{r}"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def today_str():
    return datetime.now(timezone.utc).strftime("%B %d, %Y")

# ── Trend Category Detection ──────────────────────────────────────

def detect_trend_category(keyword: str, context: str = "") -> str:
    """Map a keyword to a broad category for Unsplash queries."""
    text = f"{keyword} {context}".lower()
    if any(w in text for w in ["sport", "cricket", "football", "tennis", "olympics", "nba", "match", "tournament", "championship"]):
        return "sports"
    if any(w in text for w in ["movie", "film", "celebrity", "actor", "actress", "concert", "music", "netflix", "entertainment", "award", "oscar", "grammy"]):
        return "entertainment"
    if any(w in text for w in ["ai", "artificial intelligence", "robot", "chatgpt", "openai", "tech", "software", "google", "apple", "microsoft", "meta", "tesla", "spacex", "nasa"]):
        return "technology"
    if any(w in text for w in ["stock", "market", "economy", "inflation", "gdp", "rate", "rbi", "fed", "oil", "gold", "price", "trade", "tariff", "finance", "bank", "budget"]):
        return "economy"
    if any(w in text for w in ["war", "conflict", "attack", "strike", "protest", "election", "president", "political", "government", "policy", "law", "court"]):
        return "breaking"
    if any(w in text for w in ["bitcoin", "crypto", "ethereum", "blockchain", "defi", "altcoin", "nft", "web3"]):
        return "crypto"
    if any(w in text for w in ["ipo", "listing", "sebi", "gmp", "subscription"]):
        return "ipo"
    return "general"

# ── HTTP / Imports ────────────────────────────────────────────────

def _try_imports():
    global requests, xml_etree
    try:
        import requests as req
        requests = req
        import xml.etree.ElementTree as ET
        xml_etree = ET
        return True
    except ImportError:
        print("[!] Missing 'requests' library. Install with: pip install requests")
        return False

# ── RSS Feed Fetching ─────────────────────────────────────────────

def fetch_feeds() -> list[dict]:
    """Fetch headlines from all RSS feeds for trend discovery."""
    items = []
    for url in TREND_RSS_FEEDS:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if resp.status_code != 200:
                continue
            root = xml_etree.fromstring(resp.content)
            # Standard RSS items
            for item in root.iter("item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                pubdate = item.findtext("pubDate", "")
                if title and len(title) > 15:
                    items.append({
                        "title": title.strip(),
                        "url": link.strip(),
                        "summary": desc.strip()[:300] if desc else "",
                        "source": url.split("/")[2] if "//" in url else url,
                        "published": pubdate.strip(),
                    })
            # Atom entries
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                link = link_el.get("href", "") if link_el is not None else ""
                summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", "")
                published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")
                if title and len(title) > 15:
                    items.append({
                        "title": title.strip(),
                        "url": link.strip(),
                        "summary": summary.strip()[:300] if summary else "",
                        "source": url.split("/")[2] if "//" in url else url,
                        "published": published.strip(),
                    })
        except Exception:
            pass
    print(f"[Feeds] Fetched {len(items)} headlines from {len(TREND_RSS_FEEDS)} feeds")
    return items

# ── LLM API Callers ───────────────────────────────────────────────

def call_gemini(prompt, api_keys):
    if not api_keys:
        return None
    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.85, "topP": 0.95, "maxOutputTokens": 8192}
    }
    for key in api_keys:
        if not key:
            continue
        try:
            resp = requests.post(f"{url}?key={key}", json=payload, timeout=TIMEOUT_SEC,
                                 headers={"Content-Type": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text.strip()
            elif resp.status_code == 429:
                print(f"[Gemini] Rate limited, trying next key...")
                time.sleep(2)
                continue
        except Exception as e:
            print(f"[Gemini] Error: {e}")
            time.sleep(1)
    return None

def call_groq(prompt, api_keys):
    if not api_keys:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an expert financial journalist and market analyst. Write in a natural, human-like style. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 4096,
        "top_p": 0.95,
    }
    for key in api_keys:
        if not key:
            continue
        try:
            resp = requests.post(url, json=payload, timeout=TIMEOUT_SEC,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "")
                if text:
                    return text.strip()
            elif resp.status_code == 429:
                print(f"[Groq] Rate limited, retrying...")
                time.sleep(3)
                continue
        except Exception as e:
            print(f"[Groq] Error: {e}")
            time.sleep(1)
    return None

def call_mistral(prompt, api_keys):
    if not api_keys:
        return None
    url = "https://api.mistral.ai/v1/chat/completions"
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": "You are an expert financial journalist and market analyst. Write in a natural, human-like style. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 4096,
        "top_p": 0.95,
    }
    for key in api_keys:
        if not key:
            continue
        try:
            resp = requests.post(url, json=payload, timeout=TIMEOUT_SEC,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "")
                if text:
                    return text.strip()
        except Exception as e:
            print(f"[Mistral] Error: {e}")
            time.sleep(1)
    return None

def call_cohere(prompt, api_keys):
    if not api_keys:
        return None
    url = "https://api.cohere.com/v2/chat"
    payload = {
        "model": "command-r-plus-08-2024",
        "message": prompt,
        "temperature": 0.85,
        "max_tokens": 4096,
        "preamble": "You are an expert financial journalist and market analyst. Write in a natural, human-like style. Return ONLY valid JSON.",
    }
    for key in api_keys:
        if not key:
            continue
        try:
            resp = requests.post(url, json=payload, timeout=TIMEOUT_SEC,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("message", {}).get("content", [{}])[0].get("text", "")
                if text:
                    return text.strip()
        except Exception as e:
            print(f"[Cohere] Error: {e}")
            time.sleep(1)
    return None

def call_llm(prompt):
    """Try all LLM providers in random order. Returns text or None."""
    providers = [
        ("Groq", call_groq, os.environ.get("GROQ_API", "").split(",")),
        ("Mistral", call_mistral, os.environ.get("MISTRAL_API", "").split(",")),
        ("Gemini", call_gemini, [os.environ.get("GOOGLE_AI_API_KEY_1", ""), os.environ.get("GOOGLE_AI_API_KEY_2", "")]),
        ("Cohere", call_cohere, os.environ.get("COHERE_API", "").split(",")),
    ]
    random.shuffle(providers)
    for name, func, keys in providers:
        filtered = [k.strip() for k in (keys if isinstance(keys, (list, tuple)) else [keys]) if k.strip()]
        if not filtered:
            continue
        print(f"[LLM] Trying {name}...")
        result = func(prompt, filtered)
        if result:
            print(f"[LLM] {name} succeeded ({len(result)} chars)")
            return result
    return None

# ── Step 1 & 2: Trend Discovery ───────────────────────────────────

def discover_trending_keywords(feed_items: list[dict]) -> dict:
    """
    Use LLM to analyze news feeds and identify:
    - 3 trending crypto/blockchain keywords
    - 3 trending IPO/stock-market keywords
    - 5 trending general keywords (diverse categories)
    
    Returns dict with keys 'crypto', 'ipo', 'general' each containing a list of keyword dicts.
    """
    random.shuffle(feed_items)
    sample = feed_items[:100]
    
    headlines_text = ""
    for item in sample:
        headlines_text += f"- {item['title']} ({item['source']})\n"
    
    today = today_str()
    
    trend_prompt = f"""You are a real-time trend analyst for PulseTrends, a financial news website. Today is {today}.

Below are {len(sample)} current news headlines from major global sources.

## YOUR TASK
Analyze these headlines and identify EXACTLY 11 trending keywords across three categories:

### CATEGORY 1: CRYPTO (3 keywords)
Trending topics in cryptocurrency, blockchain, Web3, DeFi, Bitcoin, Ethereum, altcoins, NFT, crypto regulation, institutional adoption.
These MUST be genuinely trending in crypto right now.

### CATEGORY 2: IPO (3 keywords)
Trending topics in IPO markets, stock market listings, company filings, SEBI regulations, GMP trends, SME IPOs, global IPOs.
These MUST be genuinely trending in IPO/finance right now.

### CATEGORY 3: GENERAL HOT TOPICS (5 keywords)
The hottest trending topics from across the entire internet. Follow this priority order:
1. Breaking Global News (wars, disasters, major political events)
2. Major Sports Events (World Cup, IPL, Olympics, championships)
3. Entertainment & Celebrity News (movie releases, celebrity events)
4. AI & Technology News (new launches, breakthroughs, regulation)
5. Oil, Gold, Economy & Policy News (market-moving economic news)
6. Viral Internet Trends (memes, viral challenges, cultural moments)

## IMPORTANT RULES
- Keywords MUST change daily — never use fixed topics
- Each keyword must be verifiably trending with clear signals
- NO category mixing — a crypto keyword stays in crypto, IPO stays in IPO
- Keywords across categories must be DISTINCT (no overlap)
- Rank within each category by score (highest first)

## SCORING (1-100)
For each keyword calculate all five scores:
1. Search Demand
2. News Coverage Growth  
3. Social Media Mentions
4. User Engagement Potential
5. Google Discover Potential

## CURRENT HEADLINES
{headlines_text}

## OUTPUT FORMAT
Return ONLY valid JSON, no markdown, no code fences, no commentary:

{{
  "date": "{today}",
  "crypto": [
    {{"rank": 1, "keyword": "crypto keyword", "searchDemand": 92, "newsCoverageGrowth": 88, "socialMentions": 85, "engagementPotential": 90, "googleDiscoverPotential": 87, "overallScore": 88, "context": "Why trending"}},
    {{"rank": 2, ...}},
    {{"rank": 3, ...}}
  ],
  "ipo": [
    {{"rank": 1, "keyword": "ipo keyword", ...}},
    {{"rank": 2, ...}},
    {{"rank": 3, ...}}
  ],
  "general": [
    {{"rank": 1, "keyword": "hot topic", ...}},
    {{"rank": 2, ...}},
    {{"rank": 3, ...}},
    {{"rank": 4, ...}},
    {{"rank": 5, ...}}
  ]
}}"""
    
    print("\n[Trends] Discovering 11 trending keywords via LLM (3 crypto + 3 IPO + 5 general)...")
    result = call_llm(trend_prompt)
    if not result:
        print("[Trends] LLM trend analysis failed")
        return {}
    
    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
        data = json.loads(cleaned)
        result_dict = {}
        for cat in ["crypto", "ipo", "general"]:
            keywords = data.get(cat, [])
            if keywords:
                result_dict[cat] = keywords[:3 if cat != "general" else 5]
                print(f"[Trends] {cat.upper()}: {len(result_dict[cat])} keywords")
                for kw in result_dict[cat]:
                    print(f"  #{kw.get('rank', '?')}: {kw.get('keyword', 'N/A')} (score: {kw.get('overallScore', '?')})")
            else:
                result_dict[cat] = []
                print(f"[Trends] {cat.upper()}: 0 keywords (fallback needed)")
        return result_dict
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[Trends] Failed to parse: {e}")
        print(f"  Raw: {result[:500]}")
        return {}

# ── Step 3: Duplicate Check ───────────────────────────────────────

def load_existing_keywords() -> set:
    """Load all existing headlines, primaryKeywords, and tags from newsData.ts."""
    existing = set()
    if not NEWS_DATA_FILE.exists():
        return existing
    content = NEWS_DATA_FILE.read_text("utf-8")
    
    headline_pattern = re.compile(r'headline:\s*"([^"]*)"')
    for match in headline_pattern.finditer(content):
        existing.add(match.group(1).lower().strip())
    
    kw_pattern = re.compile(r'primaryKeyword:\s*"([^"]*)"')
    for match in kw_pattern.finditer(content):
        existing.add(match.group(1).lower().strip())
    
    tag_pattern = re.compile(r'tags:\s*\[(.*?)\]', re.DOTALL)
    for match in tag_pattern.finditer(content):
        tags_str = match.group(1)
        tag_items = re.findall(r'"([^"]*)"', tags_str)
        for t in tag_items:
            existing.add(t.lower().strip())
    
    print(f"[Dedup] Loaded {len(existing)} existing keywords from newsData.ts")
    return existing

def is_duplicate(keyword: str, existing_keywords: set) -> bool:
    """Check if a keyword overlaps with any existing article content."""
    kw_lower = keyword.lower().strip()
    if kw_lower in existing_keywords:
        return True
    kw_words = set(kw_lower.split())
    for existing in existing_keywords:
        existing_words = set(existing.split())
        overlap = kw_words & existing_words
        if len(overlap) >= 2 and len(overlap) / max(len(kw_words), len(existing_words)) > 0.5:
            return True
    return False

# ── Unsplash Image Fetching ───────────────────────────────────────

def _load_used_image_ids():
    try:
        if USED_IMAGES_FILE.exists():
            with open(USED_IMAGES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return set(data)
    except Exception:
        pass
    return set()

def _save_used_image_ids(ids):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(USED_IMAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(ids), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Unsplash] Save failed: {e}")

def _validate_image_url(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        if resp.status_code == 200 and "image" in resp.headers.get("Content-Type", "").lower():
            return True
        resp = requests.get(url, stream=True, timeout=5)
        return resp.status_code == 200 and "image" in resp.headers.get("Content-Type", "").lower()
    except Exception:
        return False

def fetch_unsplash_images(headline, category="stocks", count=4):
    """Fetch unique images from Unsplash for an article."""
    unsplash_keys = []
    for i in range(1, 4):
        val = os.environ.get(f"UNSPLASH_ACCESS_KEY_{i}")
        if val and val.strip():
            unsplash_keys.append(val.strip())
    if not unsplash_keys:
        return []
    
    cat = category if category in UNSPLASH_QUERY_MAP else "general"
    base_words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', '', headline).split() if len(w) > 3][:3]
    query_pool = list(UNSPLASH_QUERY_MAP.get(cat, UNSPLASH_QUERY_MAP["general"]))
    if base_words:
        query_pool = [" ".join(base_words)] + query_pool
    random.shuffle(query_pool)
    
    used_ids = _load_used_image_ids()
    results = []
    seen_photo_ids = set()
    
    for q in query_pool:
        if len(results) >= count:
            break
        for uk in unsplash_keys:
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
                    if not url or not _validate_image_url(url):
                        continue
                    user = hit.get("user", {}) or {}
                    user_name = user.get("name", "Unsplash")
                    user_link = user.get("links", {}).get("html", "https://unsplash.com")
                    alt_desc = (hit.get("alt_description") or headline).strip()
                    results.append({
                        "url": url,
                        "alt": alt_desc[:120],
                        "title": alt_desc[:80],
                        "caption": f"{alt_desc[:100]} (via Unsplash)",
                        "attribution": f"Photo by {user_name} on Unsplash",
                        "sourceUrl": f"{user_link}?utm_source=pulsetrends&utm_medium=referral",
                        "photoId": photo_id,
                        "category": cat,
                    })
                    seen_photo_ids.add(photo_id)
                    if len(results) >= count:
                        break
                    break
            except Exception:
                continue
    
    if results:
        used_ids.update(r["photoId"] for r in results if "photoId" in r)
        if len(used_ids) > 500:
            used_ids = set(sorted(used_ids)[-500:])
        _save_used_image_ids(used_ids)
        print(f"[Unsplash] Fetched {len(results)} images for '{headline[:50]}...'")
    
    return results

# ── Article Generation (Step 4) ───────────────────────────────────

def generate_article_for_trend(trend: dict, category: str, date_str: str) -> Optional[dict]:
    """Generate a full article for a single trending keyword."""
    keyword = trend.get("keyword", "")
    context = trend.get("context", "")
    
    # Map trend category to PulseTrends category
    category_map = {
        "crypto": "crypto",
        "ipo": "ipo",
        "general": "trending",
        "sports": "sports",
        "entertainment": "entertainment",
        "technology": "technology",
        "economy": "economy",
        "breaking": "breaking",
    }
    mapped_category = category_map.get(category, "trending")
    
    article_prompt = f"""You are an expert journalist writing for PulseTrends (https://pulsetrends.in). Today is {date_str}.

## TOPIC
Write a premium, engaging, click-worthy news article about this trending topic:
- **Trending Keyword:** {keyword}
- **Context:** {context}
- **Category:** {category}

## ARTICLE REQUIREMENTS
- Write in a natural, human-like journalistic style (like Bloomberg, Reuters, CoinDesk)
- Use varied sentence structures, contractions, and natural transitions
- Include specific data, percentages, and concrete details
- DO NOT sound like AI-generated content
- Avoid: "Furthermore,", "Moreover,", "In conclusion,"
- If relevant, include 1-2 analyst/expert quotes (attributed to realistic names)

## ARTICLE STRUCTURE
1. **Headline** — Compelling, clickable, SEO-optimized (50-70 chars)
2. **Subheadline** — One-sentence summary hook
3. **Key Highlights** — 5 bullet points of key facts
4. **Executive Summary** — 2-3 paragraph overview
5. **Detailed Analysis** — Full article with markdown headings (## Section Title)
   For crypto: include price data, market cap, trading volume, on-chain metrics
   For IPO: include subscription data, GMP, financials, valuation
   For general: include what happened, why it matters, key players, reactions
6. **Market Impact** — 3-4 sentences on what this means
7. **Expert Perspective** — Analyst commentary
8. **What Happens Next** — Future outlook and catalysts
9. **Conclusion** — Strong closing paragraph
10. **Author attribution** — Append at the very end: {AUTHOR_BLOCK}

## SEO REQUIREMENTS
- metaDescription: Under 160 characters, keyword-rich
- primaryKeyword: "{keyword}"
- secondaryKeywords: 3-5 related keywords
- tags: 5-8 short tags relevant to the topic
- slug: URL-friendly version of headline
- sentiment: bullish/bearish/neutral based on topic tone
- impact: low/medium/high

## OUTPUT FORMAT
Return ONLY valid JSON. No markdown. No code fences. No commentary.

{{
  "headline": "SEO-optimized clickable headline",
  "subheadline": "One-sentence hook",
  "keyHighlights": ["5 bullet points"],
  "executiveSummary": "2-3 paragraph overview",
  "marketBackground": "Background context",
  "detailedAnalysis": "Full article with markdown headings. Include author attribution at the very end.",
  "expertInsights": "Expert/analyst perspectives",
  "outlook": "What happens next",
  "conclusion": "Strong closing",
  "financialMetrics": {{"tableCaption": "", "headers": [], "rows": []}},
  "risks": ["2-3 risks"],
  "opportunities": ["2-3 opportunities"],
  "sourcesReferenced": ["2-4 source names"],
  "aiAnalysis": null,
  "category": "{mapped_category}",
  "sentiment": "bullish or bearish or neutral",
  "impact": "low or medium or high",
  "relatedCoins": [],
  "relatedStocks": [],
  "relatedEntities": ["Entity 1", "Entity 2"],
  "primaryKeyword": "{keyword}",
  "secondaryKeywords": ["kw1", "kw2", "kw3", "kw4"],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "metaDescription": "Under 160 chars SEO meta description",
  "slug": "url-friendly-slug",
  "focusKeyword": "{keyword}",
  "publishedAt": "{now_iso()}"
}}"""
    
    for attempt in range(MAX_RETRIES):
        print(f"  → Generating '{keyword}' (attempt {attempt+1})...")
        result = call_llm(article_prompt)
        if result:
            try:
                cleaned = result.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
                    cleaned = re.sub(r'\s*```$', '', cleaned)
                article = json.loads(cleaned)
                
                required = ["headline", "detailedAnalysis", "metaDescription"]
                missing = [f for f in required if f not in article]
                if missing:
                    raise ValueError(f"Missing fields: {missing}")
                
                article.setdefault("id", make_id())
                article.setdefault("subheadline", "")
                article.setdefault("keyHighlights", [])
                article.setdefault("executiveSummary", "")
                article.setdefault("marketBackground", "")
                article.setdefault("expertInsights", "")
                article.setdefault("outlook", "")
                article.setdefault("conclusion", "")
                article.setdefault("financialMetrics", {"tableCaption": "", "headers": [], "rows": []})
                article.setdefault("risks", [])
                article.setdefault("opportunities", [])
                article.setdefault("sourcesReferenced", [])
                article.setdefault("aiAnalysis", None)
                article.setdefault("sentiment", "neutral")
                article.setdefault("impact", "medium")
                article.setdefault("relatedCoins", [])
                article.setdefault("relatedStocks", [])
                article.setdefault("relatedEntities", [])
                article.setdefault("secondaryKeywords", [])
                article.setdefault("tags", [])
                article.setdefault("publishedAt", now_iso())
                article.setdefault("slug", slugify(article.get("headline", keyword)))
                article.setdefault("primaryKeyword", keyword)
                article.setdefault("focusKeyword", keyword)
                
                # Ensure author attribution
                da = article.get("detailedAnalysis", "")
                if "Author: Shiva Sandeep" not in da:
                    article["detailedAnalysis"] = da + AUTHOR_BLOCK
                
                # Fetch Unsplash images
                print(f"  → Fetching images for '{article['headline'][:50]}...'")
                img_cat = detect_trend_category(keyword, context)
                # Use mapped_category for unsplash queries if available
                if category in ("crypto",) or img_cat == "crypto":
                    img_cat = "crypto"
                elif category in ("ipo",) or img_cat == "ipo":
                    img_cat = "ipo"
                article_images = fetch_unsplash_images(
                    article.get("headline", keyword),
                    category=img_cat,
                    count=4
                )
                article["images"] = article_images
                print(f"  → {len(article_images)} images attached")
                
                print(f"  ✓ Generated: {article['headline'][:70]}...")
                return article
            except (json.JSONDecodeError, ValueError) as e:
                print(f"  ✗ Parse error (attempt {attempt+1}): {e}")
                time.sleep(2)
        else:
            print(f"  ✗ LLM call failed (attempt {attempt+1})")
            time.sleep(3)
    
    print(f"  ✗ Failed to generate article for '{keyword}'")
    return None

# ── File Writing (Step 6) ─────────────────────────────────────────

def prepend_to_news_data(articles: list[dict]):
    """Prepend articles to the beginning of the newsArticles array in newsData.ts."""
    if not articles:
        print("[Write] No articles to write")
        return
    
    if not NEWS_DATA_FILE.exists():
        print(f"[Write] ERROR: {NEWS_DATA_FILE} does not exist")
        return
    
    content = NEWS_DATA_FILE.read_text("utf-8")
    
    # Find the array declaration
    decl_pattern = "export const newsArticles: NewsArticle[] = ["
    decl_start = content.find(decl_pattern)
    if decl_start == -1:
        print("[Write] ERROR: Could not find newsArticles array declaration")
        return
    
    # The opening bracket is the '[' right after '= '
    eq_pos = content.find("= [", decl_start)
    if eq_pos == -1:
        print("[Write] ERROR: Could not find '= ['")
        return
    # Insert pos right after the '[' (which is at eq_pos+2, so we want eq_pos+3)
    insert_pos = eq_pos + 3
    
    # Build the new article entries
    new_entries = []
    for art in articles:
        new_entries.append(format_article_ts(art))
    
    entries_str = ",\n".join(new_entries)
    
    # Insert new articles right after the opening '[' of the array
    # Use lstrip("\r\n") to only strip newlines, preserving indentation
    remaining = content[insert_pos:]
    if remaining.startswith("\r\n"):
        remaining = remaining[2:]
    elif remaining.startswith("\n"):
        remaining = remaining[1:]
    
    new_content = content[:insert_pos] + "\n" + entries_str + ",\n" + remaining
    
    NEWS_DATA_FILE.write_text(new_content, encoding="utf-8")
    print(f"[Write] Prepended {len(articles)} new articles to {NEWS_DATA_FILE}")

def format_article_ts(art: dict) -> str:
    """Format a single article as TypeScript object literal string."""
    lines = []
    lines.append('  {')
    lines.append(f'    id: "{esc(art.get("id", make_id()))}",')
    lines.append(f'    headline: "{esc(art.get("headline", ""))}",')
    lines.append(f'    subheadline: "{esc(art.get("subheadline", ""))}",')
    
    kh = art.get("keyHighlights", [])
    kh = kh if isinstance(kh, list) else []
    lines.append('    keyHighlights: [' + ', '.join([f'"{esc(k)}"' for k in kh[:8]]) + '],')
    
    lines.append(f'    executiveSummary: "{esc(art.get("executiveSummary", ""))}",')
    lines.append(f'    marketBackground: "{esc(art.get("marketBackground", ""))}",')
    
    da = art.get("detailedAnalysis", "")
    if "Author: Shiva Sandeep" not in da:
        da += AUTHOR_BLOCK
    lines.append(f'    detailedAnalysis: "{esc(da)}",')
    
    # expertInsights might be a dict or list from LLM if it returned an object instead of a string
    ei = art.get("expertInsights", "")
    if ei is None:
        ei = ""
    elif isinstance(ei, (dict, list)):
        ei = json.dumps(ei)
    elif not isinstance(ei, str):
        ei = str(ei)
    lines.append(f'    expertInsights: "{esc(ei)}",')
    
    fm = art.get("financialMetrics", {"tableCaption": "", "headers": [], "rows": []})
    if not isinstance(fm, dict):
        fm = {"tableCaption": "", "headers": [], "rows": []}
    lines.append('    financialMetrics: {')
    lines.append(f'      tableCaption: "{esc(fm.get("tableCaption", ""))}",')
    headers_str = ', '.join([f'"{esc(h)}"' for h in fm.get("headers", [])])
    lines.append(f'      headers: [{headers_str}],')
    rows_lines = []
    for row in fm.get("rows", []):
        if isinstance(row, list):
            cells = ', '.join([f'"{esc(c)}"' for c in row])
            rows_lines.append(f'        [{cells}]')
    if rows_lines:
        rows_joined = ",\n".join(rows_lines)
        lines.append(f'      rows: [\n{rows_joined}\n      ],')
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
    
    ai = art.get("aiAnalysis")
    if ai and isinstance(ai, dict):
        lines.append('    aiAnalysis: {')
        lines.append(f'      bullCase: "{esc(ai.get("bullCase", ""))}",')
        lines.append(f'      bearCase: "{esc(ai.get("bearCase", ""))}",')
        lines.append(f'      neutralCase: "{esc(ai.get("neutralCase", ""))}",')
        lines.append(f'      probabilityWeightedOutlook: "{esc(ai.get("probabilityWeightedOutlook", ""))}",')
        cats = ai.get("potentialCatalysts", [])
        cats = cats if isinstance(cats, list) else []
        lines.append('      potentialCatalysts: [' + ', '.join([f'"{esc(c)}"' for c in cats[:6]]) + '],')
        krs = ai.get("keyRisks", [])
        krs = krs if isinstance(krs, list) else []
        lines.append('      keyRisks: [' + ', '.join([f'"{esc(r)}"' for r in krs[:6]]) + '],')
        lines.append('    },')
    else:
        lines.append('    aiAnalysis: null,')
    
    # Images
    images = art.get("images", [])
    if not isinstance(images, list) or not images:
        lines.append('    images: [],')
    else:
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
            if img.get("photoId"):
                lines.append(f'        photoId: "{esc(img.get("photoId", ""))}",')
            lines.append('      },')
        lines.append('    ],')
    
    lines.append(f'    category: "{esc(art.get("category", "stocks"))}",')
    lines.append(f'    sentiment: "{esc(art.get("sentiment", "neutral"))}",')
    lines.append(f'    impact: "{esc(art.get("impact", "medium"))}",')
    
    rc = art.get("relatedCoins", [])
    rc = rc if isinstance(rc, list) else []
    lines.append('    relatedCoins: [' + ', '.join([f'"{esc(c)}"' for c in rc[:6]]) + '],')
    
    rs = art.get("relatedStocks", [])
    rs = rs if isinstance(rs, list) else []
    lines.append('    relatedStocks: [' + ', '.join([f'"{esc(s)}"' for s in rs[:6]]) + '],')
    
    rel_ents = art.get("relatedEntities", [])
    rel_ents = rel_ents if isinstance(rel_ents, list) else []
    if rel_ents:
        lines.append('    relatedEntities: [' + ', '.join([f'"{esc(e)}"' for e in rel_ents[:8]]) + '],')
    
    lines.append(f'    primaryKeyword: "{esc(art.get("primaryKeyword", ""))}",')
    
    sk = art.get("secondaryKeywords", [])
    sk = sk if isinstance(sk, list) else []
    lines.append('    secondaryKeywords: [' + ', '.join([f'"{esc(k)}"' for k in sk[:5]]) + '],')
    
    tags = art.get("tags", [])
    tags = tags if isinstance(tags, list) else []
    if tags:
        lines.append('    tags: [' + ', '.join([f'"{esc(t)}"' for t in tags[:10]]) + '],')
    
    lines.append(f'    metaDescription: "{esc(art.get("metaDescription", ""))}",')
    lines.append(f'    slug: "{esc(art.get("slug", slugify(art.get("headline", ""))))}",')
    
    fk = art.get("focusKeyword", "") or art.get("primaryKeyword", "")
    lines.append(f'    focusKeyword: "{esc(fk)}",')
    
    lines.append(f'    publishedAt: "{esc(art.get("publishedAt", now_iso()))}",')
    lines.append('  }')
    
    return "\n".join(lines)

# ── Main Pipeline ─────────────────────────────────────────────────

def main():
    if not _try_imports():
        print("[!] Missing 'requests' library. Install with: pip install requests")
        return 1
    
    print("=" * 60)
    print("  PULSETRENDS DAILY NEWS — CONSOLIDATED PIPELINE")
    print(f"  Date: {today_str()}")
    print(f"  UTC:  {now_iso()}")
    print(f"  Target: 11 articles (3 Crypto + 3 IPO + 5 Trending)")
    print("=" * 60)
    
    # Check LLM availability
    available = []
    for name, env_var in [("Groq", "GROQ_API"), ("Mistral", "MISTRAL_API"),
                          ("Gemini", "GOOGLE_AI_API_KEY_1"), ("Cohere", "COHERE_API")]:
        if os.environ.get(env_var, "").strip():
            available.append(name)
    if not available:
        print("[!] No LLM API keys found. Set at least one of: GROQ_API, MISTRAL_API, GOOGLE_AI_API_KEY_1, COHERE_API")
        return 1
    print(f"[API] Available providers: {', '.join(available)}\n")
    
    # ── Step 1: Fetch RSS feeds ──
    print("[Step 1/5] Fetching news feeds for trend analysis...")
    feed_items = fetch_feeds()
    if not feed_items:
        print("[!] No feed items fetched, cannot discover trends")
        return 1
    print(f"  → {len(feed_items)} headlines collected\n")
    
    # ── Step 2: Discover trending keywords ──
    print("[Step 2/5] Discovering trending keywords (3 crypto + 3 IPO + 5 general)...")
    trends = discover_trending_keywords(feed_items)
    if not trends:
        print("[!] Failed to discover trending keywords")
        return 1
    
    # Check we have at least some keywords
    total_found = sum(len(v) for v in trends.values())
    if total_found == 0:
        print("[!] No keywords discovered across any category")
        return 1
    
    print(f"\n  → {total_found} total trending keywords discovered\n")
    
    # ── Step 3: Check for duplicates ──
    print("[Step 3/5] Checking existing articles for duplicates...")
    existing_keywords = load_existing_keywords()
    
    filtered_trends = {"crypto": [], "ipo": [], "general": []}
    total_skipped = 0
    for cat in ["crypto", "ipo", "general"]:
        for t in trends.get(cat, []):
            kw = t.get("keyword", "")
            if is_duplicate(kw, existing_keywords):
                print(f"  ✗ [{cat.upper()}] SKIP: '{kw}' — already covered")
                total_skipped += 1
            else:
                filtered_trends[cat].append(t)
                print(f"  ✓ [{cat.upper()}] '{kw}' — new topic")
    
    print(f"\n  → {total_skipped} skipped, {sum(len(v) for v in filtered_trends.values())} unique topics\n")
    
    total_to_generate = sum(len(v) for v in filtered_trends.values())
    if total_to_generate == 0:
        print("[!] All trending topics are already covered. Nothing to generate.")
        return 0
    
    # ── Step 4: Generate articles ──
    print(f"[Step 4/5] Generating {total_to_generate} articles...")
    new_articles = []
    
    for cat in ["crypto", "ipo", "general"]:
        cat_trends = filtered_trends.get(cat, [])
        if not cat_trends:
            print(f"\n  [{cat.upper()}] No new topics to generate")
            continue
        print(f"\n  [{cat.upper()}] Generating {len(cat_trends)} article(s):")
        for i, trend in enumerate(cat_trends):
            print(f"\n  [{i+1}/{len(cat_trends)}] Topic: {trend.get('keyword', 'N/A')}")
            article = generate_article_for_trend(trend, cat, today_str())
            if article:
                new_articles.append(article)
    
    if not new_articles:
        print("\n[!] No articles were generated")
        return 1
    
    print(f"\n  ✓ Total generated: {len(new_articles)} articles")
    
    # ── Step 5: Prepend to newsData.ts ──
    print("\n[Step 5/5] Prepending articles to newsData.ts...")
    prepend_to_news_data(new_articles)
    
    print("\n" + "=" * 60)
    print("  COMPLETE")
    print(f"  {len(new_articles)} articles generated and written")
    print(f"  Breakdown: {sum(1 for a in new_articles if a.get('category') == 'crypto')} crypto, "
          f"{sum(1 for a in new_articles if a.get('category') == 'ipo')} ipo, "
          f"{sum(1 for a in new_articles if a.get('category') != 'crypto' and a.get('category') != 'ipo')} trending")
    print(f"  Location: src/data/newsData.ts")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
