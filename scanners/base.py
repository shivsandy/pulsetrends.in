"""
Base scraper class for all exchange scanners.
Provides shared HTTP handling, rate limiting, parsing utilities,
and a standardized IPO data output format.
"""

import json
import os
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from xml.etree import ElementTree

import requests


# ─── Standardized IPO Data Model ─────────────────────────────────────

@dataclass
class IPOData:
    """Normalized IPO record used by all scanners."""
    id: str
    name: str
    ticker: str = ""
    exchange: str = ""
    sector: str = ""
    industry: str = ""
    country: str = ""
    status: str = "upcoming"  # upcoming | open | listed | withdrawn
    openDate: str = ""
    closeDate: str = ""
    listingDate: str = ""
    description: str = ""
    about: str = ""
    priceBandHigh: float = 0.0
    priceBandLow: float = 0.0
    lotSize: int = 0
    issueSize: str = ""
    marketCap: float = 0.0
    gmp: float = 0.0
    gmpPercent: float = 0.0
    subscriptionStatus: str = ""
    currency: str = "USD"
    drhpUrl: str = ""
    rhpUrl: str = ""
    source: str = ""
    sourceId: str = ""
    fiscalMetrics: Dict = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScraperResult:
    """Result from a scanner run."""
    source: str
    ipos: List[IPOData]
    errors: List[str] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = ""
    ipos_found: int = 0
    ipos_new: int = 0

    def complete(self):
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.ipos_found = len(self.ipos)


# ─── Base Scraper ────────────────────────────────────────────────────

class BaseScraper(ABC):
    """Abstract base class for all exchange IPO scrapers."""

    # User agent for HTTP requests
    UA = "Mozilla/5.0 (compatible; PulseTrends/1.0; +https://pulsetrends.in)"
    TIMEOUT = 20
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

    def __init__(self, name: str):
        self.name = name
        self.errors: List[str] = []

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable source name (e.g. 'NSE', 'Finnhub')."""
        ...

    @abstractmethod
    def scrape(self) -> List[IPOData]:
        """Execute the scrape and return IPO records."""
        ...

    # ─── HTTP Utilities ──────────────────────────────────────────────

    def _get(self, url: str, params: dict = None, headers: dict = None,
             retries: int = 3, backoff: float = 1.0) -> Optional[requests.Response]:
        """GET with retry + exponential backoff."""
        hdrs = {"User-Agent": self.UA}
        if headers:
            hdrs.update(headers)
        for attempt in range(retries):
            try:
                resp = requests.get(url, params=params, headers=hdrs, timeout=self.TIMEOUT)
                if resp.status_code == 429:
                    wait = backoff * (2 ** attempt) + random.uniform(0, 1)
                    print(f"  [RateLimited] {url} — retrying in {wait:.1f}s")
                    time.sleep(wait)
                    continue
                if resp.status_code != 200:
                    print(f"  [HTTP {resp.status_code}] {url}")
                    return None
                return resp
            except requests.exceptions.Timeout:
                print(f"  [Timeout] {url} (attempt {attempt + 1})")
                if attempt < retries - 1:
                    time.sleep(backoff * (2 ** attempt))
            except Exception as e:
                print(f"  [Error] {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(backoff)
        return None

    def _get_json(self, url: str, params: dict = None, headers: dict = None) -> Optional[dict]:
        resp = self._get(url, params=params, headers=headers)
        if resp and resp.status_code == 200:
            try:
                return resp.json()
            except ValueError:
                return None
        return None

    def _get_xml(self, url: str, params: dict = None, headers: dict = None) -> Optional[ElementTree.Element]:
        resp = self._get(url, params=params, headers=headers)
        if resp:
            try:
                return ElementTree.fromstring(resp.text)
            except ElementTree.ParseError:
                return None
        return None

    # ─── Parsing Utilities ───────────────────────────────────────────

    @staticmethod
    def _slugify(text: str) -> str:
        s = (text or "").strip().lower()
        s = re.sub(r"[^a-z0-9]+", "-", s)
        return re.sub(r"-+", "-", s).strip("-")

    @staticmethod
    def _normalize_date(text: str) -> str:
        if not text:
            return ""
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d %b %Y", "%b %d, %Y",
                     "%d/%m/%Y", "%Y/%m/%d", "%B %d, %Y", "%d %B %Y"):
            try:
                return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                continue
        return text

    @staticmethod
    def _strip_html(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text).strip()

    @staticmethod
    def _parse_number(text: str) -> Optional[float]:
        t = text.strip()
        if not t or t in ("-", "—", "N/A", ""):
            return None
        t = t.replace("$", "").replace("€", "").replace("£", "")
        t = t.replace("¥", "").replace("₹", "").replace(",", "").replace(" ", "")
        try:
            return float(t)
        except ValueError:
            return None

    @staticmethod
    def _parse_percent(text: str) -> Optional[float]:
        t = text.strip()
        if not t or t == "-":
            return None
        t = re.sub(r"[^\d.\-%+]", "", t)
        t = t.replace("%", "").strip()
        try:
            return float(t)
        except ValueError:
            return None

    @staticmethod
    def _make_id(prefix: str, name: str) -> str:
        return f"{prefix}-{BaseScraper._slugify(name)}"

    def _rate_limit(self, seconds: float = 0.5):
        """Sleep to avoid rate limiting."""
        time.sleep(seconds + random.uniform(0, 0.3))

    # ─── Cache / Persistence ─────────────────────────────────────────

    def _load_cache(self, filename: str) -> dict:
        path = os.path.join(self.DATA_DIR, filename)
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache(self, filename: str, data: dict):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        path = os.path.join(self.DATA_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ─── Duplicate Detection ─────────────────────────────────────────────

def make_dupe_key(ipo: IPOData) -> str:
    """Generate a composite key for duplicate detection."""
    parts = []
    if ipo.ticker:
        parts.append(f"ticker:{ipo.ticker.upper()}")
    if ipo.name:
        parts.append(f"name:{ipo.name.lower().strip()}")
    if ipo.exchange:
        parts.append(f"exch:{ipo.exchange.upper()}")
    return "|".join(parts)


def deduplicate_ipos(ipos: List[IPOData]) -> List[IPOData]:
    """Deduplicate IPO list by composite key, keeping latest."""
    seen: Dict[str, IPOData] = {}
    for ipo in ipos:
        key = make_dupe_key(ipo)
        if key not in seen or ipo.last_updated > seen[key].last_updated:
            seen[key] = ipo
    return list(seen.values())
