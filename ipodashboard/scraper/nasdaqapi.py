from datetime import datetime, timezone
from typing import List, Optional

import requests

from .base import IPO, BaseScraper, get_country


NASDAQ_API = "https://api.nasdaq.com/api/ipo/calendar"


EXCHANGE_MAP = {
    "nyse": "NYSE",
    "nyse american": "NYSE AMERICAN",
    "nyse arca": "NYSE ARCA",
    "nasdaq": "NASDAQ",
    "nasdaq global": "NASDAQ",
    "nasdaq global select": "NASDAQ",
    "nasdaq capital": "NASDAQ",
    "nasdaq cm": "NASDAQ",
    "nasdaq gm": "NASDAQ",
    "nasdaq gs": "NASDAQ",
}


class NasdaqApiScraper(BaseScraper):
    source_name = "nasdaqapi"

    def scrape(self) -> List[IPO]:
        today = datetime.now(timezone.utc)
        current_month = today.strftime("%Y-%m")
        ipos = self._fetch_current(current_month)
        return ipos

    def _request_month(self, yyyy_mm: str) -> dict:
        try:
            resp = requests.get(
                f"{NASDAQ_API}?date={yyyy_mm}",
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "application/json",
                    "Referer": "https://www.nasdaq.com/market-activity/ipos",
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[NasdaqApi] Request failed for {yyyy_mm}: {e}")
            return {}

        try:
            data = resp.json()
        except Exception as e:
            print(f"[NasdaqApi] JSON parse error for {yyyy_mm}: {e}")
            return {}

        if data.get("status", {}).get("rCode") != 200:
            return {}

        return data.get("data", {})

    def _fetch_current(self, yyyy_mm: str) -> List[IPO]:
        calendar = self._request_month(yyyy_mm)
        if not calendar:
            return []

        result = []
        for row in (calendar.get("filed") or {}).get("rows") or []:
            try:
                ipo = self._parse_filed(row)
                if ipo:
                    result.append(ipo)
            except Exception as e:
                print(f"[NasdaqApi] Error parsing filed row: {e}")

        for row in (calendar.get("priced") or {}).get("rows") or []:
            try:
                ipo = self._parse_priced(row)
                if ipo:
                    result.append(ipo)
            except Exception as e:
                print(f"[NasdaqApi] Error parsing priced row: {e}")

        return result

    def _parse_exchange(self, raw: str) -> str:
        if not raw:
            return "NASDAQ"
        cleaned = raw.strip().lower()
        if cleaned in EXCHANGE_MAP:
            return EXCHANGE_MAP[cleaned]
        for key, val in EXCHANGE_MAP.items():
            if key in cleaned or cleaned in key:
                return val
        return raw.strip().upper()

    def _parse_filed(self, row: dict) -> Optional[IPO]:
        name = (row.get("companyName") or "").strip()
        if not name:
            return None

        ipo = IPO()
        ipo.company_name = name
        ipo.symbol = (row.get("proposedTickerSymbol") or "").strip().upper()
        ipo.status = "upcoming"
        ipo.ipo_type = "mainboard"

        exchange_raw = row.get("proposedExchange") or ""
        ipo.exchange = self._parse_exchange(exchange_raw)
        ipo.country = get_country(ipo.exchange)

        value_raw = (row.get("dollarValueOfSharesOffered") or "").strip()
        ipo.issue_size = self._clean_issue_size(value_raw)

        return ipo

    def _parse_priced(self, row: dict) -> Optional[IPO]:
        name = (row.get("companyName") or "").strip()
        if not name:
            return None

        ipo = IPO()
        ipo.company_name = name
        ipo.symbol = (row.get("proposedTickerSymbol") or "").strip().upper()
        ipo.ipo_type = "mainboard"

        exchange_raw = row.get("proposedExchange") or ""
        ipo.exchange = self._parse_exchange(exchange_raw)
        ipo.country = get_country(ipo.exchange)

        date_raw = (row.get("pricedDate") or "").strip()
        ipo.listing_date = self._normalise_date(date_raw)

        status_raw = (row.get("dealStatus") or "").strip().lower()
        if status_raw == "priced":
            ipo.status = "open"
        else:
            ipo.status = "listed"

        shares_raw = (row.get("sharesOffered") or "").strip()
        ipo.lot_size = self._clean_lot_size(shares_raw)

        value_raw = (row.get("dollarValueOfSharesOffered") or "").strip()
        ipo.issue_size = self._clean_issue_size(value_raw)

        price_raw = row.get("proposedSharePrice")
        if price_raw:
            ipo.price_band = self._clean_price(str(price_raw))

        return ipo

    def _normalise_date(self, raw: str) -> str:
        parts = raw.split("/")
        if len(parts) == 3:
            m, d, y = parts
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        return raw

    def _clean_lot_size(self, raw: str) -> str:
        raw = raw.replace(",", "").strip()
        if not raw:
            return ""
        try:
            return str(int(float(raw)))
        except ValueError:
            return raw

    def _clean_issue_size(self, raw: str) -> str:
        raw = raw.strip()
        if not raw:
            return ""
        raw = raw.replace("$", "").replace(",", "").strip()
        try:
            val = float(raw)
            if val >= 1_000_000_000:
                return f"${val / 1_000_000_000:,.1f}B"
            return f"${val / 1_000_000:,.0f}M"
        except ValueError:
            return f"${raw}" if raw else ""

    def _clean_price(self, raw: str) -> str:
        try:
            val = float(raw)
            return f"${val:.2f}"
        except ValueError:
            return f"${raw}"
