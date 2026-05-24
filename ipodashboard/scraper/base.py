from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import Optional, List


@dataclass
class IPO:
    company_name: str = ""
    price_band: str = ""
    open_date: str = ""
    close_date: str = ""
    listing_date: str = ""
    lot_size: str = ""
    issue_size: str = ""
    gmp: str = ""
    subscription: str = ""
    status: str = "upcoming"
    exchange: str = "NSE"
    ipo_type: str = "mainboard"


class BaseScraper(ABC):
    source_name: str = ""

    @abstractmethod
    def scrape(self) -> List[IPO]:
        pass

    def to_dicts(self, ipos: List[IPO]) -> List[dict]:
        return [asdict(ipo) for ipo in ipos]
