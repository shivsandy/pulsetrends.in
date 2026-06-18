#!/usr/bin/env python3
"""
PULSETRENDS PREMIUM NEWS GENERATOR
====================================
Generates 10 high-quality, original, Adsense-safe, SEO-optimized news articles daily
that maximize Google Search, Google Discover, AI Overviews, Featured Snippets,
GEO SEO visibility, user engagement, organic CTR, and returning visitors.

Pipeline:
  1. TREND DISCOVERY — Gather trending topics from RSS, Google News, YouTube, Reddit
  2. TREND SCORING — LLM-based scoring across 8 dimensions
  3. TOPIC SELECTION — Pick 10 highest-opportunity topics (no category restrictions)
  4. ARTICLE GENERATION — Full premium articles with SEO/GEO/Discover/EEAT
  5. TRAFFIC SCORING — 5-dimension traffic potential scoring per article
  6. IMAGE OPTIMIZATION — Featured image prompts + SEO metadata
  7. INTERNAL LINKING — Related article suggestions
  8. OUTPUT — Structured JSON + daily archive

Run: python scripts/generate-premium-news.py

Environment variables (see .env.example):
  LLM: ZEN_API_KEY2, GROQ_API, MISTRAL_API, COHERE_API, GOOGLE_AI_API_KEY_1/2, NVIDIA_API_KEY_1
  Media: UNSPLASH_ACCESS_KEY_1/2/3
  Social: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, YOUTUBE_API_KEY
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

# ── Paths ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "premium_news.json"
DAILY_DIR = REPO_ROOT / "artifacts" / "premium-news"

MAX_RETRIES = 3
TIMEOUT_SEC = 120

# ── Import helpers ─────────────────────────────────────────────────────

def _try_imports():
    global requests, feedparser
    try:
        import requests as req
        requests = req
        import feedparser as fp
        feedparser = fp
        return True
    except ImportError:
        print("[!] Missing libraries. Install with:")
        print("    pip install requests feedparser")
        return False

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')[:80]

def make_id():
    ts = int(time.time() * 1000)
    r = random.randint(1000, 9999)
    return f"premium-{ts}-{r}"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def today_str():
    return datetime.now(timezone.utc).strftime("%B %d, %Y")

def today_slug():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 1 — RSS & NEWS FEED FETCHING
# ═══════════════════════════════════════════════════════════════════════

TREND_RSS_FEEDS = [
    # Global News
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
    # India-Specific
    "https://www.livemint.com/rss/markets",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://timesofindia.indiatimes.com/rssfeeds/1967008.cms",
    "https://www.thehindu.com/news/feeder/default.rss",
    # Sports
    "https://feeds.bbci.co.uk/sport/rss.xml",
    "https://www.espn.com/espn/rss/news",
    # Entertainment
    "https://variety.com/feed",
    "https://www.hollywoodreporter.com/feed",
    "https://deadline.com/feed",
    # Science & Health
    "https://www.nature.com/nature.rss",
    "https://www.sciencedaily.com/rss/all.xml",
    # Business & Startups
    "https://techcrunch.com/feed",
    "https://www.wired.com/feed/rss",
    "https://www.theverge.com/rss/index.xml",
]

# Google News RSS by topic — for targeted trend discovery
GOOGLE_DISCOVER_RSS_FEEDS = {
    "Discover US": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FubHdHZ0pTVHlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "Discover Technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FubHdHZ0pTVHlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "Discover Business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FubHdHZ0pTVHlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "Discover Science": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FubHdHZ0pTVHlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "Discover Health": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNR3BwZG1jU0FubHdHZ0pTVHlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "Discover India": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZqY0hNU0FubHdHZ0pTVHlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",
    "Discover Sports": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FubHdHZ0pTVHlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "Discover Entertainment": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5pU0FubHdHZ0pTVHlnQVAB?hl=en-US&gl=US&ceid=US:en",
}

GOOGLE_NEWS_TOPIC_FEEDS = {
    "AI & Technology": "https://news.google.com/rss/search?q=AI+technology+artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
    "Crypto": "https://news.google.com/rss/search?q=cryptocurrency+bitcoin+ethereum+blockchain&hl=en-US&gl=US&ceid=US:en",
    "India Business": "https://news.google.com/rss/search?q=India+business+economy+stock+market+Nifty&hl=en-IN&gl=IN&ceid=IN:en",
    "World News": "https://news.google.com/rss/search?q=world+news+breaking+global&hl=en-US&gl=US&ceid=US:en",
    "IPO & Stocks": "https://news.google.com/rss/search?q=IPO+stock+market+listing+earnings&hl=en-US&gl=US&ceid=US:en",
    "Entertainment": "https://news.google.com/rss/search?q=entertainment+movie+celebrity+music+Oscar&hl=en-US&gl=US&ceid=US:en",
    "Sports": "https://news.google.com/rss/search?q=sports+cricket+football+IPL+NBA&hl=en-US&gl=US&ceid=US:en",
    "Startups": "https://news.google.com/rss/search?q=startup+funding+valuation+venture+capital&hl=en-US&gl=US&ceid=US:en",
    "Science & Health": "https://news.google.com/rss/search?q=science+health+medical+research+breakthrough&hl=en-US&gl=US&ceid=US:en",
    "Education & Policy": "https://news.google.com/rss/search?q=education+government+policy+regulation&hl=en-US&gl=US&ceid=US:en",
}

def fetch_rss_feeds(feeds: list) -> list[dict]:
    """Fetch headlines from multiple RSS feeds."""
    items = []
    for url in feeds:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=15)
            if resp.status_code != 200:
                continue
            parsed = feedparser.parse(resp.content)
            for entry in parsed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = (entry.get("summary") or entry.get("description") or "")[:300]
                published = entry.get("published", "") or entry.get("updated", "") or ""
                source = getattr(entry, "source", None)
                source_name = source.get("title", "") if source else ""
                if not source_name and "//" in url:
                    source_name = url.split("/")[2]
                if title and len(title) > 15:
                    items.append({
                        "title": title,
                        "url": link,
                        "summary": summary.strip(),
                        "source": source_name or url.split("/")[2] if "//" in url else url,
                        "published": published,
                        "feed_url": url,
                    })
        except Exception:
            pass
    return items


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 2 — YOUTUBE TRENDING FETCHER
# ═══════════════════════════════════════════════════════════════════════

def fetch_youtube_trending() -> list[dict]:
    """Fetch trending videos from YouTube Data API v3 (free tier)."""
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        return []
    items = []
    try:
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", developerKey=api_key, cache_discovery=False)
        for region in ["US", "IN", "GB", "CA", "AU"]:
            try:
                request = youtube.videos().list(
                    part="snippet,statistics",
                    chart="mostPopular",
                    regionCode=region,
                    maxResults=10,
                )
                response = request.execute()
                for video in response.get("items", []):
                    snippet = video.get("snippet", {})
                    stats = video.get("statistics", {})
                    title = snippet.get("title", "").strip()
                    channel = snippet.get("channelTitle", "")
                    desc = (snippet.get("description", "") or "")[:300]
                    view_count = stats.get("viewCount", "0")
                    if title and len(title) > 15:
                        items.append({
                            "title": title,
                            "url": f"https://youtube.com/watch?v={video.get('id', '')}",
                            "summary": desc.strip(),
                            "source": f"YouTube/{region}/{channel}",
                            "published": snippet.get("publishedAt", ""),
                            "engagement": f"{view_count} views",
                            "type": "youtube_trending",
                        })
            except Exception:
                continue
    except ImportError:
        print("[YouTube] google-api-python-client not installed. Skipping YouTube trends.")
        print("    Install: pip install google-api-python-client")
    except Exception as e:
        print(f"[YouTube] Error: {e}")
    print(f"[YouTube] Fetched {len(items)} trending videos")
    return items


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 3 — REDDIT TRENDING FETCHER
# ═══════════════════════════════════════════════════════════════════════

SUBREDDITS_TO_WATCH = [
    "wallstreetbets", "cryptocurrency", "CryptoMarkets", "stocks",
    "investing", "technology", "ArtificialIntelligence", "MachineLearning",
    "IndiaInvestments", "IndianStockMarket", "IPO",
    "worldnews", "news", "entertainment", "movies", "gaming",
    "science", "health", "fitness", "sports", "Cricket",
    "startups", "SmallBusiness", "finance",
]

def fetch_reddit_trending() -> list[dict]:
    """Fetch trending posts from Reddit using PRAW (free tier)."""
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return []
    items = []
    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="PulseTrends/1.0 (trend discovery bot)",
        )
        for sub_name in SUBREDDITS_TO_WATCH:
            try:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.hot(limit=5):
                    title = post.title.strip()
                    if title and len(title) > 15:
                        items.append({
                            "title": title,
                            "url": post.url,
                            "summary": (post.selftext or "")[:300],
                            "source": f"Reddit/r/{sub_name}",
                            "published": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                            "engagement": f"{post.score} upvotes, {post.num_comments} comments",
                            "type": "reddit_trending",
                        })
                # Also get rising posts for early trends
                for post in subreddit.rising(limit=3):
                    title = post.title.strip()
                    if title and len(title) > 15:
                        items.append({
                            "title": title,
                            "url": post.url,
                            "summary": (post.selftext or "")[:200],
                            "source": f"Reddit/r/{sub_name}/rising",
                            "published": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                            "engagement": f"{post.score} upvotes, {post.num_comments} comments",
                            "type": "reddit_rising",
                        })
            except Exception:
                continue
    except ImportError:
        print("[Reddit] PRAW not installed. Skipping Reddit trends.")
        print("    Install: pip install praw")
    except Exception as e:
        print(f"[Reddit] Error: {e}")
    print(f"[Reddit] Fetched {len(items)} trending posts")
    return items


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 4 — LLM API CALLERS (Multi-Provider Fallback)
# ═══════════════════════════════════════════════════════════════════════

# Provider order per the prompt's MODEL USAGE POLICY:
# 1. DeepSeek V4 (via Zen API)  2. Gemini 2.5 Flash  3. Gemini Flash Lite
# 4. Groq Free Models  5. Cohere Free Models  6. Mistral Free Models
# 7. NVIDIA Free Models

def call_zen(prompt, api_keys):
    """DeepSeek V4 Flash Free via OpenRouter/Zen API."""
    if not api_keys:
        return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": "deepseek/deepseek-v4-flash:free",
        "messages": [
            {"role": "system", "content": "You are the Chief Content Editor, SEO Engineer, and News Analyst for PulseTrends.in. Return ONLY valid JSON. No markdown fences. No commentary."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 16384,
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
                print(f"  [LLM] Zen rate limited, trying next key...")
                time.sleep(2)
                continue
        except Exception as e:
            print(f"  [LLM] Zen error: {e}")
            time.sleep(1)
    return None


def call_gemini(prompt, api_keys):
    """Try Gemini models in priority order: 2.5 Flash -> 2.0 Flash -> Flash Lite."""
    if not api_keys:
        return None
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.85, "topP": 0.95, "maxOutputTokens": 16384}
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
                    print(f"  [LLM] Gemini/{model} rate limited, trying next key...")
                    time.sleep(2)
                    continue
            except Exception as e:
                print(f"  [LLM] Gemini/{model} error: {e}")
                time.sleep(1)
                continue
    return None


def call_groq(prompt, api_keys):
    if not api_keys:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an expert journalist and content strategist for PulseTrends.in. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 8192,
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
                print(f"  [LLM] Groq rate limited, retrying...")
                time.sleep(3)
                continue
        except Exception as e:
            print(f"  [LLM] Groq error: {e}")
            time.sleep(1)
    return None


def call_mistral(prompt, api_keys):
    if not api_keys:
        return None
    url = "https://api.mistral.ai/v1/chat/completions"
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": "You are an expert journalist and content strategist for PulseTrends.in. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 8192,
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
            print(f"  [LLM] Mistral error: {e}")
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
        "max_tokens": 8192,
        "preamble": "You are an expert journalist and content strategist for PulseTrends.in. Return ONLY valid JSON.",
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
            print(f"  [LLM] Cohere error: {e}")
            time.sleep(1)
    return None


def call_nvidia(prompt, api_keys):
    if not api_keys:
        return None
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    models = [
        "meta/llama-3.1-70b-instruct",
        "mistralai/mistral-large",
        "google/gemma-2-27b-it",
    ]
    for key in api_keys:
        if not key:
            continue
        for model in models:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an expert journalist and content strategist for PulseTrends.in. Return ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.85,
                    "max_tokens": 8192,
                }
                resp = requests.post(url, json=payload, timeout=TIMEOUT_SEC,
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    choice = data.get("choices", [{}])[0]
                    text = choice.get("message", {}).get("content", "")
                    if text:
                        return text.strip()
            except Exception as e:
                print(f"  [LLM] NVIDIA/{model} error: {e}")
                time.sleep(1)
                continue
    return None


def call_llm(prompt, purpose="generation"):
    """Try all LLM providers in priority order per MODEL USAGE POLICY. Returns text or None."""
    providers = [
        ("Zen (DeepSeek V4)", call_zen, [os.environ.get("ZEN_API_KEY2", ""), os.environ.get("ZEN_API_KEY", "")]),
        ("Gemini", call_gemini, [os.environ.get("GOOGLE_AI_API_KEY_1", ""), os.environ.get("GOOGLE_AI_API_KEY_2", "")]),
        ("Groq", call_groq, os.environ.get("GROQ_API", "").split(",") if os.environ.get("GROQ_API") else []),
        ("Mistral", call_mistral, os.environ.get("MISTRAL_API", "").split(",") if os.environ.get("MISTRAL_API") else []),
        ("Cohere", call_cohere, os.environ.get("COHERE_API", "").split(",") if os.environ.get("COHERE_API") else []),
        ("NVIDIA", call_nvidia, [os.environ.get("NVIDIA_API_KEY_1", "")]),
    ]
    for name, func, keys in providers:
        filtered = [k.strip() for k in (keys if isinstance(keys, (list, tuple)) else [keys]) if k.strip()]
        if not filtered:
            continue
        print(f"  [LLM/{purpose}] Trying {name}...")
        result = func(prompt, filtered)
        if result:
            print(f"  [LLM/{purpose}] {name} succeeded ({len(result)} chars)")
            return result
    return None


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 5 — TREND DISCOVERY & SCORING
# ═══════════════════════════════════════════════════════════════════════

def discover_and_score_trends(feed_items: list[dict], yt_items: list[dict], reddit_items: list[dict]) -> list[dict]:
    """
    Use LLM to analyze all trend signals and return EXACTLY 10 scored topics
    ranked by overall opportunity, regardless of category.
    """
    # Prepare a diverse sample of feed items
    random.shuffle(feed_items)
    sample = feed_items[:120]

    # Prepare YouTube and Reddit samples
    yt_sample = yt_items[:20]
    reddit_sample = reddit_items[:30]

    # Build the trend source text
    headlines_text = "=== NEWS FEEDS ===\n"
    for item in sample:
        headlines_text += f"- {item['title']} ({item['source']})\n"

    if yt_sample:
        headlines_text += "\n=== YOUTUBE TRENDING ===\n"
        for item in yt_sample:
            headlines_text += f"- {item['title']} ({item['source']}) [{item.get('engagement', '')}]\n"

    if reddit_sample:
        headlines_text += "\n=== REDDIT TRENDING ===\n"
        for item in reddit_sample:
            headlines_text += f"- {item['title']} ({item['source']}) [{item.get('engagement', '')}]\n"

    today = today_str()

    trend_prompt = f"""You are the Chief Trend Analyst for PulseTrends.in, a financial news platform. Today is {today}.

