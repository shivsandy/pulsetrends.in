import re
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from .base import IPO, BaseScraper

MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


class ZerodhaScraper(BaseScraper):
    source_name = "zerodha"
    url = "https://zerodha.com/ipo/"

    SECTION_STATUS = {
        "live-ipo": "open",
        "upcoming-ipo": "upcoming",
        "closed-ipo": "listed",
    }

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
            print(f"[Zerodha] Request failed: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        ipos = []

        for section_id, status in self.SECTION_STATUS.items():
            section = soup.find("div", id=section_id)
            if not section:
                continue
            table_wrap = section.find("div", class_="ipo-table")
            if not table_wrap:
                continue
            table = table_wrap.find("table")
            if not table:
                continue
            tbody = table.find("tbody")
            if not tbody:
                continue

            for row in tbody.find_all("tr"):
                try:
                    ipo = self._parse_row(row, status)
                    if ipo:
                        ipos.append(ipo)
                except Exception as e:
                    print(f"[Zerodha] Error parsing row: {e}")
                    continue

        return ipos

    def _parse_row(self, row, status: str) -> Optional[IPO]:
        name_cell = row.find("td", class_="name")
        if not name_cell:
            return None

        ipo = IPO()
        ipo.status = status
        ipo.exchange = "NSE"
        ipo.country = "India"

        symbol_span = name_cell.find("span", class_="ipo-symbol")
        if symbol_span:
            symbol = symbol_span.get_text(strip=True)
            type_span = symbol_span.find("span", class_="ipo-type")
            if type_span:
                type_text = type_span.get_text(strip=True)
                symbol = symbol.replace(type_text, "").strip()
                if "SME" in type_text.upper():
                    ipo.ipo_type = "sme"
            ipo.symbol = symbol

        name_span = name_cell.find("span", class_="ipo-name")
        if name_span:
            ipo.company_name = name_span.get_text(strip=True)
        if not ipo.company_name:
            return None

        date_cells = row.find_all("td", class_="date")
        if len(date_cells) >= 1:
            open_close = self._parse_open_close(date_cells[0])
            if open_close:
                ipo.open_date, ipo.close_date = open_close

        if len(date_cells) >= 2:
            ipo.listing_date = self._parse_date_text(date_cells[1].get_text(strip=True))

        price_cell = row.find("td", class_="text-right")
        if price_cell:
            ipo.price_band = self._parse_price(price_cell.get_text(strip=True))

        return ipo

    def _parse_open_close(self, cell) -> Optional[Tuple[str, str]]:
        hidden = cell.find("span", class_="hidden")
        hidden_text = hidden.get_text(strip=True) if hidden else ""
        full_text = cell.get_text(strip=True)
        visible = full_text.replace(hidden_text, "").strip()

        if not visible:
            return None

        match = re.match(
            r"(\d{1,2})(?:st|nd|rd|th)\s*(?:-|\u2013|to)\s*"
            r"(\d{1,2})(?:st|nd|rd|th)\s+(\w+)\s+(\d{4})",
            visible,
            re.IGNORECASE,
        )
        if match:
            open_day, close_day, month_str, year_str = match.groups()
            month_num = MONTHS.get(month_str.lower()[:3])
            if month_num:
                return (
                    f"{year_str}-{month_num}-{int(open_day):02d}",
                    f"{year_str}-{month_num}-{int(close_day):02d}",
                )

        match = re.match(
            r"(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})",
            visible,
            re.IGNORECASE,
        )
        if match:
            day, month_str, year_str = match.groups()
            month_num = MONTHS.get(month_str.lower()[:3])
            if month_num:
                d = f"{year_str}-{month_num}-{int(day):02d}"
                return (d, d)

        return None

    def _parse_date_text(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        match = re.match(
            r"(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})",
            text,
            re.IGNORECASE,
        )
        if match:
            day, month_str, year_str = match.groups()
            month_num = MONTHS.get(month_str.lower()[:3])
            if month_num:
                return f"{year_str}-{month_num}-{int(day):02d}"
        return text

    def _parse_price(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        text = text.replace("\u2013", "-").replace("&ndash;", "-")
        text = text.replace("\u20b9", "").replace("?", "").strip()
        return f"\u20b9{text}"
