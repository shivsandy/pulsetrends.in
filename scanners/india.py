"""
India IPO Scanner — NSE, BSE, Chittorgarh, InvestorGain, Screener.in
"""

import re
import concurrent.futures
from typing import List

from .base import BaseScraper, IPOData


class IndiaScraper(BaseScraper):
    """Scrapes Indian IPOs from NSE, BSE, Chittorgarh, InvestorGain, and Screener.in"""

    def __init__(self):
        super().__init__("India")

    @property
    def source_name(self) -> str:
        return "India (NSE/BSE/Chittorgarh/Screener)"

    def scrape(self) -> List[IPOData]:
        all_ipos: List[IPOData] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._scrape_nse_bse): "nse_bse",
                executor.submit(self._scrape_chittorgarh): "chittorgarh",
                executor.submit(self._scrape_investorgain): "investorgain",
                executor.submit(self._scrape_screener): "screener",
            }
            for fut in concurrent.futures.as_completed(futures):
                key = futures[fut]
                try:
                    batch = fut.result()
                    all_ipos.extend(batch)
                    print(f"  [India/{key}] {len(batch)} IPOs")
                except Exception as e:
                    self.errors.append(f"{key}: {e}")
                    print(f"  [India/{key}] Failed: {e}")
        return all_ipos

    def _scrape_nse_bse(self) -> List[IPOData]:
        out: List[IPOData] = []
        endpoints = [
            ("https://www.nseindia.com/api/ipo/current-issue", "nse"),
            ("https://www.nseindia.com/api/ipo/upcoming-issue", "nse-up"),
            ("https://api.bseindia.com/BseIndiaAPI/api/IPODataNew/w?strType=A", "bse"),
        ]
        headers = {
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        }
        for url, sid in endpoints:
            data = self._get_json(url, headers=headers)
            if not data:
                continue
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for key in ("data", "Table", "ipoList", "Upcoming"):
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break
            for item in items[:30]:
                name = (item.get("CompanyName") or item.get("Company") or item.get("name") or "").strip()
                if not name:
                    continue
                sym = (item.get("Symbol") or item.get("symbol") or "").strip().upper()
                out.append(IPOData(
                    id=self._make_id(sid, name),
                    name=name,
                    ticker=sym,
                    exchange="NSE" if "nse" in sid else "BSE",
                    sector=item.get("Industry", "") or item.get("Sector", ""),
                    industry=item.get("Industry", ""),
                    country="IN",
                    status="open" if (item.get("IssueType") or "").lower() == "open" else "upcoming",
                    openDate=self._normalize_date(str(item.get("IssueStartDate") or item.get("OpenDate") or "")),
                    closeDate=self._normalize_date(str(item.get("IssueEndDate") or item.get("CloseDate") or "")),
                    listingDate=self._normalize_date(str(item.get("ListingDate") or "")),
                    priceBandHigh=float(item.get("UpperPriceBand") or item.get("PriceBandHigh") or 0),
                    priceBandLow=float(item.get("LowerPriceBand") or item.get("PriceBandLow") or 0),
                    lotSize=int(item.get("LotSize") or 0),
                    issueSize=str(item.get("IssueSize") or ""),
                    source=sid,
                    currency="INR",
                ))
            self._rate_limit(0.5)
        return out

    def _scrape_chittorgarh(self) -> List[IPOData]:
        urls = [
            ("https://www.chittorgarh.com/report/ipo-in-india-list-mainboard/83/all/?type=upcoming", "ch-main"),
            ("https://www.chittorgarh.com/report/ipo-in-india-list-sme/84/all/?type=upcoming", "ch-sme"),
        ]
        out: List[IPOData] = []
        for url, sid in urls:
            resp = self._get(url)
            if not resp:
                continue
            rows = re.findall(
                r'<tr[^>]*>\s*<td[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?</tr>',
                resp.text, re.DOTALL | re.IGNORECASE,
            )
            for href, name in rows[:30]:
                name = re.sub(r"\s+", " ", name).strip()
                if not name or len(name) < 3:
                    continue
                out.append(IPOData(
                    id=self._make_id(sid, name),
                    name=name,
                    exchange="NSE/BSE",
                    country="IN",
                    status="upcoming",
                    source=sid,
                    currency="INR",
                ))
            self._rate_limit(0.5)
        return out

    def _scrape_investorgain(self) -> List[IPOData]:
        url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
        resp = self._get(url)
        out: List[IPOData] = []
        if not resp:
            return out
        blocks = re.findall(
            r'<div[^>]*class="[^"]*ipo-card[^"]*"[^>]*>(.*?)(?=<div[^>]*class="[^"]*ipo-card|</div>\s*</div>\s*</div>)',
            resp.text, re.DOTALL | re.IGNORECASE,
        )
        for block in blocks[:30]:
            name_m = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', block, re.DOTALL)
            name = re.sub(r"<[^>]+>", "", name_m.group(1)).strip() if name_m else ""
            if not name:
                continue
            gmp_m = re.search(r'GMP[^0-9-]*(-?\d+)', block, re.IGNORECASE)
            gmp = int(gmp_m.group(1)) if gmp_m else 0
            sub_m = re.search(r'(?:Subscribed|Subscription)[^0-9]*([\d.]+)x', block, re.IGNORECASE)
            sub = sub_m.group(1) + "x" if sub_m else ""
            out.append(IPOData(
                id=self._make_id("ig", name),
                name=name,
                exchange="NSE/BSE",
                country="IN",
                status="open" if sub else "upcoming",
                gmp=float(gmp),
                subscriptionStatus=sub,
                source="investorgain",
                currency="INR",
            ))
        return out

    def _scrape_screener(self) -> List[IPOData]:
        base_url = "https://www.screener.in/ipo/recent/"
        out: List[IPOData] = []
        for page in range(1, 21):
            url = f"{base_url}?page={page}"
            resp = self._get(url)
            if not resp:
                break
            tbody_m = re.search(r'<tbody>(.*?)</tbody>', resp.text, re.DOTALL | re.IGNORECASE)
            if not tbody_m:
                break
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody_m.group(1), re.DOTALL | re.IGNORECASE)
            if not rows:
                break
            for row in rows:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                if len(cells) < 4:
                    continue
                name_m = re.search(r'<a[^>]*>([^<]+)', cells[0], re.DOTALL)
                name = re.sub(r"\s+", " ", name_m.group(1)).strip() if name_m else ""
                if not name:
                    continue
                out.append(IPOData(
                    id=self._make_id("screener", name),
                    name=name,
                    exchange="BSE",
                    country="IN",
                    status="listed",
                    source="screener",
                    currency="INR",
                ))
            self._rate_limit(1.0)
        return out