Below are {len(sample) + len(yt_sample) + len(reddit_sample)} real-time signals from global news feeds, YouTube trending, and Reddit trending discussions.

## YOUR MISSION
Analyze ALL signals and identify the 10 HIGHEST OPPORTUNITY trending topics available RIGHT NOW.

## SCORING CRITERIA (1-100 each)
For every potential topic, calculate:
1. **Search Demand** — How many people are searching for this?
2. **Trending Velocity** — How fast is this topic growing?
3. **News Freshness** — Is this breaking or old news?
4. **Social Engagement** — Are people talking about this?
5. **CTR Potential** — Will people click on this headline?
6. **Discover Potential** — Will Google Discover show this?
7. **Global Interest** — Interest in US/UK/Canada/Australia
8. **India Interest** — Interest in India
9. **Competition Level** — How much existing coverage?
10. **Overall Opportunity** — Weighted composite score

## CATEGORY OPTIONS (NO restrictions)
AI, Technology, India News, World News, Business, Stock Market, IPO, Crypto, Entertainment, Sports, Consumer Trends, Science, Health, Education, Startups, Government Policies

Choose ONLY what's genuinely trending. Do NOT force category balancing.

## IMPORTANT RULES
- Select EXACTLY 10 topics total
- No category mixing within a single topic
- Each must be verifiably trending now
- Rank by overallOpportunity descending
- Include detailed reasoning for selection

