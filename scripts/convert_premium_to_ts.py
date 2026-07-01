#!/usr/bin/env python3
"""
Convert data/premium_news.json → src/data/newsData.ts

Reads the premium news output and generates a TypeScript file matching
the NewsArticle interface expected by the PulseTrends React frontend.
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PREMIUM_FILE = REPO_ROOT / "data" / "premium_news.json"
NEWS_DATA_FILE = REPO_ROOT / "src" / "data" / "newsData.ts"

CURRENT_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")

# ── Interface template (constant) ─────────────────────────────────────────

INTERFACE_DEFS = '''export interface ArticleImage {
  url: string;
  alt: string;
  attribution: string;
  title?: string;
  caption?: string;
  category?: string;
  sourceUrl?: string;
  source?: string;
  photoId?: string;
}

export interface FinancialMetrics {
  tableCaption: string;
  headers: string[];
  rows: string[][];
}

export interface AiAnalysis {
  bullCase: string;
  bearCase: string;
  neutralCase: string;
  probabilityWeightedOutlook: string;
  potentialCatalysts: string[];
  keyRisks: string[];
}

export interface NewsArticle {
  id: string;
  headline: string;
  subheadline: string;
  keyHighlights: string[];
  executiveSummary: string;
  quickAnswer?: string;
  marketBackground: string;
  detailedAnalysis: string;
  expertInsights: string;
  financialMetrics: FinancialMetrics;
  risks: string[];
  opportunities: string[];
  outlook: string;
  conclusion: string;
  frequentlyAskedQuestions?: { question: string; answer: string }[];
  investorTakeaways?: string[];
  sourcesReferenced: string[];
  aiAnalysis: AiAnalysis | null;
  images: ArticleImage[];
  ipoDetails?: { [key: string]: string };
  cryptoDetails?: { [key: string]: string };
  category: string;
  sentiment: string;
  impact: string;
  relatedCoins: string[];
  relatedStocks: string[];
  relatedEntities?: string[];
  primaryKeyword: string;
  secondaryKeywords: string[];
  tags?: string[];
  seoTitle?: string;
  metaTitle?: string;
  metaDescription: string;
  author?: string;
  authorAvatar?: string;
  telegram?: string;
  slug?: string;
  focusKeyword?: string;
  categories?: string[];
  seoHeadlines?: string[];
  ctrHeadlines?: string[];
  socialHeadlines?: string[];
  peopleAlsoAsk?: string[];
  relatedSearches?: string[];
  longTailKeywords?: string[];
  indexingNotes?: { primaryKeyword: string; searchIntent: string; category: string; tags: string[]; entityCoverage: string[] };
  searchConsoleReadiness?: number;
  adsenseReadiness?: number;
  seoScore?: number;
  geoScore?: number;
  authorityScore?: number;
  aiCitationPotential?: number;
  featuredImagePrompt?: string;
  imageFilename?: string;
  imageAltText?: string;
  imageCaption?: string;
  imageTitle?: string;
  publishedAt: string;
}'''


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')[:80]


def js_str(value) -> str:
    """Escape a value for TypeScript string literal."""
    if value is None:
        return '""'
    s = str(value)
    # Escape backslashes, quotes, newlines, tabs
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "")
    s = s.replace("\t", "\\t")
    return f'"{s}"'


def js_array(arr) -> str:
    """Format a Python list as a TypeScript array literal."""
    if not arr:
        return "[]"
    items = [js_str(item) for item in arr]
    return "[" + ", ".join(items) + "]"


def parse_iso(value: str):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def extract_existing_articles(ts_text: str):
    """Return existing article blocks from newsData.ts with id/date metadata."""
    m = re.search(r'export\s+const\s+newsArticles\s*:\s*NewsArticle\[\]\s*=\s*\[', ts_text)
    if not m:
        return []

    array_start = m.end()
    depth = 0
    array_end = -1
    for i in range(array_start, len(ts_text)):
        ch = ts_text[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            if depth == 0:
                array_end = i
                break
            depth -= 1
    if array_end == -1:
        return []

    articles_text = ts_text[array_start + 1:array_end]
    blocks = []
    depth = 0
    in_string = False
    escape_next = False
    block_start = None

    for pos, ch in enumerate(articles_text):
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
        if not in_string:
            if ch == '{':
                depth += 1
                if depth == 1:
                    line_start = articles_text.rfind('\n', 0, pos)
                    block_start = line_start + 1 if line_start >= 0 else 0
            elif ch == '}':
                depth -= 1
                if depth == 0 and block_start is not None:
                    text = articles_text[block_start:pos + 1].rstrip().rstrip(',')
                    id_m = re.search(r'\bid:\s*"((?:[^"\\]|\\.)*)"', text)
                    pub_m = re.search(r'\bpublishedAt:\s*"((?:[^"\\]|\\.)*)"', text)
                    if id_m:
                        blocks.append({
                            "id": id_m.group(1),
                            "publishedAt": parse_iso(pub_m.group(1)) if pub_m else None,
                            "text": text,
                        })
                    block_start = None
    return blocks



def convert_article(a: dict) -> str:
    """Convert a premium JSON article dict into a TypeScript NewsArticle object literal."""
    headline = a.get("headline", "Untitled")
    slug = a.get("slug", slugify(headline))
    article_id = a.get("id", f"premium-{slug}")

    # Map premium fields to TypeScript fields
    subheadline = a.get("introduction", "")[:150]
    key_highlights = a.get("key_takeaways", [])
    executive_summary = a.get("summary", "")
    market_background = a.get("background", "")
    expert_insights = a.get("expert_analysis", "")
    conclusion = a.get("conclusion", "")
    outlook = a.get("what_happens_next", a.get("conclusion", ""))

    # Build detailedAnalysis from main_story + market_impact + industry_impact + why_it_matters
    main_story = a.get("main_story", "")
    market_impact = a.get("market_impact", "")
    industry_impact = a.get("industry_impact", "")
    why_it_matters = a.get("why_it_matters", "")
    sections = [s for s in [main_story, market_impact, industry_impact, why_it_matters] if s]
    detailed_analysis = "\n\n".join(sections)

    # FAQ
    faq = a.get("faq", [])
    faq_entries = []
    for qa in faq:
        q = qa.get("question", "")
        ans = qa.get("answer", "")
        if q and ans:
            faq_entries.append(f'    {{ question: {js_str(q)}, answer: {js_str(ans)} }}')
    faq_ts = "[\n" + ",\n".join(faq_entries) + "\n  ]" if faq_entries else "undefined"

    # Tags
    tags = a.get("tags", [])
    if not tags:
        tags = [a.get("category", "Trending")]

    # Primary keyword
    primary_kw = a.get("primary_keyword", "")
    secondary_kws = a.get("secondary_keywords", [])
    long_tail_kws = a.get("long_tail_keywords", [])

    # Sources
    sources = a.get("sources_referenced", [])

    # Category
    category = a.get("category", "Trending").lower()

    # Sentiment & impact — derive from scores
    overall_score = a.get("overallOpportunityScore", 50)
    if overall_score >= 75:
        sentiment = "bullish"
    elif overall_score >= 50:
        sentiment = "neutral"
    else:
        sentiment = "bearish"
    if overall_score >= 70:
        impact = "high"
    elif overall_score >= 50:
        impact = "medium"
    else:
        impact = "low"

    # SEO fields
    seo_title = a.get("seo_title", a.get("seoTitle", headline))
    meta_title = a.get("meta_title", a.get("metaTitle", headline))
    meta_description = a.get("meta_description", a.get("metaDescription", executive_summary[:160] or headline))

    # Image prompt
    featured_image_prompt = a.get("featuredImagePrompt", "")
    image_alt_text = a.get("imageAltText", a.get("imageSeoTitle", ""))
    image_caption = a.get("imageCaption", "")

    # Use real images from fetched JSON data if available
    real_images = a.get("images", [])
    if real_images and isinstance(real_images, list) and len(real_images) > 0:
        img_lines = []
        for img in real_images[:4]:
            img_lines.append('      {')
            img_lines.append(f'        url: {js_str(img.get("url", ""))},')
            img_lines.append(f'        alt: {js_str(img.get("alt", image_alt_text))},')
            img_lines.append(f'        attribution: {js_str(img.get("attribution", "Photo via Unsplash"))},')
            if img.get("title"):
                img_lines.append(f'        title: {js_str(img.get("title", ""))},')
            if img.get("caption"):
                img_lines.append(f'        caption: {js_str(img.get("caption", ""))},')
            if img.get("category"):
                img_lines.append(f'        category: {js_str(img.get("category", category))},')
            if img.get("sourceUrl"):
                img_lines.append(f'        sourceUrl: {js_str(img.get("sourceUrl", ""))},')
            if img.get("photoId"):
                img_lines.append(f'        photoId: {js_str(img.get("photoId", ""))},')
            img_lines.append('      },')
        images_ts = "[\n" + "\n".join(img_lines) + "\n    ]"
    elif image_alt_text:
        # Fallback: build placeholder image entry from the prompt data
        placeholder_image = (
            f'{{ url: "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=1080",'
            f' alt: {js_str(image_alt_text)},'
            f' attribution: "Photo by Unsplash (via PulseTrends)",'
            f' caption: {js_str(image_caption or image_alt_text)},'
            f' category: {js_str(category)} }}'
        )
        images_ts = f'[{placeholder_image}]'
    else:
        images_ts = '[]'

    # Published date
    published_at = a.get("publishedAt", CURRENT_DATE)

    # Investor takeaways (from key_takeaways if available)
    investor_takeaways = key_highlights[:3] if key_highlights else []

    # Build the object literal line by line
    lines = []
    lines.append("  {")
    lines.append(f'    id: {js_str(article_id)},')
    lines.append(f'    headline: {js_str(headline)},')
    lines.append(f'    author: "Shiva Sandeep",')
    lines.append(f'    authorAvatar: "/author-avatar.jpg",')
    lines.append(f'    telegram: "its_terabyte",')
    lines.append(f'    subheadline: {js_str(subheadline)},')
    lines.append(f'    keyHighlights: {js_array(key_highlights)},')
    lines.append(f'    executiveSummary: {js_str(executive_summary)},')
    lines.append(f'    marketBackground: {js_str(market_background)},')
    lines.append(f'    detailedAnalysis: {js_str(detailed_analysis)},')
    lines.append(f'    expertInsights: {js_str(expert_insights)},')
    lines.append(f'    financialMetrics: {{ tableCaption: "Key Metrics", headers: ["Metric", "Value"], rows: [] }},')
    lines.append(f'    risks: [],')
    lines.append(f'    opportunities: [],')
    lines.append(f'    outlook: {js_str(outlook)},')
    lines.append(f'    conclusion: {js_str(conclusion)},')
    lines.append(f'    frequentlyAskedQuestions: {faq_ts},')
    lines.append(f'    investorTakeaways: {js_array(investor_takeaways)},')
    lines.append(f'    sourcesReferenced: {js_array(sources)},')
    lines.append(f'    aiAnalysis: null,')
    lines.append(f'    images: {images_ts},')
    lines.append(f'    category: {js_str(category)},')
    lines.append(f'    sentiment: {js_str(sentiment)},')
    lines.append(f'    impact: {js_str(impact)},')
    lines.append(f'    relatedCoins: [],')
    lines.append(f'    relatedStocks: [],')
    lines.append(f'    primaryKeyword: {js_str(primary_kw)},')
    lines.append(f'    secondaryKeywords: {js_array(secondary_kws)},')
    lines.append(f'    tags: {js_array(tags)},')
    lines.append(f'    seoTitle: {js_str(seo_title)},')
    lines.append(f'    metaTitle: {js_str(meta_title)},')
    lines.append(f'    metaDescription: {js_str(meta_description)},')
    lines.append(f'    slug: {js_str(slug)},')
    lines.append(f'    focusKeyword: {js_str(primary_kw)},')
    lines.append(f'    longTailKeywords: {js_array(long_tail_kws)},')
    lines.append(f'    featuredImagePrompt: {js_str(featured_image_prompt)},')
    lines.append(f'    imageAltText: {js_str(image_alt_text)},')
    lines.append(f'    imageCaption: {js_str(image_caption)},')
    lines.append(f'    publishedAt: {js_str(published_at)},')
    lines.append("  },")
    return "\n".join(lines)


def main() -> int:
    if not PREMIUM_FILE.exists():
        print(f"[ERROR] Premium file not found: {PREMIUM_FILE}")
        print("Run scripts/generate-premium-news.py first.")
        return 1

    with open(PREMIUM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    if not articles:
        print("[ERROR] No articles in premium output")
        return 1

    existing = []
    if NEWS_DATA_FILE.exists():
        existing_text = NEWS_DATA_FILE.read_text(encoding="utf-8")
        existing = extract_existing_articles(existing_text)

    cutoff = datetime.now(timezone.utc) - timedelta(days=20)
    merged = []

    for art in existing:
        if art["publishedAt"] and art["publishedAt"] >= cutoff:
            merged.append(art)

    for article in articles:
        converted = convert_article(article)
        pub = article.get("publishedAt") or CURRENT_DATE
        merged.append({
            "id": article.get("id", ""),
            "publishedAt": parse_iso(pub) or datetime.now(timezone.utc),
            "text": converted.rstrip().rstrip(','),
        })

    deduped = {}
    for item in merged:
        key = item["id"]
        prev = deduped.get(key)
        if not prev or (item["publishedAt"] and prev["publishedAt"] and item["publishedAt"] > prev["publishedAt"]):
            deduped[key] = item

    ordered = sorted(deduped.values(), key=lambda x: x["publishedAt"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    print(f"Converting {len(articles)} premium articles to TypeScript...")
    print(f"Merging with {len(existing)} existing article(s), keeping {len(ordered)} within 20 days...")

    ts_parts = [INTERFACE_DEFS, "", "export const newsArticles: NewsArticle[] = ["]
    for i, item in enumerate(ordered):
        if i > 0:
            ts_parts.append("")
        ts_parts.append(item["text"] + ",")
    ts_parts.append("];")
    ts_parts.append("")

    content = "\n".join(ts_parts)

    NEWS_DATA_FILE.write_text(content, encoding="utf-8")
    print(f"Written {len(articles)} articles to {NEWS_DATA_FILE}")
    print(f"File size: {NEWS_DATA_FILE.stat().st_size / 1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
