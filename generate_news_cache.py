import json
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
    cached = []
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

    # Safety: never overwrite cache if new version has < 50% of old article count
    if NEWS_CACHE_FILE.exists():
        try:
            with open(NEWS_CACHE_FILE, encoding="utf-8") as f:
                new_cache = json.load(f)
            if isinstance(new_cache, list):
                new_count = len(new_cache)
                # Compare with old cache if we had one
                if cached and isinstance(cached, list) and len(cached) > 5:
                    old_count = len(cached)
                    if new_count < old_count * 0.5:
                        print(f"[NewsCache] WARNING: New cache has {new_count} articles vs {old_count} old (>50% drop)")
                        print(f"[NewsCache] Preserving old cache to prevent data loss")
                        # Restore old cache
                        with open(NEWS_CACHE_FILE, "w", encoding="utf-8") as f:
                            json.dump(cached, f, indent=2, ensure_ascii=False)
                        print(f"[NewsCache] Restored old cache ({old_count} articles)")
                        return 0
                print(f"[NewsCache] OK ({new_count} articles, {NEWS_CACHE_FILE.stat().st_size / 1024:.1f} KB)")
            else:
                print(f"[NewsCache] Warning: cache is not a list")
        except Exception as e:
            print(f"[NewsCache] Safety check failed: {e}")
        return 0
    print("[NewsCache] No cache file produced (site will show FALLBACK_NEWS this cycle)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
