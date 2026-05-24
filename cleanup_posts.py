from datetime import datetime, timedelta
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent / "_posts"
CUTOFF = datetime.utcnow() - timedelta(days=90)

deleted = 0
for f in sorted(POSTS_DIR.glob("*.md")):
    try:
        date_str = f.name[:10]
        post_date = datetime.strptime(date_str, "%Y-%m-%d")
        if post_date < CUTOFF:
            f.unlink()
            deleted += 1
            print(f"Deleted: {f.name}")
    except (ValueError, IndexError):
        pass

if deleted:
    print(f"Cleaned up {deleted} old post(s) older than 90 days")
else:
    print("No posts older than 90 days to clean up")
