import os
import sys
import json
import re
import random
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_DIR = Path(__file__).resolve().parent
POSTS_DIR = REPO_DIR / "_posts"
POSTS_DIR.mkdir(exist_ok=True)

HIGH_CPC_KEYWORDS = [
    "insurance", "loan", "credit", "mortgage", "investing", "crypto",
    "refinance", "banking", "tax", "debt", "AI", "cybersecurity",
    "cloud computing", "VPN", "hosting", "SaaS", "SEO", "marketing",
    "lead generation", "small business", "startup", "health insurance",
    "weight loss", "fitness", "DUI", "bankruptcy", "personal injury",
    "online course", "certification", "remote work", "real estate",
]

RSS_FEEDS = [
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://www.reddit.com/r/finance/hot/.rss",
    "https://www.reddit.com/r/technology/hot/.rss",
    "https://www.reddit.com/r/startups/hot/.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
]

OPENROUTER_MODELS = [
    "mistralai/mistral-7b-instruct",
    "meta-llama/llama-3-8b-instruct",
    "google/gemma-2-9b-it",
    "microsoft/phi-3-mini-128k-instruct",
]

NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"

AD_SLOT_MARKER_START = "<!-- AD_TOP -->"
AD_SLOT_MARKER_MID = "<!-- AD_MID -->"
AD_SLOT_MARKER_END = "<!-- AD_BOTTOM -->"


def load_env_api_keys():
    keys = {}
    for i in range(1, 5):
        val = os.environ.get(f"OPENROUTER_API_KEY_{i}")
        if val:
            keys[f"openrouter_{i}"] = val
    nv = os.environ.get("NVIDIA_API_KEY_1")
    if nv:
        keys["nvidia_1"] = nv
    keys["unsplash"] = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    keys["newsapi"] = os.environ.get("NEWSAPI_KEY", "")
    return keys


def fetch_trends_rss():
    topics = []
    for url in RSS_FEEDS:
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                continue
            root = ElementTree.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"} if not root.tag.startswith("rss") else {}
            for item in root.iter("item"):
                title = item.findtext("title", "")
                desc = item.findtext("description", "")
                link = item.findtext("link", "")
                text = f"{title} {desc}"
                topics.append({"title": title, "text": text, "source": url, "link": link})
            if "feed" in root.tag.lower():
                for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                    title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                    link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                    link = link_el.attrib.get("href", "") if link_el is not None else ""
                    topics.append({"title": title, "text": title, "source": url, "link": link})
        except Exception as e:
            log.warning(f"RSS failed for {url}: {e}")
    return topics


def fetch_trends_google():
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=300, timeout=10)
        trending = pytrends.trending_searches(pn="united_states")
        if trending.empty:
            return []
        results = []
        for title in trending[0].head(10).tolist():
            results.append({"title": title, "text": title, "source": "google_trends", "link": ""})
        return results
    except Exception as e:
        log.warning(f"Google Trends failed: {e}")
        return []


def fetch_trends_newsapi(api_key):
    if not api_key:
        return []
    try:
        resp = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": "us", "pageSize": 20, "apiKey": api_key},
            timeout=15,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for article in data.get("articles", []):
            title = article.get("title", "")
            desc = article.get("description", "")
            text = f"{title} {desc}"
            results.append({"title": title, "text": text, "source": "newsapi", "link": article.get("url", "")})
        return results
    except Exception as e:
        log.warning(f"NewsAPI failed: {e}")
        return []


def score_topic(topic):
    title_lower = topic["title"].lower()
    full_text = topic["text"].lower()
    score = 0
    matched = []
    for kw in HIGH_CPC_KEYWORDS:
        if kw.lower() in title_lower:
            score += 20
            matched.append(kw)
        elif kw.lower() in full_text:
            score += 5
            matched.append(kw)
    words = full_text.split()
    if len(words) > 10:
        score += 5
    if any(c.isdigit() for c in full_text):
        score += 3
    return score, matched


def pick_best_topic(candidates):
    scored = []
    for c in candidates:
        s, matched = score_topic(c)
        if s > 0:
            scored.append((s, c, matched))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored:
        best = scored[0]
        log.info(f"Best topic: {best[1]['title']} (score={best[0]}, keywords={best[2]})")
        return best[1], best[2]
    if candidates:
        log.info(f"No high-CPC match, using first topic: {candidates[0]['title']}")
        return candidates[0], []
    return None, []


