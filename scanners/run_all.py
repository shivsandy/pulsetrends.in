#!/usr/bin/env python3
"""
Global IPO Intelligence Platform — Master Orchestrator

Runs all regional scanners in parallel, deduplicates results,
and saves to the master IPO database.
"""

import concurrent.futures
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.base import IPOData, deduplicate_ipos, make_dupe_key
from scanners.india import IndiaScraper
from scanners.us import USScraper
from scanners.europe import EuropeScraper
from scanners.asia_pacific import AsiaPacificScraper
from scanners.middle_east import MiddleEastScraper
from scanners.latin_america import LatinAmericaScraper
from scanners.africa import AfricaScraper


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_existing_db() -> dict:
    """Load the existing IPO master database."""
    path = os.path.join(DATA_DIR, "ipo_master_database.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"ipos": [], "metadata": {"total": 0, "last_updated": ""}}


def save_master_db(data: dict):
    """Save the merged master database."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "ipo_master_database.json")
    data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    data["metadata"]["total"] = len(data["ipos"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[Master DB] Saved {data['metadata']['total']} IPOs to {path}")


def save_scanner_result(source: str, ipos: List[IPOData], errors: List[str],
                        elapsed: float):
    """Save individual scanner result to a JSON file for audit."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"scan_{source.lower().replace(' ', '_')}.json")
    data = {
        "source": source,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 2),
        "ipos_found": len(ipos),
        "errors": errors,
        "ipos": [ipo.to_dict() for ipo in ipos],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_scanner(scanner_cls, name: str) -> Tuple[str, List[IPOData], List[str], float]:
    """Run a scanner and return its results."""
    print(f"\n{'='*60}")
    print(f"  Scanning: {name}")
    print(f"{'='*60}")
    start = time.time()
    scanner = scanner_cls()
    try:
        ipos = scanner.scrape()
    except Exception as e:
        print(f"  [ERROR] {name} crashed: {e}")
        return name, [], [str(e)], time.time() - start
    elapsed = time.time() - start
    print(f"  [Done] {name}: {len(ipos)} IPOs in {elapsed:.1f}s")
    if scanner.errors:
        for err in scanner.errors:
            print(f"  [Warning] {err}")
    return name, ipos, scanner.errors, elapsed


def merge_into_master(existing_db: dict, new_ipos: List[IPOData]) -> dict:
    """Merge new IPO records into the master database with deduplication."""
    existing_records = existing_db.get("ipos", [])

    # Build lookup of existing records by dupe key
    existing_map: Dict[str, dict] = {}
    for rec in existing_records:
        ipo = IPOData(
            id=rec.get("id", ""),
            name=rec.get("name", ""),
            ticker=rec.get("ticker", ""),
            exchange=rec.get("exchange", ""),
        )
        key = make_dupe_key(ipo)
        existing_map[key] = rec

    merged_count = 0
    new_count = 0
    for new_ipo in new_ipos:
        key = make_dupe_key(new_ipo)
        if key in existing_map:
            # Update fields that have new data
            existing = existing_map[key]
            for field, value in new_ipo.to_dict().items():
                if value and not existing.get(field):
                    existing[field] = value
            existing["last_updated"] = datetime.now(timezone.utc).isoformat()
            merged_count += 1
        else:
            existing_records.append(new_ipo.to_dict())
            new_count += 1

    existing_db["ipos"] = existing_records
    existing_db["metadata"] = existing_db.get("metadata", {})
    existing_db["metadata"]["total"] = len(existing_records)

    print(f"\n[Merge] {new_count} new IPOs added, {merged_count} existing updated")
    print(f"[Merge] Total in database: {len(existing_records)}")
    return existing_db


def generate_stats_summary(db: dict, scanner_results: List[tuple]):
    """Generate a stats summary JSON file."""
    ipos = db.get("ipos", [])
    status_counts: Dict[str, int] = {}
    country_counts: Dict[str, int] = {}
    exchange_counts: Dict[str, int] = {}
    sector_counts: Dict[str, int] = {}

    for ipo in ipos:
        s = ipo.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
        c = ipo.get("country", "unknown")
        country_counts[c] = country_counts.get(c, 0) + 1
        e = ipo.get("exchange", "unknown")
        exchange_counts[e] = exchange_counts.get(e, 0) + 1
        sec = ipo.get("sector", "Unknown")
        sector_counts[sec] = sector_counts.get(sec, 0) + 1

    stats = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_ipos": len(ipos),
        "status_breakdown": status_counts,
        "country_breakdown": country_counts,
        "exchange_breakdown": exchange_counts,
        "sector_breakdown": sector_counts,
        "scanner_results": {
            name: {"ipos_found": count, "errors": errors}
            for name, count, errors in scanner_results
        },
    }
    path = os.path.join(DATA_DIR, "ipo_stats_summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"[Stats] Summary saved to {path}")
    return stats


def main():
    print("\n" + "="*70)
    print("  GLOBAL IPO INTELLIGENCE PLATFORM — MASTER ORCHESTRATOR")
    print("="*70)
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}")
    print("="*70)

    # Define all scanners to run in parallel
    scanners = [
        (IndiaScraper, "India"),
        (USScraper, "United States"),
        (EuropeScraper, "Europe"),
        (AsiaPacificScraper, "Asia-Pacific"),
        (MiddleEastScraper, "Middle East"),
        (LatinAmericaScraper, "Latin America"),
        (AfricaScraper, "Africa"),
    ]

    # Run all scanners in parallel
    print(f"\n[Orchestrator] Launching {len(scanners)} scanners in parallel...")
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        fut_to_scanner = {
            executor.submit(run_scanner, cls, name): (cls, name)
            for cls, name in scanners
        }
        all_results: List[Tuple[str, List[IPOData], List[str], float]] = []
        for fut in concurrent.futures.as_completed(fut_to_scanner):
            result = fut.result()
            all_results.append(result)

    total_elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"  ALL SCANS COMPLETE — {total_elapsed:.1f}s total")
    print(f"{'='*70}")

    # Collect all IPOs and save individual scanner results
    all_ipos: List[IPOData] = []
    scanner_summary: List[Tuple[str, int, List[str]]] = []
    for name, ipos, errors, elapsed in all_results:
        all_ipos.extend(ipos)
        scanner_summary.append((name, len(ipos), errors))
        save_scanner_result(name, ipos, errors, elapsed)
        status = "✓" if not errors else "⚠"
        print(f"  {status} {name}: {len(ipos)} IPOs ({elapsed:.1f}s)")

    # Deduplicate across scanners
    unique_ipos = deduplicate_ipos(all_ipos)
    print(f"\n[Deduplication] {len(all_ipos)} → {len(unique_ipos)} unique IPOs")

    # Load existing database and merge
    existing_db = load_existing_db()
    print(f"[Database] Loaded {existing_db['metadata'].get('total', 0)} existing records")

    merged_db = merge_into_master(existing_db, unique_ipos)

    # Save master database
    save_master_db(merged_db)

    # Generate stats summary
    generate_stats_summary(merged_db, scanner_summary)

    print(f"\n{'='*70}")
    print(f"  SCAN COMPLETE ✓")
    print(f"  Total IPOs in database: {merged_db['metadata']['total']}")
    print(f"  New IPOs this run: {sum(len(r[1]) for r in all_results)}")
    print(f"  Scan time: {total_elapsed:.1f}s")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
