#!/usr/bin/env python3
"""
Daily News Generator for PulseTrends
=====================================
Generates 11 articles daily (3 crypto + 5 IPO + 3 stock market) using
LLM APIs from environment variables. Falls back across providers.

Run: python scripts/generate-daily-news.py

Environment variables (GitHub Secrets):
  GOOGLE_AI_API_KEY_1, GOOGLE_AI_API_KEY_2   — Google Gemini
  GROQ_API                                      — Groq (fast inference)
  COHERE_API                                    — Cohere
  MISTRAL_API                                   — Mistral
"""

import json
import os
import re
import sys
import random
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "data"
NEWS_DATA_FILE = DATA_DIR / "newsData.ts"
CACHE_DIR = REPO_ROOT / "data"
USED_IMAGES_FILE = CACHE_DIR / "used_news_images.json"
MAX_RETIRES = 3
TIMEOUT_SEC = 90

# ── Unsplash category queries (mirror news_api.py) ──────────────────

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
        "nasdaq trading floor",
        "global stock market trading",
        "financial charts data analytics",
        "trading desk monitors",
    ],
}

# ── Helpers ──────────────────────────────────────────────────────────

def esc(s):
    """Escape a string for embedding in TypeScript string literal."""
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
        .replace("\t", "\\t")
    )

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')[:60]

def make_id():
    import random as rnd
    ts = int(time.time() * 1000)
    r = rnd.randint(1000, 9999)
    return f"news-{ts}-{r}"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def today_str():
    return datetime.now(timezone.utc).strftime("%B %d, %Y")

# ── Author attribution ────────────────────────────────────────────────

AUTHOR_BLOCK = "\n\n---\n\nAuthor: Shiva Sandeep\n\nTelegram: @its_terabyte\n\nWhatsApp:\n\n*Default WhatsApp profile image placeholder*\n\nPublished by PulseTrends\n\n---"
AUTHOR_BLOCK_ESC = esc(AUTHOR_BLOCK)

# ── LLM API callers ──────────────────────────────────────────────────

def _try_imports():
    global requests
    try:
        import requests as req
        requests = req
        return True
    except ImportError:
        print("[!] 'requests' not installed. Install with: pip install requests")
        return False

def call_gemini(prompt, api_keys):
    """Call Google Gemini API. Tries multiple keys."""
    if not api_keys:
        return None
    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        }
    }
    for key in api_keys:
        if not key:
            continue
        try:
            resp = requests.post(
                f"{url}?key={key}",
                json=payload,
                timeout=TIMEOUT_SEC,
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text.strip()
            elif resp.status_code == 429:
                print(f"[Gemini] Rate limited on key, trying next...")
                time.sleep(2)
                continue
            else:
                print(f"[Gemini] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[Gemini] Error: {e}")
            time.sleep(1)
    return None


def call_groq(prompt, api_keys):
    """Call Groq API (fast inference)."""
    if not api_keys:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an expert financial journalist and market analyst. Write in a natural, human-like style as if you're an experienced journalist reporting on financial markets. Use varied sentence structures, contractions, and natural transitions. Avoid sounding like an AI."},
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
            resp = requests.post(
                url,
                json=payload,
                timeout=TIMEOUT_SEC,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                }
            )
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
            else:
                print(f"[Groq] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[Groq] Error: {e}")
            time.sleep(1)
    return None


def call_mistral(prompt, api_keys):
    """Call Mistral API."""
    if not api_keys:
        return None
    url = "https://api.mistral.ai/v1/chat/completions"
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": "You are an expert financial journalist and market analyst. Write in a natural, human-like style as if you're an experienced journalist reporting on financial markets. Use varied sentence structures, contractions, and natural transitions. Avoid sounding like an AI."},
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
            resp = requests.post(
                url,
                json=payload,
                timeout=TIMEOUT_SEC,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "")
                if text:
                    return text.strip()
            else:
                print(f"[Mistral] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[Mistral] Error: {e}")
            time.sleep(1)
    return None


