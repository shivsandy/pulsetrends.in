#!/usr/bin/env python3
"""
Scrape ALL Indian IPO data from Screener.in
=============================================
Scrapes:
  1. Upcoming IPOs from https://www.screener.in/ipo/
  2. Recent IPOs from https://www.screener.in/ipo/recent/ (pages 1-40)
  3. Below IPO Price from https://www.screener.in/ipo/below-price/ (pages 1-40)
  4. Upcoming Rights from https://www.screener.in/ipo/rights/

Output: data/screener_ipos.json (all IPOs merged)
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 30
MAX_PAGES = 40
RECENT_LOOKBACK_DAYS = 90  # Show IPOs within last 90 days


def fetch_page(url: str) -> Optional[str]:
    """Fetch a page with retry logic."""
    headers = {"User-Agent": UA}
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"  [RateLimited] Retrying in {wait}s...")
                time.sleep(wait)
                continue
            if resp.status_code == 200:
                return resp.text
            print(f"  [HTTP {resp.status_code}] {url}")
            return None
        except Exception as e:
            print(f"  [Error] {url}: {e}")
            if attempt < 2:
                time.sleep(3)
    return None


def parse_date(text: str) -> Optional[str]:
    """Parse various date formats from screener.in to YYYY-MM-DD."""
    if not text:
        return None
    text = text.strip().lower()

    if text == "today":
        return datetime.now().strftime("%Y-%m-%d")
    if text == "tomorrow":
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    for fmt in ["%d %b %Y", "%d %B %Y"]:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', text)
    current_year = datetime.now().year
    for fmt in ["%d %b", "%d %B"]:
        try:
            dt = datetime.strptime(f"{cleaned} {current_year}", f"{fmt} %Y")
            if dt < datetime.now() - timedelta(days=180):
                dt = dt.replace(year=current_year + 1)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    range_match = re.match(r'(\d+)(?:st|nd|rd|th)\s+(\w+)\s*-\s*(\d+)(?:st|nd|rd|th)\s+(\w+)', text)
    if range_match:
        day, month = range_match.group(1), range_match.group(2)
        try:
            dt = datetime.strptime(f"{day} {month} {current_year}", "%d %b %Y")
            if dt < datetime.now() - timedelta(days=180):
                dt = dt.replace(year=current_year + 1)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    single_match = re.match(r'(\d+)(?:st|nd|rd|th)\s+(\w+)', text)
    if single_match:
        day, month = single_match.group(1), single_match.group(2)
        try:
            dt = datetime.strptime(f"{day} {month} {current_year}", "%d %b %Y")
            if dt < datetime.now() - timedelta(days=180):
                dt = dt.replace(year=current_year + 1)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return text


def parse_number(text: str) -> Optional[float]:
    """Parse a number string, handling Indian format."""
    if not text or text in ("-", "—", "N/A", ""):
        return None
    text = text.strip()
    text = text.replace("\u20b9", "").replace(",", "").replace(" ", "")
    text = text.replace("Cr", "").replace("cr", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def parse_price(text: str) -> Optional[str]:
    """Parse a price value."""
    if not text or text in ("-", "—", "N/A", "\u20b9", ""):
        return None
    text = text.strip().replace("\u20b9", "").strip()
    return text or None


def parse_percent(text: str) -> Optional[str]:
    """Parse percentage change."""
    if not text or text in ("-", "—", "N/A", ""):
        return None
    text = text.strip()
    match = re.search(r'([\u21e1\u21e3])\s*([\d.]+)%', text)
    if match:
        sign = "+" if match.group(1) == "\u21e1" else "-"
        return f"{sign}{match.group(2)}%"
    match = re.search(r'([+\-]?[\d.]+)%', text)
    if match:
        return f"{match.group(1)}%"
    return text


def _slugify(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def scrape_table_page(url: str, label: str, columns: list, page_limit: int = 1, cutoff_date=None) -> list:
    """Scrape a paginated table on screener.in. Each page has the same column structure."""
    all_ipos = []
    for page in range(1, page_limit + 1):
        page_url = f"{url}?page={page}" if page_limit > 1 else url
        print(f"[{label}] Page {page}/{page_limit}...", end=" ")
        sys.stdout.flush()

        html = fetch_page(page_url)
        if not html:
            print("FAILED")
            continue

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tbody tr")

        if not rows:
            print("No rows found")
            continue

        page_ipos = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < len(columns):
                continue

            link = row.find("a")
            if not link:
                continue

            name = link.get_text(strip=True)
            href = link.get("href", "")

            cell_texts = [cell.get_text(strip=True) for cell in cells]

            ipo = {
                "name": name,
                "source_url": f"https://www.screener.in{href}" if href else "",
                "exchange": "NSE/BSE",
                "sector": "mainboard",
            }

            for col_idx, col_name in enumerate(columns):
                if col_idx >= len(cell_texts):
                    continue
                val = cell_texts[col_idx]

                if col_name == "listing_date":
                    dt = parse_date(val)
                    ipo["listingDate"] = dt or ""
                    if dt and cutoff_date and page_limit > 1:
                        try:
                            dto = datetime.strptime(dt, "%Y-%m-%d")
                            if dto < cutoff_date:
                                break  # Stop this page, rest will be older
                        except ValueError:
                            pass

                elif col_name == "sub_period":
                    dates = val.split("-")
                    if len(dates) >= 2:
                        ipo["openDate"] = parse_date(dates[0].strip()) or ""
                        ipo["closeDate"] = parse_date(dates[1].strip()) or ""
                    elif len(dates) == 1:
                        ipo["openDate"] = parse_date(dates[0].strip()) or ""

                elif col_name == "mcap":
                    ipo["marketCap"] = parse_number(val)

                elif col_name == "pe":
                    ipo["pe"] = parse_number(val)

                elif col_name == "roce":
                    ipo["roce"] = parse_percent(val)

                elif col_name == "ipo_mcap":
                    ipo["ipoMcap"] = parse_number(val)

                elif col_name == "ipo_price":
                    ipo["ipoPrice"] = parse_price(val)

                elif col_name == "current_price":
                    ipo["currentPrice"] = parse_price(val)

                elif col_name == "change_pct":
                    ipo["percentChange"] = parse_percent(val)

                elif col_name == "ex_date":
                    ipo["exDate"] = parse_date(val) or ""

                elif col_name == "ratio":
                    ipo["rightsRatio"] = val

                elif col_name == "rights_price":
                    ipo["rightsPrice"] = parse_price(val)

                elif col_name == "diff_pct":
                    ipo["percentDiff"] = parse_percent(val)

            # Handle the break from the inner loop (cutoff check)
            if "break" in dir() and ipo.get("listingDate") and cutoff_date:
                try:
                    dto = datetime.strptime(ipo["listingDate"], "%Y-%m-%d")
                    if dto < cutoff_date:
                        break_outer = True
                        break
                except ValueError:
                    pass

            page_ipos.append(ipo)

        all_ipos.extend(page_ipos)
        print(f"{len(page_ipos)} IPOs")
        time.sleep(1.0)

    return all_ipos


def scrape_upcoming_detail(url: str, name: str) -> dict:
    """Scrape IPO detail page for price band, lot size, and issue size."""
    html = fetch_page(url)
    if not html:
        return {}
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    # Look for "Price Band" in the page — often in a key-value table
    rows = soup.select("table td, div.flex div")
    page_text = soup.get_text()
    
    # Try to find price band: "₹XXX - ₹XXX"
    price_match = re.search(r'₹\s*([\d,.]+)\s*-\s*₹\s*([\d,.]+)', page_text)
    if price_match:
        try:
            data["priceBandLow"] = float(price_match.group(1).replace(",", ""))
            data["priceBandHigh"] = float(price_match.group(2).replace(",", ""))
        except ValueError:
            pass

    # Try to find lot size
    lot_match = re.search(r'(\d+)\s*shares\s*(?:per|/)\s*lot', page_text, re.IGNORECASE)
    if lot_match:
        try:
            data["lotSize"] = int(lot_match.group(1))
        except ValueError:
            pass
    else:
        lot_match2 = re.search(r'Lot\s*Size[:\s]*(\d+)', page_text, re.IGNORECASE)
        if lot_match2:
            try:
                data["lotSize"] = int(lot_match2.group(1))
            except ValueError:
                pass

    # Try to find issue size
    issue_match = re.search(r'(?:Issue\s*(?:Size|Amount)|Total\s*Issue)[:\s]*₹?\s*([\d,.]+)\s*(Cr|Crore)', page_text, re.IGNORECASE)
    if issue_match:
        try:
            val = float(issue_match.group(1).replace(",", ""))
            data["issueSize"] = f"₹{val:.0f} Cr"
        except ValueError:
            pass
    
    # Try "Fresh Issue" / "OFS" total
    if not data.get("issueSize"):
        total_match = re.search(r'(?:Total|Issue\s*Size)[:\s]*₹?\s*([\d,.]+)\s*(Cr|Crore)', page_text, re.IGNORECASE)
        if total_match:
            try:
                val = float(total_match.group(1).replace(",", ""))
                data["issueSize"] = f"₹{val:.0f} Cr"
            except ValueError:
                pass

    return data


def scrape_upcoming_ipos() -> list:
    """Scrape upcoming IPOs from /ipo/."""
    print("\n[Upcoming] Scraping https://www.screener.in/ipo/ ...")
    ipos = scrape_table_page(
        "https://www.screener.in/ipo/",
        "Upcoming",
        ["name", "sub_period", "listing_date", "mcap", "subscription", "pe", "roce"],
        page_limit=1,
    )
    for ipo in ipos:
        ipo["status"] = "upcoming"
        # Scrape detail page for price band, lot size, issue size
        detail_url = ipo.get("source_url", "")
        if detail_url:
            print(f"  [Detail] Scraping {ipo['name']}...")
            detail = scrape_upcoming_detail(detail_url, ipo["name"])
            if detail.get("priceBandLow"):
                ipo["priceBandLow"] = detail["priceBandLow"]
                ipo["priceBandHigh"] = detail["priceBandHigh"]
                print(f"    Price: ₹{detail['priceBandLow']} - ₹{detail['priceBandHigh']}")
            if detail.get("lotSize"):
                ipo["lotSize"] = detail["lotSize"]
                print(f"    Lot: {detail['lotSize']}")
            if detail.get("issueSize"):
                ipo["issueSize"] = detail["issueSize"]
                print(f"    Issue: {detail['issueSize']}")
            time.sleep(1.5)
    print(f"[Upcoming] Found {len(ipos)} IPOs")
    return ipos


def scrape_recent_ipos() -> list:
    """Scrape recent IPOs from /ipo/recent/ pages 1-40."""
    print(f"\n[Recent] Scraping https://www.screener.in/ipo/recent/ (1-{MAX_PAGES}) ...")
    cutoff = datetime.now() - timedelta(days=RECENT_LOOKBACK_DAYS)
    ipos = scrape_table_page(
        "https://www.screener.in/ipo/recent/",
        "Recent",
        ["name", "listing_date", "ipo_mcap", "ipo_price", "current_price", "change_pct"],
        page_limit=MAX_PAGES,
        cutoff_date=cutoff,
    )
    for ipo in ipos:
        ipo["status"] = "listed"
    print(f"[Recent] Found {len(ipos)} IPOs within {RECENT_LOOKBACK_DAYS} days")
    return ipos


def scrape_below_price_ipos() -> list:
    """Scrape IPOs trading below issue price."""
    print(f"\n[BelowPrice] Scraping https://www.screener.in/ipo/below-price/ (1-{MAX_PAGES}) ...")
    cutoff = datetime.now() - timedelta(days=365)  # Last 1 year
    ipos = scrape_table_page(
        "https://www.screener.in/ipo/below-price/",
        "BelowPrice",
        ["name", "listing_date", "ipo_mcap", "ipo_price", "current_price", "change_pct"],
        page_limit=MAX_PAGES,
        cutoff_date=cutoff,
    )
    for ipo in ipos:
        ipo["status"] = "listed"
        ipo["source_category"] = "below_price"
    print(f"[BelowPrice] Found {len(ipos)} IPOs below IPO price")
    return ipos


def scrape_rights_ipos() -> list:
    """Scrape upcoming rights issues."""
    print("\n[Rights] Scraping https://www.screener.in/ipo/rights/ ...")
    ipos = scrape_table_page(
        "https://www.screener.in/ipo/rights/",
        "Rights",
        ["name", "ex_date", "ratio", "rights_price", "current_price", "diff_pct"],
        page_limit=1,
    )
    for ipo in ipos:
        ipo["status"] = "rights"
        ipo["source_category"] = "rights"
    print(f"[Rights] Found {len(ipos)} rights issues")
    return ipos


def merge_and_deduplicate(all_ipos_list: list) -> list:
    """Merge lists of IPOs, deduplicating by source_url."""
    seen_urls = set()
    merged = []
    for ipo in all_ipos_list:
        key = ipo.get("source_url", "") or ipo.get("name", "")
        if key and key not in seen_urls:
            seen_urls.add(key)
            merged.append(ipo)
    return merged


def map_to_ipo_data_format(upcoming: list, recent: list, below_price: list, rights: list) -> list:
    """Map scraped data to standardized format."""
    ipos = []

    for ipo in upcoming:
        entry = {
            "id": f"screener-upcoming-{_slugify(ipo['name'])}",
            "name": ipo["name"],
            "ticker": "",
            "exchange": ipo.get("exchange", "NSE/BSE"),
            "sector": ipo.get("sector", "mainboard"),
            "industry": "",
            "country": "IN",
            "status": "upcoming",
            "openDate": ipo.get("openDate", ""),
            "closeDate": ipo.get("closeDate", ""),
            "listingDate": ipo.get("listingDate", ""),
            "description": f"{ipo['name']} - Upcoming IPO",
            "about": "",
            "priceBandHigh": 0,
            "priceBandLow": 0,
            "lotSize": 0,
            "issueSize": "",
            "marketCap": ipo.get("marketCap") or 0,
            "gmp": 0,
            "gmpPercent": 0,
            "subscriptionStatus": "",
            "currency": "INR",
            "source": "screener.in",
            "source_url": ipo.get("source_url", ""),
            "source_category": "upcoming",
            "fiscalMetrics": {
                "pe": ipo.get("pe"),
                "roce": ipo.get("roce"),
            },
            "currentPrice": 0,
            "percentChange": 0,
        }
        ipos.append(entry)

    for ipo_list, category in [(recent, "recent"), (below_price, "below_price"), (rights, "rights")]:
        for ipo in ipo_list:
            ipo_price_raw = ipo.get("ipoPrice") or ""
            ipo_price_num = 0
            if ipo_price_raw:
                # Strip ₹ and other chars
                clean = re.sub(r'[₹,\s]', '', str(ipo_price_raw))
                try:
                    ipo_price_num = float(clean)
                except (ValueError, TypeError):
                    pass

            entry = {
                "id": f"screener-{category}-{_slugify(ipo['name'])}",
                "name": ipo["name"],
                "ticker": "",
                "exchange": ipo.get("exchange", "NSE/BSE"),
                "sector": ipo.get("sector", "mainboard"),
                "industry": "",
                "country": "IN",
                "status": "rights" if category == "rights" else "listed",
                "openDate": "",
                "closeDate": "",
                "listingDate": ipo.get("listingDate", ""),
                "description": f"{ipo['name']} - Listed on {ipo.get('listingDate', 'N/A')}",
                "about": "",
                "priceBandHigh": ipo_price_num,
                "priceBandLow": ipo_price_num,
                "lotSize": 0,
                "issueSize": "",
                "marketCap": ipo.get("ipoMcap") or ipo.get("marketCap") or 0,
                "gmp": 0,
                "gmpPercent": 0,
                "subscriptionStatus": "",
                "currency": "INR",
                "source": "screener.in",
                "source_url": ipo.get("source_url", ""),
                "source_category": category,
                "fiscalMetrics": {
                    "ipoPrice": ipo_price_raw,
                    "currentPrice": ipo.get("currentPrice"),
                    "exDate": ipo.get("exDate", ""),
                    "rightsRatio": ipo.get("rightsRatio", ""),
                    "rightsPrice": ipo.get("rightsPrice", ""),
                },
                "currentPrice": parse_number(ipo.get("currentPrice")) or 0,
                "percentChange": 0,
            }
            ipos.append(entry)

    return ipos


def save_output(ipos: list):
    """Save scraped IPO data to JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)

    output_path = os.path.join(DATA_DIR, "screener_ipos.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": "screener.in",
            "count": len(ipos),
            "ipos": ipos,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n[Output] Saved {len(ipos)} IPOs to {output_path}")

    preview_path = os.path.join(DATA_DIR, "screener_ipos_preview.json")
    preview = [{
        "name": ipo["name"],
        "status": ipo.get("status", ""),
        "source_category": ipo.get("source_category", ""),
        "listingDate": ipo.get("listingDate", ""),
        "marketCap": ipo.get("marketCap", 0),
    } for ipo in ipos]
    with open(preview_path, "w", encoding="utf-8") as f:
        json.dump(preview, f, indent=2, ensure_ascii=False)
    print(f"[Output] Saved preview to {preview_path}")


def main():
    print("=" * 60)
    print("  SCREENER.IN COMPREHENSIVE IPO SCRAPER")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Sources: Upcoming, Recent(1-{MAX_PAGES}), BelowPrice(1-{MAX_PAGES}), Rights")
    print(f"  Recent lookback: {RECENT_LOOKBACK_DAYS} days")
    print("=" * 60)

    upcoming = scrape_upcoming_ipos()
    recent = scrape_recent_ipos()
    below_price = scrape_below_price_ipos()
    rights = scrape_rights_ipos()

    print(f"\n[Merge] Raw counts: {len(upcoming)} upcoming + {len(recent)} recent + {len(below_price)} below-price + {len(rights)} rights")
    all_raw = merge_and_deduplicate(upcoming + recent + below_price + rights)
    print(f"[Merge] After dedup: {len(all_raw)} unique IPOs")

    print(f"\n[Merge] Mapping to standard format...")
    all_ipos = map_to_ipo_data_format(upcoming, recent, below_price, rights)

    save_output(all_ipos)

    print(f"\n{'=' * 60}")
    print(f"  COMPLETE")
    cats = {}
    for ipo in all_ipos:
        cat = ipo.get("source_category", "unknown")
        cats[cat] = cats.get(cat, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
    print(f"  Total: {len(all_ipos)}")
    print(f"  File: data/screener_ipos.json")
    print(f"  Next: Run python scripts/scrape_screener_financial_data.py to fetch detailed financials")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
