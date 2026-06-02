import atexit
import json
import os
import random
import re
import threading
import time
from datetime import datetime, timezone
from typing import List, Optional

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

NEWS_CACHE: List[dict] = []
CACHE_LOCK = threading.Lock()

OPENROUTER_KEYS = []
for i in range(1, 5):
    val = os.environ.get(f"OPENROUTER_API_KEY_{i}")
    if val:
        OPENROUTER_KEYS.append({"key": val, "index": i})

NVIDIA_KEYS = []
for i in range(1, 3):
    val = os.environ.get(f"NVIDIA_API_KEY_{i}")
    if val:
        NVIDIA_KEYS.append({"key": val, "index": i})

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
UNSPLASH_KEYS = []
for i in range(1, 4):
    val = os.environ.get(f"UNSPLASH_ACCESS_KEY_{i}")
    if val:
        UNSPLASH_KEYS.append(val)


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

FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-32b:free",
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-chat:free",
    "microsoft/phi-4:free",
]


def fetch_rss_news() -> List[dict]:
    items = []
    rss_urls = [
        "https://news.google.com/rss/search?q=cryptocurrency+bitcoin&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=IPO+stock+market&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=crypto+news&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=stock+market+news&hl=en-US&gl=US&ceid=US:en",
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://cointelegraph.com/rss",
        "https://coindesk.com/feed",
        "https://cryptonews.com/rss.xml",
        "https://finance.yahoo.com/news/rss/index",
        "https://www.investing.com/rss/news.rss",
        "https://www.investing.com/rss/market_overview.rss",
    ]
    for url in rss_urls:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if resp.status_code != 200:
                continue
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom", "rss": ""}
            for item in root.iter("item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                pubdate = item.findtext("pubDate", "")
                if title and len(title) > 20:
                    items.append({
                        "title": title.strip(),
                        "url": link.strip(),
                        "summary": desc.strip()[:300] if desc else "",
                        "published": pubdate.strip(),
                        "source": url,
                    })
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                link = link_el.get("href", "") if link_el is not None else ""
                summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", "")
                published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")
                if title and len(title) > 20:
                    items.append({
                        "title": title.strip(),
                        "url": link.strip(),
                        "summary": summary.strip()[:300] if summary else "",
                        "published": published.strip(),
                        "source": url.split("/")[2] if "//" in url else url,
                    })
        except Exception:
            pass
    print(f"[NewsAPI] RSS: {len(items)} raw items")
    return items


def fetch_newsapi() -> List[dict]:
    if not NEWSAPI_KEY:
        return []
    items = []
    queries = ["cryptocurrency", "bitcoin", "IPO", "stock market", "crypto", "investing"]
    for q in queries:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={"q": q, "pageSize": 10, "language": "en", "sortBy": "popularity", "apiKey": NEWSAPI_KEY},
                timeout=15,
            )
            if resp.status_code == 200:
                for article in resp.json().get("articles", []):
                    title = (article.get("title") or "").strip()
                    if title and len(title) > 20:
                        items.append({
                            "title": title,
                            "url": article.get("url", ""),
                            "summary": (article.get("description") or "")[:300],
                            "published": article.get("publishedAt", ""),
                            "source": article.get("source", {}).get("name", "newsapi"),
                        })
        except Exception:
            pass
    print(f"[NewsAPI] NewsAPI: {len(items)} items")
    return items


def deduplicate(items: List[dict]) -> List[dict]:
    seen_titles = set()
    result = []
    for item in items:
        title_lower = item["title"].lower().strip()
        if any(s in title_lower for s in ["trump", "election", "sports", "weather", "celebrity"]):
            continue
        is_dup = False
        for seen in seen_titles:
            from difflib import SequenceMatcher
            if SequenceMatcher(None, title_lower, seen).ratio() > 0.7:
                is_dup = True
                break
        if not is_dup:
            seen_titles.add(title_lower)
            result.append(item)
    return result


def fetch_image_for_news(title: str) -> dict:
    keywords = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    words = [w for w in keywords.split() if len(w) > 3][:5]
    query = " ".join(words) if words else "business finance"
    for uk in UNSPLASH_KEYS:
        try:
            resp = requests.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": 3, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {uk}"},
                timeout=10,
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    r = results[0]
                    return {
                        "image": r["urls"]["regular"],
                        "imageAlt": r.get("alt_description") or title,
                        "imageAttribution": f"Photo by {r['user']['name']} on Unsplash",
                    }
        except Exception:
            pass
    return {"image": "", "imageAlt": title, "imageAttribution": ""}


