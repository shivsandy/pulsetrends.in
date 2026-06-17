"""
Europe IPO Scanner — LSE, Euronext (Paris, Amsterdam, Brussels, Dublin)
Includes major European listed companies as a base dataset.
"""

import re
from typing import List

from .base import BaseScraper, IPOData


# Major European companies for base coverage
EUROPEAN_STOCKS = [
    {"name":"ASML Holding N.V.","ticker":"ASML","exchange":"EURONEXT","sector":"Technology","industry":"Semiconductors","country":"NL"},
    {"name":"SAP SE","ticker":"SAP","exchange":"XETRA","sector":"Technology","industry":"Software","country":"DE"},
    {"name":"Novo Nordisk A/S","ticker":"NOVO-B","exchange":"OMXCOP","sector":"Healthcare","industry":"Drug Manufacturers","country":"DK"},
    {"name":"Nestlé S.A.","ticker":"NESN","exchange":"SIX","sector":"Consumer Defensive","industry":"Food","country":"CH"},
    {"name":"Roche Holding AG","ticker":"ROG","exchange":"SIX","sector":"Healthcare","industry":"Drug Manufacturers","country":"CH"},
    {"name":"LVMH Moet Hennessy","ticker":"MC","exchange":"EURONEXT","sector":"Consumer Cyclical","industry":"Luxury Goods","country":"FR"},
    {"name":"Shell plc","ticker":"SHEL","exchange":"LSE","sector":"Energy","industry":"Oil & Gas","country":"GB"},
    {"name":"AstraZeneca PLC","ticker":"AZN","exchange":"LSE","sector":"Healthcare","industry":"Drug Manufacturers","country":"GB"},
    {"name":"HSBC Holdings plc","ticker":"HSBA","exchange":"LSE","sector":"Financial","industry":"Banks","country":"GB"},
    {"name":"Unilever PLC","ticker":"ULVR","exchange":"LSE","sector":"Consumer Defensive","industry":"Household Products","country":"GB"},
    {"name":"BP p.l.c.","ticker":"BP.","exchange":"LSE","sector":"Energy","industry":"Oil & Gas","country":"GB"},
    {"name":"GlaxoSmithKline plc","ticker":"GSK","exchange":"LSE","sector":"Healthcare","industry":"Drug Manufacturers","country":"GB"},
    {"name":"Diageo plc","ticker":"DGE","exchange":"LSE","sector":"Consumer Defensive","industry":"Beverages","country":"GB"},
    {"name":"Rio Tinto Group","ticker":"RIO","exchange":"LSE","sector":"Basic Materials","industry":"Metals & Mining","country":"GB"},
    {"name":"BHP Group Ltd","ticker":"BHP","exchange":"LSE","sector":"Basic Materials","industry":"Metals & Mining","country":"GB"},
    {"name":"TotalEnergies SE","ticker":"TTE","exchange":"EURONEXT","sector":"Energy","industry":"Oil & Gas","country":"FR"},
    {"name":"Airbus SE","ticker":"AIR","exchange":"EURONEXT","sector":"Industrials","industry":"Aerospace","country":"NL"},
    {"name":"Siemens AG","ticker":"SIE","exchange":"XETRA","sector":"Industrials","industry":"Industrial Equipment","country":"DE"},
    {"name":"Allianz SE","ticker":"ALV","exchange":"XETRA","sector":"Financial","industry":"Insurance","country":"DE"},
    {"name":"Deutsche Telekom AG","ticker":"DTE","exchange":"XETRA","sector":"Communication","industry":"Telecom","country":"DE"},
    {"name":"Bayer AG","ticker":"BAYN","exchange":"XETRA","sector":"Healthcare","industry":"Drug Manufacturers","country":"DE"},
    {"name":"Mercedes-Benz Group","ticker":"MBG","exchange":"XETRA","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"DE"},
    {"name":"BMW Group","ticker":"BMW","exchange":"XETRA","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"DE"},
    {"name":"Volkswagen AG","ticker":"VOW3","exchange":"XETRA","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"DE"},
    {"name":"Adidas AG","ticker":"ADS","exchange":"XETRA","sector":"Consumer Cyclical","industry":"Apparel","country":"DE"},
    {"name":"Infineon Technologies","ticker":"IFX","exchange":"XETRA","sector":"Technology","industry":"Semiconductors","country":"DE"},
    {"name":"Deutsche Bank AG","ticker":"DBK","exchange":"XETRA","sector":"Financial","industry":"Banks","country":"DE"},
    {"name":"Anheuser-Busch InBev","ticker":"ABI","exchange":"EURONEXT","sector":"Consumer Defensive","industry":"Beverages","country":"BE"},
    {"name":"Linde plc","ticker":"LIN","exchange":"XETRA","sector":"Basic Materials","industry":"Specialty Chemicals","country":"GB"},
    {"name":"CRH plc","ticker":"CRH","exchange":"LSE","sector":"Basic Materials","industry":"Building Materials","country":"IE"},
    {"name":"Experian plc","ticker":"EXPN","exchange":"LSE","sector":"Industrials","industry":"Consulting","country":"GB"},
    {"name":"RELX plc","ticker":"REL","exchange":"LSE","sector":"Industrials","industry":"Consulting","country":"GB"},
    {"name":"London Stock Exchange Group","ticker":"LSEG","exchange":"LSE","sector":"Financial","industry":"Financial Services","country":"GB"},
    {"name":"National Grid plc","ticker":"NG.","exchange":"LSE","sector":"Utilities","industry":"Electric Utilities","country":"GB"},
    {"name":"Vodafone Group plc","ticker":"VOD","exchange":"LSE","sector":"Communication","industry":"Telecom","country":"GB"},
    {"name":"Barclays plc","ticker":"BARC","exchange":"LSE","sector":"Financial","industry":"Banks","country":"GB"},
    {"name":"Lloyds Banking Group","ticker":"LLOY","exchange":"LSE","sector":"Financial","industry":"Banks","country":"GB"},
    {"name":"SSE plc","ticker":"SSE","exchange":"LSE","sector":"Utilities","industry":"Electric Utilities","country":"GB"},
    {"name":"Reckitt Benckiser Group","ticker":"RKT","exchange":"LSE","sector":"Consumer Defensive","industry":"Household Products","country":"GB"},
    {"name":"Compass Group plc","ticker":"CPG","exchange":"LSE","sector":"Consumer Cyclical","industry":"Restaurants","country":"GB"},
    {"name":"Schneider Electric SE","ticker":"SU","exchange":"EURONEXT","sector":"Industrials","industry":"Electrical Equipment","country":"FR"},
    {"name":"AXA SA","ticker":"CS","exchange":"EURONEXT","sector":"Financial","industry":"Insurance","country":"FR"},
    {"name":"BNP Paribas SA","ticker":"BNP","exchange":"EURONEXT","sector":"Financial","industry":"Banks","country":"FR"},
    {"name":"Sanofi SA","ticker":"SAN","exchange":"EURONEXT","sector":"Healthcare","industry":"Drug Manufacturers","country":"FR"},
    {"name":"L'Oréal S.A.","ticker":"OR","exchange":"EURONEXT","sector":"Consumer Defensive","industry":"Personal Care","country":"FR"},
    {"name":"Hermès International","ticker":"RMS","exchange":"EURONEXT","sector":"Consumer Cyclical","industry":"Luxury Goods","country":"FR"},
    {"name":"Danone S.A.","ticker":"BN","exchange":"EURONEXT","sector":"Consumer Defensive","industry":"Food","country":"FR"},
    {"name":"Air Liquide S.A.","ticker":"AI","exchange":"EURONEXT","sector":"Basic Materials","industry":"Chemicals","country":"FR"},
    {"name":"EssilorLuxottica","ticker":"EL","exchange":"EURONEXT","sector":"Healthcare","industry":"Medical Devices","country":"FR"},
    {"name":"Vinci SA","ticker":"DG","exchange":"EURONEXT","sector":"Industrials","industry":"Infrastructure","country":"FR"},
    {"name":"Kering SA","ticker":"KER","exchange":"EURONEXT","sector":"Consumer Cyclical","industry":"Luxury Goods","country":"FR"},
    {"name":"Deutsche Post AG","ticker":"DPW","exchange":"XETRA","sector":"Industrials","industry":"Logistics","country":"DE"},
    {"name":"Merck KGaA","ticker":"MRK","exchange":"XETRA","sector":"Healthcare","industry":"Drug Manufacturers","country":"DE"},
    {"name":"Henkel AG & Co.","ticker":"HEN3","exchange":"XETRA","sector":"Consumer Defensive","industry":"Household Products","country":"DE"},
    {"name":"Fresenius SE & Co.","ticker":"FRE","exchange":"XETRA","sector":"Healthcare","industry":"Healthcare Services","country":"DE"},
    {"name":"Sartorius AG","ticker":"SRT3","exchange":"XETRA","sector":"Healthcare","industry":"Medical Devices","country":"DE"},
    {"name":"Vonovia SE","ticker":"VNA","exchange":"XETRA","sector":"Real Estate","industry":"Real Estate Development","country":"DE"},
    {"name":"Zurich Insurance Group","ticker":"ZURN","exchange":"SIX","sector":"Financial","industry":"Insurance","country":"CH"},
    {"name":"UBS Group AG","ticker":"UBSG","exchange":"SIX","sector":"Financial","industry":"Banks","country":"CH"},
    {"name":"ABB Ltd","ticker":"ABBN","exchange":"SIX","sector":"Industrials","industry":"Electrical Equipment","country":"CH"},
    {"name":"Novartis AG","ticker":"NOVN","exchange":"SIX","sector":"Healthcare","industry":"Drug Manufacturers","country":"CH"},
    {"name":"Logitech International","ticker":"LOGN","exchange":"SIX","sector":"Technology","industry":"Computer Hardware","country":"CH"},
]


class EuropeScraper(BaseScraper):
    """Scrapes European IPOs from LSE and Euronext, plus major listed stocks."""

    def __init__(self):
        super().__init__("Europe")

    @property
    def source_name(self) -> str:
        return "Europe (LSE/Euronext/XETRA/SIX)"

    def scrape(self) -> List[IPOData]:
        all_ipos: List[IPOData] = []
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._scrape_lse): "lse",
                executor.submit(self._scrape_major_listed): "listed",
            }
            for fut in concurrent.futures.as_completed(futures):
                key = futures[fut]
                try:
                    batch = fut.result()
                    all_ipos.extend(batch)
                    print(f"  [Europe/{key}] {len(batch)} IPOs")
                except Exception as e:
                    self.errors.append(f"{key}: {e}")
                    print(f"  [Europe/{key}] Failed: {e}")
        return all_ipos

    def _scrape_lse(self) -> List[IPOData]:
        """Scrape LSE new issue list (best-effort HTML scraping)."""
        out: List[IPOData] = []
        url = "https://www.londonstockexchange.com/reports/new-issues"
        resp = self._get(url)
        if not resp:
            return out
        # Look for IPO/new issue data in the page
        rows = re.findall(
            r'<tr[^>]*>(.*?)</tr>', resp.text, re.DOTALL | re.IGNORECASE
        )[:30]
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
            if len(cells) < 3:
                continue
            name = self._strip_html(cells[0]) if cells[0] else ""
            if not name or len(name) < 3:
                continue
            out.append(IPOData(
                id=self._make_id("lse", name),
                name=name,
                exchange="LSE",
                country="GB",
                status="upcoming",
                source="lse",
                currency="GBP",
            ))
        return out

    def _scrape_major_listed(self) -> List[IPOData]:
        out: List[IPOData] = []
        for stock in EUROPEAN_STOCKS:
            out.append(IPOData(
                id=self._make_id("eu", stock["name"]),
                name=stock["name"],
                ticker=stock["ticker"],
                exchange=stock["exchange"],
                sector=stock.get("sector", ""),
                industry=stock.get("industry", ""),
                country=stock.get("country", "EU"),
                status="listed",
                description=f"{stock['name']} is a {stock.get('industry', '').lower()} company listed on {stock['exchange']}.",
                source="eu_listed",
            ))
        return out
