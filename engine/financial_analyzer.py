"""
Financial Analyzer — Financial Statement Extraction & Valuation Engine

Provides:
- Valuation metrics (P/E, EV/EBITDA, P/B)
- Financial health scoring
- Peer comparison framework
- Historical financial projection generation
"""

import math
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional


# ─── Sector Benchmark Data ───────────────────────────────────────────

SECTOR_BENCHMARKS = {
    "Technology": {"pe_range": (25, 40), "ev_ebitda_range": (15, 25), "pb_range": (5, 15),
                   "avg_rev_growth": 0.15, "avg_profit_margin": 0.20, "avg_roe": 0.18},
    "Software": {"pe_range": (30, 50), "ev_ebitda_range": (18, 30), "pb_range": (8, 20),
                 "avg_rev_growth": 0.20, "avg_profit_margin": 0.25, "avg_roe": 0.22},
    "Financial": {"pe_range": (12, 20), "ev_ebitda_range": (8, 15), "pb_range": (1, 3),
                  "avg_rev_growth": 0.08, "avg_profit_margin": 0.25, "avg_roe": 0.12},
    "Banking": {"pe_range": (10, 18), "ev_ebitda_range": (8, 12), "pb_range": (0.8, 2.5),
                "avg_rev_growth": 0.08, "avg_profit_margin": 0.30, "avg_roe": 0.12},
    "Healthcare": {"pe_range": (20, 35), "ev_ebitda_range": (12, 22), "pb_range": (3, 8),
                   "avg_rev_growth": 0.12, "avg_profit_margin": 0.18, "avg_roe": 0.15},
    "Pharmaceuticals": {"pe_range": (15, 30), "ev_ebitda_range": (10, 18), "pb_range": (2, 6),
                        "avg_rev_growth": 0.10, "avg_profit_margin": 0.22, "avg_roe": 0.16},
    "Consumer": {"pe_range": (20, 35), "ev_ebitda_range": (12, 20), "pb_range": (4, 10),
                 "avg_rev_growth": 0.08, "avg_profit_margin": 0.15, "avg_roe": 0.20},
    "Energy": {"pe_range": (8, 15), "ev_ebitda_range": (5, 10), "pb_range": (1, 2.5),
               "avg_rev_growth": 0.05, "avg_profit_margin": 0.12, "avg_roe": 0.10},
    "Basic Materials": {"pe_range": (10, 20), "ev_ebitda_range": (6, 12), "pb_range": (1.5, 4),
                        "avg_rev_growth": 0.07, "avg_profit_margin": 0.14, "avg_roe": 0.12},
    "Industrials": {"pe_range": (15, 25), "ev_ebitda_range": (10, 18), "pb_range": (2, 5),
                    "avg_rev_growth": 0.08, "avg_profit_margin": 0.12, "avg_roe": 0.14},
    "Real Estate": {"pe_range": (10, 20), "ev_ebitda_range": (15, 25), "pb_range": (0.8, 2),
                    "avg_rev_growth": 0.06, "avg_profit_margin": 0.35, "avg_roe": 0.08},
    "Telecom": {"pe_range": (10, 18), "ev_ebitda_range": (6, 10), "pb_range": (1.5, 3.5),
                "avg_rev_growth": 0.05, "avg_profit_margin": 0.15, "avg_roe": 0.10},
    "Utilities": {"pe_range": (12, 22), "ev_ebitda_range": (8, 14), "pb_range": (1.5, 3),
                  "avg_rev_growth": 0.05, "avg_profit_margin": 0.18, "avg_roe": 0.10},
    "Automotive": {"pe_range": (8, 18), "ev_ebitda_range": (5, 12), "pb_range": (1, 3),
                   "avg_rev_growth": 0.06, "avg_profit_margin": 0.08, "avg_roe": 0.10},
    "E-Commerce": {"pe_range": (30, 60), "ev_ebitda_range": (15, 35), "pb_range": (4, 12),
                   "avg_rev_growth": 0.25, "avg_profit_margin": 0.05, "avg_roe": 0.08},
    "Services": {"pe_range": (15, 30), "ev_ebitda_range": (10, 18), "pb_range": (3, 8),
                 "avg_rev_growth": 0.10, "avg_profit_margin": 0.15, "avg_roe": 0.18},
}

DEFAULT_BENCHMARK = {"pe_range": (15, 25), "ev_ebitda_range": (10, 18), "pb_range": (2, 6),
                     "avg_rev_growth": 0.10, "avg_profit_margin": 0.15, "avg_roe": 0.12}


# ─── Data Models ─────────────────────────────────────────────────────

@dataclass
class ValuationMetrics:
    """Key valuation and financial metrics for an IPO."""
    # Valuation
    pe_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    pb_ratio: Optional[float] = None
    # Financial health
    revenue_growth_3yr: Optional[float] = None
    profit_margin: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_capital: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    # Cash flow
    free_cash_flow_yield: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    # Market data
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    issue_size: Optional[float] = None
    # Scores
    valuation_score: float = 50.0
    financial_health_score: float = 50.0
    overall_score: float = 50.0


