"""
US IPO Scanner — NASDAQ, NYSE via Finnhub API + SEC EDGAR S-1 filings
"""

import re
from datetime import datetime, timezone
from typing import List, Optional

from .base import BaseScraper, IPOData


# Static list of major US-listed global companies with their sector data
US_LISTED_STOCKS = [
    {"name":"Apple Inc.","ticker":"AAPL","sector":"Technology","industry":"Consumer Electronics"},
    {"name":"Microsoft Corporation","ticker":"MSFT","sector":"Technology","industry":"Software"},
    {"name":"Alphabet Inc.","ticker":"GOOGL","sector":"Technology","industry":"Internet Services"},
    {"name":"Amazon.com Inc.","ticker":"AMZN","sector":"Consumer Cyclical","industry":"E-Commerce"},
    {"name":"NVIDIA Corporation","ticker":"NVDA","sector":"Technology","industry":"Semiconductors"},
    {"name":"Meta Platforms Inc.","ticker":"META","sector":"Technology","industry":"Social Media"},
    {"name":"Tesla Inc.","ticker":"TSLA","sector":"Consumer Cyclical","industry":"Auto Manufacturers"},
    {"name":"Berkshire Hathaway Inc.","ticker":"BRK.B","sector":"Financial","industry":"Insurance"},
    {"name":"Broadcom Inc.","ticker":"AVGO","sector":"Technology","industry":"Semiconductors"},
    {"name":"JPMorgan Chase & Co.","ticker":"JPM","sector":"Financial","industry":"Banks"},
    {"name":"Visa Inc.","ticker":"V","sector":"Financial","industry":"Credit Services"},
    {"name":"UnitedHealth Group Inc.","ticker":"UNH","sector":"Healthcare","industry":"Healthcare Plans"},
    {"name":"Walmart Inc.","ticker":"WMT","sector":"Consumer Defensive","industry":"Discount Stores"},
    {"name":"Mastercard Incorporated","ticker":"MA","sector":"Financial","industry":"Credit Services"},
    {"name":"Johnson & Johnson","ticker":"JNJ","sector":"Healthcare","industry":"Drug Manufacturers"},
    {"name":"Procter & Gamble","ticker":"PG","sector":"Consumer Defensive","industry":"Household Products"},
    {"name":"Coca-Cola Company","ticker":"KO","sector":"Consumer Defensive","industry":"Beverages"},
    {"name":"PepsiCo Inc.","ticker":"PEP","sector":"Consumer Defensive","industry":"Beverages"},
    {"name":"Exxon Mobil Corporation","ticker":"XOM","sector":"Energy","industry":"Oil & Gas"},
    {"name":"Chevron Corporation","ticker":"CVX","sector":"Energy","industry":"Oil & Gas"},
    {"name":"Cisco Systems Inc.","ticker":"CSCO","sector":"Technology","industry":"Communication Equipment"},
    {"name":"Oracle Corporation","ticker":"ORCL","sector":"Technology","industry":"Software"},
    {"name":"Salesforce Inc.","ticker":"CRM","sector":"Technology","industry":"Software"},
    {"name":"Netflix Inc.","ticker":"NFLX","sector":"Communication","industry":"Entertainment"},
    {"name":"Adobe Inc.","ticker":"ADBE","sector":"Technology","industry":"Software"},
    {"name":"Intel Corporation","ticker":"INTC","sector":"Technology","industry":"Semiconductors"},
    {"name":"Advanced Micro Devices","ticker":"AMD","sector":"Technology","industry":"Semiconductors"},
    {"name":"Uber Technologies Inc.","ticker":"UBER","sector":"Technology","industry":"Software"},
    {"name":"Palantir Technologies Inc.","ticker":"PLTR","sector":"Technology","industry":"Software"},
    {"name":"Costco Wholesale Corp","ticker":"COST","sector":"Consumer Defensive","industry":"Discount Stores"},
    {"name":"Home Depot Inc.","ticker":"HD","sector":"Consumer Cyclical","industry":"Home Improvement"},
    {"name":"McDonald's Corporation","ticker":"MCD","sector":"Consumer Cyclical","industry":"Restaurants"},
    {"name":"AbbVie Inc.","ticker":"ABBV","sector":"Healthcare","industry":"Drug Manufacturers"},
    {"name":"Merck & Co. Inc.","ticker":"MRK","sector":"Healthcare","industry":"Drug Manufacturers"},
    {"name":"Eli Lilly and Company","ticker":"LLY","sector":"Healthcare","industry":"Pharmaceuticals"},
    {"name":"Pfizer Inc.","ticker":"PFE","sector":"Healthcare","industry":"Pharmaceuticals"},
    {"name":"Coca-Cola Company","ticker":"KO","sector":"Consumer Defensive","industry":"Beverages"},
    {"name":"Thermo Fisher Scientific","ticker":"TMO","sector":"Healthcare","industry":"Diagnostics"},
    {"name":"Accenture plc","ticker":"ACN","sector":"Technology","industry":"Consulting"},
    {"name":"Comcast Corporation","ticker":"CMCSA","sector":"Communication","industry":"Telecom"},
    {"name":"Intuitive Surgical Inc.","ticker":"ISRG","sector":"Healthcare","industry":"Medical Devices"},
    {"name":"CrowdStrike Holdings Inc.","ticker":"CRWD","sector":"Technology","industry":"Cybersecurity"},
    {"name":"Zoom Video Communications","ticker":"ZM","sector":"Technology","industry":"Software"},
    {"name":"Coinbase Global Inc.","ticker":"COIN","sector":"Financial","industry":"Digital Assets"},
    {"name":"Robinhood Markets Inc.","ticker":"HOOD","sector":"Financial","industry":"Brokerage"},
    {"name":"Airbnb Inc.","ticker":"ABNB","sector":"Consumer Cyclical","industry":"Travel Services"},
    {"name":"DoorDash Inc.","ticker":"DASH","sector":"Technology","industry":"Software"},
    {"name":"Snowflake Inc.","ticker":"SNOW","sector":"Technology","industry":"Software"},
    {"name":"Rivian Automotive Inc.","ticker":"RIVN","sector":"Consumer Cyclical","industry":"Auto Manufacturers"},
    {"name":"Spotify Technology S.A.","ticker":"SPOT","sector":"Communication","industry":"Entertainment"},
    {"name":"Moderna Inc.","ticker":"MRNA","sector":"Healthcare","industry":"Biotechnology"},
    {"name":"Arm Holdings PLC","ticker":"ARM","sector":"Technology","industry":"Semiconductors"},
    {"name":"Reddit Inc.","ticker":"RDDT","sector":"Communication","industry":"Internet Services"},
    {"name":"GitLab Inc.","ticker":"GTLB","sector":"Technology","industry":"Software"},
    {"name":"MongoDB Inc.","ticker":"MDB","sector":"Technology","industry":"Software"},
    {"name":"Shopify Inc.","ticker":"SHOP","sector":"Technology","industry":"Software","exchange":"NYSE"},
    {"name":"Nu Holdings Ltd","ticker":"NU","sector":"Financial","industry":"Banks","country":"BR"},
    {"name":"Alibaba Group Holding Ltd","ticker":"BABA","sector":"Consumer Cyclical","industry":"E-Commerce","country":"CN"},
    {"name":"PDD Holdings Inc.","ticker":"PDD","sector":"Consumer Cyclical","industry":"E-Commerce","country":"CN"},
    {"name":"JD.com Inc.","ticker":"JD","sector":"Consumer Cyclical","industry":"E-Commerce","country":"CN"},
    {"name":"Baidu Inc.","ticker":"BIDU","sector":"Technology","industry":"Internet Services","country":"CN"},
    {"name":"NIO Inc.","ticker":"NIO","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"CN"},
    {"name":"Sea Limited","ticker":"SE","sector":"Technology","industry":"Internet Services","country":"SG"},
    {"name":"Novo Nordisk A/S","ticker":"NVO","sector":"Healthcare","industry":"Drug Manufacturers","country":"DK"},
    {"name":"ASML Holding N.V.","ticker":"ASML","sector":"Technology","industry":"Semiconductors","country":"NL"},
    {"name":"TSMC","ticker":"TSM","sector":"Technology","industry":"Semiconductors","country":"TW"},
    {"name":"Toyota Motor Corporation","ticker":"TM","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"JP"},
    {"name":"Honda Motor Co. Ltd.","ticker":"HMC","sector":"Consumer Cyclical","industry":"Auto Manufacturers","country":"JP"},
    {"name":"BP p.l.c.","ticker":"BP","sector":"Energy","industry":"Oil & Gas","country":"GB"},
    {"name":"Shell plc","ticker":"SHEL","sector":"Energy","industry":"Oil & Gas","country":"GB"},
    {"name":"HSBC Holdings plc","ticker":"HSBC","sector":"Financial","industry":"Banks","country":"GB"},
    {"name":"AstraZeneca PLC","ticker":"AZN","sector":"Healthcare","industry":"Drug Manufacturers","country":"GB"},
    {"name":"Unilever PLC","ticker":"UL","sector":"Consumer Defensive","industry":"Household Products","country":"GB"},
    {"name":"BHP Group Ltd","ticker":"BHP","sector":"Basic Materials","industry":"Metals & Mining","country":"AU"},
    {"name":"Rio Tinto Group","ticker":"RIO","sector":"Basic Materials","industry":"Metals & Mining","country":"GB"},
    {"name":"Linde plc","ticker":"LIN","sector":"Basic Materials","industry":"Specialty Chemicals","country":"GB"},
    {"name":"Diageo plc","ticker":"DEO","sector":"Consumer Defensive","industry":"Beverages","country":"GB"},
    {"name":"Anheuser-Busch InBev","ticker":"BUD","sector":"Consumer Defensive","industry":"Beverages","country":"BE"},
    {"name":"Sony Group Corporation","ticker":"SONY","sector":"Technology","industry":"Consumer Electronics","country":"JP"},
    {"name":"Canon Inc.","ticker":"CAJ","sector":"Technology","industry":"Office Equipment","country":"JP"},
    {"name":"Mitsubishi UFJ Financial","ticker":"MUFG","sector":"Financial","industry":"Banks","country":"JP"},
    {"name":"Canadian National Railway","ticker":"CNI","sector":"Industrials","industry":"Railroads","country":"CA"},
    {"name":"Shopify Inc.","ticker":"SHOP","sector":"Technology","industry":"Software","country":"CA"},
    {"name":"Royal Bank of Canada","ticker":"RY","sector":"Financial","industry":"Banks","country":"CA"},
    {"name":"TC Energy Corporation","ticker":"TRP","sector":"Energy","industry":"Oil & Gas Midstream","country":"CA"},
    {"name":"Brookfield Asset Mgmt","ticker":"BAM","sector":"Financial","industry":"Asset Management","country":"CA"},
]


class USScraper(BaseScraper):
    """Scrapes US IPOs from Finnhub API and SEC EDGAR, plus major listed stocks."""

    def __init__(self):
        super().__init__("US")
        self.finnhub_keys = []
        for i in range(1, 6):
            val = __import__("os").environ.get(f"FINNHUB_API_KEY_{i}")
            if val:
                self.finnhub_keys.append({"key": val, "index": i})

    @property
    def source_name(self) -> str:
        return "US (NASDAQ/NYSE/Finnhub/SEC)"

    def _finnhub_call(self, path: str, params: dict) -> Optional[dict]:
        if not self.finnhub_keys:
            return None
        for offset in range(len(self.finnhub_keys)):
            key_entry = self.finnhub_keys[offset]
            try:
                resp = self._get(
                    f"https://finnhub.io/api/v1{path}",
                    params={**params, "token": key_entry["key"]},
                )
                if resp:
                    return resp.json()
            except Exception:
                continue
        return None

    def scrape(self) -> List[IPOData]:
        all_ipos: List[IPOData] = []
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._scrape_finnhub): "finnhub",
                executor.submit(self._scrape_sec_edgar): "sec",
                executor.submit(self._scrape_major_listed): "listed",
            }
            for fut in concurrent.futures.as_completed(futures):
                key = futures[fut]
                try:
                    batch = fut.result()
                    all_ipos.extend(batch)
                    print(f"  [US/{key}] {len(batch)} IPOs")
                except Exception as e:
                    self.errors.append(f"{key}: {e}")
                    print(f"  [US/{key}] Failed: {e}")
        return all_ipos

    def _scrape_finnhub(self) -> List[IPOData]:
        out: List[IPOData] = []
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        future = (datetime.now(timezone.utc) + __import__("datetime").timedelta(days=60)).strftime("%Y-%m-%d")
        data = self._finnhub_call("/ipo/calendar", {"from": today, "to": future})
        if isinstance(data, dict):
            for item in data.get("ipoCalendar", []) or []:
                name = (item.get("name") or "").strip()
                if not name:
                    continue
                ticker = (item.get("symbol") or "").strip().upper()
                exchange = (item.get("exchange") or "").strip()
                out.append(IPOData(
                    id=self._make_id("fh", name),
                    name=name,
                    ticker=ticker,
                    exchange=exchange or "NASDAQ",
                    country="US",
                    status="upcoming",
                    openDate=(item.get("date") or "")[:10],
                    listingDate=(item.get("date") or "")[:10],
                    priceBandHigh=float(item.get("price", 0) or 0),
                    priceBandLow=float(item.get("price", 0) or 0),
                    issueSize=str(item.get("numberOfShares", "") or ""),
                    source="finnhub",
                ))
        return out

    def _scrape_sec_edgar(self) -> List[IPOData]:
        out: List[IPOData] = []
        url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "type": "S-1",
            "owner": "include",
            "count": "40",
            "output": "atom",
        }
        headers = {"User-Agent": "PulseTrends admin@pulsetrends.in"}
        root = self._get_xml(url, params=params, headers=headers)
        if root is None:
            return out
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("a:entry", ns)[:30]:
            title = entry.findtext("a:title", default="", namespaces=ns)
            link = entry.findtext("a:id", default="", namespaces=ns)
            updated = entry.findtext("a:updated", default="", namespaces=ns)
            company = ""
            ticker = ""
            m = re.search(r"^([^(]+?)\s*\(([A-Z]+)\)", title)
            if m:
                company = m.group(1).strip()
                ticker = m.group(2).strip()
            else:
                company = title.strip()
            if not company:
                continue
            out.append(IPOData(
                id=self._make_id("sec", company),
                name=company,
                ticker=ticker,
                exchange="NASDAQ",
                country="US",
                status="upcoming",
                openDate=updated[:10] if updated else "",
                description=(title or "")[:500],
                drhpUrl=link,
                source="sec_edgar",
            ))
        return out

    def _scrape_major_listed(self) -> List[IPOData]:
        out: List[IPOData] = []
        for stock in US_LISTED_STOCKS:
            ticker = stock["ticker"]
            exchange = stock.get("exchange", "NASDAQ")
            if ticker in ("BRK.B",):
                exchange = "NYSE"
            country = stock.get("country", "US")
            out.append(IPOData(
                id=self._make_id("us", stock["name"]),
                name=stock["name"],
                ticker=ticker,
                exchange=exchange,
                sector=stock.get("sector", ""),
                industry=stock.get("industry", ""),
                country=country,
                status="listed",
                description=f"{stock['name']} is a {stock.get('industry', '').lower()} company listed on {exchange}.",
                source="us_listed",
            ))
        return out
