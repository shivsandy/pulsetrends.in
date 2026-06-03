#!/usr/bin/env python3
"""
Airdrop Intelligence Pipeline — Full Orchestrator

Runs the complete pipeline:
  1. Scrape  →  airdrops_scraper.py  (fetch live data from airdrops.io, airdropalert, etc.)
  2. Analyze →  crypto_analyzer.py   (generate AI analysis via OpenRouter)
  3. Generate→  generate_data_ts.py  (produce airdropData.ts for the frontend)

Usage:
  python airdrop_pipeline.py              # full pipeline
  python airdrop_pipeline.py --scrape-only  # only scrape
  python airdrop_pipeline.py --analyze-only # only analyze (uses cached data)
  python airdrop_pipeline.py --generate-only # only generate TS
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

# Project root
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
AIRDROP_DATA_FILE = os.path.join(DATA_DIR, "airdrops_data.json")
ANALYSIS_FILE = os.path.join(DATA_DIR, "airdrop_analysis.json")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)


def step_scrape():
    """Step 1: Scrape airdrop data from multiple sources."""
    print("=" * 60)
    print("STEP 1: Scrape Airdrop Data")
    print("=" * 60)

    # Import and run the enhanced scraper
    sys.path.insert(0, ROOT)
    import airdrops_scraper as scraper

    airdrops = scraper.scrape(force_refresh=True)
    scraper.save(airdrops)

    print(f"  [OK] Scraped {len(airdrops)} airdrops")
    return airdrops


def step_analyze():
    """Step 2: Run AI analysis on each airdrop using OpenRouter."""
    print("=" * 60)
    print("STEP 2: Analyze Airdrops with AI")
    print("=" * 60)

    # Load scraped data
    try:
        with open(AIRDROP_DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        airdrops = data.get("airdrops", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  [FAIL] Cannot load airdrops data: {e}")
        print("  Run scrape step first: python airdrop_pipeline.py --scrape-only")
        return []

    if not airdrops:
        print("  [!]  No airdrops to analyze")
        return []

    # Load cached analysis
    try:
        with open(ANALYSIS_FILE, encoding="utf-8") as f:
            analysis_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        analysis_cache = {}

    # Check for API keys
    api_keys = []
    try:
        sys.path.insert(0, ROOT)
        import crypto_analyzer as ca
        api_keys = ca.load_or_keys()
    except Exception as e:
        print(f"  [FAIL] Error loading crypto_analyzer: {e}")

    if not api_keys:
        print("  [!]  No OpenRouter API keys found (set OPENROUTER_API_1..8)")
        print("  Skipping AI analysis. Using default analysis values.")
        return airdrops

    # Determine which airdrops need analysis
    to_analyze = []
    for ad in airdrops:
        aid = ad.get("id", "")
        if aid not in analysis_cache:
            to_analyze.append(ad)

    if not to_analyze:
        print(f"  [OK] All {len(airdrops)} airdrops already analyzed")
        return airdrops

    print(f"  [Stats] {len(to_analyze)}/{len(airdrops)} airdrops need AI analysis")
    analyzed_count = 0

    for i, ad in enumerate(to_analyze):
        name = ad.get("name", "Unknown")
        print(f"  [{i + 1}/{len(to_analyze)}] Analyzing: {name}...", end=" ", flush=True)

        try:
            sys.path.insert(0, ROOT)
            import crypto_analyzer as ca
            result = ca.generate_airdrop_analysis(ad, api_keys)
            if result:
                aid = ad.get("id", "")
                analysis_cache[aid] = result
                # Save incrementally
                with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
                    json.dump(analysis_cache, f, indent=2, ensure_ascii=False)
                analyzed_count += 1
                print("[OK]")
            else:
                print("[FAIL] (no result)")
        except Exception as e:
            print(f"[FAIL] (error: {e})")

        # Small delay between calls to be polite
        time.sleep(0.5)

    print(f"  [OK] Analyzed {analyzed_count} new airdrops. Total cached: {len(analysis_cache)}")
    return airdrops


def step_generate():
    """Step 3: Generate TypeScript data file for the frontend."""
    print("=" * 60)
    print("STEP 3: Generate TypeScript Data File")
    print("=" * 60)

    sys.path.insert(0, ROOT)
    import generate_data_ts as gen

    gen.generate_airdrop_data()

    # Verify the output exists and has content
    ts_path = os.path.join(ROOT, "src", "data", "airdropData.ts")
    if os.path.exists(ts_path):
        size = os.path.getsize(ts_path)
        print(f"  [OK] Generated {ts_path} ({size:,} bytes)")
    else:
        print(f"  [FAIL] Failed to generate {ts_path}")

    return ts_path


def main():
    args = set(sys.argv[1:])
    scrape_only = "--scrape-only" in args
    analyze_only = "--analyze-only" in args
    generate_only = "--generate-only" in args
    skip_scrape = "--skip-scrape" in args
    skip_analyze = "--skip-analyze" in args
    skip_generate = "--skip-generate" in args

    start = time.time()

    # Default: run full pipeline
    if not any([scrape_only, analyze_only, generate_only]):
        scrape_only = not skip_scrape
        analyze_only = not skip_analyze
        generate_only = not skip_generate
    # If --analyze-only, include scrape if data missing
    if analyze_only and not scrape_only and not generate_only:
        if not os.path.exists(AIRDROP_DATA_FILE):
            print("[!]  No scraped data found, running scrape step first...")
            scrape_only = True

    print()
    print("=" * 56)
    print("   Airdrop Intelligence Pipeline v1.0")
    print("=" * 56)
    print()

    if scrape_only:
        airdrops = step_scrape()
        if analyze_only or generate_only:
            print()

    if analyze_only:
        airdrops = step_analyze()
        print()

    if generate_only:
        step_generate()
        print()

    elapsed = time.time() - start
    print("=" * 60)
    print(f"Pipeline completed in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
