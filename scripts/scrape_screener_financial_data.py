#!/usr/bin/env python3
"""
Scrape comprehensive financial data for each IPO from Screener.in
==================================================================
Visits each company page and extracts:
  1. Company Overview
  2. Stock Price & Valuation Metrics
  3. Pros & Cons
  4. Peer Comparison
  5. Half Yearly Results
  6. Profit & Loss (Annual)
  7. Growth Metrics
  8. Balance Sheet
  9. Cash Flow Analysis
  10. Key Financial Ratios
  11. Key Insights (AI Extracted)
  12. Shareholding Pattern
  13. Recent Announcements
  14. Annual Reports

Output: data/screener_financial_data.json
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 1.0
MAX_COMPANIES = 50  # Limit for testing; set to None for all

# Sections that require login (will be skipped)
LOGIN_REQUIRED_SECTIONS = [
    "Number of Cities Present",
    "Number of Company Owned Stores",
    "Number of Franchise Stores",
    "Total Number of Stores",
    "Number of Permanent Employees",
]


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


def parse_table_data(soup: BeautifulSoup, table_title: str) -> list:
    """Parse a financial table by finding its title text and extracting rows."""
    tables_data = []

    # Find all h2 elements and look for the one containing our title
    for h2 in soup.find_all("h2"):
        if table_title.lower() in h2.get_text(strip=True).lower():
            # Find the next table after this h2
            table = h2.find_next("table")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        tables_data.append(row_data)
            break

    return tables_data


def extract_company_overview(soup: BeautifulSoup) -> dict:
    """Extract company overview from the about section."""
    result = {
        "businessDescription": "",
        "keyPoints": [],
        "website": "",
        "exchange": "",
    }

    # Get the about/text description
    about_div = soup.find("div", class_="about")
    if about_div:
        result["businessDescription"] = about_div.get_text(strip=True)

    # Get key points
    key_points_section = soup.find(string=re.compile(r"Key Points"))
    if key_points_section:
        parent = key_points_section.find_parent(["div", "section"])
        if parent:
            items = parent.find_all("li")
            result["keyPoints"] = [item.get_text(strip=True) for item in items]

    # Get website - look for "Website" text
    website_link = soup.find("a", href=re.compile(r"^https?://"))
    # Find the about section text
    about_text = soup.get_text()
    about_match = re.search(r"Website\s*\n\s*(\S+)", about_text)
    if about_match:
        result["website"] = about_match.group(1).strip()

    # Exchange listing info
    exchange_elem = soup.find(string=re.compile(r"NSE|BSE"))
    if exchange_elem:
        parent = exchange_elem.find_parent(["td", "th", "div"])
        if parent:
            result["exchange"] = parent.get_text(strip=True)

    return result


def extract_valuation_metrics(soup: BeautifulSoup) -> dict:
    """Extract stock price and valuation metrics from the company header."""
    result = {}
    text = soup.get_text()

    # Use regex to find metrics
    patterns = {
        "currentPrice": r"Current Price\s*[₹]?\s*([\d,]+\.?\d*)",
        "marketCap": r"Market Cap\s*[₹]?\s*([\d,]+)\s*Cr",
        "highLow": r"High / Low\s*[₹]?\s*([\d,]+)\s*/\s*[₹]?\s*([\d,]+)",
        "stockPE": r"Stock P/E\s*([\d,]+\.?\d*)",
        "bookValue": r"Book Value\s*[₹]?\s*([\d,]+\.?\d*)",
        "dividendYield": r"Dividend Yield\s*([\d,]+\.?\d*)%",
        "roce": r"ROCE\s*([\d,]+\.?\d*)%",
        "roe": r"ROE\s*([\d,]+\.?\d*)%",
        "faceValue": r"Face Value\s*[₹]?\s*([\d,]+\.?\d*)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if key == "highLow":
                result["high"] = match.group(1).replace(",", "")
                result["low"] = match.group(2).replace(",", "")
            else:
                result[key] = match.group(1).replace(",", "") if match.group(1) else ""

    return result


def extract_pros_cons(soup: BeautifulSoup) -> dict:
    """Extract pros and cons lists."""
    result = {"pros": [], "cons": []}
    text = soup.get_text()
    lines = text.split("\n")

    in_pros = False
    in_cons = False

    for line in lines:
        line = line.strip()
        if line == "Pros":
            in_pros = True
            in_cons = False
            continue
        if line == "Cons":
            in_pros = False
            in_cons = True
            continue
        if line.startswith("The pros and cons are machine generated"):
            break
        if line.startswith("Pros / cons are based on a checklist"):
            break

        if in_pros and line and not line.startswith("Pros"):
            result["pros"].append(line)
        elif in_cons and line and not line.startswith("Cons"):
            result["cons"].append(line)

    return result


def extract_peer_comparison(soup: BeautifulSoup) -> dict:
    """Extract sector, industry, and benchmark info."""
    result = {
        "sector": "",
        "industry": "",
        "benchmarkIndex": "",
    }
    text = soup.get_text()

    # Find "Peer comparison" section
    peer_section = text.split("Peer comparison")
    if len(peer_section) > 1:
        peer_text = peer_section[1][:500]
        lines = peer_text.split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("Loading") and not line.startswith("Detailed"):
                if not result["sector"]:
                    result["sector"] = line
                elif not result["industry"]:
                    result["industry"] = line
                elif not result["benchmarkIndex"] and "Nifty" in line:
                    result["benchmarkIndex"] = line

    # Also try to find sector from the company header
    sector_elem = soup.find(string=re.compile(r"Sector|Industry"))
    if sector_elem:
        parent = sector_elem.find_parent(["tr", "div"])
        if parent:
            cells = parent.find_all(["td", "th"])
            if len(cells) >= 2:
                if not result["sector"]:
                    result["sector"] = cells[1].get_text(strip=True)

    return result


def extract_financial_table(soup: BeautifulSoup, section_title: str) -> dict:
    """Extract a financial table (Half Yearly Results, P&L, Balance Sheet, etc.) from the page."""
    result = {
        "headers": [],
        "rows": [],
        "rawText": "",
    }

    # Find the h2 containing the section title
    for h2 in soup.find_all("h2"):
        if section_title.lower() in h2.get_text(strip=True).lower():
            # Get the table that follows
            table = h2.find_next("table")
            if table:
                result["rawText"] = table.get_text("\n", strip=True)

                # Parse rows
                trs = table.find_all("tr")
                for tr in trs:
                    cells = tr.find_all(["td", "th"])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        # First row might be headers
                        if not result["headers"] and any(
                            cell.name == "th" for cell in cells
                        ):
                            result["headers"] = row_data
                        else:
                            result["rows"].append(row_data)
            break

    return result


def extract_growth_metrics(soup: BeautifulSoup) -> dict:
    """Extract compounded growth metrics."""
    result = {
        "salesGrowth": {},
        "profitGrowth": {},
        "stockPriceCAGR": {},
        "returnOnEquity": {},
    }
    text = soup.get_text()

    # Compounded Sales Growth
    sales_match = re.search(
        r"Compounded Sales Growth.*?10 Years:\s*([\d.]+%)\s*5 Years:\s*([\d.]+%)\s*3 Years:\s*([\d.]+%)\s*TTM:\s*([\d.]+%)",
        text,
        re.DOTALL,
    )
    if sales_match:
        result["salesGrowth"] = {
            "10Y": sales_match.group(1).strip(),
            "5Y": sales_match.group(2).strip(),
            "3Y": sales_match.group(3).strip(),
            "TTM": sales_match.group(4).strip(),
        }

    # Compounded Profit Growth
    profit_match = re.search(
        r"Compounded Profit Growth.*?10 Years:\s*([\d.]+%)\s*5 Years:\s*([\d.]+%)\s*3 Years:\s*([\d.]+%)\s*TTM:\s*([\d.]+%)",
        text,
        re.DOTALL,
    )
    if profit_match:
        result["profitGrowth"] = {
            "10Y": profit_match.group(1).strip(),
            "5Y": profit_match.group(2).strip(),
            "3Y": profit_match.group(3).strip(),
            "TTM": profit_match.group(4).strip(),
        }

    # Stock Price CAGR
    price_match = re.search(
        r"Stock Price CAGR.*?10 Years:\s*([\d.]+%)\s*5 Years:\s*([\d.]+%)\s*3 Years:\s*([\d.]+%)\s*1 Year:\s*([\d.]+%)",
        text,
        re.DOTALL,
    )
    if price_match:
        result["stockPriceCAGR"] = {
            "10Y": price_match.group(1).strip(),
            "5Y": price_match.group(2).strip(),
            "3Y": price_match.group(3).strip(),
            "1Y": price_match.group(4).strip(),
        }

    # Return on Equity
    roe_match = re.search(
        r"Return on Equity.*?10 Years:\s*([\d.]+%)\s*5 Years:\s*([\d.]+%)\s*3 Years:\s*([\d.]+%)\s*Last Year:\s*([\d.]+%)",
        text,
        re.DOTALL,
    )
    if roe_match:
        result["returnOnEquity"] = {
            "10Y": roe_match.group(1).strip(),
            "5Y": roe_match.group(2).strip(),
            "3Y": roe_match.group(3).strip(),
            "LastYear": roe_match.group(4).strip(),
        }

    return result


def extract_shareholding_pattern(soup: BeautifulSoup) -> dict:
    """Extract shareholding pattern."""
    result = {
        "promoterHolding": "",
        "fiiHolding": "",
        "publicHolding": "",
        "totalShareholders": "",
        "recentTrades": [],
    }
    text = soup.get_text()

    # Find the Shareholding Pattern section
    section = text.split("Shareholding Pattern")
    if len(section) > 1:
        sh_text = section[1][:1000]
        lines = sh_text.split("\n")

        # Parse the percentage tables
        promoter_match = re.search(r"Promoter.*?([\d.]+)%", sh_text)
        if promoter_match:
            result["promoterHolding"] = f"{promoter_match.group(1)}%"

        fii_match = re.search(r"FII.*?([\d.]+)%", sh_text)
        if fii_match:
            result["fiiHolding"] = f"{fii_match.group(1)}%"

        public_match = re.search(r"Public.*?([\d.]+)%", sh_text)
        if public_match:
            result["publicHolding"] = f"{public_match.group(1)}%"

        shareholder_match = re.search(r"No\.?\s*of\s*Shareholders\s*([\d,]+)", sh_text)
        if shareholder_match:
            result["totalShareholders"] = shareholder_match.group(1)

    return result


def extract_announcements(soup: BeautifulSoup) -> list:
    """Extract recent announcements."""
    announcements = []
    text = soup.get_text()

    # Find the Announcements section
    section = text.split("Announcements")
    if len(section) > 1:
        ann_text = section[1][:2000]
        ann_text = ann_text.split("Annual reports")[0] if "Annual reports" in ann_text else ann_text

        # Parse individual announcements (each on a line with a date)
        lines = ann_text.split("\n")
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith("All") and not line.startswith("Updates"):
                # Check if it contains a date pattern
                if re.search(
                    r"\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}",
                    line,
                    re.IGNORECASE,
                ):
                    announcements.append(line)

    return announcements[:20]


def extract_annual_reports(soup: BeautifulSoup) -> list:
    """Extract list of available annual reports."""
    reports = []
    text = soup.get_text()

    # Find Annual reports section
    section = text.split("Annual reports")
    if len(section) > 1:
        ann_report_text = section[1][:500]
        lines = ann_report_text.split("\n")
        for line in lines:
            line = line.strip()
            if line and re.search(r"FY\s*\d{4}", line, re.IGNORECASE):
                reports.append(line)

    return reports


def extract_insights(soup: BeautifulSoup) -> dict:
    """Extract insights (AI-extracted operational data)."""
    result = {}
    text = soup.get_text()

    section = text.split("Insights")
    if len(section) > 1:
        insight_text = section[1][:1500]
        # Extract numbers next to metric names
        metrics = [
            "Number of Cities Present",
            "Number of Company Owned Stores",
            "Number of Franchise Stores",
            "Total Number of Stores",
            "Number of Permanent Employees",
        ]
        for metric in metrics:
            match = re.search(re.escape(metric) + r"\s*([\d,]+|xx)", insight_text)
            if match:
                val = match.group(1)
                if val.lower() != "xx" and val.lower() != "requires premium":
                    result[_slugify_key(metric)] = val

    return result


def extract_cash_flow(soup: BeautifulSoup) -> dict:
    """Extract cash flow data."""
    table = extract_financial_table(soup, "Cash Flows")
    return table


def extract_ratios(soup: BeautifulSoup) -> dict:
    """Extract key financial ratios."""
    table = extract_financial_table(soup, "Ratios")
    return table


def _slugify_key(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def scrape_company_financials(url: str, company_name: str) -> dict:
    """Scrape comprehensive financial data for a single company."""
    print(f"  Fetching {company_name}...", end=" ")
    sys.stdout.flush()

    html = fetch_page(url)
    if not html:
        print("FAILED")
        return {}

    soup = BeautifulSoup(html, "html.parser")
    print("OK")

    financials = {
        "companyName": company_name,
        "sourceUrl": url,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
    }

    # Section 1: Company Overview
    financials["companyOverview"] = extract_company_overview(soup)

    # Section 2: Stock Price & Valuation Metrics
    financials["valuationMetrics"] = extract_valuation_metrics(soup)

    # Section 3: Pros & Cons
    financials["prosCons"] = extract_pros_cons(soup)

    # Section 4: Peer Comparison
    financials["peerComparison"] = extract_peer_comparison(soup)

    # Section 5: Half Yearly Results
    financials["halfYearlyResults"] = extract_financial_table(soup, "Half Yearly Results")

    # Section 6: Profit & Loss (Annual)
    financials["profitLoss"] = extract_financial_table(soup, "Profit & Loss")

    # Section 7: Growth Metrics
    financials["growthMetrics"] = extract_growth_metrics(soup)

    # Section 8: Balance Sheet
    financials["balanceSheet"] = extract_financial_table(soup, "Balance Sheet")

    # Section 9: Cash Flow Analysis
    financials["cashFlow"] = extract_cash_flow(soup)

    # Section 10: Key Financial Ratios
    financials["ratios"] = extract_ratios(soup)

    # Section 11: Key Insights (AI Extracted)
    financials["insights"] = extract_insights(soup)

    # Section 12: Shareholding Pattern
    financials["shareholdingPattern"] = extract_shareholding_pattern(soup)

    # Section 13: Recent Announcements
    financials["announcements"] = extract_announcements(soup)

    # Section 14: Annual Reports
    financials["annualReports"] = extract_annual_reports(soup)

    return financials


def load_existing_financials() -> dict:
    """Load existing financial data to resume from where we left off."""
    path = os.path.join(DATA_DIR, "screener_financial_data.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            pass
    return {}


def save_financials(financials: dict):
    """Save financial data incrementally."""
    path = os.path.join(DATA_DIR, "screener_financial_data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(financials, f, indent=2, ensure_ascii=False)


def main():
    print("=" * 60)
    print("  SCREENER.IN FINANCIAL DATA SCRAPER")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Delay: {DELAY_BETWEEN_REQUESTS}s between requests")
    print("=" * 60)

    # Load IPO listing data
    ipos_path = os.path.join(DATA_DIR, "screener_ipos.json")
    if not os.path.exists(ipos_path):
        print("ERROR: Run scrape_screener_ipo.py first!")
        return 1

    with open(ipos_path, encoding="utf-8") as f:
        ipos_data = json.load(f)

    ipos = ipos_data.get("ipos", [])
    print(f"\nLoaded {len(ipos)} IPOs from listing data")

    # Load existing financial data (for resuming)
    existing = load_existing_financials()
    already_scraped = set(existing.keys())
    print(f"Already scraped: {len(already_scraped)} companies")

    # Filter IPOs that have source_url
    companies_to_scrape = []
    for ipo in ipos:
        url = ipo.get("source_url", "")
        name = ipo.get("name", "")
        if url and name and url not in already_scraped and name not in already_scraped:
            companies_to_scrape.append((name, url))

    print(f"Remaining to scrape: {len(companies_to_scrape)}")

    # Limit for testing
    if MAX_COMPANIES and len(companies_to_scrape) > MAX_COMPANIES:
        print(f"Limiting to {MAX_COMPANIES} companies for this run")
        companies_to_scrape = companies_to_scrape[:MAX_COMPANIES]

    if not companies_to_scrape:
        print("All companies already scraped!")
    else:
        print(f"\nScraping {len(companies_to_scrape)} companies...")
        for i, (name, url) in enumerate(companies_to_scrape, 1):
            print(f"\n[{i}/{len(companies_to_scrape)}] ", end="")
            financials = scrape_company_financials(url, name)
            if financials:
                key = name
                existing[key] = financials
                save_financials(existing)
                print(f"  Saved ({len(existing)} total)")

            if i < len(companies_to_scrape):
                time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\n{'=' * 60}")
    print(f"  COMPLETE")
    print(f"  Total companies scraped: {len(existing)}")
    print(f"  File: data/screener_financial_data.json")
    print(f"  Next: Run generate_financial_data_ts.py to produce TypeScript data")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
