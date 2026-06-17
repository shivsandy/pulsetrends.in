"""
Middle East IPO Scanner — Tadawul (Saudi Arabia), DFM (Dubai), ADX (Abu Dhabi)
"""

import re
from typing import List

from .base import BaseScraper, IPOData


# Major Middle Eastern companies for base coverage
MIDDLE_EAST_STOCKS = [
    # Saudi Arabia
    {"name":"Saudi Arabian Oil Co (Saudi Aramco)","ticker":"2222","exchange":"TADAWUL","sector":"Energy","industry":"Oil & Gas","country":"SA"},
    {"name":"Al Rajhi Bank","ticker":"1120","exchange":"TADAWUL","sector":"Financial","industry":"Banks","country":"SA"},
    {"name":"Saudi National Bank","ticker":"1180","exchange":"TADAWUL","sector":"Financial","industry":"Banks","country":"SA"},
    {"name":"SABIC (Saudi Basic Industries)","ticker":"2010","exchange":"TADAWUL","sector":"Basic Materials","industry":"Chemicals","country":"SA"},
    {"name":"Saudi Telecom Company (STC)","ticker":"7010","exchange":"TADAWUL","sector":"Communication","industry":"Telecom","country":"SA"},
    {"name":"ACWA Power Company","ticker":"2082","exchange":"TADAWUL","sector":"Utilities","industry":"Electric Utilities","country":"SA"},
    {"name":"Ma'aden (Saudi Arabian Mining)","ticker":"1211","exchange":"TADAWUL","sector":"Basic Materials","industry":"Metals & Mining","country":"SA"},
    {"name":"Saudi British Bank (SABB)","ticker":"1060","exchange":"TADAWUL","sector":"Financial","industry":"Banks","country":"SA"},
    {"name":"Riyad Bank","ticker":"1010","exchange":"TADAWUL","sector":"Financial","industry":"Banks","country":"SA"},
    {"name":"Jarir Marketing Company","ticker":"4190","exchange":"TADAWUL","sector":"Consumer Cyclical","industry":"Retail","country":"SA"},
    # UAE
    {"name":"Emirates Telecommunications (Etisalat)","ticker":"EEC","exchange":"ADX","sector":"Communication","industry":"Telecom","country":"AE"},
    {"name":"First Abu Dhabi Bank (FAB)","ticker":"FAB","exchange":"ADX","sector":"Financial","industry":"Banks","country":"AE"},
    {"name":"Abu Dhabi National Oil Co (ADNOC)","ticker":"ADNOC","exchange":"ADX","sector":"Energy","industry":"Oil & Gas","country":"AE"},
    {"name":"Dubai Electricity & Water Authority (DEWA)","ticker":"DEWA","exchange":"DFM","sector":"Utilities","industry":"Electric Utilities","country":"AE"},
    {"name":"Emirates NBD Bank","ticker":"ENBD","exchange":"DFM","sector":"Financial","industry":"Banks","country":"AE"},
    {"name":"Emaar Properties","ticker":"EMAAR","exchange":"DFM","sector":"Real Estate","industry":"Real Estate Development","country":"AE"},
    {"name":"DP World PLC","ticker":"DPW","exchange":"DFM","sector":"Industrials","industry":"Logistics","country":"AE"},
    {"name":"Abu Dhabi Ports Company","ticker":"ADPORTS","exchange":"ADX","sector":"Industrials","industry":"Infrastructure","country":"AE"},
    {"name":"Mashreq Bank","ticker":"MASQ","exchange":"DFM","sector":"Financial","industry":"Banks","country":"AE"},
    {"name":"Dubai Islamic Bank","ticker":"DIB","exchange":"DFM","sector":"Financial","industry":"Banks","country":"AE"},
    {"name":"Almarai Company","ticker":"2280","exchange":"TADAWUL","sector":"Consumer Defensive","industry":"Food","country":"SA"},
    {"name":"Saudi Electricity Company","ticker":"5110","exchange":"TADAWUL","sector":"Utilities","industry":"Electric Utilities","country":"SA"},
    {"name":"Savola Group","ticker":"2050","exchange":"TADAWUL","sector":"Consumer Defensive","industry":"Food","country":"SA"},
    {"name":"Saudi Kayan Petrochemical","ticker":"2350","exchange":"TADAWUL","sector":"Basic Materials","industry":"Chemicals","country":"SA"},
]


class MiddleEastScraper(BaseScraper):
    """Scrapes Middle Eastern IPOs from Tadawul, DFM, and ADX."""

    def __init__(self):
        super().__init__("Middle East")

    @property
    def source_name(self) -> str:
        return "Middle East (Tadawul/DFM/ADX)"

    def scrape(self) -> List[IPOData]:
        all_ipos: List[IPOData] = []
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self._scrape_tadawul): "tadawul",
                executor.submit(self._scrape_major_listed): "listed",
            }
            for fut in concurrent.futures.as_completed(futures):
                key = futures[fut]
                try:
                    batch = fut.result()
                    all_ipos.extend(batch)
                    print(f"  [MiddleEast/{key}] {len(batch)} IPOs")
                except Exception as e:
                    self.errors.append(f"{key}: {e}")
                    print(f"  [MiddleEast/{key}] Failed: {e}")
        return all_ipos

    def _scrape_tadawul(self) -> List[IPOData]:
        """Scrape Tadawul new listings."""
        out: List[IPOData] = []
        url = "https://www.saudiexchange.sa/wps/portal/tadawul/market-participants/issuers/issuers-directory"
        resp = self._get(url)
        if not resp:
            return out
        rows = re.findall(
            r'<tr[^>]*>(.*?)</tr>', resp.text, re.DOTALL | re.IGNORECASE
        )[:30]
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            if len(cells) < 2:
                continue
            name = self._strip_html(cells[0]) if cells[0] else ""
            if not name or len(name) < 3:
                continue
            out.append(IPOData(
                id=self._make_id("tadawul", name),
                name=name,
                exchange="TADAWUL",
                country="SA",
                status="upcoming",
                source="tadawul",
                currency="SAR",
            ))
        return out

    def _scrape_major_listed(self) -> List[IPOData]:
        out: List[IPOData] = []
        for stock in MIDDLE_EAST_STOCKS:
            out.append(IPOData(
                id=self._make_id("me", stock["name"]),
                name=stock["name"],
                ticker=stock["ticker"],
                exchange=stock["exchange"],
                sector=stock.get("sector", ""),
                industry=stock.get("industry", ""),
                country=stock.get("country", ""),
                status="listed",
                description=f"{stock['name']} is a {stock.get('industry', '').lower()} company listed on {stock['exchange']}.",
                source="me_listed",
            ))
        return out
