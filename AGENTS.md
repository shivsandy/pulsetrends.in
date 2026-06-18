## Goal
Build and maintain a comprehensive 2,001-IPO intelligence system with weekly availability checks, incremental AI analysis, institutional-grade reports, and a 13-section fundamental analysis framework for every IPO.

## Constraints & Preferences
- Static React SPA (Vite 7 + TypeScript + Tailwind v4) deployed via GitHub Pages; no backend database
- All data stored as JSON in `data/` and `src/data/`, converted to TypeScript at build time
- AI score weighting: Fundamentals 30%, IPO Demand 15%, Valuation 15%, Governance 15%, Business Quality 15%, Post-Listing Performance 10%
- Incremental mode by default for all analysis scripts (`--force` to regenerate all); old IPOs are never re-scored or re-analyzed in normal operation
- Weekly cron (every 3 days) only runs lightweight: availability check → TS generation → build → deploy
- GitHub `ipoComprehensiveAnalysis.json` (24.7 MB) exceeds Git LFS warning threshold but pushes successfully

## Progress
### Done
- Regenerated `src/data/ipoData.ts` via `generate_data_ts.py` — website now consumes all 2,001 IPOs
- Built and deployed; live site at pulsetrends.in shows 2,001 IPOs
- Created `scripts/check_ipo_availability.py` — weekly checker that parses dates (ISO, Indian short `8th jun`, ranges) and transitions past-date upcoming/open IPOs to listed
- Ran checker: 20 IPOs moved to listed (17 upcoming + 3 open)
- Updated `generate_data_ts.py` to add `closed` status type, map `rights` → `closed`
- Changed `IPOAnalysisPage.tsx` default filter from `'all'` to `'upcoming'` so available IPOs show first
- Added IPO availability step to `.github/workflows/deploy.yml` (runs before TS generation)
- Fixed `generate_data_ts.py` to populate `aiAnalysis`/`aiVerdict` from master DB fallback when `ipo_analysis.json` has no entry
- Fixed score key name mismatch between comprehensive JSON (`fundamentals_score`) and TS reader (`financial_strength`)
- Regenerated `src/data/ipoComprehensiveAnalysis.json` — 1,995 entries, 24.7 MB (down from 56 MB)
- Rewrote `IPODetailPage.tsx` — replaced old 21-section accordion with 13 new sections (Executive Summary, Business Overview, Industry & Market, Financial Performance, Balance Sheet, Cash Flow, IPO Details, Valuation, Management Quality, Risk Assessment, Strengths/Weaknesses, Market Sentiment, Final Verdict); removed unused imports, helpers, and sub-components

## Key Decisions
- All 2,001 IPOs now have comprehensive 13-section analysis entries in `ipoComprehensiveAnalysis.json` (was 1,094)
- `aiAnalysis`/`aiVerdict` fallback chain: `ipo_analysis.json` → master DB fields (`ai_score_explanation`, `investment_thesis`, `ipo_summary`) → empty string
- Score key names unified to `_score` suffix (e.g., `fundamentals_score`) across both data generator and TypeScript reader

## Relevant Files
- **`scripts/check_ipo_availability.py`** — weekly date-based status transitioner (upcoming→listed)
- **`generate_data_ts.py`** — reads `ipo_data.json` + `ipo_master_database.json` fallback + `ipoComprehensiveAnalysis.json` scores → `src/data/ipoData.ts`
- **`src/pages/IPODetailPage.tsx`** — detail page that fetches `ipoComprehensiveAnalysis.json` and renders 13-section accordion with `MarkdownSection` renderer
- **`src/pages/IPOAnalysisPage.tsx`** — listing page; default filter changed to `upcoming`
- **`src/components/IPOCard.tsx`** — IPO card component with status badge colors
- **`build_ipo_database.py`** — full AI scoring pipeline; now incremental (skip existing, `--force` to rescore)
- **`.github/workflows/deploy.yml`** — added IPO availability check step
