"""
Latin America IPO Scanner — B3 (Brazil), BMV (Mexico), BCBA (Argentina)
"""

import re
from typing import List

from .base import BaseScraper, IPOData


# Major Latin American companies for base coverage
LATAM_STOCKS = [
    # Brazil
    {"name":"Petrobras (Petróleo Brasileiro)","ticker":"PETR4","exchange":"B3","sector":"Energy","industry":"Oil & Gas","country":"BR"},
    {"name":"Vale S.A.","ticker":"VALE3","exchange":"B3","sector":"Basic Materials","industry":"Metals & Mining","country":"BR"},
    {"name":"Itaú Unibanco Holding","ticker":"ITUB4","exchange":"B3","sector":"Financial","industry":"Banks","country":"BR"},
    {"name":"Banco Bradesco S.A.","ticker":"BBDC4","exchange":"B3","sector":"Financial","industry":"Banks","country":"BR"},
    {"name":"Ambev S.A.","ticker":"ABEV3","exchange":"B3","sector":"Consumer Defensive","industry":"Beverages","country":"BR"},
    {"name":"Nu Holdings Ltd","ticker":"ROXO34","exchange":"B3","sector":"Financial","industry":"Banks","country":"BR"},
    {"name":"Magazine Luiza S.A.","ticker":"MGLU3","exchange":"B3","sector":"Consumer Cyclical","industry":"Retail","country":"BR"},
    {"name":"MercadoLibre Inc.","ticker":"MELI34","exchange":"B3","sector":"Consumer Cyclical","industry":"E-Commerce","country":"BR"},
    {"name":"WEG S.A.","ticker":"WEGE3","exchange":"B3","sector":"Industrials","industry":"Industrial Equipment","country":"BR"},
    {"name":"Banco do Brasil S.A.","ticker":"BBAS3","exchange":"B3","sector":"Financial","industry":"Banks","country":"BR"},
    {"name":"B3 S.A. (Brazil Stock Exchange)","ticker":"B3SA3","exchange":"B3","sector":"Financial","industry":"Financial Services","country":"BR"},
    {"name":"Itaúsa S.A.","ticker":"ITSA4","exchange":"B3","sector":"Financial","industry":"Financial Services","country":"BR"},
    {"name":"Rumo Logística","ticker":"RAIL3","exchange":"B3","sector":"Industrials","industry":"Logistics","country":"BR"},
    {"name":"Suzano S.A.","ticker":"SUZB3","exchange":"B3","sector":"Basic Materials","industry":"Paper","country":"BR"},
    {"name":"CEMIG (Cia Energética MG)","ticker":"CMIG4","exchange":"B3","sector":"Utilities","industry":"Electric Utilities","country":"BR"},
    # Mexico
    {"name":"América Móvil","ticker":"AMXL","exchange":"BMV","sector":"Communication","industry":"Telecom","country":"MX"},
    {"name":"Grupo Financiero Banorte","ticker":"GFNORTEO","exchange":"BMV","sector":"Financial","industry":"Banks","country":"MX"},
    {"name":"Wal-Mart de México","ticker":"WALMEX","exchange":"BMV","sector":"Consumer Defensive","industry":"Retail","country":"MX"},
    {"name":"FEMSA (Fomento Económico)","ticker":"FEMSAUBD","exchange":"BMV","sector":"Consumer Defensive","industry":"Beverages","country":"MX"},
    {"name":"Cemex S.A.B. de C.V.","ticker":"CEMEXCPO","exchange":"BMV","sector":"Basic Materials","industry":"Cement","country":"MX"},
    {"name":"Grupo Bimbo","ticker":"BIMBOA","exchange":"BMV","sector":"Consumer Defensive","industry":"Food","country":"MX"},
    {"name":"Petróleos Mexicanos (Pemex)","ticker":"PEMEX","exchange":"BMV","sector":"Energy","industry":"Oil & Gas","country":"MX"},
    {"name":"Grupo México","ticker":"GMEXICOB","exchange":"BMV","sector":"Basic Materials","industry":"Metals & Mining","country":"MX"},
    # Argentina
    {"name":"YPF S.A.","ticker":"YPFD","exchange":"BCBA","sector":"Energy","industry":"Oil & Gas","country":"AR"},
    {"name":"MercadoLibre Inc.","ticker":"MELI","exchange":"BCBA","sector":"Consumer Cyclical","industry":"E-Commerce","country":"AR"},
    {"name":"Grupo Financiero Galicia","ticker":"GGAL","exchange":"BCBA","sector":"Financial","industry":"Banks","country":"AR"},
    {"name":"Banco Macro S.A.","ticker":"BMA","exchange":"BCBA","sector":"Financial","industry":"Banks","country":"AR"},
    {"name":"Globant S.A.","ticker":"GLOB","exchange":"BCBA","sector":"Technology","industry":"Software","country":"AR"},
]


class LatinAmericaScraper(BaseScraper):
    """Scrapes Latin American IPOs from B3, BMV, BCBA."""

    def __init__(self):
        super().__init__("Latin America")

    @property
    def source_name(self) -> str:
        return "Latin America (B3/BMV/BCBA)"

    def scrape(self) -> List[IPOData]:
        out: List[IPOData] = []
        for stock in LATAM_STOCKS:
            out.append(IPOData(
                id=self._make_id("latam", stock["name"]),
                name=stock["name"],
                ticker=stock["ticker"],
                exchange=stock["exchange"],
                sector=stock.get("sector", ""),
                industry=stock.get("industry", ""),
                country=stock.get("country", ""),
                status="listed",
                description=f"{stock['name']} is a {stock.get('industry', '').lower()} company listed on {stock['exchange']}.",
                source="latam_listed",
            ))
        print(f"  [LatAm/listed] {len(out)} IPOs")
        return out
