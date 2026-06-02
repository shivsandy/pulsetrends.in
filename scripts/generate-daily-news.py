#!/usr/bin/env python3
"""
Daily News Generator for PulseTrends
=====================================
Generates 9 articles daily (3 crypto + 4 IPO + 2 stock market) using
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

# ── Article Generation ──────────────────────────────────────────────

def generate_articles_batch(category, count, date_str):
    """
    Generate `count` articles for a given category.
    Returns a list of article dicts.
    """
    today = date_str
    articles = []

    category_prompts = {
        "crypto": f"""You are a veteran financial journalist covering cryptocurrency markets at PulseTrends.

Today's date: {today}

Generate exactly ONE (1) news article about cryptocurrency markets. The article must be written in a natural, human-like journalistic style — as if a real financial reporter wrote it after researching the markets this morning.

Requirements:
- Write like a human financial journalist — use varied sentence lengths, contractions ("it's", "they're", "we've seen"), and natural paragraph transitions
- Include specific price numbers, percentages, or market data to make it concrete
- Cover topics like: Bitcoin/Ethereum price movements, DeFi trends, regulatory developments, institutional adoption, layer-2 growth, or crypto market analysis
- Vary vocabulary — don't repeat the same phrases
- Avoid AI-sounding patterns: no "Furthermore,", "Moreover,", "In conclusion," — just write naturally
- The article should feel like something you'd read on Bloomberg or CoinDesk — factual, insightful, with a bit of personality
- Include 1-2 sentences of expert-sounding commentary (attributed to "analysts" or a made-up analyst name)

Output ONLY a valid JSON object with NO markdown formatting, NO code fences, NO commentary. Just the raw JSON.

The JSON must have exactly these fields:
{{
  "headline": "A compelling, clickable news headline",
  "subheadline": "A supporting subheadline (1 sentence)",
  "keyHighlights": ["5 bullet points as strings highlighting key facts"],
  "executiveSummary": "2-3 sentence executive summary",
  "marketBackground": "3-4 sentences providing market context",
  "detailedAnalysis": "5-7 paragraphs of detailed analysis with markdown headings (## Bullish Factors, ## Bearish Factors, ## Risk Analysis, ## Expert Perspective, ## Historical Comparison, ## Market Impact)",
  "expertInsights": "1-2 sentences of analyst commentary",
  "financialMetrics": {{ "tableCaption": "Table title", "headers": ["3-4 column headers as strings"], "rows": [["row1_col1", "row1_col2", ...], ["row2_col1", ...]] }},
  "risks": ["3-5 risk factors as strings"],
  "opportunities": ["3-5 opportunities as strings"],
  "outlook": "2-3 sentence market outlook",
  "conclusion": "2-3 sentence conclusion",
  "category": "crypto",
  "sentiment": "bullish or bearish or neutral",
  "impact": "low or medium or high",
  "relatedCoins": ["BTC", "ETH", ...],
  "relatedStocks": [],
  "primaryKeyword": "main SEO keyword",
  "secondaryKeywords": ["3-5 related keywords"],
  "tags": ["3-5 tags"],
  "metaDescription": "SEO meta description under 160 chars",
  "slug": "url-friendly-slug-here",
  "focusKeyword": "primary SEO keyword",
  "sourcesReferenced": ["Source 1", "Source 2", "Source 3"],
  "aiAnalysis": {{
    "bullCase": "bullish scenario",
    "bearCase": "bearish scenario",
    "neutralCase": "neutral scenario",
    "probabilityWeightedOutlook": "probability split",
    "potentialCatalysts": ["2-3 catalysts"],
    "keyRisks": ["2-3 risks"]
  }},
  "publishedAt": "{datetime.now(timezone.utc).isoformat()}"
}}

WRITE THE ARTICLE TEXT NATURALLY as if a human journalist wrote it. Make the detailedAnalysis section substantive and insightful, not generic.""",

        "ipo": f"""You are a veteran financial journalist covering IPO markets at PulseTrends.

