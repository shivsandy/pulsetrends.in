import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CRYPTO_FILE = os.path.join(DATA_DIR, "crypto_data.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "crypto_projects.json")
AIRDROP_IO_FILE = os.path.join(DATA_DIR, "airdrops_data.json")
AIRDROPALERT_FILE = os.path.join(DATA_DIR, "airdropalert_data.json")
AIRDROPS_CACHE_DIR = os.path.join(DATA_DIR, "airdrop_sources")

AIRDROPS_IO_URL = "https://airdrops.io"
AIRDROPS_ALERT_URL = "https://airdropalert.com"
MIN_AIRDROP_COUNT = 40

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(AIRDROPS_CACHE_DIR, exist_ok=True)


def _setdefault(it, source: str):
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
    it.setdefault("description", "")
    it.setdefault("heat_score", "")
    it.setdefault("status", "active")
    it["source"] = source
    return it


def load_airdrops_io() -> list[dict]:
    cache_path = os.path.join(AIRDROPS_CACHE_DIR, "airdrops_io.json")
    try:
        with open(AIRDROP_IO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("airdrops", [])
        for it in items:
            _setdefault(it, "airdrops.io")
        print(f"[Collector] airdrops.io (cached): {len(items)}")
        return items
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("airdrops", [])
            for it in items:
                _setdefault(it, "airdrops.io")
            print(f"[Collector] airdrops.io (disk cache): {len(items)}")
            return items
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    try:
        resp = requests.get(AIRDROPS_IO_URL, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"[Collector] airdrops.io fetch failed: HTTP {resp.status_code}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        cards = soup.select("article") or soup.find_all("div", class_=re.compile(r"airdrop|item|card|post", re.I))
        for card in cards:
            name_el = card.select_one("h1, h2, h3, h4, .title, .name")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 2:
                continue
            link_el = card.select_one("a[href*='airdrops.io']") or name_el.find_parent("a")
            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                href = AIRDROPS_IO_URL + href
            if "airdrops.io" not in href:
                continue
            desc_el = card.select_one("p, .description, .desc")
            description = desc_el.get_text(strip=True) if desc_el else ""
            chain_el = card.select_one(".chain, [class*='chain']")
            chain = chain_el.get_text(strip=True) if chain_el else ""
            items.append({
                "id": name.lower().replace(" ", "-"),
                "name": name,
                "url": href,
                "description": description,
                "chain": chain,
                "status": "active",
                "category": "airdrop",
                "source": "airdrops.io",
            })
        items = [_setdefault(it, "airdrops.io") for it in items]
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"airdrops": items}, f, indent=2, ensure_ascii=False)
        print(f"[Collector] airdrops.io (scraped): {len(items)}")
        return items
    except Exception as e:
        print(f"[Collector] airdrops.io scrape error: {e}")
        return []


def load_airdropalert() -> list[dict]:
    cache_path = os.path.join(AIRDROPS_CACHE_DIR, "airdropalert.json")
    try:
        with open(AIRDROPALERT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("airdrops", [])
        for it in items:
            _setdefault(it, "airdropalert")
        print(f"[Collector] airdropalert (cached): {len(items)}")
        return items
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("airdrops", [])
            for it in items:
                _setdefault(it, "airdropalert")
            print(f"[Collector] airdropalert (disk cache): {len(items)}")
            return items
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    try:
        resp = requests.get(AIRDROPS_ALERT_URL, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"[Collector] airdropalert fetch failed: HTTP {resp.status_code}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        cards = soup.select(".airdrop-card, .airdrop-item, article")
        for card in cards:
            name_el = card.select_one("h2, h3, .airdrop-name, .title")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 2:
                continue
            link_el = card.select_one("a[href]")
            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                href = AIRDROPS_ALERT_URL + href
            desc_el = card.select_one("p, .airdrop-desc, .description")
            description = desc_el.get_text(strip=True) if desc_el else ""
            items.append({
                "id": name.lower().replace(" ", "-"),
                "name": name,
                "url": href,
                "description": description,
                "status": "active",
                "category": "airdrop",
                "source": "airdropalert",
            })
        items = [_setdefault(it, "airdropalert") for it in items]
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"airdrops": items}, f, indent=2, ensure_ascii=False)
        print(f"[Collector] airdropalert (scraped): {len(items)}")
        return items
    except Exception as e:
        print(f"[Collector] airdropalert scrape error: {e}")
        return []


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def merge_airdrops(sources: list[list[dict]]) -> list[dict]:
    seen: dict = {}
    for batch in sources:
        for ad in batch:
            key = normalize_name(ad.get("name", ""))
            if not key:
                continue
            if key in seen:
                existing = seen[key]
                for field in ["description", "chain", "estimated_value", "eligibility",
                              "farming_guide", "tge_date", "website", "steps",
                              "available_from", "status", "url", "heat_score"]:
                    new_val = ad.get(field)
                    old_val = existing.get(field)
                    if new_val and not old_val:
                        existing[field] = new_val
                new_social = ad.get("social_links", {})
                old_social = existing.get("social_links", {})
                if isinstance(new_social, dict) and isinstance(old_social, dict):
                    merged = dict(old_social)
                    for k, v in new_social.items():
                        if v and not merged.get(k):
                            merged[k] = v
                    existing["social_links"] = merged
            else:
                seen[key] = dict(ad)
    merged = list(seen.values())
    print(f"[Collector] Merged: {len(merged)} unique airdrops")
    return merged


def pad_airdrops(airdrops: list[dict], target: int = MIN_AIRDROP_COUNT) -> list[dict]:
    if len(airdrops) >= target:
        return airdrops
    print(f"[Collector] Airdrops below target ({len(airdrops)} < {target}), attempting to pad")
    fallback = load_airdropalert()
    if not fallback:
        return airdrops
    existing_names = {normalize_name(a.get("name", "")) for a in airdrops}
    added = 0
    for ad in fallback:
        if len(airdrops) >= target:
            break
        if normalize_name(ad.get("name", "")) in existing_names:
            continue
        airdrops.append(ad)
        existing_names.add(normalize_name(ad.get("name", "")))
        added += 1
    print(f"[Collector] Padded with {added} airdrops from airdropalert, total now {len(airdrops)}")
    return airdrops


def load_crypto_projects() -> list[dict]:
    try:
        with open(PROJECTS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("projects", [])
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"[Collector] {PROJECTS_FILE} not found, returning empty list")
        return []


def needs_data_refresh() -> bool:
    try:
        with open(CRYPTO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        last = data.get("last_updated", "")
        if last:
            updated = datetime.fromisoformat(last.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_days = (now - updated).days
            if age_days < 2:
                print(f"[Collector] Data is {age_days}d old, skipping collection")
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
    crypto_projects = load_crypto_projects()
    print(f"[Collector] Loaded {len(crypto_projects)} base crypto projects from {PROJECTS_FILE}")
    airdrops_io = load_airdrops_io()
    time.sleep(1)
    airdropalert = load_airdropalert()
    airdrops = merge_airdrops([airdrops_io, airdropalert])
    airdrops = pad_airdrops(airdrops, MIN_AIRDROP_COUNT)
    for a in airdrops:
        a.setdefault("ticker", a.get("name", "")[:6].upper())
    combined = crypto_projects + airdrops
    print(f"[Collector] Combined: {len(crypto_projects)} crypto + {len(airdrops)} airdrops = {len(combined)} total")
    return combined


def save(data: list[dict]):
    _ensure_dirs()
    output = {
        "last_updated": datetime.now(timezone.utc).astimezone().isoformat(),
        "total": len(data),
        "projects": data,
    }
    with open(CRYPTO_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[Collector] Saved {len(data)} projects to {CRYPTO_FILE}")


if __name__ == "__main__":
    _ensure_dirs()
    data = collect_all()
    save(data)
