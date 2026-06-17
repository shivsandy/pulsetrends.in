# Global IPO Intelligence Platform

## Architecture Overview

An institutional-grade IPO research and intelligence system covering 2,000+ IPOs across 14+ global markets with AI-powered scoring, parallel scanning, and duplicate prevention.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Pipeline                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ India    │ │ US       │ │ Europe   │ │ Asia-    │ │ Middle   │  │
│  │ Scanner  │ │ Scanner  │ │ Scanner  │ │ Pacific  │ │ East     │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       └────────────┴────────────┴────────────┴────────────┘        │
│                                │                                    │
│                        ┌───────┴───────┐                            │
│                        │   Duplicate   │                            │
│                        │   Detector    │                            │
│                        └───────┬───────┘                            │
│                                │                                    │
│          ┌─────────────────────┼─────────────────────┐              │
│          ▼                     ▼                     ▼              │
│  ┌───────────────┐   ┌───────────────┐   ┌──────────────────┐      │
│  │  Financial    │   │   Valuation   │   │  AI Scoring      │      │
│  │  Analyzer     │   │   Engine      │   │  Engine (10-fac) │      │
│  └───────┬───────┘   └───────┬───────┘   └────────┬─────────┘      │
│          └───────────────────┼────────────────────┘                 │
│                              ▼                                      │
│                    ┌──────────────────┐                             │
│                    │   Master DB &    │                             │
│                    │   Report Gen     │                             │
│                    └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌────────────────────────────┐
              │   Frontend (React/TS)     │
              │  IPOAnalysisPage          │
              │  IPODetailPage            │
              │  IPOCard                  │
              └────────────────────────────┘
```

## Market Coverage

| Region | Exchanges | Scraper | Source Type |
|--------|-----------|---------|-------------|
| India | NSE, BSE, SME | `india.py` | Scraping + APIs |
| United States | NASDAQ, NYSE | `us.py` | Finnhub API + SEC EDGAR |
| United Kingdom | LSE | `europe.py` | Web scraping |
| Europe | Euronext (Paris, Amsterdam, Brussels) | `europe.py` | Web scraping |
| Canada | TSX | `asia_pacific.py` | Web scraping |
| Australia | ASX | `asia_pacific.py` | Web scraping |
| Singapore | SGX | `asia_pacific.py` | Web scraping |
| Hong Kong | HKEX | `asia_pacific.py` | Web scraping |
| Japan | TSE | `asia_pacific.py` | Web scraping |
| South Korea | KRX | `asia_pacific.py` | Web scraping |
| UAE | DFM, ADX | `middle_east.py` | Web scraping |
| Saudi Arabia | Tadawul | `middle_east.py` | Web scraping |
| Brazil | B3 | `latin_america.py` | Web scraping |
| South Africa | JSE | `africa.py` | Web scraping |

## Duplicate Prevention

Before adding any IPO, check these fields:
1. Company Name (fuzzy match)
2. Exchange
3. Ticker Symbol
4. Filing/Prospectus ID
5. Filing Date (within 90-day window)

## AI Scoring System (10 Factors)

| Factor | Weight | Range |
|--------|--------|-------|
| Business Quality | 15% | 20-100 |
| Financial Health | 15% | 20-100 |
| Management Quality | 10% | 20-100 |
| Industry Potential | 10% | 20-100 |
| Valuation | 10% | 20-100 |
| Risk Assessment | 10% | 20-100 |
| Growth Potential | 10% | 20-100 |
| Corporate Governance | 10% | 20-100 |
| Market Sentiment | 5% | 20-100 |
| Listing Gain Potential | 5% | 20-100 |

**Final Score:** Weighted sum, clamped to 20-100 range.

### Score Interpretation

| Range | Classification |
|-------|---------------|
| 90-100 | Exceptional IPO |
| 80-89 | Strong IPO |
| 70-79 | Good IPO |
| 60-69 | Average IPO |
| 50-59 | Speculative IPO |
| 40-49 | High Risk IPO |
| 20-39 | Avoid IPO |

## Output Files

| File | Format | Description |
|------|--------|-------------|
| `data/ipo_master_database.json` | JSON | Complete normalized database |
| `data/ipo_master_database.csv` | CSV | CSV export |
| `data/ipo_scores_ranking.json` | JSON | Ranked by AI score |
| `data/ipo_sql_schema.sql` | SQL | Database schema |
| `data/ipo_api_dataset.json` | JSON | API-ready format |
| `data/ipo_stats_summary.json` | JSON | Summary statistics |
| `data/ipo_data.json` | JSON | Frontend-consumable format |

## File Structure

```
Pulsetrends.in/
├── scanners/                    # Modular exchange scrapers
│   ├── __init__.py
│   ├── base.py                  # Base scraper class
│   ├── india.py                 # NSE/BSE/Screener/Chittorgarh/InvestorGain
│   ├── us.py                    # Finnhub + SEC EDGAR
│   ├── europe.py                # LSE + Euronext
│   ├── asia_pacific.py          # HKEX + SGX + ASX + TSE + KRX
│   ├── middle_east.py           # Tadawul + UAE
│   ├── latin_america.py         # B3 (Brazil)
│   └── africa.py                # JSE (South Africa)
├── engine/                      # AI scoring & analysis
│   ├── __init__.py
│   ├── scorer.py                # 10-factor weighted scoring
│   ├── dupe_detector.py         # Multi-field duplicate prevention
│   └── financial_analyzer.py    # Financial statement extraction
├── ipo_scraper.py               # Legacy (kept for reference)
├── build_ipo_database.py        # Master DB builder
├── .github/workflows/
│   ├── ipo-crypto.yml           # Legacy single job
│   └── global-ipo-scanner.yml   # 10-parallel-job pipeline
└── data/                        # All data files
```

## Build Status ✅ All 6 Phases Complete

1. **Phase 1:** Modular scanner system — 7 regional scanners + orchestrator ✅
2. **Phase 2:** 10-parallel-job GitHub Actions pipeline with retry/queue/audit ✅
3. **Phase 3:** Duplicate prevention system — 7-field checks (source ID, ticker, ISIN, filing ID, fuzzy name, date window) ✅
4. **Phase 4:** AI scoring engine — 10-factor weighted scoring (20-100 scale) ✅
5. **Phase 5:** Financial data pipeline — valuation metrics, peer comparison, forward projections ✅
6. **Phase 6:** Historical tracking — GMP/subscription/sentiment analysis in CI/CD pipeline ✅