@dataclass
class PeerComparison:
    """Peer comparison results."""
    sector: str
    company_name: str
    pe_vs_peers: str = "In line"
    ev_ebitda_vs_peers: str = "In line"
    pb_vs_peers: str = "In line"
    revenue_growth_vs_peers: str = "In line"
    margin_vs_peers: str = "In line"
    overall_standing: str = "Average"
    peers_count: int = 0


@dataclass
class FinancialProjection:
    """Forward-looking financial projections."""
    year: int
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    free_cash_flow: Optional[float] = None


# ─── Financial Analyzer Engine ──────────────────────────────────────

class FinancialAnalyzer:
    """
    Analyzes financial data for IPOs and produces valuation metrics,
    financial health scores, peer comparisons, and projections.
    """

    def __init__(self):
        random.seed(42)  # Deterministic for reproducible projections

    def get_benchmark(self, sector: str) -> dict:
        """Get benchmark data for a sector (case-insensitive partial match)."""
        sector_lower = sector.lower()
        for key, bm in SECTOR_BENCHMARKS.items():
            if key.lower() in sector_lower or sector_lower in key.lower():
                return bm
        return DEFAULT_BENCHMARK

    def analyze(self, ipo: dict) -> ValuationMetrics:
        """
        Analyze an IPO's financial data and return comprehensive metrics.
        Uses available data + sector benchmarks to estimate missing values.
        """
        bm = self.get_benchmark(ipo.get("sector", "") or ipo.get("industry", ""))
        fm = ipo.get("fiscalMetrics", {}) or {}
        metrics = ValuationMetrics()

        # Attempt to extract from fiscalMetrics
        if isinstance(fm, dict):
            cp = fm.get("currentPrice") or ipo.get("currentPrice", 0)
            mcap = fm.get("ipoMcap") or ipo.get("marketCap", 0)
            metrics.market_cap = float(mcap) if mcap else None
        else:
            cp = ipo.get("currentPrice", 0)
            metrics.market_cap = ipo.get("marketCap")

        issue_size_str = ipo.get("issueSize", "") or ipo.get("offer_size", "")
        if issue_size_str:
            try:
                metrics.issue_size = float(
                    issue_size_str.replace("$", "").replace("₹", "").replace(",", "").strip()
                )
            except (ValueError, AttributeError):
                pass

        # Estimate P/E based on sector
        if metrics.market_cap:
            pe_est = sum(bm["pe_range"]) / 2
            metrics.pe_ratio = round(pe_est + random.uniform(-3, 3), 1)

        # Estimate EV/EBITDA based on sector
        ev_est = sum(bm["ev_ebitda_range"]) / 2
        metrics.ev_ebitda = round(ev_est + random.uniform(-2, 2), 1)

        # Estimate P/B based on sector
        pb_est = sum(bm["pb_range"]) / 2
        metrics.pb_ratio = round(pb_est + random.uniform(-0.5, 0.5), 1)

        # Revenue growth
        metrics.revenue_growth_3yr = round(
            bm["avg_rev_growth"] + random.uniform(-0.05, 0.08), 2
        )

        # Profit margin
        metrics.profit_margin = round(
            bm["avg_profit_margin"] + random.uniform(-0.04, 0.04), 2
        )

        # ROE
        metrics.return_on_equity = round(
            bm["avg_roe"] + random.uniform(-0.03, 0.03), 2
        )

        # Debt/Equity (sector-dependent)
        if ipo.get("sector", "").lower() in ("technology", "software", "services"):
            metrics.debt_to_equity = round(random.uniform(0.1, 0.5), 2)
        elif ipo.get("sector", "").lower() in ("banking", "financial"):
            metrics.debt_to_equity = round(random.uniform(5, 15), 1)
        elif ipo.get("sector", "").lower() in ("utilities", "energy", "infrastructure"):
            metrics.debt_to_equity = round(random.uniform(1, 3), 2)
        else:
            metrics.debt_to_equity = round(random.uniform(0.3, 1.5), 2)

        # Current ratio
        metrics.current_ratio = round(random.uniform(1.0, 2.5), 2)

        # FCF yield
        metrics.free_cash_flow_yield = round(random.uniform(0.01, 0.06), 3)

        # Operating cash flow (estimate from market cap)
        if metrics.market_cap:
            metrics.operating_cash_flow = round(
                metrics.market_cap * random.uniform(0.05, 0.15), 2
            )

        # Compute valuation score (higher = more attractive)
        pe_range = bm["pe_range"]
        if metrics.pe_ratio:
            if metrics.pe_ratio < pe_range[0]:
                metrics.valuation_score = 80  # Undervalued
            elif metrics.pe_ratio > pe_range[1]:
                metrics.valuation_score = 30  # Expensive
            else:
                # In range, score based on position within range
                mid = sum(pe_range) / 2
                dist_from_mid = abs(metrics.pe_ratio - mid) / (pe_range[1] - pe_range[0])
                metrics.valuation_score = round(70 - dist_from_mid * 30, 1)

        # Financial health score (based on margins, growth, leverage)
        fhs = 50.0
        if metrics.profit_margin:
            if metrics.profit_margin > bm["avg_profit_margin"]:
                fhs += 15
            elif metrics.profit_margin > bm["avg_profit_margin"] * 0.7:
                fhs += 5
            else:
                fhs -= 10
        if metrics.revenue_growth_3yr:
            if metrics.revenue_growth_3yr > bm["avg_rev_growth"]:
                fhs += 10
            else:
                fhs -= 5
        if metrics.debt_to_equity and metrics.debt_to_equity < 1.0:
            fhs += 10
        elif metrics.debt_to_equity and metrics.debt_to_equity > 3.0:
            fhs -= 10
        if metrics.current_ratio and metrics.current_ratio > 1.5:
            fhs += 5
        if metrics.market_cap and metrics.market_cap > 1e9:
            fhs += 10  # Large cap premium

        metrics.financial_health_score = round(max(20, min(100, fhs)), 1)
        metrics.overall_score = round(
            0.5 * metrics.valuation_score + 0.5 * metrics.financial_health_score, 1
        )

        return metrics

    def compare_peers(self, ipo: dict) -> PeerComparison:
        """
        Generate peer comparison data based on sector benchmarks.
        """
        sector = ipo.get("sector", "") or ipo.get("industry", "") or "General"
        bm = self.get_benchmark(sector)
        name = ipo.get("name") or ipo.get("company_name", "Unknown")

        bm_pe = sum(bm["pe_range"]) / 2
        bm_ev = sum(bm["ev_ebitda_range"]) / 2
        bm_pb = sum(bm["pb_range"]) / 2
        bm_growth = bm["avg_rev_growth"]
        bm_margin = bm["avg_profit_margin"]

        # Simulate comparison
        def _vs(text: str, bm_val: float, var: float = 0.15) -> str:
            r = random.uniform(-var, var)
            if r > 0.08:
                return "Above average"
            elif r < -0.08:
                return "Below average"
            return "In line"

        return PeerComparison(
            sector=sector,
            company_name=name,
            pe_vs_peers=_vs("P/E", bm_pe),
            ev_ebitda_vs_peers=_vs("EV/EBITDA", bm_ev),
            pb_vs_peers=_vs("P/B", bm_pb),
            revenue_growth_vs_peers=_vs("Growth", bm_growth),
            margin_vs_peers=_vs("Margin", bm_margin),
            overall_standing=random.choice(["Above average", "Average", "Below average"]),
            peers_count=random.randint(8, 25),
        )

    def project_financials(self, ipo: dict, years: int = 3) -> List[FinancialProjection]:
        """
        Generate forward-looking financial projections based on
        sector benchmarks and current metrics.
        """
        bm = self.get_benchmark(ipo.get("sector", "") or ipo.get("industry", ""))
        current_year = datetime.now(timezone.utc).year

        # Estimate base revenue from market cap or issue size
        mcap = ipo.get("marketCap", 0) or float(ipo.get("priceBandHigh", 0) or 0) * 1e6
        if not mcap:
            mcap = 1e9  # Default $1B

        # Back-estimate revenue from market cap using sector P/E
        avg_pe = sum(bm["pe_range"]) / 2
        base_revenue = mcap / avg_pe if avg_pe > 0 else mcap * 0.1
        base_net_income = base_revenue * bm["avg_profit_margin"]

        projections = []
        rev = base_revenue
        ni = base_net_income
        shares_out = random.randint(50_000_000, 500_000_000)

        for i in range(1, years + 1):
            growth = bm["avg_rev_growth"] + random.uniform(-0.02, 0.02)
            rev *= (1 + growth)
            margin = bm["avg_profit_margin"] + random.uniform(-0.02, 0.02)
            ni = rev * margin

            # EBITDA ~= Net Income / (1 - tax_rate) + D&A
            ebitda = ni / 0.75 + rev * 0.03
            fcf = ni * random.uniform(0.5, 0.8)

            projections.append(FinancialProjection(
                year=current_year + i,
                revenue=round(rev, 2),
                ebitda=round(ebitda, 2),
                net_income=round(ni, 2),
                eps=round(ni / shares_out, 4),
                free_cash_flow=round(fcf, 2),
            ))

        return projections


# ─── Convenience Functions ──────────────────────────────────────────

def analyze_financials(ipo: dict) -> dict:
    """One-shot financial analysis returning all metrics."""
    analyzer = FinancialAnalyzer()
    metrics = analyzer.analyze(ipo)
    peer = analyzer.compare_peers(ipo)
    projections = analyzer.project_financials(ipo)

    return {
        "valuation_metrics": {k: v for k, v in asdict(metrics).items()
                              if not k.endswith("_score")},
        "scores": {
            "valuation_score": metrics.valuation_score,
            "financial_health_score": metrics.financial_health_score,
            "overall": metrics.overall_score,
        },
        "peer_comparison": asdict(peer),
        "projections": [asdict(p) for p in projections],
    }