def generate_article(item: dict) -> Optional[dict]:
    title = item["title"]
    summary = item["summary"]

    system_prompt = """You are a senior financial journalist and SEO content writer for PulseTrends.

Your task is to create a completely original, human-like article using the provided structured data, research, news sources, and company information.

IMPORTANT RULES:
* Never rewrite or paraphrase source articles.
* Do not copy sentences from any source.
* Synthesize information from multiple sources.
* Add original analysis, context, comparisons, risks, and insights.
* Write as an experienced analyst, not a news aggregator.
* Use natural human writing.
* Avoid AI-sounding phrases.
* Provide balanced analysis.
* Do not make investment recommendations.
* Focus on value, education, and insights.
* Optimize for SEO naturally.
* Use clear headings and subheadings.
* Write in a professional editorial tone.

OUTPUT FORMAT:
Return ONLY a valid JSON object with these fields:
{
  "title": "SEO-optimized title",
  "metaDescription": "Compelling meta description under 160 chars",
  "content": "Full article in clean Markdown format following the structure below",
  "category": "crypto or ipo or stocks",
  "sentiment": "bullish or bearish or neutral",
  "impact": "high or medium or low",
  "relatedCoins": ["BTC", "ETH"],
  "relatedStocks": ["AAPL"]
}

ARTICLE STRUCTURE for the content field:
# Title
## Quick Summary
## What Happened?
## Key Facts (bullet points)
## Background & Context
## Industry Context
## Strengths
## Risks & Concerns
## AI Analysis
### Bull Case
### Bear Case
## Historical Comparison
## What Investors Should Watch
## Final Verdict
## FAQs (5-10 Q&A pairs)

WRITING REQUIREMENTS: Minimum 1200 words. Maximum 2500 words. Use short paragraphs, tables where useful, bullet points when appropriate. Include relevant statistics and metrics when available. Avoid keyword stuffing. Make the article feel written by a professional analyst. Ensure every section provides unique value beyond the original sources."""

    user_prompt = f"""Write a premium SEO article based on this news:

Title: {title}
Summary: {summary}

Generate the article following the strict JSON output format."""

    provider_models = []
    for key_entry in OPENROUTER_KEYS:
        provider_models.append(("openrouter", key_entry))
    for key_entry in NVIDIA_KEYS:
        provider_models.append(("nvidia", key_entry))

    random.shuffle(provider_models)

    for provider, key_entry in provider_models:
        healthy = model_health.healthy_models(FREE_MODELS)
        if not healthy:
            continue
        model = healthy[0]
        try:
            start = time.time()
            if provider == "openrouter":
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key_entry['key']}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.8,
                        "max_tokens": 8192,
                    },
                    timeout=180,
                )
            else:
                resp = requests.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key_entry['key']}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model.replace(":free", ""),
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.8,
                        "max_tokens": 8192,
                    },
                    timeout=180,
                )

            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"]
            model_health.record_success(model)
            latency = time.time() - start
            print(f"[NewsAPI] Generated article in {latency:.0f}s using {provider}/{model}")

            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                img_data = fetch_image_for_news(title)
                result.update(img_data)
                result["id"] = f"news-{int(time.time())}-{hash(title) % 10000}"
                result["publishedAt"] = datetime.now(timezone.utc).isoformat()
                result["title"] = title
                return result
        except Exception as e:
            model_health.record_failure(model)
            continue

    return None


def refresh_news():
    print("[NewsAPI] Refreshing news cache...")
    items = fetch_rss_news()
    items += fetch_newsapi()
    items = deduplicate(items)
    items = items[:15]
    print(f"[NewsAPI] {len(items)} unique items to process")

    new_articles = []
    for item in items[:5]:
        try:
            article = generate_article(item)
            if article:
                new_articles.append(article)
        except Exception as e:
            print(f"[NewsAPI] Article gen error: {e}")

    with CACHE_LOCK:
        NEWS_CACHE.clear()
        NEWS_CACHE.extend(new_articles)
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
    scheduler.add_job(refresh_news, "interval", hours=1, next_run_time=None)
    scheduler.add_job(refresh_news, "interval", seconds=30, max_instances=1)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))


if __name__ == "__main__":
    print("[NewsAPI] Initializing...")
    refresh_news()
    start_scheduler()
    print(f"[NewsAPI] Server starting on http://0.0.0.0:5000")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
