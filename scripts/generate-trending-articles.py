#!/usr/bin/env python3
"""
⚠️ OBSOLETE — Consolidated into generate-daily-news.py
======================================================
The trending hot-topic generator has been merged into generate-daily-news.py
which now generates all 11 daily articles (3 crypto + 3 IPO + 5 trending)
in a single consolidated pipeline.

Please use: python scripts/generate-daily-news.py
"""

import sys

if __name__ == "__main__":
    print("=" * 60)
    print("  ⚠️  OBSOLETE SCRIPT")
    print("  This script has been consolidated into generate-daily-news.py")
    print()
    print("  Please use: python scripts/generate-daily-news.py")
    print("  The new pipeline generates all 11 daily articles at once:")
    print("    - 3 trending Crypto articles")
    print("    - 3 trending IPO articles")
    print("    - 5 trending Hot-Topic articles")
    print("=" * 60)
    sys.exit(1)
