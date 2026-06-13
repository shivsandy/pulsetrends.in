#!/usr/bin/env python3
"""
Weekly IPO availability checker.
Reads data/ipo_data.json, checks if upcoming/open IPOs have passed their
listing dates, and transitions them to 'listed'. Updates the file in place.
"""
import json, os, re, logging
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
IPO_DATA_PATH = os.path.join(DATA_DIR, "ipo_data.json")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("ipo-avail")

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def parse_iso_date(s: str):
    """Parse YYYY-MM-DD date (timezone-aware UTC)."""
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
    return None

def parse_indian_short(s: str):
    """Parse '8th jun', '11th jun' etc into a datetime (assumes current year)."""
    s = s.strip().lower().replace("\n", " ")
    m = re.match(r"(\d+)(?:st|nd|rd|th)?\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", s)
    if m:
        day = int(m.group(1))
        month_name = m.group(2)
        month = MONTH_MAP.get(month_name)
        if month:
            now = datetime.now(timezone.utc)
            return datetime(now.year, month, day, tzinfo=timezone.utc)
    return None

def parse_indian_range(s: str):
    """Parse '4th Jun \\n-\\n8th Jun' — use the END date (close date)."""
    s = s.strip().replace("\n", " ").replace("\\n", " ")
    parts = re.split(r"\s*[-–]\s*", s)
    if len(parts) >= 2:
        return parse_indian_short(parts[-1])
    return None

def parse_listing_date(ipo: dict):
    """Try multiple date fields to find a listing date."""
    raw = ipo.get("listingDate") or ipo.get("listing_date") or ""
    if raw and raw.strip() not in ("", chr(65533)):
        d = parse_iso_date(raw) or parse_indian_short(raw)
        if d:
            return d
    raw = ipo.get("openDate") or ipo.get("open_date") or ""
    if raw and raw.strip() not in ("", chr(65533)):
        d = parse_iso_date(raw) or parse_indian_range(raw) or parse_indian_short(raw)
        if d:
            return d
    raw = ipo.get("ipo_date") or ""
    if raw and raw.strip():
        d = parse_iso_date(raw)
        if d:
            return d
    return None

def check_and_update():
    with open(IPO_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    now = datetime.now(timezone.utc)
    changed = 0
    updated = []

    for ipo in data["ipos"]:
        status = ipo.get("status", "")
        if status in ("upcoming", "open"):
            listing_date = parse_listing_date(ipo)
            if listing_date and listing_date < now:
                old_status = ipo["status"]
                ipo["status"] = "listed"
                log.info("%s: %s → listed (listing: %s)", ipo.get("name","?"), old_status, listing_date.date())
                changed += 1
                updated.append(ipo)
    
    if changed:
        data["last_updated"] = now.isoformat()
        data["count"] = len(data["ipos"])
        with open(IPO_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info("Transitioned %d IPOs to listed. File updated.", changed)
    else:
        log.info("No upcoming/open IPOs have passed their listing dates.")
    
    return changed

if __name__ == "__main__":
    check_and_update()
