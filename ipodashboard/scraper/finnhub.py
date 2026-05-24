import os
import random
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests

from .base import IPO, BaseScraper, get_country


FINNHUB_BASE = "https://finnhub.io/api/v1"

def _pick_key(api_keys):
    now = time.time()
    healthy = []
    for entry in api_keys:
        if entry.get("cooldown", 0) > now:
            continue
        healthy.append(entry)
    if not healthy:
        return None
    return random.choice(healthy)

def _record_failure(entry):
    entry["cooldown"] = time.time() + 300

def _record_success(entry):
    entry["cooldown"] = 0.0


class FinnhubScraper(BaseScraper):
    source_name = "finnhub"

    def __init__(self):
        self.api_keys = []
        for i in range(1, 6):
            val = os.environ.get(f"FINNHUB_API_KEY_{i}")
            if val:
                self.api_keys.append({"key": val, "index": i, "cooldown": 0.0})

    def scrape(self) -> List[IPO]:
        if not self.api_keys:
            print("[Finnhub] No FINNHUB_API_KEY_1..5 set, skipping")
            return []

        today = datetime.now(timezone.utc)
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")

        ipos = []
        for status_filter in ["", "expected", "priced"]:
            try:
                batch = self._fetch_calendar(from_date, to_date, status_filter)
                ipos.extend(batch)
            except Exception as e:
                print(f"[Finnhub] Error fetching status={status_filter}: {e}")

        return ipos

    def _fetch_calendar(self, from_date: str, to_date: str, status: str = "") -> List[IPO]:
        entry = _pick_key(self.api_keys)
        if not entry:
            print("[Finnhub] All API keys cooled down, skipping")
            return []

        params = {"from": from_date, "to": to_date, "token": entry["key"]}
        if status:
            params["status"] = status

        resp = requests.get(
            f"{FINNHUB_BASE}/ipo-calendar",
            params=params,
            timeout=30,
        )

        if resp.status_code == 429:
            _record_failure(entry)
            print(f"[Finnhub] Key {entry['index']} rate limited, cooling down")
            return []
        if resp.status_code == 403:
            _record_failure(entry)
            print(f"[Finnhub] Key {entry['index']} forbidden, cooling down")
            return []

        resp.raise_for_status()
        _record_success(entry)

        data = resp.json()
        result = []
        for item in data.get("ipoCalendar", []):
            try:
                ipo = self._parse_item(item)
                if ipo:
                    result.append(ipo)
            except Exception as e:
                print(f"[Finnhub] Error parsing item: {e}")
        return result

    def _parse_item(self, item: dict) -> Optional[IPO]:
        name = (item.get("name") or "").strip()
        if not name:
            return None

        ipo = IPO()
        ipo.company_name = name
        ipo.symbol = (item.get("symbol") or "").strip().upper()
        ipo.exchange = (item.get("exchange") or "").strip().upper()
        ipo.country = get_country(ipo.exchange)

        price_low = item.get("priceRangeLow")
        price_high = item.get("priceRangeHigh")
        if price_low and price_high:
            ipo.price_band = f"${price_low:.2f} - ${price_high:.2f}"
        elif price_low:
            ipo.price_band = f"${price_low:.2f}"

        date_raw = (item.get("date") or "").strip()
        ipo.listing_date = date_raw[:10] if date_raw else ""

        shares = item.get("numberOfShares", 0) or 0
        total_value = item.get("totalSharesValue", 0) or 0
        if total_value:
            ipo.issue_size = f"${total_value / 1_000_000:,.1f}M"
        if shares:
            ipo.lot_size = str(int(shares))

        finnhub_status = (item.get("status") or "").lower()
        if finnhub_status in ("expected", "filed"):
            ipo.status = "upcoming"
        elif finnhub_status == "priced":
            ipo.status = "open"
        elif finnhub_status in ("withdrawn", "postponed"):
            ipo.status = "closed"
        else:
            ipo.status = "upcoming"

        if ipo.exchange in ("NSE", "BSE"):
            ipo.ipo_type = "mainboard"

        return ipo
