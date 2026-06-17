#!/usr/bin/env python3
"""Generate TypeScript data file from scraped screener.in financial data."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "data")


def esc(s):
    if s is None:
        return ""
    if isinstance(s, (int, float)):
        return str(s)
    if not isinstance(s, str):
        return str(s)
    val = json.dumps(s, ensure_ascii=False)[1:-1]
    val = val.replace("\\'", "'").replace("'", "\\'")
    return val


def q(s, force_quote=False):
    """Wrap string in single quotes for TypeScript, properly escaped."""
    if s is None or (not force_quote and s == ""):
        return "''"
    return "'" + esc(str(s)) + "'"


def format_table_rows(rows):
    if not rows:
        return "[]"
    lines = []
    for row in rows[:8]:
        cells = ", ".join(q(c, force_quote=True) for c in row)
        lines.append("    [" + cells + "]")
    return "[\n" + ",\n".join(lines) + "\n  ]"


def generate_financial_data():
    fin_path = os.path.join(DATA_DIR, "screener_financial_data.json")
    if not os.path.exists(fin_path):
        print("[FinDataGen] No screener financial data found.")
        return

    with open(fin_path, encoding="utf-8") as f:
        financial_data = json.load(f)

    print(f"[FinDataGen] Loaded {len(financial_data)} companies")

    lines = []
    lines.append("// Screener.in Comprehensive Financial Analysis")
    lines.append("export interface FinancialTable {")
    lines.append("  headers: string[];")
    lines.append("  rows: string[][];")
    lines.append("}")
    lines.append("export interface GrowthData {")
    lines.append("  salesGrowth: Record<string, string>;")
    lines.append("  profitGrowth: Record<string, string>;")
    lines.append("  stockPriceCAGR: Record<string, string>;")
    lines.append("  returnOnEquity: Record<string, string>;")
    lines.append("}")
    lines.append("export interface ShareholdingData {")
    lines.append("  promoterHolding: string;")
    lines.append("  fiiHolding: string;")
    lines.append("  publicHolding: string;")
    lines.append("  totalShareholders: string;")
    lines.append("}")
    lines.append("export interface CompanyFinancialAnalysis {")
    lines.append("  companyName: string;")
    lines.append("  companyOverview: { businessDescription: string; keyPoints: string[]; website: string; exchange: string };")
    lines.append("  valuationMetrics: Record<string, string>;")
    lines.append("  prosCons: { pros: string[]; cons: string[] };")
    lines.append("  peerComparison: { sector: string; industry: string; benchmarkIndex: string };")
    lines.append("  halfYearlyResults: FinancialTable;")
    lines.append("  profitLoss: FinancialTable;")
    lines.append("  growthMetrics: GrowthData;")
    lines.append("  balanceSheet: FinancialTable;")
    lines.append("  cashFlow: FinancialTable;")
    lines.append("  ratios: FinancialTable;")
    lines.append("  insights: Record<string, string>;")
    lines.append("  shareholdingPattern: ShareholdingData;")
    lines.append("  announcements: string[];")
    lines.append("  annualReports: string[];")
    lines.append("}")
    lines.append("")
    lines.append("export const screenerFinancialData: Record<string, CompanyFinancialAnalysis> = {")

    for i, (company_name, data) in enumerate(financial_data.items()):
        if not isinstance(data, dict):
            continue
        cn = q(company_name)

        lines.append("  " + cn + ": {")
        lines.append("    companyName: " + cn + ",")

        # Company Overview
        co = data.get("companyOverview", {})
        biz_desc = q(co.get("businessDescription", ""))
        kp = co.get("keyPoints", [])
        kp_str = ", ".join(q(k) for k in kp[:5])
        web = q(co.get("website", ""))
        exch = q(co.get("exchange", ""))
        lines.append("    companyOverview: {")
        lines.append("      businessDescription: " + biz_desc + ",")
        lines.append("      keyPoints: [" + kp_str + "],")
        lines.append("      website: " + web + ",")
        lines.append("      exchange: " + exch + "")
        lines.append("    },")

        # Valuation Metrics
        vm = data.get("valuationMetrics", {})
        vm_items = []
        for field in ["currentPrice", "marketCap", "high", "low", "stockPE", "bookValue", "dividendYield", "roce", "roe", "faceValue"]:
            val = vm.get(field, "")
            if val:
                vm_items.append(field + ": " + q(val))
        lines.append("    valuationMetrics: { " + ", ".join(vm_items) + " },")

        # Pros & Cons
        pc = data.get("prosCons", {})
        pros = pc.get("pros", [])
        cons = pc.get("cons", [])
        pros_str = ", ".join(q(p) for p in pros[:10])
        cons_str = ", ".join(q(c_) for c_ in cons[:10])
        lines.append("    prosCons: { pros: [" + pros_str + "], cons: [" + cons_str + "] },")

        # Peer Comparison
        peer = data.get("peerComparison", {})
        sec = q(peer.get("sector", ""))
        ind = q(peer.get("industry", ""))
        bm = q(peer.get("benchmarkIndex", ""))
        lines.append("    peerComparison: { sector: " + sec + ", industry: " + ind + ", benchmarkIndex: " + bm + " },")

        # Financial Tables
        for table_key in ["halfYearlyResults", "profitLoss", "balanceSheet", "cashFlow", "ratios"]:
            table = data.get(table_key, {})
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            h_str = ", ".join(q(h) for h in headers)
            lines.append("    " + table_key + ": {")
            lines.append("      headers: [" + h_str + "],")
            lines.append("      rows: " + format_table_rows(rows) + "")
            lines.append("    },")

        # Growth Metrics
        gm = data.get("growthMetrics", {})
        lines.append("    growthMetrics: {")
        for gk in ["salesGrowth", "profitGrowth", "stockPriceCAGR", "returnOnEquity"]:
            gdata = gm.get(gk, {})
            if gdata:
                items = ", ".join(k + ": " + q(v) for k, v in gdata.items())
                lines.append("      " + gk + ": { " + items + " },")
            else:
                lines.append("      " + gk + ": {},")
        lines.append("    },")

        # Insights
        insights = data.get("insights", {})
        if insights:
            ins_items = ", ".join(q(k) + ": " + q(v) for k, v in insights.items())
            lines.append("    insights: { " + ins_items + " },")
        else:
            lines.append("    insights: {},")

        # Shareholding Pattern
        sh = data.get("shareholdingPattern", {})
        ph = q(sh.get("promoterHolding", ""))
        fh = q(sh.get("fiiHolding", ""))
        puh = q(sh.get("publicHolding", ""))
        ts = q(sh.get("totalShareholders", ""))
        lines.append("    shareholdingPattern: { promoterHolding: " + ph + ", fiiHolding: " + fh + ", publicHolding: " + puh + ", totalShareholders: " + ts + " },")

        # Announcements
        ann = data.get("announcements", [])
        ann_str = ", ".join(q(a) for a in ann[:10])
        lines.append("    announcements: [" + ann_str + "],")

        # Annual Reports
        ar = data.get("annualReports", [])
        ar_str = ", ".join(q(r) for r in ar[:10])
        lines.append("    annualReports: [" + ar_str + "]")

        lines.append("  },")

        if (i + 1) % 50 == 0:
            print(f"[FinDataGen] Processed {i + 1}/{len(financial_data)}")

    lines.append("};")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "screenerFinancialData.ts")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[FinDataGen] Wrote {len(financial_data)} entries to {out_path}")


if __name__ == "__main__":
    generate_financial_data()