def get_existing_titles():
    titles = set()
    for f in POSTS_DIR.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            m = re.search(r'title:\s*["\']?(.+?)["\']?\n', content)
            if m:
                titles.add(m.group(1).strip().lower())
        except Exception:
            pass
    return titles


def is_duplicate(title, existing):
    t = title.lower().strip()
    if t in existing:
        return True
    t_clean = re.sub(r'[^a-z0-9\s]', '', t)
    for e in existing:
        e_clean = re.sub(r'[^a-z0-9\s]', '', e)
        if t_clean == e_clean:
            return True
    return False


def call_openrouter(api_key, prompt, model=None):
    if not model:
        model = random.choice(OPENROUTER_MODELS)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional content writer. Write well-researched, engaging articles in natural English. Vary sentence structure. Use a professional but accessible tone."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 4096,
        "top_p": 0.95,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=180,
    )
    if resp.status_code != 200:
        raise Exception(f"OpenRouter error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"]


def call_nvidia(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional content writer. Write well-researched, engaging articles in natural English."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 4096,
        "top_p": 0.95,
    }
    resp = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=180,
    )
    if resp.status_code != 200:
        raise Exception(f"NVIDIA error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"]


def generate_article(topic, keywords, api_keys):
    kw_str = ", ".join(keywords[:5]) if keywords else topic["title"]
    prompt = f"""Write a comprehensive, well-researched article about the following topic.

Topic: {topic['title']}
Source reference: {topic.get('link', '')}

CRITICAL: Write strictly about the TOPIC above, not about the keywords.
Naturally include these keywords where relevant: {kw_str}

Requirements:
- Write at least 1200 words
- Use a natural, engaging, professional tone
- Vary sentence length and structure
- Include specific examples, data points, or statistics where relevant
- Structure with clear H2 and H3 subheadings
- Include a FAQ section with at least 4 questions and answers at the end
- Write in markdown format
- Start with a compelling introduction paragraph
- End with a conclusion paragraph
- Do NOT include any meta-commentary or notes about the writing process
- Write directly as if you are an expert in this field

Return only the article content in markdown format with no additional commentary."""

    errors = []
    for i in range(1, 5):
        key = api_keys.get(f"openrouter_{i}")
        if not key:
            continue
        try:
            log.info(f"Trying OpenRouter key {i}...")
            content = call_openrouter(key, prompt)
            if len(content) > 500:
                return content
            errors.append(f"OpenRouter key {i}: content too short ({len(content)} chars)")
        except Exception as e:
            errors.append(f"OpenRouter key {i}: {e}")
            continue

    nv_key = api_keys.get("nvidia_1")
    if nv_key:
        try:
            log.info("Trying NVIDIA...")
            content = call_nvidia(nv_key, prompt)
            if len(content) > 500:
                return content
            errors.append(f"NVIDIA: content too short ({len(content)} chars)")
        except Exception as e:
            errors.append(f"NVIDIA: {e}")

    raise Exception(f"All LLM APIs failed: {'; '.join(errors)}")


def fetch_image(query, api_key):
    if not api_key:
        return ""
    try:
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {api_key}"},
            timeout=15,
        )
        if resp.status_code != 200:
            return ""
        data = resp.json()
        if data.get("results"):
            img = data["results"][0]
            url = img["urls"]["regular"]
            credit = f"Photo by {img['user']['name']} on Unsplash"
            return f"{url}?w=1200"
        return ""
    except Exception as e:
        log.warning(f"Unsplash failed: {e}")
        return ""


def slugify(title):
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    s = s[:80].strip('-')
    return s


