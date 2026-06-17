"""
Asia-Pacific IPO Scanner — HKEX, SGX, ASX, TSE, KRX, TSX (Canada)
Includes major APAC listed companies.
"""

import re
from typing import List

from .base import BaseScraper, IPOData


# Major Asia-Pacific companies for base coverage
APAC_STOCKS_HK = [
    {"name":"Tencent Holdings Ltd","ticker":"0700","exchange":"HKEX","sector":"Technology","industry":"Internet Services","country":"HK"},
    {"name":"Alibaba Group Holding Ltd","ticker":"9988","exchange":"HKEX","sector":"Consumer Cyclical","industry":"E-Commerce","country":"HK"},
    {"name":"Meituan","ticker":"3690","exchange":"HKEX","sector":"Technology","industry":"Internet Services","country":"HK"},
    {"name":"JD.com Inc.","ticker":"9618","exchange":"HKEX","sector":"Consumer Cyclical","industry":"E-Commerce","country":"HK"},
    {"name":"NetEase Inc.","ticker":"9999","exchange":"HKEX","sector":"Technology","industry":"Internet Services","country":"HK"},
    {"name":"Xiaomi Corporation","ticker":"1810","exchange":"HKEX","sector":"Technology","industry":"Consumer Electronics","country":"HK"},
    {"name":"BYD Company Ltd","ticker":"1211","exchange":"HKEX","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"CN"},
    {"name":"China Mobile Ltd","ticker":"0941","exchange":"HKEX","sector":"Communication","industry":"Telecom","country":"CN"},
    {"name":"AIA Group Ltd","ticker":"1299","exchange":"HKEX","sector":"Financial","industry":"Insurance","country":"HK"},
    {"name":"Hong Kong Exchanges & Clearing","ticker":"0388","exchange":"HKEX","sector":"Financial","industry":"Financial Services","country":"HK"},
    {"name":"CK Hutchison Holdings","ticker":"0001","exchange":"HKEX","sector":"Industrials","industry":"Conglomerate","country":"HK"},
    {"name":"Sun Hung Kai Properties","ticker":"0016","exchange":"HKEX","sector":"Real Estate","industry":"Real Estate Development","country":"HK"},
]

APAC_STOCKS_JP = [
    {"name":"Toyota Motor Corporation","ticker":"7203","exchange":"TSE","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"JP"},
    {"name":"Sony Group Corporation","ticker":"6758","exchange":"TSE","sector":"Technology","industry":"Consumer Electronics","country":"JP"},
    {"name":"Nintendo Co. Ltd.","ticker":"7974","exchange":"TSE","sector":"Technology","industry":"Entertainment","country":"JP"},
    {"name":"Keyence Corporation","ticker":"6861","exchange":"TSE","sector":"Technology","industry":"Scientific Instruments","country":"JP"},
    {"name":"Mitsubishi UFJ Financial","ticker":"8306","exchange":"TSE","sector":"Financial","industry":"Banks","country":"JP"},
    {"name":"Recruit Holdings Co.","ticker":"6098","exchange":"TSE","sector":"Industrials","industry":"Staffing","country":"JP"},
    {"name":"SoftBank Group Corp","ticker":"9984","exchange":"TSE","sector":"Financial","industry":"Asset Management","country":"JP"},
    {"name":"Fast Retailing Co. Ltd","ticker":"9983","exchange":"TSE","sector":"Consumer Cyclical","industry":"Retail","country":"JP"},
    {"name":"Tokyo Electron Ltd","ticker":"8035","exchange":"TSE","sector":"Technology","industry":"Semiconductors","country":"JP"},
    {"name":"Honda Motor Co. Ltd.","ticker":"7267","exchange":"TSE","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"JP"},
    {"name":"NTT Corporation","ticker":"9432","exchange":"TSE","sector":"Communication","industry":"Telecom","country":"JP"},
    {"name":"Hitachi Ltd","ticker":"6501","exchange":"TSE","sector":"Industrials","industry":"Conglomerate","country":"JP"},
]

APAC_STOCKS_KR = [
    {"name":"Samsung Electronics Co.","ticker":"005930","exchange":"KRX","sector":"Technology","industry":"Consumer Electronics","country":"KR"},
    {"name":"SK Hynix Inc.","ticker":"000660","exchange":"KRX","sector":"Technology","industry":"Semiconductors","country":"KR"},
    {"name":"LG Energy Solution Ltd","ticker":"373220","exchange":"KRX","sector":"Technology","industry":"Batteries","country":"KR"},
    {"name":"Hyundai Motor Company","ticker":"005380","exchange":"KRX","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"KR"},
    {"name":"POSCO Holdings Inc.","ticker":"005490","exchange":"KRX","sector":"Basic Materials","industry":"Steel","country":"KR"},
    {"name":"LG Electronics Inc.","ticker":"066570","exchange":"KRX","sector":"Technology","industry":"Consumer Electronics","country":"KR"},
    {"name":"Kakao Corporation","ticker":"035720","exchange":"KRX","sector":"Technology","industry":"Internet Services","country":"KR"},
    {"name":"Naver Corporation","ticker":"035420","exchange":"KRX","sector":"Technology","industry":"Internet Services","country":"KR"},
]

APAC_STOCKS_SG = [
    {"name":"DBS Group Holdings Ltd","ticker":"D05","exchange":"SGX","sector":"Financial","industry":"Banks","country":"SG"},
    {"name":"Oversea-Chinese Banking Corp","ticker":"O39","exchange":"SGX","sector":"Financial","industry":"Banks","country":"SG"},
    {"name":"United Overseas Bank Ltd","ticker":"U11","exchange":"SGX","sector":"Financial","industry":"Banks","country":"SG"},
    {"name":"Sea Limited","ticker":"SE","exchange":"SGX","sector":"Technology","industry":"Internet Services","country":"SG"},
    {"name":"Singapore Telecommunications","ticker":"Z74","exchange":"SGX","sector":"Communication","industry":"Telecom","country":"SG"},
]

APAC_STOCKS_AU = [
    {"name":"BHP Group Ltd","ticker":"BHP","exchange":"ASX","sector":"Basic Materials","industry":"Metals & Mining","country":"AU"},
    {"name":"Commonwealth Bank of Australia","ticker":"CBA","exchange":"ASX","sector":"Financial","industry":"Banks","country":"AU"},
    {"name":"CSL Limited","ticker":"CSL","exchange":"ASX","sector":"Healthcare","industry":"Biotechnology","country":"AU"},
    {"name":"National Australia Bank","ticker":"NAB","exchange":"ASX","sector":"Financial","industry":"Banks","country":"AU"},
    {"name":"Woolworths Group Ltd","ticker":"WOW","exchange":"ASX","sector":"Consumer Defensive","industry":"Retail","country":"AU"},
    {"name":"Rio Tinto Limited","ticker":"RIO","exchange":"ASX","sector":"Basic Materials","industry":"Metals & Mining","country":"AU"},
    {"name":"Macquarie Group Ltd","ticker":"MQG","exchange":"ASX","sector":"Financial","industry":"Financial Services","country":"AU"},
    {"name":"Fortescue Metals Group","ticker":"FMG","exchange":"ASX","sector":"Basic Materials","industry":"Metals & Mining","country":"AU"},
    {"name":"Wesfarmers Ltd","ticker":"WES","exchange":"ASX","sector":"Consumer Cyclical","industry":"Retail","country":"AU"},
    {"name":"Qantas Airways Ltd","ticker":"QAN","exchange":"ASX","sector":"Industrials","industry":"Airlines","country":"AU"},
]

APAC_STOCKS_CA = [
    {"name":"Shopify Inc.","ticker":"SHOP","exchange":"TSX","sector":"Technology","industry":"Software","country":"CA"},
    {"name":"Royal Bank of Canada","ticker":"RY","exchange":"TSX","sector":"Financial","industry":"Banks","country":"CA"},
    {"name":"Toronto-Dominion Bank","ticker":"TD","exchange":"TSX","sector":"Financial","industry":"Banks","country":"CA"},
    {"name":"Canadian National Railway","ticker":"CNR","exchange":"TSX","sector":"Industrials","industry":"Railroads","country":"CA"},
    {"name":"Brookfield Asset Mgmt","ticker":"BAM","exchange":"TSX","sector":"Financial","industry":"Asset Management","country":"CA"},
    {"name":"Enbridge Inc.","ticker":"ENB","exchange":"TSX","sector":"Energy","industry":"Oil & Gas Midstream","country":"CA"},
    {"name":"TC Energy Corporation","ticker":"TRP","exchange":"TSX","sector":"Energy","industry":"Oil & Gas Midstream","country":"CA"},
    {"name":"Bank of Montreal","ticker":"BMO","exchange":"TSX","sector":"Financial","industry":"Banks","country":"CA"},
    {"name":"Bank of Nova Scotia","ticker":"BNS","exchange":"TSX","sector":"Financial","industry":"Banks","country":"CA"},
    {"name":"Canadian Pacific Kansas City","ticker":"CP","exchange":"TSX","sector":"Industrials","industry":"Railroads","country":"CA"},
    {"name":"Suncor Energy Inc.","ticker":"SU","exchange":"TSX","sector":"Energy","industry":"Oil & Gas","country":"CA"},
    {"name":"Constellation Software","ticker":"CSU","exchange":"TSX","sector":"Technology","industry":"Software","country":"CA"},
]

ALL_APAC_STOCKS = APAC_STOCKS_HK + APAC_STOCKS_JP + APAC_STOCKS_KR + APAC_STOCKS_SG + APAC_STOCKS_AU + APAC_STOCKS_CA


class AsiaPacificScraper(BaseScraper):
    """Scrapes Asia-Pacific IPOs from HKEX, SGX, ASX, TSE, KRX, TSX."""

    def __init__(self):
        super().__init__("Asia-Pacific")

    @property
    def source_name(self) -> str:
        return "Asia-Pacific (HKEX/SGX/ASX/TSE/KRX/TSX)"

    def scrape(self) -> List[IPOData]:
        all_ipos: List[IPOData] = []
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._scrape_hkex): "hkex",
                executor.submit(self._scrape_asx): "asx",
                executor.submit(self._scrape_major_listed): "listed",
            }
            for fut in concurrent.futures.as_completed(futures):
                key = futures[fut]
                try:
                    batch = fut.result()
                    all_ipos.extend(batch)
                    print(f"  [APAC/{key}] {len(batch)} IPOs")
                except Exception as e:
                    self.errors.append(f"{key}: {e}")
                    print(f"  [APAC/{key}] Failed: {e}")
        return all_ipos

    def _scrape_hkex(self) -> List[IPOData]:
        """Scrape HKEX new listings page."""
        out: List[IPOData] = []
        url = "https://www.hkex.com.hk/Market/New-Listings?sc_lang=en"
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
                id=self._make_id("hkex", name),
                name=name,
                exchange="HKEX",
                country="HK",
                status="upcoming",
                source="hkex",
                currency="HKD",
            ))
        return out

    def _scrape_asx(self) -> List[IPOData]:
        """Scrape ASX new listings."""
        out: List[IPOData] = []
        url = "https://www.asx.com.au/listed-companies/new-listings"
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
                id=self._make_id("asx", name),
                name=name,
                exchange="ASX",
                country="AU",
                status="upcoming",
                source="asx",
                currency="AUD",
            ))
        return out

    def _scrape_major_listed(self) -> List[IPOData]:
        out: List[IPOData] = []
        for stock in ALL_APAC_STOCKS:
            out.append(IPOData(
                id=self._make_id("apac", stock["name"]),
                name=stock["name"],
                ticker=stock["ticker"],
                exchange=stock["exchange"],
                sector=stock.get("sector", ""),
                industry=stock.get("industry", ""),
                country=stock.get("country", ""),
                status="listed",
                description=f"{stock['name']} is a {stock.get('industry', '').lower()} company listed on {stock['exchange']}.",
                source="apac_listed",
            ))
        return out
