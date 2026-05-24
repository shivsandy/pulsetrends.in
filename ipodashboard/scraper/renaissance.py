from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .base import IPO, BaseScraper


class RenaissanceScraper(BaseScraper):
    source_name = "renaissance"

    URLS = [
        "https://www.renaissancecapital.com/IPO-Center/",
        "https://www.renaissancecapital.com/IPO-Center/Calendar",
    ]

    def scrape(self) -> List[IPO]:
        ipos = []
        for url in self.URLS:
            try:
                batch = self._scrape_url(url)
                ipos.extend(batch)
            except Exception as e:
                print(f"[Renaissance] Error scraping {url}: {e}")
        return ipos

    def _scrape_url(self, url: str) -> List[IPO]:
        resp = requests.get(
            url,
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

        soup = BeautifulSoup(resp.text, "lxml")
        ipos = []

        for table in soup.find_all("table", class_="ipo-center-table"):
            tbody = table.find("tbody")
            if not tbody:
                continue
            is_calendar = "calendar" in str(table.get("class", []))
            for row in tbody.find_all("tr"):
                try:
                    ipo = self._parse_row(row, is_calendar)
                    if ipo:
                        ipos.append(ipo)
                except Exception as e:
                    print(f"[Renaissance] Row error: {e}")

        return ipos

    def _parse_row(self, row, is_calendar: bool) -> Optional[IPO]:
        cells = row.find_all("td")
        if len(cells) < 4:
            return None

        ipo = IPO()
        ipo.exchange = "NASDAQ"
        ipo.country = "USA"

        ticker_link = cells[0].find("a")
        if ticker_link:
            ipo.symbol = ticker_link.get_text(strip=True).upper()

        company_link = cells[1].find("a")
        if company_link:
            ipo.company_name = company_link.get_text(strip=True)

        if not ipo.company_name:
            return None

        if is_calendar:
            self._parse_calendar_row(ipo, cells)
        else:
            self._parse_center_row(ipo, cells)

        return ipo

    def _parse_calendar_row(self, ipo: IPO, cells):
        if len(cells) >= 6:
            shares_text = cells[4].get_text(strip=True)
            try:
                shares_m = float(shares_text.replace(",", ""))
                ipo.lot_size = str(int(shares_m * 1_000_000)) if shares_m > 0 else ""
            except ValueError:
                pass

        if len(cells) >= 6:
            price_text = cells[5].get_text(strip=True)
            if price_text:
                ipo.price_band = price_text.strip()

        if len(cells) >= 7:
            deal_text = cells[6].get_text(strip=True).replace("$", "").replace(",", "").strip()
            try:
                deal_val = float(deal_text)
                ipo.issue_size = f"${deal_val:,.0f}M"
            except ValueError:
                ipo.issue_size = f"${deal_text}M" if deal_text else ""

        ipo.status = "upcoming"

    def _parse_center_row(self, ipo: IPO, cells):
        if len(cells) >= 4:
            date_text = cells[3].get_text(strip=True)
            if date_text and date_text != "00/00/00":
                try:
                    m, d, y = date_text.split("/")
                    ipo.listing_date = f"20{y}-{int(m):02d}-{int(d):02d}"
                    ipo.status = "open"
                except ValueError:
                    pass

        if len(cells) >= 5:
            deal_text = cells[4].get_text(strip=True).replace("$", "").replace(",", "").strip()
            if deal_text:
                try:
                    ipo.issue_size = f"${float(deal_text):,.0f}M"
                except ValueError:
                    ipo.issue_size = f"${deal_text}M"