def build_post(content, topic, keywords, image_url, existing_titles):
    title = topic["title"]
    if len(title) > 100:
        title = title[:97] + "..."

    if is_duplicate(title, existing_titles):
        log.warning(f"Duplicate title: {title}")
        return None

    slug = slugify(title)
    date = datetime.utcnow()
    filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
    filepath = POSTS_DIR / filename

    excerpt = re.sub(r'[#*`>\[\]]+', '', content[:200]).replace("\n", " ").strip()
    excerpt = excerpt[:150] + "..." if len(excerpt) > 150 else excerpt

    kw_tags = ", ".join(keywords[:5]) if keywords else topic["title"].lower().replace(" ", ", ")
    tag_list = re.sub(r'[^\w,\s]', '', kw_tags).strip().lower()

    frontmatter = f"""---
title: "{title}"
date: {date.strftime('%Y-%m-%d %H:%M:%S')}
excerpt: "{excerpt}"
image: "{image_url}"
tags: [{tag_list}]
categories: [{tag_list}]
---

"""

    content_clean = re.sub(r'^```markdown\s*', '', content)
    content_clean = re.sub(r'^```\s*$', '', content_clean, flags=re.MULTILINE)
    content_clean = re.sub(r'^---.*?---\s*', '', content_clean, flags=re.DOTALL)

    final_content = frontmatter + content_clean.strip()
    filepath.write_text(final_content, encoding="utf-8")
    log.info(f"Post saved: {filepath.name}")
    return filepath


def git_commit_push(filepath):
    try:
        import subprocess
        repo_dir = str(REPO_DIR)
        subprocess.run(["git", "config", "user.name", "AutoPublisher"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bot@yoursite.com"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "pull", "--rebase"], cwd=repo_dir, capture_output=True)
        r = subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True)
        if r.returncode != 0:
            log.error(f"git add failed: {r.stderr.decode()}")
            return False
        r = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_dir, capture_output=True,
        )
        if r.returncode == 0:
            log.info("No changes to commit")
            return True
        r = subprocess.run(
            ["git", "commit", "-m", f"Auto: {filepath.name.replace('.md', '').replace('-', ' ')[11:]}"],
            cwd=repo_dir, capture_output=True,
        )
        if r.returncode != 0:
            log.error(f"git commit failed: {r.stderr.decode()}")
            return False
        r = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True)
        if r.returncode != 0:
            log.error(f"git push failed: {r.stderr.decode()}")
            return False
        log.info("Pushed to GitHub successfully")
        return True
    except Exception as e:
        log.error(f"Git operation failed: {e}")
        return False


def main():
    log.info("=" * 50)
    log.info("Starting daily content generation")
    log.info("=" * 50)

    api_keys = load_env_api_keys()
    key_count = sum(1 for k in api_keys if k.startswith("openrouter") or k.startswith("nvidia"))
    log.info(f"LLM API keys loaded: {key_count}")

    log.info("Fetching trends...")
    all_candidates = []

    trends_rss = fetch_trends_rss()
    log.info(f"RSS feeds returned: {len(trends_rss)} items")
    all_candidates.extend(trends_rss)

    trends_google = fetch_trends_google()
    log.info(f"Google Trends returned: {len(trends_google)} items")
    all_candidates.extend(trends_google)

    trends_news = fetch_trends_newsapi(api_keys.get("newsapi", ""))
    log.info(f"NewsAPI returned: {len(trends_news)} items")
    all_candidates.extend(trends_news)

    if not all_candidates:
        log.error("No trends found from any source")
        sys.exit(1)

    topic, keywords = pick_best_topic(all_candidates)
    if not topic:
        log.error("No suitable topic found")
        sys.exit(1)

    existing_titles = get_existing_titles()
    log.info(f"Existing posts: {len(existing_titles)}")

    if is_duplicate(topic["title"], existing_titles):
        log.info(f"Topic already covered: {topic['title']}")
        candidates_no_dup = [c for c in all_candidates if not is_duplicate(c["title"], existing_titles)]
        if candidates_no_dup:
            topic, keywords = pick_best_topic(candidates_no_dup)
            if not topic:
                log.error("No non-duplicate topic found")
                sys.exit(1)
        else:
            log.error("All topics already covered")
            sys.exit(0)

    log.info(f"Generating article for: {topic['title']}")
    try:
        article = generate_article(topic, keywords, api_keys)
    except Exception as e:
        log.error(f"Article generation failed: {e}")
        sys.exit(1)

    log.info(f"Article generated: {len(article)} characters")

    image_query = topic["title"]
    image_url = fetch_image(image_query, api_keys.get("unsplash", ""))
    if not image_url and keywords:
        image_url = fetch_image(" ".join(keywords[:3]), api_keys.get("unsplash", ""))

    post_file = build_post(article, topic, keywords, image_url, existing_titles)
    if not post_file:
        sys.exit(0)

    success = git_commit_push(post_file)
    if success:
        log.info("Done! Article published successfully.")
    else:
        log.error("Article saved locally but git push failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
