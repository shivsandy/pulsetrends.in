from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Optional


EXCHANGE_COUNTRY = {
    "NSE": "India", "BSE": "India",
    "NASDAQ": "USA", "NYSE": "USA", "NYSE AMERICAN": "USA", "NYSE ARCA": "USA",
    "LSE": "UK", "LSE MAIN MARKET": "UK", "AIM": "UK",
    "HKSE": "Hong Kong", "HKEX": "Hong Kong",
    "TSE": "Japan", "TYO": "Japan",
    "ASX": "Australia",
    "TSX": "Canada", "TSXV": "Canada",
    "EURONEXT": "Europe", "ENX.PA": "Europe", "XPAR": "Europe",
    "XETRA": "Europe", "FRA": "Europe",
    "SIX": "Switzerland",
    "SGX": "Singapore",
    "KRX": "South Korea", "KOSDAQ": "South Korea",
    "TWSE": "Taiwan",
    "SSE": "China", "SZSE": "China", "HKG": "Hong Kong",
    "BMV": "Mexico",
    "B3": "Brazil", "BVMF": "Brazil",
    "JSE": "South Africa",
    "TEL AVIV": "Israel", "TASE": "Israel",
}


def get_country(exchange: str) -> str:
    exchange_upper = exchange.strip().upper()
    if exchange_upper in EXCHANGE_COUNTRY:
        return EXCHANGE_COUNTRY[exchange_upper]
    for key, country in EXCHANGE_COUNTRY.items():
        if key in exchange_upper or exchange_upper in key:
            return country
    return "Global"


@dataclass
class IPO:
    company_name: str = ""
    symbol: str = ""
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
    country: str = "India"


class BaseScraper(ABC):
    source_name: str = ""

    @abstractmethod
    def scrape(self) -> List[IPO]:
        pass

    def to_dicts(self, ipos: List[IPO]) -> List[dict]:
        return [asdict(ipo) for ipo in ipos]

    def set_country(self, ipo: IPO):
        if not ipo.country or ipo.country == "India":
            ipo.country = get_country(ipo.exchange)
