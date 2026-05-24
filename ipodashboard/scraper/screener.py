import re
from datetime import datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import IPO, BaseScraper


class ScreenerScraper(BaseScraper):
    source_name = "screener"
    url = "https://www.screener.in/ipo/"

    def scrape(self) -> List[IPO]:
        try:
            resp = requests.get(self.url, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[Screener] Request failed: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", class_="data-table")
        if not table:
            print("[Screener] Could not find data table")
            return []

        tbody = table.find("tbody")
        if not tbody:
            print("[Screener] Could not find tbody")
            return []

        rows = tbody.find_all("tr")
        ipos = []
        for row in rows:
            try:
                ipo = self._parse_row(row)
                if ipo:
                    ipos.append(ipo)
            except Exception as e:
                print(f"[Screener] Error parsing row: {e}")
                continue

        return ipos

    def _parse_row(self, row) -> Optional[IPO]:
        cells = row.find_all("td")
        if len(cells) < 7:
            return None

        ipo = IPO()

        # --- Company name ---
        name_link = cells[0].find("a", class_="font-weight-500")
        if name_link:
            ipo.company_name = name_link.get_text(strip=True)

        # --- Exchange & type from links in first cell ---
        exchange_links = cells[0].find_all("a", href=True)
        for el in exchange_links:
            text = el.get_text(strip=True)
            if "NSE" in text:
                ipo.exchange = "NSE"
            elif "BSE" in text:
                ipo.exchange = "BSE"
            if "SME" in text:
                ipo.ipo_type = "sme"
            elif "FPO" in text:
                ipo.ipo_type = "fpo"

        # --- Subscription period (open/close dates) ---
        period_cell = cells[1]
        date_spans = period_cell.find_all("span", class_="font-weight-500")
        if len(date_spans) >= 2:
            ipo.open_date = date_spans[0].get_text(strip=True)
            ipo.close_date = date_spans[1].get_text(strip=True)
            ipo.open_date = self._normalise_date(ipo.open_date)
            ipo.close_date = self._normalise_date(ipo.close_date)

        # --- Listing date ---
        listing_text = cells[2].get_text(strip=True)
        if listing_text:
            ipo.listing_date = self._normalise_date(listing_text)

        # --- Market cap (use as issue_size proxy) ---
        mcap_text = cells[3].get_text(strip=True)
        if mcap_text:
            ipo.issue_size = f"₹{mcap_text} Cr (M.Cap)"

        # --- Subscription ---
        sub_btn = cells[4].find("button", class_="font-weight-500")
        if sub_btn:
            sub_text = sub_btn.get_text(strip=True).split("times")[0].strip()
            if sub_text:
                ipo.subscription = f"{sub_text} times"
        if not ipo.subscription:
            sub_btn_mobile = cells[4].find("button", class_=re.compile(r"hide-from-tablet"))
            if sub_btn_mobile:
                sub_text = sub_btn_mobile.get_text(strip=True).split("times")[0].strip()
                if sub_text:
                    ipo.subscription = f"{sub_text} times"

        # --- Determine status ---
        ipo.status = self._determine_status(ipo)

        if not ipo.company_name:
            return None

        return ipo

    def _normalise_date(self, raw: str) -> str:
        raw = raw.strip().lower().replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
        parts = raw.split()
        if len(parts) < 2:
            return raw
        day_str = parts[0]
        month_str = parts[1]
        months = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        }
        month_num = months.get(month_str[:3], "")
        if not day_str.isdigit() or not month_num:
            return raw
        day = int(day_str)
        year = datetime.now().year
        check_date = datetime(year, int(month_num), 1)
        if month_str[:3] in months and list(months.keys()).index(month_str[:3]) < datetime.now().month - 2:
            year += 1
        return f"{year}-{month_num}-{day:02d}"

    def _determine_status(self, ipo: IPO) -> str:
        today = datetime.now().date()
        try:
            if ipo.close_date:
                close = datetime.strptime(ipo.close_date, "%Y-%m-%d").date()
                if close >= today:
                    return "open" if ipo.open_date and datetime.strptime(ipo.open_date, "%Y-%m-%d").date() <= today else "upcoming"
            if ipo.listing_date:
                listing = datetime.strptime(ipo.listing_date, "%Y-%m-%d").date()
                if listing >= today:
                    if ipo.close_date and datetime.strptime(ipo.close_date, "%Y-%m-%d").date() < today:
                        return "subscribed"
                    return "upcoming"
        except ValueError:
            pass
        return "upcoming"