Today's date: {today}

Generate exactly ONE (1) news article about IPOs (initial public offerings). The article must be written in a natural, human-like journalistic style.

Requirements:
- Write like a human financial journalist — use varied sentence structures, natural transitions, contractions
- Cover topics like: upcoming IPOs, IPO performance analysis, subscription rates, GMP trends, SEBI regulations, institutional investor activity, or specific IPO reviews
- Include specific numbers (issue size, price bands, GMP, subscription figures) to make it concrete
- Vary vocabulary — don't repeat phrases
- Avoid AI-sounding patterns
- Include 1-2 sentences of analyst commentary

Output ONLY a valid JSON object with NO markdown formatting, NO code fences. The JSON fields are the same as above:
{{
  "headline": "...",
  "subheadline": "...",
  "keyHighlights": [...],
  "executiveSummary": "...",
  "marketBackground": "...",
  "detailedAnalysis": "...",
  "expertInsights": "...",
  "financialMetrics": {{ "tableCaption": "...", "headers": [...], "rows": [...] }},
  "risks": [...],
  "opportunities": [...],
  "outlook": "...",
  "conclusion": "...",
  "category": "ipo",
  "sentiment": "bullish or bearish or neutral",
  "impact": "low or medium or high",
  "relatedCoins": [],
  "relatedStocks": ["TICKER1", "TICKER2", ...],
  "primaryKeyword": "...",
  "secondaryKeywords": [...],
  "tags": [...],
  "metaDescription": "...",
  "slug": "...",
  "focusKeyword": "...",
  "sourcesReferenced": [...],
  "aiAnalysis": {{
    "bullCase": "...",
    "bearCase": "...",
    "neutralCase": "...",
    "probabilityWeightedOutlook": "...",
    "potentialCatalysts": [...],
    "keyRisks": [...]
  }},
  "publishedAt": "{datetime.now(timezone.utc).isoformat()}"
}}

Make the article text sound natural and human-written, not like AI-generated content.""",

        "stocks": f"""You are a veteran financial journalist covering stock markets at PulseTrends.

Today's date: {today}

Generate exactly ONE (1) news article about stock markets. The article must be written in a natural, human-like journalistic style.

Requirements:
- Write like a human financial journalist — use varied sentence structures, natural transitions, contractions
- Cover topics like: Nifty/Sensex movements, Fed policy impact, sector performance, quarterly earnings analysis, FII/DII flows, global market trends, or specific stock analysis
- Include specific numbers (index levels, percentage changes, earnings figures) to make it concrete
- Vary vocabulary
- Avoid AI-sounding patterns
- Include analyst commentary

Output ONLY a valid JSON object with NO markdown formatting, NO code fences. Same JSON fields as above:
{{
  "headline": "...",
  "subheadline": "...",
  "keyHighlights": [...],
  "executiveSummary": "...",
  "marketBackground": "...",
  "detailedAnalysis": "...",
  "expertInsights": "...",
  "financialMetrics": {{ "tableCaption": "...", "headers": [...], "rows": [...] }},
  "risks": [...],
  "opportunities": [...],
  "outlook": "...",
  "conclusion": "...",
  "category": "stocks",
  "sentiment": "bullish or bearish or neutral",
  "impact": "low or medium or high",
  "relatedCoins": [],
  "relatedStocks": ["TICKER1", "TICKER2", ...],
  "primaryKeyword": "...",
  "secondaryKeywords": [...],
  "tags": [...],
  "metaDescription": "...",
  "slug": "...",
  "focusKeyword": "...",
  "sourcesReferenced": [...],
  "aiAnalysis": {{
    "bullCase": "...",
    "bearCase": "...",
    "neutralCase": "...",
    "probabilityWeightedOutlook": "...",
    "potentialCatalysts": [...],
    "keyRisks": [...]
  }},
  "publishedAt": "{datetime.now(timezone.utc).isoformat()}"
}}

