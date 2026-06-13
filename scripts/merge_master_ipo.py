#!/usr/bin/env python3
"""
Merge the 2,001 IPO master database back into data/ipo_data.json
so generate_data_ts.py can create src/data/ipoData.ts.
"""
import json, os, copy
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Load master database
with open(os.path.join(DATA_DIR, "ipo_master_database.json"), encoding="utf-8") as f:
    master = json.load(f)

# Load existing ipo_data.json for reference schema
existing_path = os.path.join(DATA_DIR, "ipo_data.json")
with open(existing_path, encoding="utf-8") as f:
    existing = json.load(f)

# Convert master records to ipo_data.json format
converted = []
for ipo in master.get("ipos", []):
    fm = {}
    if ipo.get("current_price"):
        try:
            fm["currentPrice"] = float(ipo["current_price"])
        except ValueError:
            pass
    if ipo.get("current_market_cap"):
        try:
            fm["ipoMcap"] = float(ipo["current_market_cap"])
        except ValueError:
            pass

    entry = {
        "id": ipo.get("source_id", "") or f'merged-{ipo.get("ticker", "").lower() or ipo["company_name"].lower().replace(" ", "-")[:30]}',
        "name": ipo["company_name"],
        "ticker": ipo.get("ticker", ""),
        "exchange": ipo.get("exchange", ""),
        "sector": ipo.get("sector", ""),
        "industry": ipo.get("industry", ""),
        "status": ipo.get("status", "listed"),
        "openDate": ipo.get("ipo_date", ""),
        "closeDate": "",
        "listingDate": ipo.get("ipo_date", ""),
        "description": "",
        "about": "",
        "priceBandHigh": 0,
        "priceBandLow": 0,
        "lotSize": 0,
        "issueSize": ipo.get("offer_size", ""),
        "gmp": 0,
        "gmpPercent": 0,
        "subscriptionStatus": ipo.get("subscription", ""),
        "anchorInvestors": [],
        "rhpDate": "",
        "allotmentDate": "",
        "refundDate": "",
        "drhpUrl": "",
        "rhpUrl": "",
        "fiscalMetrics": fm,
        "source": ipo.get("source", "merged"),
        "country": ipo.get("country", ""),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    converted.append(entry)

# Merge with existing IPOs (dedup by name)
existing_names = {ipo["name"].lower().strip(): ipo for ipo in existing.get("ipos", [])}
merged = list(existing_names.values())
added = 0
for entry in converted:
    key = entry["name"].lower().strip()
    if key not in existing_names:
        merged.append(entry)
        existing_names[key] = entry
        added += 1

# Save merged result
output = {
    "last_updated": datetime.now(timezone.utc).isoformat(),
    "count": len(merged),
    "ipos": merged,
}
with open(existing_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Merged: {len(existing.get('ipos', []))} existing + {added} new = {len(merged)} total")
print(f"Saved to {existing_path}")
