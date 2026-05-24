import json
import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import IPO, BaseScraper


class GrowwScraper(BaseScraper):
    source_name = "groww"
    url = "https://www.groww.in/ipo"

    def scrape(self) -> List[IPO]:
        try:
            resp = requests.get(
                self.url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[Groww] Request failed: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        ipos = []

        scripts = soup.find_all("script")
        ipo_data = None

        for script in scripts:
            if script.string and '"ipoList"' in script.string:
                match = re.search(r'"ipoList"\s*:\s*(\[[\s\S]*?\])', script.string)
                if match:
                    try:
                        ipo_data = json.loads(match.group(1))
                    except json.JSONDecodeError:
                        pass
                    break

        if ipo_data and isinstance(ipo_data, list):
            for item in ipo_data:
                try:
                    ipo = self._parse_item(item)
                    if ipo:
                        ipos.append(ipo)
                except Exception as e:
                    print(f"[Groww] Error parsing item: {e}")

        return ipos

    def _parse_item(self, item: dict) -> Optional[IPO]:
        ipo = IPO()
        ipo.company_name = item.get("companyName", "") or item.get("name", "") or ""
        if not ipo.company_name:
            return None

        ipo.price_band = self._format_price_band(
            item.get("issuePrice", ""),
            item.get("minPrice", ""),
            item.get("maxPrice", ""),
        )

        ipo.open_date = self._clean_date(item.get("openDate", "") or item.get("issueOpenDate", ""))
        ipo.close_date = self._clean_date(item.get("closeDate", "") or item.get("issueCloseDate", ""))
        ipo.listing_date = self._clean_date(item.get("listingDate", ""))

        lot = item.get("lotSize", "") or item.get("minLotSize", "")
        if lot:
            try:
                ipo.lot_size = str(int(float(lot)))
            except (ValueError, TypeError):
                ipo.lot_size = str(lot)

        issue_size = item.get("issueSize", "") or item.get("issueSizeInCr", "")
        if issue_size:
            try:
                val = float(issue_size)
                ipo.issue_size = f"\u20b9{val:,.0f} Cr"
            except (ValueError, TypeError):
                ipo.issue_size = str(issue_size)

        ipo.subscription = item.get("subscriptionStatus", "") or item.get("subscription", "") or ""

        status = item.get("status", "") or ""
        if "open" in status.lower():
            ipo.status = "open"
        elif "upcoming" in status.lower():
            ipo.status = "upcoming"
        elif "closed" in status.lower():
            ipo.status = "closed"

        ipo_type = item.get("ipoType", "") or item.get("type", "") or ""
        if "SME" in ipo_type.upper():
            ipo.ipo_type = "sme"
            ipo.exchange = "NSE"

        return ipo

    def _format_price_band(self, *values) -> str:
        cleaned = [v for v in values if v]
        if not cleaned:
            return ""
        if len(cleaned) == 1:
            return f"\u20b9{cleaned[0]}"
        if len(cleaned) >= 2:
            return f"\u20b9{cleaned[0]} - \u20b9{cleaned[1]}"
        return ""

    def _clean_date(self, date_str: str) -> str:
        if not date_str:
            return ""
        date_str = date_str.strip()
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
            try:
                from datetime import datetime
                return datetime.strptime(date_str[:10], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str[:10] if len(date_str) >= 10 else date_str

