import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import IPO, BaseScraper


class IpoScoopScraper(BaseScraper):
    source_name = "iposcoop"
    url = "https://www.iposcoop.com/ipo-calendar/"

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
            print(f"[IPOScoop] Request failed: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table", class_="standard-table")
        if not table:
            print("[IPOScoop] Could not find table")
            return []

        tbody = table.find("tbody")
        if not tbody:
            return []

        ipos = []
        for row in tbody.find_all("tr"):
            try:
                ipo = self._parse_row(row)
                if ipo:
                    ipos.append(ipo)
            except Exception as e:
                print(f"[IPOScoop] Error parsing row: {e}")
        return ipos

    def _parse_row(self, row) -> Optional[IPO]:
        cells = row.find_all("td")
        if len(cells) < 8:
            return None

        ipo = IPO()
        ipo.exchange = "NASDAQ"

        name_link = cells[0].find("a")
        ipo.company_name = (name_link.get_text(strip=True) if name_link else cells[0].get_text(strip=True))

        sym_link = cells[1].find("a")
        ipo.symbol = (sym_link.get_text(strip=True).upper() if sym_link else cells[1].get_text(strip=True).upper())

        shares_text = cells[3].get_text(strip=True)
        try:
            shares_m = float(shares_text.replace(",", ""))
            ipo.lot_size = str(int(shares_m * 1_000_000)) if shares_m else ""
        except ValueError:
            pass

        price_low = cells[4].get_text(strip=True)
        price_high = cells[5].get_text(strip=True)
        try:
            low = float(price_low)
            high = float(price_high)
            ipo.price_band = f"${low:.2f} - ${high:.2f}"
        except ValueError:
            pass

        vol_text = cells[6].get_text(strip=True)
        vol_text = vol_text.replace("$", "").replace("mil", "M").replace(" ", "")
        if vol_text:
            ipo.issue_size = f"${vol_text}"

        trade_text = cells[7].get_text(strip=True)
        ipo.listing_date = self._parse_trade_date(trade_text)
        ipo.status = self._determine_status(trade_text)

        ipo.country = "USA"

        return ipo

    def _parse_trade_date(self, text: str) -> str:
        match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
        if match:
            m, d, y = match.group(1), match.group(2), match.group(3)
            return f"{y}-{int(m):02d}-{int(d):02d}"
        return ""

    def _determine_status(self, text: str) -> str:
        if "priced" in text.lower():
            return "open"
        if "week of" in text.lower() or "day" in text.lower() or not text:
            return "upcoming"
        return "upcoming"