def call_cohere(prompt, api_keys):
    """Call Cohere API."""
    if not api_keys:
        return None
    url = "https://api.cohere.com/v2/chat"
    payload = {
        "model": "command-r-plus-08-2024",
        "message": prompt,
        "temperature": 0.85,
        "max_tokens": 4096,
        "preamble": "You are an expert financial journalist and market analyst. Write in a natural, human-like style as if you're an experienced journalist reporting on financial markets. Use varied sentence structures, contractions, and natural transitions. Avoid sounding like an AI.",
    }
    for key in api_keys:
        if not key:
            continue
        try:
            resp = requests.post(
                url,
                json=payload,
                timeout=TIMEOUT_SEC,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("message", {}).get("content", [{}])[0].get("text", "")
                if text:
                    return text.strip()
            else:
                print(f"[Cohere] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[Cohere] Error: {e}")
            time.sleep(1)
    return None


def call_llm(prompt):
    """Try all LLM providers in order. Returns text or None."""
    providers = [
        ("Groq", call_groq, os.environ.get("GROQ_API", "").split(",")),
        ("Mistral", call_mistral, os.environ.get("MISTRAL_API", "").split(",")),
        ("Gemini", call_gemini, (os.environ.get("GOOGLE_AI_API_KEY_1", ""), os.environ.get("GOOGLE_AI_API_KEY_2", ""))),
        ("Cohere", call_cohere, os.environ.get("COHERE_API", "").split(",")),
    ]
    random.shuffle(providers)  # vary which provider gets called first each run
    for name, func, keys in providers:
        filtered = [k.strip() for k in (keys if isinstance(keys, (list, tuple)) else [keys]) if k.strip()]
        if not filtered:
            continue
        print(f"[LLM] Trying {name}...")
        result = func(prompt, filtered)
        if result:
            print(f"[LLM] {name} succeeded ({len(result)} chars)")
            return result
        print(f"[LLM] {name} failed, trying next provider...")
    return None

# ── Unsplash Image Fetching ─────────────────────────────────────────

def _load_used_image_ids():
    """Load set of already-used Unsplash photo IDs."""
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
    """Save set of used Unsplash photo IDs to disk."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(USED_IMAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(ids), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Unsplash] Save failed: {e}")


def _validate_image_url(url):
    """Quick HEAD check to ensure image URL is valid."""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        if resp.status_code == 200 and "image" in resp.headers.get("Content-Type", "").lower():
            return True
        resp = requests.get(url, stream=True, timeout=5)
        return resp.status_code == 200 and "image" in resp.headers.get("Content-Type", "").lower()
    except Exception:
        return False


def fetch_unsplash_images(headline, category="stocks", count=4):
    """
    Fetch unique images from Unsplash for an article.
    Deduplicates against used_news_images.json to avoid reusing photos.
    Returns a list of image dicts matching the ArticleImage interface.
    """
    unsplash_keys = []
    for i in range(1, 4):
        val = os.environ.get(f"UNSPLASH_ACCESS_KEY_{i}")
        if val and val.strip():
            unsplash_keys.append(val.strip())

    if not unsplash_keys:
        print("[Unsplash] No API keys found")
        return []

    # Build query pool from headline words + category queries
    cat = category if category in UNSPLASH_QUERY_MAP else "stocks"
    base_words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', '', headline).split() if len(w) > 3][:3]
    query_pool = list(UNSPLASH_QUERY_MAP.get(cat, UNSPLASH_QUERY_MAP["stocks"]))
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
                    if not url:
                        continue
                    if not _validate_image_url(url):
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
                    break  # one image per query, move to next query
            except Exception as e:
                continue
        if len(results) >= count:
            break

    # Save used IDs to prevent reuse
    if results:
        used_ids.update(r["photoId"] for r in results if "photoId" in r)
        if len(used_ids) > 500:
            used_ids = set(sorted(used_ids)[-500:])
        _save_used_image_ids(used_ids)
        print(f"[Unsplash] Fetched {len(results)} images for '{headline[:50]}...'")

    return results

# ── Existing Article Update ──────────────────────────────────────────

def _find_ts_string_end(text, start):
    """Find the end of a TypeScript string literal starting at start (after the opening quote)."""
    i = start
    while i < len(text):
        if text[i] == '\\':
            i += 2
        elif text[i] == '"':
            return i
        else:
            i += 1
    return -1


def update_existing_articles_author():
    """
    Scan existing newsData.ts and append author attribution to any articles
    that are missing it. Does not modify article content, metadata, or structure.
    """
    if not NEWS_DATA_FILE.exists():
        print("[Author Update] No existing news data file found, skipping.")
        return

    content = NEWS_DATA_FILE.read_text("utf-8")

    if "Author: Shiva Sandeep" in content:
        print("[Author Update] All existing articles already have author attribution.")
        return

    modified = 0
    idx = 0
    result = []
    last_end = 0

    while True:
        da_start = content.find("detailedAnalysis:", idx)
        if da_start == -1:
            break

        open_quote = content.find('"', da_start)
        if open_quote == -1:
            idx = da_start + 1
            continue

        close_quote = _find_ts_string_end(content, open_quote + 1)
        if close_quote == -1:
            idx = open_quote + 1
            continue

        inner = content[open_quote + 1:close_quote]

        if "Author: Shiva Sandeep" not in inner:
            new_inner = inner + AUTHOR_BLOCK_ESC
            result.append(content[last_end:open_quote + 1])
            result.append(new_inner)
            result.append(content[close_quote])
            last_end = close_quote + 1
            modified += 1

        idx = close_quote + 1

    if modified:
        result.append(content[last_end:])
        NEWS_DATA_FILE.write_text("".join(result), "utf-8")
        print(f"[Author Update] Appended author attribution to {modified} existing article(s).")
    else:
        print("[Author Update] No articles needed updating.")


# ── Article Generation ──────────────────────────────────────────────

def generate_articles_batch(category, count, date_str):
    """
    Generate `count` articles for a given category.
    Returns a list of article dicts.
    """
    today = date_str
    articles = []

    # ── Base prompt shared across all categories ──────────────────────
    base_prompt = f"""You are an expert financial journalist, SEO strategist, and newsroom editor working for PulseTrends (https://pulsetrends.in).

Today's date: {today}

## NEWS DISCOVERY PROCESS
Before creating content, gather information from multiple reputable sources. Identify trending topics with strong search demand. Research Google Trends data, trending search queries, high-volume keywords, related semantic keywords, long-tail keywords, and question-based keywords. Prioritize topics with the highest traffic potential.

## CONTENT CREATION RULES
- Never copy content from any source. Never publish rewritten paragraphs from source articles.
- Read and understand source material, then independently write original content.
- Produce journalist-quality reporting. Content must feel completely human-written.
- Avoid robotic, repetitive, or AI-generated language patterns.
- Use professional newsroom standards. Maintain factual accuracy. Verify information.
- Use varied sentence lengths, contractions ("it's", "they're", "we've seen"), and natural paragraph transitions.
- Include specific numbers, percentages, or market data to make it concrete.
- Vary vocabulary — don't repeat the same phrases.
- Avoid AI-sounding patterns: no "Furthermore,", "Moreover,", "In conclusion," — write naturally.
- The article should feel like something you'd read on Bloomberg, Reuters, or CoinDesk.
- Include 1-2 sentences of expert-sounding commentary (attributed to real-sounding analyst names).

## ARTICLE STRUCTURE (follow this structure in your writing)
1. **Headline** — Compelling, clickable, SEO-optimized headline
2. **Introduction** — 2-3 sentences drawing readers in with the key news
3. **Key Highlights** — 5 bullet points highlighting key facts
4. **Main Story** — 5-7 paragraphs of in-depth analysis with markdown headings (## Market Overview, ## Key Developments, ## Market Impact, ## Expert Perspective, ## Historical Context)
5. **Market Impact** — 3-4 sentences on what this means for the market
6. **Investor Takeaway** — Key action items for investors (3-4 bullet points)
7. **Expert Analysis** — Analyst commentary and expert perspectives
8. **What Happens Next** — Future outlook and catalysts to watch
9. **Conclusion** — Strong closing paragraph

## SEO REQUIREMENTS
For every article generate:
- SEO Title (seoTitle)
- Meta Title (metaTitle)
- Meta Description (metaDescription) — under 160 characters
- Focus Keyword (focusKeyword)
- Secondary Keywords (secondaryKeywords) — 3-5 related keywords
- URL Slug (slug)
- Suggested Tags (tags) — 3-5 tags
- Featured Image Prompt (featuredImagePrompt)

Optimize for: Google Search, Google Discover, Google News, Bing News, Featured Snippets, AI Search Engines, Semantic SEO.

## AUTHOR ATTRIBUTION
At the end of every article's detailed analysis section, append:

---

Author: Shiva Sandeep

Telegram: @its_terabyte

WhatsApp:

*Default WhatsApp profile image placeholder*

Published by PulseTrends

---

## QUALITY CONTROL
Before finalizing: ensure content is unique, passes plagiarism checks, does not appear AI-generated, is publication-ready, has proper grammar and readability, SEO optimization is complete, and facts are verified.

## OUTPUT FORMAT
Output ONLY a valid JSON object with NO markdown formatting, NO code fences, NO commentary. Just the raw JSON.

The JSON must have exactly these fields:
{{
  "headline": "Compelling, clickable headline",
  "subheadline": "Supporting subheadline (1 sentence)",
  "keyHighlights": ["5 bullet points as strings highlighting key facts"],
  "executiveSummary": "2-3 sentence introduction",
  "marketBackground": "3-4 sentences on market impact and context",
  "detailedAnalysis": "5-7 paragraphs with markdown headings. Include the author attribution block at the very end.",
  "expertInsights": "Expert perspective and analyst commentary",
  "financialMetrics": {{ "tableCaption": "Table title", "headers": ["3-4 column headers"], "rows": [["row1_col1", "row1_col2", ...], ["row2_col1", ...]] }},
  "risks": ["3-5 risk factors"],
  "opportunities": ["3-5 opportunities"],
  "outlook": "2-3 sentence future outlook (What Happens Next)",
  "conclusion": "2-3 sentence strong conclusion",
  "investorTakeaways": ["3-4 investor action items"],
  "category": "{category}",
  "sentiment": "bullish or bearish or neutral",
  "impact": "low or medium or high",
  "relatedCoins": ["TICKER", ...],
  "relatedStocks": ["TICKER", ...],
  "primaryKeyword": "main SEO keyword",
  "secondaryKeywords": ["3-5 related SEO keywords"],
  "tags": ["3-5 content tags"],
  "seoTitle": "SEO-optimized title tag",
  "metaTitle": "Meta title for search engines",
  "metaDescription": "SEO meta description under 160 characters",
  "slug": "url-friendly-slug",
  "focusKeyword": "primary SEO keyword",
  "featuredImagePrompt": "Image generation prompt for the featured image",
  "sourcesReferenced": ["Source 1", "Source 2", "Source 3"],
  "aiAnalysis": {{
    "bullCase": "bullish scenario",
    "bearCase": "bearish scenario",
    "neutralCase": "neutral scenario",
    "probabilityWeightedOutlook": "probability split e.g. 60%% bullish / 40%% bearish",
    "potentialCatalysts": ["2-3 catalysts"],
    "keyRisks": ["2-3 risks"]
  }},
  "publishedAt": "{datetime.now(timezone.utc).isoformat()}"
}}
"""

    # ── Category-specific topic coverage ──────────────────────────────
    category_topics = {
        "crypto": """This article is about CRYPTOCURRENCY markets.

Cover topics like: Bitcoin price movements, Ethereum updates, altcoin trends, DeFi developments, blockchain technology, Web3 ecosystem, regulatory updates, institutional adoption, crypto market analysis, ETF flows, on-chain metrics, or layer-2 scaling.

Focus on making this feel like a natural crypto market report a journalist would write.""",

        "ipo": """This article is about IPO (Initial Public Offering) markets.

Cover topics like: upcoming IPOs, recently filed IPOs, SME IPOs, mainboard IPOs, global IPO developments, IPO GMP analysis, company fundamentals, risks and opportunities, subscription data, price band analysis, listing day performance, or SEBI regulatory changes.

Focus on Indian IPO market with specific company examples and subscription/GMP data.""",

        "stocks": """This article is about STOCK MARKET analysis.

Cover topics like: trending stocks, earnings reports, market movers, institutional activity (FII/DII), sector performance, Nifty/Sensex movements, Fed policy impact, quarterly results, or global market trends.

Focus on Indian stock market with specific company examples and index levels.""",
    }

    topic_instructions = category_topics.get(category, category_topics["crypto"])

    # ── Topic angles for variety ──────────────────────────────────────────
    angles = {
        "crypto": [
            "Focus on Bitcoin and Ethereum price action with specific price targets and market sentiment analysis. Use recent on-chain data.",
            "Focus on altcoin season, DeFi protocols, or layer-2 ecosystem developments with TVL and usage metrics.",
            "Focus on regulatory news, institutional adoption, or spot ETF flows with real fund flow data.",
            "Focus on emerging trends like AI x crypto, RWAs, or Bitcoin L2s with specific project examples.",
            "Focus on macro factors affecting crypto (Fed, dollar index, liquidity) and how traders are positioning.",
        ],
        "ipo": [
            "Focus on an upcoming high-profile IPO with details on the company's financials, valuation, and investor sentiment.",
            "Focus on recent IPO listings with listing-day performance, GMP trends, and what it signals for the market.",
            "Focus on SME IPO activity — which SMEs are filing, subscription rates, and investor appetite.",
            "Focus on IPO market trends — overall subscription data, number of filings, SEBI clearance pipeline, and 2026 outlook.",
            "Focus on a global IPO development (e.g., a big US or Chinese listing) and its implications for Indian markets.",
        ],
        "stocks": [
            "Focus on Nifty/Sensex weekly performance with sectoral rotation analysis and FII/DII flow data.",
            "Focus on a major company's quarterly earnings report — revenue, profit, margins, guidance, and analyst reactions.",
            "Focus on FII/DII activity, global fund flows, and how foreign institutional investors are positioned on India.",
            "Focus on Fed policy, US interest rates, dollar index, and their cascading impact on emerging markets including India.",
            "Focus on a specific sector showing strong momentum (e.g., banking, IT, pharma, auto, renewables) with top picks.",
        ],
    }

    prompt_template = base_prompt

    for i in range(count):
        print(f"\n[{category.upper()}] Generating article {i+1}/{count}...")

        extra_angle = random.choice(angles.get(category, angles["crypto"]))
        full_prompt = f"{prompt_template}\n\n## CATEGORY-SPECIFIC INSTRUCTIONS\n{topic_instructions}\n\n## THIS ARTICLE MUST BE DIFFERENT\n{extra_angle}\n\n## ARTICLE VARIETY\nMake this article feel distinct from any others in the same category. Use a different angle, different companies/examples, and a different narrative structure. Ensure the author attribution block is included at the end of detailedAnalysis.\n\nOutput ONLY valid JSON. No markdown. No code fences."

        result = None
        for attempt in range(MAX_RETIRES):
            result = call_llm(full_prompt)
            if result:
                try:
                    cleaned = result.strip()
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r'^```(?:json)?\\s*', '', cleaned)
                        cleaned = re.sub(r'\\s*```$', '', cleaned)

                    article = json.loads(cleaned)
                    if not isinstance(article, dict):
                        raise ValueError("Response is not a JSON object")
                    required = ["headline", "detailedAnalysis", "metaDescription", "category", "publishedAt"]
                    missing = [f for f in required if f not in article]
                    if missing:
                        raise ValueError(f"Missing fields: {missing}")

                    # Ensure defaults
                    article.setdefault("id", make_id())
                    article.setdefault("subheadline", "")
                    article.setdefault("keyHighlights", [])
                    article.setdefault("executiveSummary", "")
                    article.setdefault("marketBackground", "")
                    article.setdefault("expertInsights", "")
                    article.setdefault("investorTakeaways", [])
                    article.setdefault("financialMetrics", {"tableCaption": "", "headers": [], "rows": []})
                    article.setdefault("risks", [])
                    article.setdefault("opportunities", [])
                    article.setdefault("outlook", "")
                    article.setdefault("conclusion", "")
                    article.setdefault("sourcesReferenced", [])
                    article.setdefault("aiAnalysis", None)
                    article.setdefault("sentiment", "neutral")
                    article.setdefault("impact", "medium")
                    article.setdefault("relatedCoins", [])
                    article.setdefault("relatedStocks", [])
                    article.setdefault("primaryKeyword", "")
                    article.setdefault("secondaryKeywords", [])
                    article.setdefault("tags", [])
                    article.setdefault("seoTitle", "")
                    article.setdefault("metaTitle", "")
                    article.setdefault("featuredImagePrompt", "")
                    article.setdefault("slug", slugify(article.get("headline", "")))
                    article.setdefault("focusKeyword", article.get("primaryKeyword", ""))
                    article.setdefault("publishedAt", now_iso())

                    # Ensure author attribution is in detailedAnalysis
                    da = article.get("detailedAnalysis", "")
                    if "Author: Shiva Sandeep" not in da:
                        article["detailedAnalysis"] = da + AUTHOR_BLOCK

                    # Fetch Unsplash images
                    print(f"  → Fetching images for '{article['headline'][:50]}...'")
                    article_images = fetch_unsplash_images(
                        article.get("headline", ""),
                        category=article.get("category", "stocks"),
                        count=4
                    )
                    article["images"] = article_images
                    print(f"  → {len(article_images)} images attached")

                    articles.append(article)
                    print(f"  ✓ Article: {article['headline'][:70]}...")
                    break
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"  ✗ Parse error (attempt {attempt+1}): {e}")
                    preview = result[:300] if result else "None"
                    print(f"  Response preview: {{preview}}...")
                    time.sleep(2)
            else:
                print(f"  ✗ LLM call failed (attempt {attempt+1})")
                time.sleep(3)

        if not result:
            print(f"  ✗ Failed to generate article after {MAX_RETIRES} attempts")

    return articles


def generate_all_articles(date_str):
    """Generate all 11 articles for today."""
    all_articles = []
    
    # 3 Crypto
    all_articles.extend(generate_articles_batch("crypto", 3, date_str))
    
    # 5 IPO
    all_articles.extend(generate_articles_batch("ipo", 5, date_str))
    
    # 3 Stock Market
    all_articles.extend(generate_articles_batch("stocks", 3, date_str))
    
    return all_articles

# ── File Writing ─────────────────────────────────────────────────────

def write_news_data(all_articles):
    """Write all articles to newsData.ts in the exact TypeScript format."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
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
    
    for i, art in enumerate(all_articles):
        # Format images (use empty array as default since we don't generate Unsplash URLs)
        images = art.get("images", [])
        if not isinstance(images, list):
            images = []
        
        # Financial metrics
        fm = art.get("financialMetrics", {})
        if not isinstance(fm, dict):
            fm = {"tableCaption": "", "headers": [], "rows": []}
        fm_headers = fm.get("headers", [])
        fm_rows = fm.get("rows", [])
        if not isinstance(fm_headers, list):
            fm_headers = []
        if not isinstance(fm_rows, list):
            fm_rows = []
        
        # AI Analysis
        ai = art.get("aiAnalysis")
        if not isinstance(ai, dict):
            ai = None
        
        lines.append('  {')
        lines.append(f'    id: "{esc(art.get("id", make_id()))}",')
        lines.append(f'    headline: "{esc(art.get("headline", ""))}",')
        lines.append(f'    subheadline: "{esc(art.get("subheadline", ""))}",')
        
        kh = art.get("keyHighlights", [])
        kh = kh if isinstance(kh, list) else []
        lines.append('    keyHighlights: [' + ', '.join([f'"{esc(k)}"' for k in kh[:8]]) + '],')
        
        lines.append(f'    executiveSummary: "{esc(art.get("executiveSummary", ""))}",')
        
        qa = art.get("quickAnswer", "")
        if qa:
            lines.append(f'    quickAnswer: "{esc(qa)}",')
        
        lines.append(f'    marketBackground: "{esc(art.get("marketBackground", ""))}",')
        # Ensure author attribution is in detailedAnalysis
        da_content = art.get("detailedAnalysis", "")
        if "Author: Shiva Sandeep" not in da_content:
            da_content += AUTHOR_BLOCK
        lines.append(f'    detailedAnalysis: "{esc(da_content)}",')
        lines.append(f'    expertInsights: "{esc(art.get("expertInsights", ""))}",')
        
        lines.append('    financialMetrics: {')
        lines.append(f'      tableCaption: "{esc(fm.get("tableCaption", ""))}",')
        headers_str = ', '.join([f'"{esc(h)}"' for h in fm_headers])
        lines.append(f'      headers: [{headers_str}],')
        rows_lines = []
        for row in fm_rows:
            if not isinstance(row, list):
                continue
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
        
        if ai:
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
        
        # Images from Unsplash
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
        
        lines.append(f'    primaryKeyword: "{esc(art.get("primaryKeyword", ""))}",')
        
        sk = art.get("secondaryKeywords", [])
        sk = sk if isinstance(sk, list) else []
        lines.append('    secondaryKeywords: [' + ', '.join([f'"{esc(k)}"' for k in sk[:5]]) + '],')
        
        tags = art.get("tags", [])
        tags = tags if isinstance(tags, list) else []
        if tags:
            lines.append('    tags: [' + ', '.join([f'"{esc(t)}"' for t in tags[:10]]) + '],')
        
        seo_title = art.get("seoTitle", "")
        if seo_title:
            lines.append(f'    seoTitle: "{esc(seo_title)}",')
        
        meta_title = art.get("metaTitle", "")
        if meta_title:
            lines.append(f'    metaTitle: "{esc(meta_title)}",')
        
        lines.append(f'    metaDescription: "{esc(art.get("metaDescription", ""))}",')
        
        slug = art.get("slug", "")
        if slug:
            lines.append(f'    slug: "{esc(slug)}",')
        else:
            lines.append(f'    slug: "{slugify(art.get("headline", ""))}",')
        
        fk = art.get("focusKeyword", "")
        if fk:
            lines.append(f'    focusKeyword: "{esc(fk)}",')
        
        cats = art.get("categories", [])
        cats = cats if isinstance(cats, list) else []
        if cats:
            lines.append('    categories: [' + ', '.join([f'"{esc(c)}"' for c in cats[:5]]) + '],')
        
        rel_ents = art.get("relatedEntities", [])
        rel_ents = rel_ents if isinstance(rel_ents, list) else []
        if rel_ents:
            lines.append('    relatedEntities: [' + ', '.join([f'"{esc(e)}"' for e in rel_ents[:8]]) + '],')
        
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
        
        for score_field in ["searchConsoleReadiness", "adsenseReadiness", "seoScore", "geoScore", "authorityScore", "aiCitationPotential"]:
            v = art.get(score_field)
            if isinstance(v, (int, float)):
                lines.append(f'    {score_field}: {int(v)},')
        
        lines.append(f'    publishedAt: "{esc(art.get("publishedAt", now_iso()))}",')
        lines.append('  },')
    
    lines.append('];')
    lines.append('')
    
    NEWS_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    NEWS_DATA_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[Write] Wrote {len(all_articles)} articles to {NEWS_DATA_FILE}")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    if not _try_imports():
        print("[!] Missing 'requests' library. Install with: pip install requests")
    
    print("=" * 60)
    print("  PULSETRENDS DAILY NEWS GENERATOR")
    print(f"  Date: {today_str()}")
    print(f"  UTC: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # Check if at least one API key is available
    available = []
    for name, env_var in [
        ("Groq", "GROQ_API"),
        ("Mistral", "MISTRAL_API"),
        ("Gemini", "GOOGLE_AI_API_KEY_1"),
        ("Cohere", "COHERE_API"),
    ]:
        if os.environ.get(env_var, "").strip():
            available.append(name)
    
    if not available:
        print("[!] No LLM API keys found in environment variables.")
        print("    Set at least one of: GROQ_API, MISTRAL_API, GOOGLE_AI_API_KEY_1, COHERE_API")
        print("    (These are configured as GitHub Secrets in the repository.)")
        print("    Running in dry-run mode — using fallback articles.")
        return 1
    
    print(f"[API] Available providers: {', '.join(available)}")
    
    # Update existing articles with author attribution
    print("\n[Author Update] Checking existing articles...")
    update_existing_articles_author()
    
    date_str = today_str()
    
    print(f"\n[Generate] Creating 11 articles (3 crypto + 5 IPO + 3 stocks)...")
    new_articles = generate_all_articles(date_str)
    
    print(f"\n[Results] Generated {len(new_articles)} articles successfully")
    
    if not new_articles:
        print("[!] No articles were generated. Something went wrong.")
        return 1
    
    # Write all articles
    write_news_data(new_articles)
    
    print("\n" + "=" * 60)
    print("  COMPLETE")
    print(f"  {len(new_articles)} new articles written to src/data/newsData.ts")
    print("  11 articles total (3 Crypto + 5 IPO + 3 Stocks)")
    print("  Author attribution appended to all articles")
    print("  Next: Build and deploy")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
