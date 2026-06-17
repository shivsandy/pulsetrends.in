"""
Africa IPO Scanner — JSE (South Africa), EGX (Egypt), NSE (Nigeria), BRVM, ZSE
"""

import re
from typing import List, Optional

from .base import BaseScraper, IPOData


class AfricaScraper(BaseScraper):
    """Scrapes African IPOs from JSE, EGX, NSE Nigeria, and other major African exchanges."""

    def __init__(self):
        super().__init__("Africa")

    @property
    def source_name(self) -> str:
        return "Africa (JSE/EGX/NSE)"

    def scrape(self) -> List[IPOData]:
        ipos: List[IPOData] = []
        for method in [self._scrape_jse, self._scrape_egx, self._scrape_nse_ng,
                       self._scrape_zse, self._scrape_brvm]:
            try:
                batch = method()
                ipos.extend(batch)
                print(f"  [Africa/{method.__name__}] {len(batch)} IPOs")
            except Exception as e:
                self.errors.append(f"{method.__name__}: {e}")
                print(f"  [Africa/{method.__name__}] Failed: {e}")
        return ipos

    def _scrape_jse(self) -> List[IPOData]:
        """JSE (Johannesburg Stock Exchange) - scrape public announcements."""
        url = "https://www.jse.co.za/redirect/ipo-listings"
        resp = self._get(url)
        out: List[IPOData] = []
        if not resp:
            return out
        # Parse IPO listings from the page
        rows = re.findall(
            r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
            resp.text, re.DOTALL | re.IGNORECASE,
        )
        for name, date_str in rows[:20]:
            name = re.sub(r"<[^>]+>", "", name).strip()
            if not name or len(name) < 3:
                continue
            out.append(IPOData(
                id=self._make_id("jse", name),
                name=name,
                exchange="JSE",
                country="ZA",
                status="upcoming",
                listingDate=self._normalize_date(date_str.strip()),
                source="jse",
                currency="ZAR",
            ))
        return out

    def _scrape_egx(self) -> List[IPOData]:
        """EGX (Egyptian Exchange) IPO listings."""
        url = "https://www.egx.com.eg/en/IPOList.aspx"
        resp = self._get(url)
        out: List[IPOData] = []
        if not resp:
            return out
        rows = re.findall(
            r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
            resp.text, re.DOTALL | re.IGNORECASE,
        )
        for name, date_str in rows[:15]:
            name = re.sub(r"<[^>]+>", "", name).strip()
            if not name:
                continue
            out.append(IPOData(
                id=self._make_id("egx", name),
                name=name,
                exchange="EGX",
                country="EG",
                status="upcoming",
                listingDate=self._normalize_date(date_str.strip()),
                source="egx",
                currency="EGP",
            ))
        return out

    def _scrape_nse_ng(self) -> List[IPOData]:
        """Nigerian Exchange (NGX) Group IPO announcements."""
        url = "https://www.nigerianexchange.com/ipo-listings"
        resp = self._get(url)
        out: List[IPOData] = []
        if not resp:
            return out
        rows = re.findall(
            r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
            resp.text, re.DOTALL | re.IGNORECASE,
        )
        for name, date_str in rows[:15]:
            name = re.sub(r"<[^>]+>", "", name).strip()
            if not name:
                continue
            out.append(IPOData(
                id=self._make_id("nse-ng", name),
                name=name,
                exchange="NGX",
                country="NG",
                status="upcoming",
                listingDate=self._normalize_date(date_str.strip()),
                source="nse-ng",
                currency="NGN",
            ))
        return out

    def _scrape_zse(self) -> List[IPOData]:
        """ZSE (Zimbabwe Stock Exchange) - primary market announcements."""
        url = "https://www.zse.co.zw/primary-market"
        resp = self._get(url)
        out: List[IPOData] = []
        if not resp:
            return out
        rows = re.findall(
            r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
            resp.text, re.DOTALL | re.IGNORECASE,
        )
        for name, date_str in rows[:10]:
            name = re.sub(r"<[^>]+>", "", name).strip()
            if not name:
                continue
            out.append(IPOData(
                id=self._make_id("zse", name),
                name=name,
                exchange="ZSE",
                country="ZW",
                status="upcoming",
                listingDate=self._normalize_date(date_str.strip()),
                source="zse",
                currency="ZWL",
            ))
        return out

    def _scrape_brvm(self) -> List[IPOData]:
        """BRVM (Bourse Régionale des Valeurs Mobilières) - West African exchange."""
        url = "https://www.brvm.org/en/ipos"
        resp = self._get(url)
        out: List[IPOData] = []
        if not resp:
            return out
        rows = re.findall(
            r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
            resp.text, re.DOTALL | re.IGNORECASE,
        )
        for name, date_str in rows[:10]:
            name = re.sub(r"<[^>]+>", "", name).strip()
            if not name:
                continue
            out.append(IPOData(
                id=self._make_id("brvm", name),
                name=name,
                exchange="BRVM",
                country="CI",
                status="upcoming",
                listingDate=self._normalize_date(date_str.strip()),
                source="brvm",
                currency="XOF",
            ))
        return out
