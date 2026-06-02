import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "airdrops_data.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

BASE_URL = "https://airdrops.io"


def load_cache() -> dict:
    try:
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(data: list):
    os.makedirs(DATA_DIR, exist_ok=True)
    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total": len(data),
        "airdrops": data,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[Airdrops Scraper] Saved {len(data)} airdrops to {OUTPUT_FILE}")


def needs_refresh() -> bool:
    try:
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            data = json.load(f)
        last = data.get("last_updated", "")
        if last:
            updated = datetime.fromisoformat(last)
            age = datetime.now(timezone.utc) - updated
            if age.days < 2:
                print(f"[Airdrops Scraper] Data is {age.days}d old, skipping refresh")
                return False
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        pass
    return True


def scrape_listing() -> list[dict]:
    print("[Airdrops Scraper] Fetching homepage...")
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    airdrops = []
    seen_names = set()

    cards = soup.select("article, .airdrop-item, .entry, .post, [class*=airdrop]")
    if not cards:
        cards = soup.find_all("article") or soup.find_all("div", class_=re.compile(r"airdrop|item|card|post"))

    for card in cards:
        try:
            name_el = card.select_one("h2, h3, h4, .entry-title, .title, strong")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 2 or name.lower() in seen_names:
                continue

            link_el = card.select_one("a[href*='airdrops.io']") or name_el.find_parent("a")
            link = ""
            if link_el:
                href = link_el.get("href", "")
                if isinstance(href, str) and href.startswith("/"):
                    href = BASE_URL + href
                if "airdrops.io" in href:
                    link = href

            text = card.get_text(separator=" ", strip=True)

            status = "ongoing"
            if "confirmed" in text.lower():
                status = "confirmed"

            heat_match = re.search(r'(\d+)°', text)
            heat_score = int(heat_match.group(1)) if heat_match else 0

            description = text[:300] if len(text) > 300 else text
            description = re.sub(r'\s+', ' ', description).strip()

            seen_names.add(name.lower())
            airdrops.append({
                "id": re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_'),
                "name": name,
                "status": status,
                "heat_score": heat_score,
                "description": description,
                "url": link,
                "category": "airdrop",
                "chain": "",
                "estimated_value": "",
                "eligibility": "",
                "farming_guide": "",
                "tge_date": "",
                "source": "airdrops.io",
            })
        except Exception:
            pass

    print(f"[Airdrops Scraper] Found {len(airdrops)} airdrops from listing")
    return airdrops


def scrape_detail(url: str) -> dict:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        result = {}

        chain_match = re.search(r'(?:Chain|Network|Blockchain)\s*:?\s*(\w+(?:\s*\w+)*)', text, re.I)
        if chain_match:
            result["chain"] = chain_match.group(1).strip()

        value_match = re.search(r'(?:Estimated\s*Value|Value|Worth)\s*:?\s*(\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?)', text, re.I)
        if value_match:
            result["estimated_value"] = value_match.group(1).strip()

        tge_match = re.search(r'(?:TGE|Token\s*Generation|Launch\s*Date)\s*:?\s*(\w+\s*\d{1,2},?\s*\d{4})', text, re.I)
        if tge_match:
            result["tge_date"] = tge_match.group(1).strip()

        return result
    except Exception:
        return {}


def scrape():
    if not needs_refresh():
        return

    airdrops = scrape_listing()

    for i, ad in enumerate(airdrops):
        if ad["url"]:
            detail = scrape_detail(ad["url"])
            ad.update(detail)
            time.sleep(0.5)
        if (i + 1) % 10 == 0:
            print(f"[Airdrops Scraper] Processed {i + 1}/{len(airdrops)} details")

    save_cache(airdrops)


if __name__ == "__main__":
    scrape()
