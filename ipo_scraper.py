import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
from xml.etree import ElementTree

import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
IPO_FILE = os.path.join(DATA_DIR, "ipo_data.json")
IPO_CACHE_META = os.path.join(DATA_DIR, "ipo_cache_meta.json")

UA = "Mozilla/5.0 (compatible; PulseTrends/1.0; +https://pulsetrends.in)"
TIMEOUT = 20

FINNHUB_KEYS = []
for i in range(1, 6):
    val = os.environ.get(f"FINNHUB_API_KEY_{i}")
    if val:
        FINNHUB_KEYS.append({"key": val, "index": i})


def _finnhub_call(path: str, params: dict, fallback_idx: int = 0) -> Optional[dict]:
    if not FINNHUB_KEYS:
        return None
    for offset in range(len(FINNHUB_KEYS)):
        key_entry = FINNHUB_KEYS[(fallback_idx + offset) % len(FINNHUB_KEYS)]
        try:
            resp = requests.get(
                f"https://finnhub.io/api/v1{path}",
                params={**params, "token": key_entry["key"]},
                headers={"User-Agent": UA},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                continue
            return None
        except Exception as e:
            print(f"[IPO Scraper] Finnhub {path} failed on key {key_entry['index']}: {e}")
            continue
    return None


def _slugify(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def _normalize_date(text: str) -> str:
    if not text:
        return ""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d %b %Y", "%b %d, %Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    return text


def load_existing_ipos() -> List[dict]:
    if not os.path.exists(IPO_FILE):
        return []
    try:
        with open(IPO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("ipos", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_cache_meta() -> dict:
    if not os.path.exists(IPO_CACHE_META):
        return {}
    try:
        with open(IPO_CACHE_META, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache_meta(meta: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(IPO_CACHE_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def needs_refresh() -> bool:
    meta = load_cache_meta()
    last = meta.get("last_updated")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        age_days = (datetime.now(timezone.utc) - last_dt).days
        return age_days >= 2
    except (ValueError, TypeError):
        return True


def scrape_sec_edgar() -> List[dict]:
    """Pull recent SEC filings (S-1, 424B4, EFFECT) for IPOs in the last 30 days."""
    url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        "action": "getcompany",
        "type": "S-1",
        "dateb": "",
        "owner": "include",
        "count": "40",
        "action": "getcompany",
        "output": "atom",
    }
    headers = {"User-Agent": "PulseTrends admin@pulsetrends.in"}
    out: List[dict] = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"[IPO Scraper] SEC EDGAR HTTP {resp.status_code}")
            return out
        root = ElementTree.fromstring(resp.text)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("a:entry", ns)[:30]:
            title = entry.findtext("a:title", default="", namespaces=ns)
            link = entry.findtext("a:id", default="", namespaces=ns)
            updated = entry.findtext("a:updated", default="", namespaces=ns)
            content = entry.findtext("a:content", default="", namespaces=ns)
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
            out.append({
                "id": f"sec-{_slugify(company)}",
                "name": company,
                "ticker": ticker,
                "exchange": "NASDAQ",
                "sector": "",
                "industry": "",
                "status": "upcoming",
                "openDate": updated[:10] if updated else "",
                "closeDate": "",
                "listingDate": "",
                "description": (content or "")[:500],
                "about": "",
                "priceBandHigh": 0,
                "priceBandLow": 0,
                "lotSize": 0,
                "issueSize": "",
                "gmp": 0,
                "gmpPercent": 0,
                "subscriptionStatus": "",
                "anchorInvestors": [],
                "rhpDate": "",
                "allotmentDate": "",
                "refundDate": "",
                "drhpUrl": link,
                "rhpUrl": "",
                "fiscalMetrics": {},
                "source": "sec_edgar",
                "last_updated": datetime.now(timezone.utc).isoformat(),
            })
        time.sleep(0.15)
    except Exception as e:
        print(f"[IPO Scraper] SEC EDGAR failed: {e}")
    print(f"[IPO Scraper] SEC EDGAR: {len(out)} filings")
    return out


def scrape_finnhub() -> List[dict]:
    """Use Finnhub /ipo/calendar and /stock/symbol for upcoming IPOs."""
    out: List[dict] = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    end = datetime.now(timezone.utc)
    from datetime import timedelta
    future = (end + timedelta(days=60)).strftime("%Y-%m-%d")
    data = _finnhub_call("/ipo/calendar", {"from": today, "to": future})
    if isinstance(data, dict):
        items = data.get("ipoCalendar", []) or []
        for item in items[:50]:
            name = (item.get("name") or "").strip()
            if not name:
                continue
            ticker = (item.get("symbol") or "").strip().upper()
            exchange = (item.get("exchange") or "").strip()
            out.append({
                "id": f"fh-{_slugify(name)}",
                "name": name,
                "ticker": ticker,
                "exchange": exchange or "US",
                "sector": "",
                "industry": "",
                "status": "upcoming",
                "openDate": (item.get("date") or "")[:10],
                "closeDate": "",
                "listingDate": (item.get("date") or "")[:10],
                "description": "",
                "about": "",
                "priceBandHigh": float(item.get("price", 0) or 0),
                "priceBandLow": float(item.get("price", 0) or 0),
                "lotSize": 0,
                "issueSize": str(item.get("numberOfShares", "") or ""),
                "gmp": 0,
                "gmpPercent": 0,
                "subscriptionStatus": "",
                "anchorInvestors": [],
                "rhpDate": "",
                "allotmentDate": "",
                "refundDate": "",
                "drhpUrl": "",
                "rhpUrl": "",
                "fiscalMetrics": {},
                "source": "finnhub",
                "last_updated": datetime.now(timezone.utc).isoformat(),
            })
    print(f"[IPO Scraper] Finnhub: {len(out)} IPOs")
    return out


def scrape_chittorgarh() -> List[dict]:
    """Scrape Chittorgarh.com mainboard + SME board."""
    urls = [
        ("https://www.chittorgarh.com/report/ipo-in-india-list-mainboard/83/all/?type=upcoming", "ch-main-upcoming"),
        ("https://www.chittorgarh.com/report/ipo-in-india-list-sme/84/all/?type=upcoming", "ch-sme-upcoming"),
    ]
    out: List[dict] = []
    for url, sid_prefix in urls:
        try:
            resp = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
            if resp.status_code != 200:
                print(f"[IPO Scraper] Chittorgarh {url} HTTP {resp.status_code}")
                continue
            html = resp.text
            rows = re.findall(
                r'<tr[^>]*>\s*<td[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?</tr>',
                html, re.DOTALL | re.IGNORECASE,
            )
            for href, name in rows[:30]:
                name = re.sub(r"\s+", " ", name).strip()
                if not name or len(name) < 3:
                    continue
                out.append({
                    "id": f"{sid_prefix}-{_slugify(name)}",
                    "name": name,
                    "ticker": "",
                    "exchange": "NSE/BSE",
                    "sector": "",
                    "industry": "",
                    "status": "upcoming",
                    "openDate": "",
                    "closeDate": "",
                    "listingDate": "",
                    "description": "",
                    "about": "",
                    "priceBandHigh": 0,
                    "priceBandLow": 0,
                    "lotSize": 0,
                    "issueSize": "",
                    "gmp": 0,
                    "gmpPercent": 0,
                    "subscriptionStatus": "",
                    "anchorInvestors": [],
                    "rhpDate": "",
                    "allotmentDate": "",
                    "refundDate": "",
                    "drhpUrl": "",
                    "rhpUrl": f"https://www.chittorgarh.com{href}" if href.startswith("/") else href,
                    "fiscalMetrics": {},
                    "source": "chittorgarh",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                })
            time.sleep(0.4)
        except Exception as e:
            print(f"[IPO Scraper] Chittorgarh {url} failed: {e}")
    print(f"[IPO Scraper] Chittorgarh: {len(out)} IPOs")
    return out


def scrape_investorgain() -> List[dict]:
    """Scrape InvestorGain IPO list (GMP + subscription)."""
    url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
    out: List[dict] = []
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"[IPO Scraper] InvestorGain HTTP {resp.status_code}")
            return out
        html = resp.text
        block_re = re.compile(
            r'<div[^>]*class="[^"]*ipo-card[^"]*"[^>]*>(.*?)(?=<div[^>]*class="[^"]*ipo-card|</div>\s*</div>\s*</div>)',
            re.DOTALL | re.IGNORECASE,
        )
        for block in block_re.findall(html)[:30]:
            name_m = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', block, re.DOTALL)
            name = re.sub(r"<[^>]+>", "", name_m.group(1)).strip() if name_m else ""
            if not name:
                continue
            gmp_m = re.search(r'GMP[^0-9-]*(-?\d+)', block, re.IGNORECASE)
            gmp = int(gmp_m.group(1)) if gmp_m else 0
            sub_m = re.search(r'(?:Subscribed|Subscription)[^0-9]*([\d.]+)x', block, re.IGNORECASE)
            sub = sub_m.group(1) + "x" if sub_m else ""
            out.append({
                "id": f"ig-{_slugify(name)}",
                "name": name,
                "ticker": "",
                "exchange": "NSE/BSE",
                "sector": "",
                "industry": "",
                "status": "open" if sub else "upcoming",
                "openDate": "",
                "closeDate": "",
                "listingDate": "",
                "description": "",
                "about": "",
                "priceBandHigh": 0,
                "priceBandLow": 0,
                "lotSize": 0,
                "issueSize": "",
                "gmp": gmp,
                "gmpPercent": 0,
                "subscriptionStatus": sub,
                "anchorInvestors": [],
                "rhpDate": "",
                "allotmentDate": "",
                "refundDate": "",
                "drhpUrl": "",
                "rhpUrl": "",
                "fiscalMetrics": {},
                "source": "investorgain",
                "last_updated": datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        print(f"[IPO Scraper] InvestorGain failed: {e}")
    print(f"[IPO Scraper] InvestorGain: {len(out)} IPOs")
    return out


def scrape_nse_bse() -> List[dict]:
    """Pull NSE + BSE current/upcoming IPO JSON endpoints (best-effort, no auth)."""
    out: List[dict] = []
    endpoints = [
        ("https://www.nseindia.com/api/ipo/current-issue", "nse"),
        ("https://www.nseindia.com/api/ipo/upcoming-issue", "nse-up"),
        ("https://api.bseindia.com/BseIndiaAPI/api/IPODataNew/w?strType=A", "bse"),
    ]
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    }
    for url, sid in endpoints:
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
            if resp.status_code != 200:
                print(f"[IPO Scraper] {sid} HTTP {resp.status_code}")
                continue
            try:
                payload = resp.json()
            except ValueError:
                continue
            items = []
            if isinstance(payload, list):
                items = payload
            elif isinstance(payload, dict):
                for key in ("data", "Table", "ipoList", "Upcoming"):
                    if key in payload and isinstance(payload[key], list):
                        items = payload[key]
                        break
            for item in items[:30]:
                name = (item.get("CompanyName") or item.get("Company") or item.get("name") or "").strip()
                if not name:
                    continue
                sym = (item.get("Symbol") or item.get("symbol") or "").strip().upper()
                series = (item.get("Series") or "").strip()
                out.append({
                    "id": f"{sid}-{_slugify(name)}",
                    "name": name,
                    "ticker": sym,
                    "exchange": "NSE" if "nse" in sid else "BSE",
                    "sector": item.get("Industry", "") or item.get("Sector", ""),
                    "industry": item.get("Industry", "") or item.get("IndustryNew", ""),
                    "status": "open" if (item.get("IssueType") or "").lower() == "open" else "upcoming",
                    "openDate": _normalize_date(str(item.get("IssueStartDate") or item.get("OpenDate") or "")),
                    "closeDate": _normalize_date(str(item.get("IssueEndDate") or item.get("CloseDate") or "")),
                    "listingDate": _normalize_date(str(item.get("ListingDate") or "")),
                    "description": item.get("CompanyAddress", ""),
                    "about": item.get("CompanyName", ""),
                    "priceBandHigh": float(item.get("UpperPriceBand") or item.get("PriceBandHigh") or 0),
                    "priceBandLow": float(item.get("LowerPriceBand") or item.get("PriceBandLow") or 0),
                    "lotSize": int(item.get("LotSize") or 0),
                    "issueSize": str(item.get("IssueSize") or ""),
                    "gmp": 0,
                    "gmpPercent": 0,
                    "subscriptionStatus": "",
                    "anchorInvestors": [],
                    "rhpDate": "",
                    "allotmentDate": _normalize_date(str(item.get("AllotmentDate") or "")),
                    "refundDate": _normalize_date(str(item.get("RefundDate") or "")),
                    "drhpUrl": "",
                    "rhpUrl": item.get("RHP", "") or "",
                    "fiscalMetrics": {},
                    "source": sid,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                })
            time.sleep(0.5)
        except Exception as e:
            print(f"[IPO Scraper] {sid} failed: {e}")
    print(f"[IPO Scraper] NSE/BSE: {len(out)} IPOs")
    return out


def merge_ipos(existing: List[dict], fresh: List[dict]) -> List[dict]:
    """Merge by id; existing wins on duplicate (preserve manual edits)."""
    by_id = {ipo.get("id"): ipo for ipo in existing}
    added = 0
    updated = 0
    for ipo in fresh:
        iid = ipo.get("id")
        if not iid:
            continue
        if iid not in by_id:
            by_id[iid] = ipo
            added += 1
        else:
            merged = {**ipo, **by_id[iid]}
            for k, v in by_id[iid].items():
                if v and v != "" and v != 0 and v != [] and v != {}:
                    merged[k] = v
            by_id[iid] = merged
            updated += 1
    print(f"[IPO Scraper] Merged: {added} new, {updated} updated, {len(by_id)} total")
    return list(by_id.values())


def save_ipos(ipos: List[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "count": len(ipos),
        "ipos": ipos,
    }
    with open(IPO_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[IPO Scraper] Saved {len(ipos)} IPOs to {IPO_FILE}")


def main():
    if not needs_refresh():
        print("[IPO Scraper] Data is fresh (< 2 days), skipping scrape")
        return
    existing = load_existing_ipos()
    print(f"[IPO Scraper] Loaded {len(existing)} existing IPOs")
    fresh: List[dict] = []
    fresh.extend(scrape_finnhub())
    fresh.extend(scrape_nse_bse())
    fresh.extend(scrape_investorgain())
    fresh.extend(scrape_chittorgarh())
    fresh.extend(scrape_sec_edgar())
    merged = merge_ipos(existing, fresh)
    save_ipos(merged)
    save_cache_meta({"last_updated": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    main()
