import json
import os
import sys
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CRYPTO_FILE = os.path.join(DATA_DIR, "crypto_data.json")
AIRDROP_IO_FILE = os.path.join(DATA_DIR, "airdrops_data.json")
AIRDROPALERT_FILE = os.path.join(DATA_DIR, "airdropalert_data.json")


def load_airdrops_io() -> list[dict]:
    try:
        with open(AIRDROP_IO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("airdrops", [])
        for it in items:
            it.setdefault("category", "airdrop")
            it.setdefault("chain", "")
            it.setdefault("estimated_value", "")
            it.setdefault("eligibility", "")
            it.setdefault("farming_guide", "")
            it.setdefault("tge_date", "")
            it.setdefault("website", "")
            it.setdefault("social_links", {})
            it.setdefault("steps", [])
            it.setdefault("available_from", "")
            it.setdefault("source", "airdrops.io")
        print(f"[Collector] Airdrops.io: {len(items)}")
        return items
    except (FileNotFoundError, json.JSONDecodeError):
        print("[Collector] No airdrops.io data found")
        return []


def load_airdropalert() -> list[dict]:
    try:
        with open(AIRDROPALERT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("airdrops", [])
        for it in items:
            it.setdefault("category", "airdrop")
            it.setdefault("chain", "")
            it.setdefault("estimated_value", "")
            it.setdefault("eligibility", "")
            it.setdefault("farming_guide", "")
            it.setdefault("tge_date", "")
            it.setdefault("website", "")
            it.setdefault("social_links", {})
            it.setdefault("steps", [])
            it.setdefault("available_from", "")
            it.setdefault("source", "airdropalert")
        print(f"[Collector] AirdropAlert: {len(items)}")
        return items
    except (FileNotFoundError, json.JSONDecodeError):
        print("[Collector] No airdropalert data found")
        return []


def normalize_name(name: str) -> str:
    return name.strip().lower().replace(" ", "").replace("-", "").replace("_", "")


def merge_airdrops(sources: list[list[dict]]) -> list[dict]:
    seen = {}
    for batch in sources:
        for ad in batch:
            key = normalize_name(ad.get("name", ""))
            if not key:
                continue
            if key in seen:
                existing = seen[key]
                # merge fields: prefer non-empty from newer source
                for field in ["description", "chain", "estimated_value", "eligibility",
                              "farming_guide", "tge_date", "website", "steps",
                              "available_from", "status"]:
                    new_val = ad.get(field)
                    old_val = existing.get(field)
                    if new_val and not old_val:
                        existing[field] = new_val
                # merge social links
                new_social = ad.get("social_links", {})
                old_social = existing.get("social_links", {})
                if isinstance(new_social, dict) and isinstance(old_social, dict):
                    merged = dict(old_social)
                    for k, v in new_social.items():
                        if v and not merged.get(k):
                            merged[k] = v
                    existing["social_links"] = merged
                # merge steps
                new_steps = ad.get("steps", [])
                old_steps = existing.get("steps", [])
                if new_steps and not old_steps:
                    existing["steps"] = new_steps
            else:
                seen[key] = dict(ad)

    merged = list(seen.values())
    print(f"[Collector] Merged: {len(merged)} unique airdrops")
    return merged


def needs_data_refresh() -> bool:
    try:
        with open(CRYPTO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        last = data.get("last_updated", "")
        if last:
            updated = datetime.fromisoformat(last)
            age = datetime.now(timezone.utc).astimezone() - updated
            if age.days < 2:
                print(f"[Collector] Data is {age.days}d old, skipping collection")
                return False
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        pass
    return True


def load_cached() -> list[dict]:
    try:
        with open(CRYPTO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("projects", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def collect_all() -> list[dict]:
    if not needs_data_refresh():
        cached = load_cached()
        if cached:
            return cached

    sources = [load_airdrops_io(), load_airdropalert()]
    merged = merge_airdrops(sources)
    return merged


def save(data: list[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    output = {
        "last_updated": datetime.now(timezone.utc).astimezone().isoformat(),
        "total": len(data),
        "projects": data,
    }
    with open(CRYPTO_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[Collector] Saved {len(data)} airdrops to {CRYPTO_FILE}")


if __name__ == "__main__":
    data = collect_all()
    save(data)