Make the article text sound natural and human-written.""",
    }

    prompt_template = category_prompts.get(category, category_prompts["crypto"])

    for i in range(count):
        print(f"\n[{category.upper()}] Generating article {i+1}/{count}...")
        
        # Add variety by randomizing the topic angle
        angles = {
            "crypto": [
                "Focus on Bitcoin and Ethereum price action and market sentiment.",
                "Focus on altcoin season, DeFi, or layer-2 ecosystem developments.",
                "Focus on regulatory news, institutional adoption, or ETF flows.",
                "Focus on on-chain metrics, whale activity, or market structure.",
                "Focus on a specific emerging trend in the crypto space.",
            ],
            "ipo": [
                "Focus on an upcoming high-profile IPO and its market reception.",
                "Focus on recent IPO listings and their listing-day performance.",
                "Focus on IPO market trends, subscription data, and GMP movements.",
                "Focus on SEBI regulatory changes affecting the IPO market.",
                "Focus on a specific sector's IPO activity (e.g., fintech, tech, SME).",
            ],
            "stocks": [
                "Focus on Nifty/Sensex movement and sectoral rotation.",
                "Focus on a major company's quarterly earnings report.",
                "Focus on FII/DII flows and global market impact on Indian markets.",
                "Focus on Fed policy and its impact on emerging markets.",
                "Focus on a specific sector showing strong momentum.",
            ]
        }

        extra_angle = random.choice(angles.get(category, angles["crypto"]))
        full_prompt = f"{prompt_template}\n\nCRITICAL - Make this article feel DIFFERENT from the others. {extra_angle}\n\nEnsure the article reads like it was written by a human journalist, not an AI."

        result = None
        for attempt in range(MAX_RETIRES):
            result = call_llm(full_prompt)
            if result:
                # Try to extract JSON
                try:
                    # Strip markdown code fences if present
                    cleaned = result.strip()
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
                        cleaned = re.sub(r'\s*```$', '', cleaned)
                    
                    article = json.loads(cleaned)
                    # Validate required fields
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
                    article.setdefault("slug", slugify(article.get("headline", "")))
                    article.setdefault("focusKeyword", article.get("primaryKeyword", ""))
                    article.setdefault("publishedAt", now_iso())
                    
                    # Fetch Unsplash images for this article
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
                    # Show part of the response for debugging
                    preview = result[:300] if result else "None"
                    print(f"  Response preview: {preview}...")
                    time.sleep(2)
            else:
                print(f"  ✗ LLM call failed (attempt {attempt+1})")
                time.sleep(3)
        
        if not result:
            print(f"  ✗ Failed to generate article after {MAX_RETIRES} attempts")
    
    return articles


def generate_all_articles(date_str):
    """Generate all 9 articles for today."""
    all_articles = []
    
    # 3 Crypto
    all_articles.extend(generate_articles_batch("crypto", 3, date_str))
    
    # 4 IPO
    all_articles.extend(generate_articles_batch("ipo", 4, date_str))
    
    # 2 Stock Market
    all_articles.extend(generate_articles_batch("stocks", 2, date_str))
    
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
        lines.append(f'    detailedAnalysis: "{esc(art.get("detailedAnalysis", ""))}",')
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
    
    date_str = today_str()
    
    print(f"\n[Generate] Creating 9 articles (3 crypto + 4 IPO + 2 stocks)...")
    new_articles = generate_all_articles(date_str)
    
    print(f"\n[Results] Generated {len(new_articles)} articles successfully")
    
    if not new_articles:
        print("[!] No articles were generated. Something went wrong.")
        return 1
    
    # Write all articles
    write_news_data(new_articles)
    
    print("\n" + "=" * 60)
    print("  COMPLETE")
    print(f"  {len(new_articles)} articles written to src/data/newsData.ts")
    print("  Next: Build and deploy")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