## SIGNALS TO ANALYZE
{headlines_text}

## OUTPUT FORMAT
Return ONLY valid JSON. No markdown fences. No commentary.

{{
  "generated_at": "{now_iso()}",
  "date": "{today}",
  "total_signals_analyzed": {len(sample) + len(yt_sample) + len(reddit_sample)},
  "top_trending_topics": [
    {{
      "rank": 1,
      "topic": "Topic headline",
      "category": "Category",
      "searchDemand": 95,
      "trendingVelocity": 90,
      "newsFreshness": 92,
      "socialEngagement": 88,
      "ctrPotential": 93,
      "discoverPotential": 91,
      "globalInterest": 85,
      "indiaInterest": 80,
      "competitionLevel": 45,
      "overallOpportunity": 89,
      "selectionReasoning": "Why this topic was selected"
    }},
    ... (9 more topics)
  ]
}}"""

    print("\n[Trends] Discovering & scoring top 10 trending topics via LLM...")
    result = call_llm(trend_prompt, "trend-discovery")
    if not result:
        print("[Trends] LLM trend analysis failed completely")
        return []
    try:
        cleaned = result.strip()
        # Extract JSON from anywhere in the response (handles code blocks, leading/trailing text)
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group()
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        data = json.loads(cleaned)
        topics = data.get("top_trending_topics", [])
        if topics:
            print(f"\n[Trends] ✓ Selected {len(topics)} trending topics:")
            for t in topics[:10]:
                print(f"  #{t.get('rank', '?')}: [{t.get('category', '?')}] {t.get('topic', 'N/A')} (Score: {t.get('overallOpportunity', '?')})")
            return topics[:10]
        else:
            print("[Trends] No topics in response")
            return []
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[Trends] Failed to parse LLM response: {e}")
        print(f"  Raw (first 500): {result[:500]}")
        return []


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 6 — EVERGREEN BOOST CHECK
# ═══════════════════════════════════════════════════════════════════════

EVERGREEN_TOPICS = [
    {
        "topic": "What Is Artificial Intelligence? A Beginner's Guide to AI in 2026",
        "category": "AI",
        "context": "Explainer guide covering AI fundamentals, types of AI, real-world applications, and future trends in 2026. Target beginners and general audience.",
        "search_volume_estimate": 92,
        "evergreen_score": 95,
    },
    {
        "topic": "How to Invest in IPO: Complete Guide for Indian Investors 2026",
        "category": "IPO",
        "context": "Step-by-step guide on investing in Indian IPOs: understanding DRHP, GMP, allotment process, listing strategies, and SEBI regulations for 2026.",
        "search_volume_estimate": 90,
        "evergreen_score": 94,
    },
    {
        "topic": "Crypto Trading for Beginners: Complete Guide to Cryptocurrency in 2026",
        "category": "Crypto",
        "context": "Beginner-friendly guide covering cryptocurrency basics, how to buy/sell, exchanges, wallet setup, risks, and opportunities in 2026.",
        "search_volume_estimate": 88,
        "evergreen_score": 93,
    },
    {
        "topic": "Best Mutual Funds to Invest in India 2026: Top Performing Funds",
        "category": "Stock Market",
        "context": "Curated list of best-performing mutual funds in India for 2026 across categories: large-cap, mid-cap, small-cap, ELSS, and debt funds with returns data.",
        "search_volume_estimate": 91,
        "evergreen_score": 92,
    },
    {
        "topic": "How to File Income Tax Returns (ITR) in India 2026: Complete Guide",
        "category": "India News",
        "context": "Complete step-by-step guide on filing ITR in India for FY 2025-26: documents needed, online process, deductions, deadlines, and common mistakes.",
        "search_volume_estimate": 94,
        "evergreen_score": 96,
    },
    {
        "topic": "Stock Market Basics: Complete Guide for Beginners in 2026",
        "category": "Stock Market",
        "context": "Comprehensive beginner's guide to stock market investing: how the market works, types of orders, fundamental vs technical analysis, risk management.",
        "search_volume_estimate": 89,
        "evergreen_score": 93,
    },
    {
        "topic": "Top 10 Cryptocurrencies to Watch in 2026: Analysis and Predictions",
        "category": "Crypto",
        "context": "Analysis of top cryptocurrencies for 2026 including Bitcoin, Ethereum, Solana, and emerging altcoins. Price predictions, technology analysis, and risk assessment.",
        "search_volume_estimate": 87,
        "evergreen_score": 88,
    },
    {
        "topic": "How to Start a Business in India 2026: Complete Registration Guide",
        "category": "Startups",
        "context": "Complete guide on starting a business in India: company registration, GST, MSME registration, funding options, compliance requirements for 2026.",
        "search_volume_estimate": 86,
        "evergreen_score": 91,
    },
]


def check_evergreen_boost(trending_topics: list[dict]) -> list[dict]:
    """
    If trending opportunities are weak (avg score < 65), replace up to 2 articles
    with evergreen high-traffic content.
    """
    if not trending_topics:
        print("[Evergreen] No trending topics found — using 2 evergreen replacements")
        return trending_topics + random.sample(EVERGREEN_TOPICS, min(2, len(EVERGREEN_TOPICS)))

    avg_score = sum(t.get("overallOpportunity", 0) for t in trending_topics) / len(trending_topics)
    print(f"[Evergreen] Average trend score: {avg_score:.1f}/100")

    if avg_score < 65:
        replace_count = min(2, len(trending_topics))
        print(f"[Evergreen] Low trend score — replacing {replace_count} topics with evergreen content")
        trending_topics = trending_topics[:-replace_count] if replace_count > 0 else trending_topics
        selected_evergreen = random.sample(EVERGREEN_TOPICS, min(replace_count, len(EVERGREEN_TOPICS)))
        for eg in selected_evergreen:
            trending_topics.append({
                "rank": len(trending_topics) + 1,
                "topic": eg["topic"],
                "category": eg["category"],
                "overallOpportunity": eg["evergreen_score"],
                "searchDemand": eg["search_volume_estimate"],
                "trendingVelocity": 70,
                "newsFreshness": 85,
                "socialEngagement": 75,
                "ctrPotential": 88,
                "discoverPotential": 80,
                "globalInterest": 75,
                "indiaInterest": 85,
                "competitionLevel": 60,
                "selectionReasoning": eg["context"][:200],
                "_evergreen": True,
            })
        print(f"[Evergreen] Added {len(selected_evergreen)} evergreen topics")
    else:
        print("[Evergreen] Trend scores strong — no evergreen replacement needed")

    return trending_topics


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 7 — ARTICLE GENERATION (Full Premium)
# ═══════════════════════════════════════════════════════════════════════

def generate_premium_article(topic: dict, date_str: str) -> Optional[dict]:
    """Generate a single premium article with full SEO/GEO/Discover/EEAT treatment."""

    topic_name = topic.get("topic", "")
    category = topic.get("category", "Trending")
    context = topic.get("selectionReasoning", topic.get("context", ""))
    is_evergreen = topic.get("_evergreen", False)

    article_prompt = f"""You are the Chief Content Editor, SEO Engineer, GEO Engineer, Google Discover Strategist, and News Analyst for PulseTrends.in (https://pulsetrends.in). Today is {date_str}.

## TOPIC
{'- [EVERGREEN CONTENT]' if is_evergreen else '- [TRENDING NEWS]'}
- **Topic:** {topic_name}
- **Context:** {context}
- **Category:** {category}

## MISSION
Write 1 premium, original, Adsense-safe, SEO-optimized news article that maximizes Google Search traffic, Google Discover traffic, AI Overviews visibility, Featured Snippets, GEO SEO visibility, and user engagement.

## ABSOLUTE RULES
- NEVER copy content. Extract facts only. Rewrite completely.
- Create unique newsroom-quality content written by a professional journalist.
- Avoid AI-sounding language, generic filler, keyword stuffing, plagiarism, duplicate content.
- Every article MUST provide: New context | Analysis | Background | Impact | Future outlook

## ARTICLE STRUCTURE
Write the article with these sections (natural flow, not robotic):

### H1 Headline
Clickable, SEO-optimized, Google Discover-friendly. NOT clickbait, NOT sensational.
Good examples:
- "Why Nvidia's Latest AI Move Is Getting Attention"
- "Bitcoin Traders Are Watching This Critical Level"
- "Google Launches Major Gemini Upgrade"
- "India Announces New Digital Initiative"

### Summary
1-2 paragraph overview that can be used for AI Overviews and Featured Snippets.

### Key Takeaways
5 bullet points of the most important facts.

### Introduction
Hook the reader immediately with what's happening and why it matters.

### Main Story
The full story with verified facts, data points, and context. 300-500 words.

### Background
Historical context, industry background, what led to this moment.

### Expert Analysis
Analyst perspectives, industry expert commentary (attributed to realistic, verifiable names).

### Market Impact
How this affects markets, investors, consumers, or the industry.

### Industry Impact
Broader implications for the industry sector.

### Why It Matters
Connect the story to readers' lives, investments, or interests.

### What Happens Next
Future outlook, catalysts to watch, potential scenarios.

### Conclusion
Strong closing that reinforces the key message.

### FAQ Section
5 frequently asked questions with concise answers. (Will be used for FAQPage schema.)

## SEO PACKAGE

### SEO Title: 50-60 chars, includes primary keyword
### Meta Title: 50-60 chars
### Meta Description: Under 160 chars, keyword-rich, compelling
### URL Slug: lowercase, hyphenated
### Primary Keyword: Main target keyword
### Secondary Keywords: 3-5 related keywords
### Long Tail Keywords: 3-5 long-tail phrases
### OpenGraph Title: Compelling social share title
### OpenGraph Description: Social share description
### Twitter Title: X/Twitter optimized title
### Twitter Description: X/Twitter optimized description
### Suggested Tags: 5-8 short tags
### Suggested Category: {category}

## GOOGLE DISCOVER OPTIMIZATION
- Headline must be highly clickable WITHOUT being clickbait
- Follow Google Discover guidelines
- Avoid misleading headlines
- Avoid sensationalism

"Good examples:
Why Nvidia's Latest AI Move Is Getting Attention
Bitcoin Traders Are Watching This Critical Level
Google Launches Major Gemini Upgrade
India Announces New Digital Initiative
OpenAI's New Update Could Change AI Adoption"

## AI OVERVIEW OPTIMIZATION
- Answer the topic question clearly in the summary
- Use concise summaries that AI can extract
- Use entity-rich language
- Include facts and context
- Use bullet points where useful

## ENTITY SEO
Extract and naturally mention these entities where relevant:
- People (founders, CEOs, analysts, policymakers)
- Companies (relevant organizations)
- Countries (geographic context)
- Products (specific products/services)
- Technologies (relevant tech)
- Events (specific events)
- Organizations (regulatory bodies, institutions)

## GEO SEO (Generative Engine Optimization)
Optimize for India, United States, United Kingdom, Canada, and Australia.
Include location-relevant context when applicable.
Deep knowledge signals for AI citations.

## EEAT OPTIMIZATION
Demonstrate: Experience, Expertise, Authoritativeness, Trustworthiness
- Verified facts only
- Reliable sources cited
- Balanced viewpoints
- Transparent analysis
- No financial guarantees or misleading claims

## ADSENSE COMPLIANCE
STRICTLY AVOID: Adult content, gambling, hate speech, violence promotion, medical misinformation, financial guarantees, misleading claims, fake news.

## IMAGE OPTIMIZATION
Generate:
- featuredImagePrompt: Detailed prompt for AI image generation (unique, topic-relevant, high quality)
- imageAltText: Descriptive alt text including primary keyword
- imageCaption: Engaging caption
- imageSeoTitle: Image SEO title

## TRAFFIC SCORING
For this article, calculate realistic scores (0-100):
- searchTrafficScore: Search traffic potential
- discoverPotentialScore: Google Discover potential
- ctrPotentialScore: Click-through rate potential
- viralityScore: Social sharing/viral potential
- competitionScore: Competition level (lower = better opportunity)
- overallOpportunityScore: Weighted composite

Also provide: scoringReasoning — 1-sentence explaining the scores.

## INTERNAL LINKING
Suggest 3-5 related articles or pages on PulseTrends.in:
- relatedInternalLinks: ["/news/related-article-slug", "/ipo-analysis/related-ipo"]

## OUTPUT FORMAT
Return ONLY valid JSON. No markdown. No code fences. No commentary.

{{
  "headline": "H1 Headline",
  "seo_title": "SEO title 50-60 chars",
  "meta_title": "Meta title",
  "meta_description": "Under 160 chars",
  "slug": "url-friendly-slug",
  "primary_keyword": "main keyword",
  "secondary_keywords": ["kw1", "kw2", "kw3", "kw4"],
  "long_tail_keywords": ["phrase 1", "phrase 2", "phrase 3"],
  "og_title": "OpenGraph title",
  "og_description": "OpenGraph description",
  "twitter_title": "Twitter title",
  "twitter_description": "Twitter description",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "category": "{category}",
  "summary": "1-2 paragraph summary for AI Overviews",
  "key_takeaways": ["5 bullet points"],
  "introduction": "Hook paragraph",
  "main_story": "Full story content with details, facts, data",
  "background": "Historical and industry context",
  "expert_analysis": "Analyst perspectives with attributed quotes",
  "market_impact": "Market effects and implications",
  "industry_impact": "Industry-wide implications",
  "why_it_matters": "Reader relevance",
  "what_happens_next": "Future outlook and catalysts",
  "conclusion": "Strong closing paragraph",
  "faq": [
    {{"question": "Question 1?", "answer": "Answer 1"}},
    {{"question": "Question 2?", "answer": "Answer 2"}},
    {{"question": "Question 3?", "answer": "Answer 3"}},
    {{"question": "Question 4?", "answer": "Answer 4"}},
    {{"question": "Question 5?", "answer": "Answer 5"}}
  ],
  "entities_mentioned": ["Entity 1", "Entity 2", "Entity 3"],
  "sources_referenced": ["Source 1", "Source 2", "Source 3"],
  "geo_regions": ["India", "United States", "United Kingdom", "Canada", "Australia"],
  "searchTrafficScore": 85,
  "discoverPotentialScore": 82,
  "ctrPotentialScore": 88,
  "viralityScore": 75,
  "competitionScore": 45,
  "overallOpportunityScore": 83,
  "scoringReasoning": "Brief explanation of scores",
  "featuredImagePrompt": "Detailed image generation prompt",
  "imageAltText": "SEO alt text for image",
  "imageCaption": "Image caption",
  "imageSeoTitle": "Image SEO title",
  "canonical_url": "https://pulsetrends.in/news/{slug}",
  "relatedInternalLinks": ["/news/suggested-article", "/ipo-analysis/suggested-ipo"],
  "publishedAt": "{now_iso()}"
}}"""

    for attempt in range(MAX_RETRIES):
        print(f"  → Generating '{topic_name[:60]}...' (attempt {attempt+1}/{MAX_RETRIES})")
        result = call_llm(article_prompt, "article-generation")
        if result:
            try:
                cleaned = result.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
                    cleaned = re.sub(r'\s*```$', '', cleaned)
                # Extract JSON from anywhere in the response for robustness
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    cleaned = json_match.group()
                article = json.loads(cleaned)
                required = ["headline", "summary", "main_story"]
                missing = [f for f in required if f not in article]
                if missing:
                    print(f"  ✗ Missing fields: {missing}")
                    continue
                article["id"] = make_id()
                article["topic_rank"] = topic.get("rank", 0)
                article["is_evergreen"] = is_evergreen
                article.setdefault("seo_title", article.get("headline", ""))
                article.setdefault("meta_description", (article.get("summary", "") or "")[:160])
                article.setdefault("slug", slugify(article.get("headline", "")))
                article.setdefault("tags", [])
                article.setdefault("primary_keyword", topic_name)
                article.setdefault("secondary_keywords", [])
                article.setdefault("faq", [])
                article.setdefault("entities_mentioned", [])
                article.setdefault("sources_referenced", [])
                article.setdefault("geo_regions", ["India", "United States", "United Kingdom", "Canada", "Australia"])
                article.setdefault("key_takeaways", [])
                article.setdefault("publishedAt", now_iso())

                # Normalize fields for spec compliance
                slug_val = article.get("slug", slugify(article.get("headline", "")))
                article.setdefault("canonical_url", f"https://pulsetrends.in/news/{slug_val}")

                # Build content field: concatenation of all sections for downstream compatibility
                content_parts = []
                for sec_key in ["summary", "introduction", "main_story", "background", "expert_analysis", "market_impact", "industry_impact", "why_it_matters", "what_happens_next", "conclusion"]:
                    sec_val = article.get(sec_key, "")
                    if sec_val:
                        content_parts.append(sec_val)
                article["content"] = "\n\n".join(content_parts)

                # Build keywords array
                kw = article.get("primary_keyword", "")
                sk = article.get("secondary_keywords", [])
                lt = article.get("long_tail_keywords", [])
                article["keywords"] = [kw] + sk + lt if kw else sk + lt

                # Build traffic_scores object
                article["traffic_scores"] = {
                    "searchTrafficScore": article.get("searchTrafficScore", 0),
                    "discoverPotentialScore": article.get("discoverPotentialScore", 0),
                    "ctrPotentialScore": article.get("ctrPotentialScore", 0),
                    "viralityScore": article.get("viralityScore", 0),
                    "competitionScore": article.get("competitionScore", 0),
                    "overallOpportunityScore": article.get("overallOpportunityScore", 0),
                }

                print(f"  ✓ Generated: {article['headline'][:70]}...")
                return article
            except (json.JSONDecodeError, ValueError) as e:
                print(f"  ✗ Parse error (attempt {attempt+1}): {e}")
                time.sleep(2)
        else:
            print(f"  ✗ LLM call failed (attempt {attempt+1})")
            time.sleep(3)

    print(f"  ✗ Failed to generate article for '{topic_name}'")
    return None


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 8 — OUTPUT & ARCHIVING
# ═══════════════════════════════════════════════════════════════════════

def save_output(articles: list[dict], top_topics: list[dict]):
    """Save the generated articles to the output JSON file and archive."""
    if not articles:
        print("[Output] No articles to save")
        return False

    output = {
        "generated_at": now_iso(),
        "date": today_str(),
        "total_articles": len(articles),
        "top_trending_topics": top_topics,
        "articles": articles,
    }

    # Save to main output
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"[Output] ✓ Saved {len(articles)} articles to {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB)")
    except Exception as e:
        print(f"[Output] ✗ Failed to save: {e}")
        return False

    # Archive to daily file
    try:
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        daily_path = DAILY_DIR / f"{today_slug()}.json"
        with open(daily_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"[Output] ✓ Archived to {daily_path}")
    except Exception as e:
        print(f"[Output] ⚠ Archive failed: {e}")

    return True


# ═══════════════════════════════════════════════════════════════════════
#  SECTION 9 — MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════

def main() -> int:
    if not _try_imports():
        return 1

    print("=" * 70)
    print("  PULSETRENDS PREMIUM NEWS GENERATOR")
    print(f"  Date: {today_str()}")
    print(f"  UTC:  {now_iso()}")
    print(f"  Target: 10 premium articles (highest traffic opportunities)")
    print("=" * 70)

    # ── Check LLM availability ──
    available_providers = []
    if os.environ.get("ZEN_API_KEY2", "") or os.environ.get("ZEN_API_KEY", ""):
        available_providers.append("Zen (DeepSeek V4)")
    if os.environ.get("GOOGLE_AI_API_KEY_1", ""):
        available_providers.append("Gemini")
    if os.environ.get("GROQ_API", ""):
        available_providers.append("Groq")
    if os.environ.get("MISTRAL_API", ""):
        available_providers.append("Mistral")
    if os.environ.get("COHERE_API", ""):
        available_providers.append("Cohere")
    if os.environ.get("NVIDIA_API_KEY_1", ""):
        available_providers.append("NVIDIA")

    if not available_providers:
        print("[!] No LLM API keys found. Set at least one of:")
        print("    ZEN_API_KEY2, GOOGLE_AI_API_KEY_1, GROQ_API, MISTRAL_API, COHERE_API, NVIDIA_API_KEY_1")
        return 1
    print(f"[API] Available LLM providers: {', '.join(available_providers)}\n")

    # ── Step 1: Trend Discovery ──
    print("\n[Step 1/5] Gathering trend signals from multiple sources...")

    # RSS feeds (parallel-like via simple sequential)
    print("  → Fetching RSS feeds...")
    feed_items = fetch_rss_feeds(TREND_RSS_FEEDS)
    print(f"    RSS feeds: {len(feed_items)} headlines")

    # Google News topic feeds
    print("  → Fetching Google News topic feeds...")
    topic_feeds = fetch_rss_feeds(list(GOOGLE_NEWS_TOPIC_FEEDS.values()))
    feed_items.extend(topic_feeds)
    print(f"    Google News topics: {len(topic_feeds)} headlines")

    # Google Discover RSS feeds
    print("  → Fetching Google Discover topic feeds...")
    discover_feeds = fetch_rss_feeds(list(GOOGLE_DISCOVER_RSS_FEEDS.values()))
    feed_items.extend(discover_feeds)
    print(f"    Google Discover feeds: {len(discover_feeds)} headlines")

    # YouTube trending
    print("  → Fetching YouTube trending...")
    yt_items = fetch_youtube_trending()

    # Reddit trending
    print("  → Fetching Reddit trending...")
    reddit_items = fetch_reddit_trending()

    total_signals = len(feed_items) + len(yt_items) + len(reddit_items)
    print(f"\n  ✓ Total signals collected: {total_signals}")

    if total_signals < 20:
        print("[!] Very few signals collected. Proceeding with available data anyway.")

    # ── Step 2: Trend Scoring & Selection ──
    print("\n[Step 2/5] Scoring trends and selecting top 10 opportunities...")
    top_topics = discover_and_score_trends(feed_items, yt_items, reddit_items)

    if not top_topics:
        print("[!] No topics identified. Cannot generate articles.")
        return 1

    # ── Step 3: Evergreen Boost Check ──
    print("\n[Step 3/5] Checking for evergreen boost opportunity...")
    top_topics = check_evergreen_boost(top_topics)
    top_topics = top_topics[:10]

    print(f"\n  ✓ Final topic selection:")
    for t in top_topics:
        eg = " [EVERGREEN]" if t.get("_evergreen") else ""
        print(f"    #{t.get('rank', '?')}: [{t.get('category', '?')}] {t.get('topic', 'N/A')} (Score: {t.get('overallOpportunity', '?')}){eg}")

    # ── Step 4: Article Generation ──
    print(f"\n[Step 4/5] Generating {len(top_topics)} premium articles...")
    articles = []
    for i, topic in enumerate(top_topics):
        print(f"\n  [{i+1}/{len(top_topics)}] Generating article...")
        article = generate_premium_article(topic, today_str())
        if article:
            articles.append(article)
            print(f"  ✓ Article {i+1} complete")
        else:
            print(f"  ✗ Failed to generate article {i+1}")

    if not articles:
        print("\n[!] No articles were generated successfully")
        return 1

    print(f"\n  ✓ Generated {len(articles)}/{len(top_topics)} articles successfully")

    # ── Step 5: Output ──
    print(f"\n[Step 5/5] Saving output...")
    if save_output(articles, top_topics):
        # Print summary
        print("\n" + "=" * 70)
        print("  GENERATION COMPLETE")
        print(f"  {len(articles)} premium articles generated")
        for a in articles:
            print(f"    ✓ [{a.get('category', '?')}] {a['headline'][:70]}...")
        print(f"  Output: {OUTPUT_FILE}")
        print(f"  Cost: Free models used where possible")
        print("=" * 70)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
