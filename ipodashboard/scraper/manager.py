import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .base import IPO
from .screener import ScreenerScraper
from .fivepaisa import FivePaisaScraper
from .finnhub import FinnhubScraper
from .iposcoop import IpoScoopScraper
from .renaissance import RenaissanceScraper
from .nse import NSEScraper
from .groww import GrowwScraper
from .zerodha import ZerodhaScraper
from .nasdaqapi import NasdaqApiScraper
from .ipo_analyzer import analyze as analyze_ipos


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DATA_FILE = os.path.join(DATA_DIR, "ipos.json")


STATUS_PRIORITY = {"upcoming": 0, "open": 1, "subscribed": 2, "listed": 3, "closed": 3}


def _normalise_name(name: str) -> str:
    n = name.strip().lower()
    n = n.rstrip(".").strip()
    for suffix in [" ltd", " limited", " l", " pvt", " private", " ltd.", " pvt.", " private limited"]:
        if n.endswith(suffix):
            n = n[: -len(suffix)]
    n = n.strip()
    return n


def _dates_match(a: IPO, b: IPO) -> bool:
    return a.open_date == b.open_date and a.close_date == b.close_date


def _find_matching_key(raw_name: str, ipo: IPO, seen: Dict[str, IPO], name_mapping: Dict[str, str]) -> str:
    key = _normalise_name(raw_name)
    if key in seen:
        return key

    cleaned = raw_name.strip().lower().rstrip(".").strip()

    if ipo.symbol:
        for existing_key, existing_ipo in seen.items():
            if existing_ipo.symbol and existing_ipo.symbol.upper() == ipo.symbol.upper():
                return existing_key

    for existing_key, existing_ipo in seen.items():
        existing_raw = name_mapping.get(existing_key, "").lower().rstrip(".").strip()
        if existing_raw == cleaned:
            return existing_key
        if _dates_match(ipo, existing_ipo):
            if cleaned in existing_raw or existing_raw in cleaned:
                return existing_key

    return key


def merge_ipos(all_ipos: List[IPO]) -> List[dict]:
    seen: Dict[str, IPO] = {}
    name_mapping: Dict[str, str] = {}

    for ipo in all_ipos:
        raw_name = ipo.company_name.strip()
        if not raw_name:
            continue
        key = _find_matching_key(raw_name, ipo, seen, name_mapping)

        if key in seen:
            existing = seen[key]
            existing.symbol = existing.symbol or ipo.symbol
            existing.price_band = existing.price_band or ipo.price_band
            existing.open_date = existing.open_date or ipo.open_date
            existing.close_date = existing.close_date or ipo.close_date
            existing.listing_date = existing.listing_date or ipo.listing_date
            existing.lot_size = existing.lot_size or ipo.lot_size
            existing.issue_size = existing.issue_size or ipo.issue_size
            existing.gmp = existing.gmp or ipo.gmp
            existing.subscription = existing.subscription or ipo.subscription
            if ipo.exchange and ipo.exchange != "NSE":
                existing.exchange = ipo.exchange
            if ipo.ipo_type and ipo.ipo_type != "mainboard":
                existing.ipo_type = ipo.ipo_type
            if ipo.country and ipo.country != "India":
                existing.country = ipo.country
            existing_status_priority = STATUS_PRIORITY.get(existing.status, 0)
            new_status_priority = STATUS_PRIORITY.get(ipo.status, 0)
            if new_status_priority > existing_status_priority:
                existing.status = ipo.status
        else:
            seen[key] = ipo
            name_mapping[key] = raw_name

    result = []
    for key, ipo in seen.items():
        d = {
            "company_name": name_mapping.get(key, ipo.company_name),
            "symbol": ipo.symbol,
            "price_band": ipo.price_band,
            "open_date": ipo.open_date,
            "close_date": ipo.close_date,
            "listing_date": ipo.listing_date,
            "lot_size": ipo.lot_size,
            "issue_size": ipo.issue_size,
            "gmp": ipo.gmp,
            "subscription": ipo.subscription,
            "status": ipo.status,
            "exchange": ipo.exchange,
            "ipo_type": ipo.ipo_type,
            "country": ipo.country,
        }
        result.append(d)

    result.sort(key=lambda x: ((x.get("listing_date") or x.get("open_date") or "9999"), (x.get("company_name") or "")))
    return result


def _sort_key(x: dict) -> Tuple:
    date = x.get("listing_date") or x.get("open_date") or x.get("close_date") or "9999"
    return (date, x.get("company_name") or "")


def _balance_ipos(ipos: List[dict]) -> List[dict]:
    india = [x for x in ipos if x.get("country") == "India"]
    global_ = [x for x in ipos if x.get("country") != "India"]

    india_upcoming = sorted(
        [x for x in india if x.get("status") == "upcoming"],
        key=lambda x: x.get("open_date") or x.get("close_date") or "9999",
    )[:15]
    india_other = [x for x in india if x.get("status") != "upcoming"]

    global_upcoming = sorted(
        [x for x in global_ if x.get("status") == "upcoming"],
        key=lambda x: x.get("open_date") or x.get("listing_date") or x.get("close_date") or "9999",
    )[:15]
    global_other = sorted(
        [x for x in global_ if x.get("status") != "upcoming"],
        key=lambda x: x.get("listing_date") or x.get("open_date") or "9999",
        reverse=True,
    )
    remaining = 50 - len(global_upcoming)
    if remaining > 0:
        global_other = global_other[:remaining]
    else:
        global_other = []

    result = india_upcoming + india_other + global_upcoming + global_other
    result.sort(key=_sort_key)
    return result


def run():
    os.makedirs(DATA_DIR, exist_ok=True)

    scrapers = [
        ScreenerScraper(),
        FivePaisaScraper(),
        FinnhubScraper(),
        IpoScoopScraper(),
        RenaissanceScraper(),
        NSEScraper(),
        GrowwScraper(),
        ZerodhaScraper(),
        NasdaqApiScraper(),
    ]

    all_ipos: List[IPO] = []
    for scraper in scrapers:
        try:
            print(f"[Manager] Running {scraper.source_name} scraper...")
            results = scraper.scrape()
            print(f"[Manager] {scraper.source_name}: {len(results)} IPOs found")
            all_ipos.extend(results)
        except Exception as e:
            print(f"[Manager] {scraper.source_name} scraper failed: {e}")

    merged = merge_ipos(all_ipos)
    balanced = _balance_ipos(merged)
    output = {
        "last_updated": datetime.now(timezone.utc).astimezone().isoformat(),
        "total": len(balanced),
        "ipos": balanced,
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[Manager] Saved {len(balanced)} IPOs to {DATA_FILE}")

    analyze_ipos(balanced)

    return output


if __name__ == "__main__":
    run()
