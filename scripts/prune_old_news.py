#!/usr/bin/env python3
"""
prune_old_news.py — Remove up to N articles older than M days from newsData.ts.

Reads src/data/newsData.ts, identifies articles whose publishedAt date is older
than MAX_AGE_DAYS, removes the oldest MAX_REMOVE_COUNT of them, and writes the
file back. After this, a build step will regenerate sitemaps + static pages.

Usage:
    python scripts/prune_old_news.py
    MAX_AGE_DAYS=2 MAX_REMOVE_COUNT=60 python scripts/prune_old_news.py
"""

import os
import re
import sys
from datetime import datetime, timezone, timedelta

# ── Config from environment ──────────────────────────────────────────
MAX_AGE_DAYS = int(os.environ.get("MAX_AGE_DAYS", "30"))
MAX_REMOVE_COUNT = int(os.environ.get("MAX_REMOVE_COUNT", "60"))
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")

# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_TS_PATH = os.path.join(PROJECT_ROOT, "src", "data", "newsData.ts")

if not os.path.exists(NEWS_TS_PATH):
    print(f"ERROR: {NEWS_TS_PATH} not found")
    sys.exit(1)

# ── Read file ─────────────────────────────────────────────────────────
with open(NEWS_TS_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# ── Find the newsArticles array ──────────────────────────────────────
match = re.search(r'export\s+const\s+newsArticles\s*:\s*NewsArticle\[\]\s*=\s*\[', content)
if not match:
    print("ERROR: Could not find 'export const newsArticles: NewsArticle[] = [' in file")
    sys.exit(1)

array_start_idx = match.end()  # position right after '['
before_array = content[:match.start()]

# Walk forward from array_start_idx to find matching ']'
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
    print("ERROR: Could not find matching ']' for newsArticles array")
    sys.exit(1)

after_array = content[array_end_idx + 1:]

# ── Parse individual article objects by tracking brace depth ─────────
articles_text = content[array_start_idx + 1:array_end_idx]  # text inside []

# Also capture any trailing text after the last article before ']'
# (there might be a trailing comma and whitespace)

raw_articles = []  # list of (start_pos_in_text, end_pos_in_text, text)

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
                # Find start of line for proper indentation
                line_start = articles_text.rfind('\n', 0, pos)
                block_start = line_start + 1 if line_start >= 0 else 0
        elif ch == '}':
            depth -= 1
            if depth == 0 and block_start is not None:
                block_text = articles_text[block_start:pos + 1]
                raw_articles.append({
                    "start": block_start,
                    "end": pos + 1,
                    "text": block_text,
                })
                block_start = None

if not raw_articles:
    print("ERROR: No article objects found in the array")
    sys.exit(1)

print(f"Found {len(raw_articles)} article(s) in newsData.ts")

# ── Extract id and publishedAt from each article ─────────────────────
def extract_field(text: str, field_name: str) -> str:
    """Extract the string value of a field from article TS text."""
    m = re.search(rf'\b{field_name}:\s*"((?:[^"\\]|\\.)*)"', text)
    return m.group(1) if m else ""

article_entries = []
for art in raw_articles:
    aid = extract_field(art["text"], "id") or "unknown"
    pub_str = extract_field(art["text"], "publishedAt") or ""

    pub_date = None
    if pub_str:
        try:
            pub_date = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    article_entries.append({
        "id": aid,
        "publishedAt": pub_date,
        "publishedAt_str": pub_str,
        "text": art["text"],
    })

# ── Find articles older than cutoff ──────────────────────────────────
now = datetime.now(timezone.utc)
cutoff = now - timedelta(days=MAX_AGE_DAYS)

old_articles = [a for a in article_entries if a["publishedAt"] and a["publishedAt"] < cutoff]
old_articles.sort(key=lambda a: a["publishedAt"])  # oldest first

print(f"  {len(old_articles)} article(s) older than {MAX_AGE_DAYS} day(s) (cutoff: {cutoff.isoformat()[:19]}Z)")

to_remove = old_articles[:MAX_REMOVE_COUNT]
remove_ids = {a["id"] for a in to_remove}

print(f"Removing {len(to_remove)} article(s) (max configured: {MAX_REMOVE_COUNT}):")
for a in to_remove:
    pub = a["publishedAt"].isoformat()[:19] if a["publishedAt"] else "no date"
    print(f"  - {a['id']}  (published: {pub})")

if len(to_remove) == 0:
    print("No articles to remove. Exiting.")
    sys.exit(0)

# ── Keep articles not in removal set ─────────────────────────────────
kept_entries = [a for a in article_entries if a["id"] not in remove_ids]

# Safety: keep at least 1 article (bypass when MAX_AGE_DAYS=0 for full wipe)
if len(kept_entries) == 0 and MAX_AGE_DAYS != 0:
    print("ERROR: Would remove ALL articles. Aborting to keep at least 1.")
    sys.exit(1)

# ── Reconstruct the file ─────────────────────────────────────────────
# Build the array body line by line, preserving formatting
lines_out = []
lines_out.append(before_array.strip())
lines_out.append("export const newsArticles: NewsArticle[] = [")

for i, entry in enumerate(kept_entries):
    lines_out.append(entry["text"])
    if i < len(kept_entries) - 1:
        lines_out[-1] += ","  # add comma between articles

lines_out.append("];")

# Append whatever was after the array (interface definitions remain)
after_stripped = after_array.strip()
if after_stripped:
    lines_out.append(after_stripped)

new_content = "\n".join(lines_out)

# ── Verify the output has the same number of articles ────────────────
new_article_count = len(re.findall(r'\bid:\s*"(news-[^"]+)"', new_content))
expected_count = len(kept_entries)
if new_article_count != expected_count:
    print(f"ERROR: Article count mismatch after reconstruction: expected {expected_count}, got {new_article_count}")
    sys.exit(1)

# ── Write back ───────────────────────────────────────────────────────
if DRY_RUN:
    print(f"\n[DRY RUN] Would write {len(kept_entries)} article(s) to {NEWS_TS_PATH}")
    print(f"[DRY RUN] Removed: {len(to_remove)}, Kept: {len(kept_entries)}")
else:
    with open(NEWS_TS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"\nDone. Wrote {len(kept_entries)} article(s) to {NEWS_TS_PATH}")
    print(f"Removed: {len(to_remove)}, Kept: {len(kept_entries)}")
