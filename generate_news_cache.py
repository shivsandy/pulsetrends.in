import os
import sys
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
NEWS_CACHE_FILE = DATA_DIR / "news_cache.json"
NEWS_LOCK_FILE = DATA_DIR / "news_cache.lock"
MAX_AGE_SECONDS = 24 * 3600


def is_cache_fresh() -> bool:
    if not NEWS_CACHE_FILE.exists():
        return False
    try:
        age = time.time() - NEWS_CACHE_FILE.stat().st_mtime
        if age < MAX_AGE_SECONDS:
            print(f"[NewsCache] Using existing cache (age: {age/3600:.1f}h)")
            return True
    except Exception:
        pass
    return False


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if NEWS_LOCK_FILE.exists():
        print("[NewsCache] Lock file present, skipping refresh")
        if NEWS_CACHE_FILE.exists():
            return 0
        try:
            NEWS_LOCK_FILE.unlink()
        except Exception:
            pass

    if is_cache_fresh():
        return 0

    NEWS_LOCK_FILE.write_text("locked")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import news_api
        news_api.validate_env()
        cached = news_api.load_cached_news()
        if cached:
            from news_api import NEWS_CACHE, CACHE_LOCK
            with CACHE_LOCK:
                NEWS_CACHE.clear()
                NEWS_CACHE.extend(cached)
        news_api.refresh_news()
    except Exception as e:
        print(f"[NewsCache] Refresh failed: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            NEWS_LOCK_FILE.unlink()
        except Exception:
            pass

    if NEWS_CACHE_FILE.exists():
        size_kb = NEWS_CACHE_FILE.stat().st_size / 1024
        print(f"[NewsCache] OK ({size_kb:.1f} KB)")
        return 0
    print("[NewsCache] No cache file produced (site will show FALLBACK_NEWS this cycle)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
