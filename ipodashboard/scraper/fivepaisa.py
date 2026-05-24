from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import IPO, BaseScraper


class FivePaisaScraper(BaseScraper):
    source_name = "5paisa"
    url = "https://www.5paisa.com/ipo"

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
            print(f"[5paisa] Request failed: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        ipos = []

        lists = soup.find_all("ul", class_="explore__data")
        if not lists:
            print("[5paisa] Could not find IPO data lists")
            return []

        for ul in lists:
            card = ul.find_parent("div", class_="ipo-block__card")
            if not card:
                continue
            is_hidden = card.get("class", []) and "hide" in card.get("class", [])
            is_recent = card.get("class", []) and "recent__ipo" in card.get("class", [])
            if is_recent:
                continue
            try:
                ipo = self._parse_card(ul, card)
                if ipo:
                    ipos.append(ipo)
            except Exception as e:
                print(f"[5paisa] Error parsing card: {e}")
                continue

        return ipos

    def _parse_card(self, ul, card) -> Optional[IPO]:
        lis = ul.find_all("li")
        if len(lis) < 4:
            return None

        ipo = IPO()

        # --- Company name & type ---
        name_elem = lis[0].find("span", class_="c-name")
        if name_elem:
            link = name_elem.find("a")
            if link:
                ipo.company_name = link.get_text(strip=True).rstrip(".").strip()
            type_span = name_elem.find("span", class_=lambda c: c and "ipobg" in str(c))
            if type_span:
                type_text = type_span.get_text(strip=True).upper()
                if "SME" in type_text:
                    ipo.ipo_type = "sme"
                elif "FPO" in type_text:
                    ipo.ipo_type = "fpo"

        # --- Issue date ---
        date_text = lis[1].get_text(" ", strip=True)
        date_text = date_text.replace("Issue Date", "").strip()
        parts = date_text.split("-")
        if len(parts) == 2:
            ipo.open_date = self._normalise_date(parts[0].strip())
            ipo.close_date = self._normalise_date(parts[1].strip())

        # --- Price ---
        price_text = lis[2].get_text(" ", strip=True)
        price_text = price_text.replace("Price", "").replace("\u20b9", "").strip()
        price_parts = [p.strip() for p in price_text.split("-") if p.strip()]
        if len(price_parts) >= 2:
            ipo.price_band = f"\u20b9{price_parts[0]} - \u20b9{price_parts[1]}"
        elif price_parts:
            ipo.price_band = f"\u20b9{price_parts[0]}"

        # --- Issue size ---
        size_text = lis[3].get_text(" ", strip=True)
        size_text = size_text.replace("IPO Size", "").replace("\u20b9", "").strip()
        size_text = size_text.replace("Cr.", "Cr").replace("cr", "Cr").strip()
        if size_text:
            ipo.issue_size = f"\u20b9{size_text}"

        # --- Determine status from card class ---
        card_classes = card.get("class", [])
        if any("upcoming" in (c or "") for c in card_classes):
            ipo.status = "upcoming"
        elif any("closed" in (c or "") for c in card_classes):
            ipo.status = "subscribed"
        else:
            ipo.status = "open"

        if not ipo.company_name:
            return None

        return ipo

    def _normalise_date(self, raw: str) -> str:
        from datetime import datetime
        raw = raw.strip().lower().replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
        parts = raw.split()
        if len(parts) < 2:
            return raw
        day_str, month_str = parts[0], parts[1]
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
        if month_str[:3] in months and list(months.keys()).index(month_str[:3]) < datetime.now().month - 2:
            year += 1
        return f"{year}-{month_num}-{day:02d}"

