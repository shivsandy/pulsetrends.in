import json
import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import IPO, BaseScraper


class NSEScraper(BaseScraper):
    source_name = "nse"

    def scrape(self) -> List[IPO]:
        ipos = []
        for status in ["open", "upcoming"]:
            try:
                result = self._fetch_ipo_list(status)
                ipos.extend(result)
            except Exception as e:
                print(f"[NSE] Failed to fetch {status} IPOs: {e}")
        return ipos

    def _fetch_ipo_list(self, status: str) -> List[IPO]:
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.nseindia.com/market-data/ipos",
        })

        session.get("https://www.nseindia.com", timeout=15)
        session.get("https://www.nseindia.com/market-data/ipos", timeout=15)

        api_url = f"https://www.nseindia.com/api/ipo-market?status={status}"
        resp = session.get(api_url, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        ipos = []
        for item in data if isinstance(data, list) else data.get("data", []):
            try:
                ipo = self._parse_item(item)
                if ipo:
                    ipos.append(ipo)
            except Exception as e:
                print(f"[NSE] Error parsing item: {e}")
        return ipos

    def _parse_item(self, item: dict) -> Optional[IPO]:
        ipo = IPO()
        ipo.company_name = item.get("symbol", "") or item.get("companyName", "") or ""
        if not ipo.company_name:
            return None

        price_band = item.get("priceBand", "")
        if not price_band:
            min_p = item.get("minPrice", "")
            max_p = item.get("maxPrice", "")
            if min_p and max_p:
                price_band = f"\u20b9{min_p} - \u20b9{max_p}"
            elif min_p:
                price_band = f"\u20b9{min_p}"
        ipo.price_band = price_band

        ipo.open_date = item.get("openDate", "") or item.get("issueOpenDate", "") or ""
        ipo.close_date = item.get("closeDate", "") or item.get("issueCloseDate", "") or ""
        ipo.listing_date = item.get("listingDate", "") or ""

        lot_raw = item.get("lotSize", "") or item.get("minLotSize", "")
        if lot_raw:
            try:
                ipo.lot_size = str(int(float(lot_raw)))
            except (ValueError, TypeError):
                ipo.lot_size = str(lot_raw)

        issue_size = item.get("issueSize", "") or ""
        if issue_size:
            try:
                val = float(issue_size)
                if val > 100:
                    ipo.issue_size = f"\u20b9{val:,.0f} Cr"
                else:
                    ipo.issue_size = f"\u20b9{val} Cr"
            except (ValueError, TypeError):
                ipo.issue_size = str(issue_size)

        exchange_text = item.get("exchange", "") or ""
        if "BSE" in exchange_text.upper():
            ipo.exchange = "BSE"
        else:
            ipo.exchange = "NSE"

        series = item.get("series", "") or ""
        if "SME" in series.upper() or "SME" in exchange_text.upper():
            ipo.ipo_type = "sme"

        status = item.get("status", "") or ""
        if "open" in status.lower():
            ipo.status = "open"
        elif "upcoming" in status.lower() or "closed" in status.lower() or "listed" in status.lower():
            ipo.status = "upcoming"

        return ipo

