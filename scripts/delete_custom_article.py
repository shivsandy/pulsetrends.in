#!/usr/bin/env python3
"""
delete_custom_article.py — Delete specific articles from newsData.ts by URL.

Takes article URLs (e.g. from GitHub workflow input), extracts the article ID
from each URL, finds and removes the matching article(s) from the newsArticles
array, and writes back the file.

Usage:
    python scripts/delete_custom_article.py
    DELETE_URLS="https://pulsetrends.in/news/some-slug-news-12345-6789" python scripts/delete_custom_article.py
    DELETE_URLS="url1,url2,url3" python scripts/delete_custom_article.py

URL format expected:
    https://pulsetrends.in/news/{slugified-headline}-news-{timestamp}-{random}
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NEWS_TS_PATH = PROJECT_ROOT / "src" / "data" / "newsData.ts"

DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")


def extract_article_ids_from_urls(urls_text: str) -> list[str]:
    """Parse article URLs and extract news article IDs."""
    if not urls_text:
        return []

    # Split by newlines, commas, or spaces
    urls = re.split(r'[\n,]+', urls_text)
    ids = []

    for url in urls:
        url = url.strip()
        if not url:
            continue

        # Parse the URL path
        parsed = urlparse(url)
        path = parsed.path.rstrip('/')

        # Extract the last path segment (the slug with ID)
        last_segment = path.split('/')[-1] if '/' in path else path

        # The article ID is at the end of the slug, format: news-{digits}-{digits}
        match = re.search(r'(news-\d+-\d+)$', last_segment)
        if match:
            article_id = match.group(1)
            ids.append(article_id)
            print(f"  [OK] Extracted ID '{article_id}' from URL")
        else:
            # Try direct fallback: maybe the user just pasted an ID or a slug
            # Check if it looks like a news ID
            direct_match = re.match(r'^(news-\d+-\d+)$', last_segment)
            if direct_match:
                ids.append(last_segment)
                print(f"  [OK] Direct ID match: '{last_segment}'")
            else:
                # Try matching by slug in the file
                print(f"  [!] Could not extract ID from URL: {url}")
                print(f"    Last segment: {last_segment}")

    return ids


def load_article_blocks(content: str) -> list[dict]:
    """Parse newsData.ts and return article blocks with their IDs."""
    match = re.search(r'export\s+const\s+newsArticles\s*:\s*NewsArticle\[\]\s*=\s*\[', content)
    if not match:
        print("ERROR: Could not find newsArticles array")
        return []

    array_start_idx = match.end()
    before_array = content[:match.start()]

    # Find matching closing bracket
    depth = 0
    array_end_idx = -1
    for i in range(array_start_idx, len(content)):
        ch = content[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            if depth == 0:
                array_end_idx = i
                break
            depth -= 1
    if array_end_idx == -1:
        print("ERROR: Could not find matching ']'")
        return []

    after_array = content[array_end_idx + 1:]
    articles_text = content[array_start_idx + 1:array_end_idx]

    # Parse individual articles by tracking brace depth
    raw_articles = []
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
                    block_text = articles_text[block_start:pos + 1]
                    raw_articles.append({
                        "text": block_text,
                        "block_start": block_start,
                        "block_end": pos + 1,
                    })
                    block_start = None

    # Extract IDs from each article
    article_entries = []
    for art in raw_articles:
        id_match = re.search(r'id:\s*"([^"]+)"', art["text"])
        article_id = id_match.group(1) if id_match else ""
        article_entries.append({
            "id": article_id,
            "text": art["text"],
        })

    return article_entries


def main() -> int:
    if not NEWS_TS_PATH.exists():
        print(f"ERROR: {NEWS_TS_PATH} not found")
        return 1

    # Get URLs from environment
    urls_text = os.environ.get("DELETE_URLS", "")
    if not urls_text:
        print("ERROR: No DELETE_URLS environment variable set.")
        print("Usage: DELETE_URLS='https://pulsetrends.in/news/some-url...' python scripts/delete_custom_article.py")
        return 1

    # Extract article IDs from URLs
    print(f"Parsing article URLs...")
    to_delete_ids = extract_article_ids_from_urls(urls_text)

    if not to_delete_ids:
        print("ERROR: Could not extract any valid article IDs from the provided URLs.")
        print("Make sure URLs follow the pattern: https://pulsetrends.in/news/{slug}-news-{timestamp}-{random}")
        return 1

    print(f"\nFound {len(to_delete_ids)} article ID(s) to delete: {to_delete_ids}")

    # Read the file
    with open(NEWS_TS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Load all articles
    articles = load_article_blocks(content)
    if not articles:
        print("ERROR: No articles found in the file")
        return 1

    print(f"Loaded {len(articles)} articles from file")

    # Find the array boundaries again
    match = re.search(r'export\s+const\s+newsArticles\s*:\s*NewsArticle\[\]\s*=\s*\[', content)
    before_array = content[:match.start()]

    array_start_idx = match.end()
    depth = 0
    array_end_idx = -1
    for i in range(array_start_idx, len(content)):
        ch = content[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            if depth == 0:
                array_end_idx = i
                break
            depth -= 1
    after_array = content[array_end_idx + 1:]

    # Find which articles to remove
    to_remove_set = set(to_delete_ids)
    kept_articles = []
    removed = []
    ids_in_file = set()

    for art in articles:
        ids_in_file.add(art["id"])
        if art["id"] in to_remove_set:
            removed.append(art)
        else:
            kept_articles.append(art)

    # Report which IDs were not found
    not_found = to_remove_set - ids_in_file
    for missing_id in not_found:
        print(f"  [!] Article ID '{missing_id}' was NOT found in the file")

    if not removed:
        print("ERROR: None of the provided article IDs were found in the file.")
        return 1

    print(f"\nRemoving {len(removed)} article(s):")
    for r in removed:
        print(f"  - {r['id']}")
    print(f"Keeping {len(kept_articles)} article(s)")

    # Safety: keep at least 1 article
    if len(kept_articles) == 0:
        print("ERROR: Would remove ALL articles. Aborting to keep at least 1.")
        return 1

    # Reconstruct the file
    lines_out = []
    lines_out.append(before_array.strip())
    lines_out.append("export const newsArticles: NewsArticle[] = [")

    for i, entry in enumerate(kept_articles):
        lines_out.append(entry["text"])
        if i < len(kept_articles) - 1:
            lines_out[-1] += ","

    lines_out.append("];")
    after_stripped = after_array.strip()
    if after_stripped:
        lines_out.append(after_stripped)

    new_content = "\n".join(lines_out)

    # Verify the reconstruction
    new_count = len(re.findall(r'\bid:\s*"(news-[^"]+)"', new_content))
    expected_count = len(kept_articles)
    if new_count != expected_count:
        print(f"ERROR: Article count mismatch: expected {expected_count}, got {new_count}")
        return 1

    # Write back
    if DRY_RUN:
        print(f"\n[DRY RUN] Would write {len(kept_articles)} articles to {NEWS_TS_PATH}")
        print(f"[DRY RUN] Removed: {len(removed)}, Kept: {len(kept_articles)}")
    else:
        with open(NEWS_TS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"\nDone. Wrote {len(kept_articles)} articles to {NEWS_TS_PATH}")
        print(f"Removed: {len(removed)}, Kept: {len(kept_articles)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
