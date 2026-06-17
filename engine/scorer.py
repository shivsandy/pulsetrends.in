"""
AI Scoring Engine — 10-Factor Weighted Scoring System

Each factor is scored 20-100. The weighted sum produces the final AI Score.
Scores are clamped to 20-100 at every stage.

Score Interpretation:
  90-100  Exceptional IPO
  80-89   Strong IPO
  70-79   Good IPO
  60-69   Average IPO
  50-59   Speculative IPO
  40-49   High Risk IPO
  20-39   Avoid IPO
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional


# ─── Factor Definitions ──────────────────────────────────────────────

@dataclass
class FactorWeights:
    """Weight allocation across all 10 scoring factors."""
    business_quality: float = 0.15      # 15%
    financial_health: float = 0.15      # 15%
    management_quality: float = 0.10    # 10%
    industry_potential: float = 0.10    # 10%
    valuation: float = 0.10             # 10%
    risk_assessment: float = 0.10       # 10%
    growth_potential: float = 0.10      # 10%
    corporate_governance: float = 0.10  # 10%
    market_sentiment: float = 0.05      # 5%
    listing_gain_potential: float = 0.05 # 5%

    def validate(self):
        total = sum(asdict(self).values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")


@dataclass
class FactorScores:
    """Scores for each factor, range 20-100."""
    business_quality: float = 50.0
    financial_health: float = 50.0
    management_quality: float = 50.0
    industry_potential: float = 50.0
    valuation: float = 50.0
    risk_assessment: float = 50.0
    growth_potential: float = 50.0
    corporate_governance: float = 50.0
    market_sentiment: float = 50.0
    listing_gain_potential: float = 50.0

    def validate(self):
        for name, value in asdict(self).items():
            if not 20 <= value <= 100:
                raise ValueError(
                    f"{name} score {value} is out of range [20, 100]"
                )


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown with weighted contributions."""
    factor_scores: FactorScores
    weights: FactorWeights = field(default_factory=FactorWeights)
    final_score: float = 50.0
    classification: str = "Average IPO"
    explanation: str = ""

    def compute(self) -> float:
        """Compute weighted final score, clamped to 20-100."""
        self.weights.validate()
        self.factor_scores.validate()

        scores = asdict(self.factor_scores)
        wts = asdict(self.weights)
        weighted_sum = sum(scores[k] * wts[k] for k in scores)

        self.final_score = max(20.0, min(100.0, weighted_sum))
        self.classification = self._classify(self.final_score)
        return self.final_score

    @staticmethod
    def _classify(score: float) -> str:
        if score >= 90: return "Exceptional IPO"
        if score >= 80: return "Strong IPO"
        if score >= 70: return "Good IPO"
        if score >= 60: return "Average IPO"
        if score >= 50: return "Speculative IPO"
        if score >= 40: return "High Risk IPO"
        return "Avoid IPO"

    @staticmethod
    def _recommendation(score: float) -> str:
        if score >= 80: return "Strong Subscribe"
        if score >= 70: return "Subscribe"
        if score >= 60: return "Subscribe"
        if score >= 50: return "Neutral"
        return "Avoid"

    def to_dict(self) -> dict:
        return {
            "final_score": round(self.final_score, 1),
            "classification": self.classification,
            "recommendation": self._recommendation(self.final_score),
            "breakdown": asdict(self.factor_scores),
            "weights": asdict(self.weights),
            "weighted_contributions": {
                k: round(v * getattr(self.weights, k, 0), 1)
                for k, v in asdict(self.factor_scores).items()
            },
            "explanation": self.explanation,
        }


# ─── Scoring Engine ──────────────────────────────────────────────────

class ScoringEngine:
    """Generates AI scores for IPOs based on available data."""

    def __init__(self):
        self.default_weights = FactorWeights()

    def score_from_data(self, ipo_data: dict) -> ScoreBreakdown:
        """Produce a full score breakdown from an IPO data dict."""
        scores = self._evaluate_factors(ipo_data)
        breakdown = ScoreBreakdown(
            factor_scores=scores,
            weights=self.default_weights,
        )
        final = breakdown.compute()
        breakdown.explanation = self._generate_explanation(scores, final)
        return breakdown

    def _evaluate_factors(self, ipo: dict) -> FactorScores:
        """Evaluate each factor based on available IPO data."""
        sector = (ipo.get("sector") or ipo.get("industry") or "").lower()
        status = (ipo.get("status") or "upcoming").lower()
        country = (ipo.get("country") or "").upper()
        has_financials = bool(ipo.get("fiscalMetrics") or ipo.get("revenue") or ipo.get("marketCap"))
        has_gmp = float(ipo.get("gmp", 0) or 0) > 0
        has_description = bool(ipo.get("description") or ipo.get("about"))
        subscription = (ipo.get("subscriptionStatus") or ipo.get("subscription") or "")
        is_listed = status == "listed"
        is_upcoming = status in ("upcoming",)

        # ── Business Quality (15%) ──
        bq_score = 50.0
        if has_description:
            bq_score += 10
        if sector:
            bq_score += 10
        if is_listed:
            bq_score += 10
        if has_financials:
            bq_score += 10
        # Sector bonus
        premium_sectors = {"technology", "software", "healthcare", "fintech", "ai", "semiconductor"}
        if any(s in sector for s in premium_sectors):
            bq_score += 10
        bq_score = min(100, max(20, bq_score))

        # ── Financial Health (15%) ──
        fh_score = 40.0
        if has_financials:
            fh_score += 20
        if is_listed:
            fh_score += 15
        if has_gmp:
            fh_score += 10
        if country in ("US", "GB", "JP", "DE", "FR", "CH", "SG", "HK", "AU"):
            fh_score += 5  # Developed market premium
        if ipo.get("currentPrice"):
            fh_score += 5
        if ipo.get("marketCap"):
            fh_score += 5
        fh_score = min(100, max(20, fh_score))

        # ── Management Quality (10%) ──
        mgmt_score = 45.0
        if has_description:
            mgmt_score += 10
        if ipo.get("drhpUrl") or ipo.get("rhpUrl"):
            mgmt_score += 15  # Filing documents available
        if country in ("US", "GB", "DE", "JP", "SG", "HK"):
            mgmt_score += 10
        if isinstance(ipo.get("strengths"), list) and len(ipo["strengths"]) > 0:
            mgmt_score += 10
        if is_listed:
            mgmt_score += 10
        mgmt_score = min(100, max(20, mgmt_score))

        # ── Industry Potential (10%) ──
        ind_score = 50.0
        growth_sectors = {"technology", "software", "healthcare", "biotechnology",
                          "renewable", "fintech", "e-commerce", "ai", "semiconductor",
                          "electric vehicle", "cloud", "cybersecurity"}
        if any(s in sector for s in growth_sectors):
            ind_score += 20
        if sector:
            ind_score += 10
        if country:
            ind_score += 5
        if is_upcoming:
            ind_score += 5  # Pre-IPO companies often in growth stages
        ind_score = min(100, max(20, ind_score))

        # ── Valuation (10%) ──
        val_score = 50.0
        if has_financials:
            val_score += 15
        if has_gmp:
            val_score += 10
        if is_listed and ipo.get("currentPrice") and ipo.get("priceBandLow"):
            try:
                curr = float(ipo["currentPrice"])
                band = float(ipo["priceBandLow"])
                change_pct = ((curr - band) / band) * 100
                if 0 < change_pct < 100:
                    val_score += 10  # Reasonable listing gain
                elif change_pct > 100:
                    val_score -= 10  # Overheated
                elif change_pct < 0:
                    val_score += 5   # Below issue price — potentially undervalued
            except (ValueError, ZeroDivisionError):
                pass
        val_score = min(100, max(20, val_score))

        # ── Risk Assessment (10%) ──
        risk_score = 60.0  # Start neutral-cautious
        if isinstance(ipo.get("risks"), list):
            risk_count = len(ipo["risks"])
            risk_score -= risk_count * 5  # More risks = lower score
        if isinstance(ipo.get("red_flags"), list):
            risk_score -= len(ipo["red_flags"]) * 8
        if country in ("US", "GB", "DE", "JP", "CH", "SG", "HK", "AU", "CA", "NL", "FR"):
            risk_score += 10  # Stronger regulatory frameworks
        if is_listed:
            risk_score += 10
        if has_financials:
            risk_score += 5
        risk_score = min(100, max(20, risk_score))

        # ── Growth Potential (10%) ──
        growth_score = 50.0
        growth_keywords = {"growth", "expand", "scale", "new market", "innovation",
                           "r&d", "patent", "market leader", "fast growth"}
        desc_text = (ipo.get("description") or ipo.get("about") or "").lower()
        for kw in growth_keywords:
            if kw in desc_text:
                growth_score += 5
        if any(s in sector for s in growth_sectors):
            growth_score += 15
        if is_upcoming:
            growth_score += 5
        if ipo.get("revenueGrowth"):
            try:
                rg = float(ipo["revenueGrowth"].replace("%", ""))
                growth_score += min(20, rg / 5)
            except (ValueError, AttributeError):
                pass
        growth_score = min(100, max(20, growth_score))

        # ── Corporate Governance (10%) ──
        gov_score = 50.0
        if ipo.get("drhpUrl") or ipo.get("rhpUrl"):
            gov_score += 15  # Filing transparency
        has_sector = bool(sector)
        has_desc = bool(ipo.get("description") or ipo.get("about"))
        if has_sector and has_desc:
            gov_score += 10
        if country in ("US", "GB", "DE", "JP", "SG", "HK", "AU", "CA", "CH", "NL"):
            gov_score += 10
        if is_listed:
            gov_score += 10
        if isinstance(ipo.get("anchorInvestors"), list) and len(ipo["anchorInvestors"]) > 0:
            gov_score += 5
        gov_score = min(100, max(20, gov_score))

        # ── Market Sentiment (5%) ──
        sent_score = 50.0
        if has_gmp:
            try:
                gmp_val = float(ipo["gmp"])
                price = float(ipo.get("priceBandLow", 1) or 1)
                if price > 0:
                    gmp_pct = (gmp_val / price) * 100
                    if gmp_pct > 50:
                        sent_score += 25
                    elif gmp_pct > 20:
                        sent_score += 15
                    elif gmp_pct > 0:
                        sent_score += 10
            except (ValueError, ZeroDivisionError):
                pass
        if subscription:
            try:
                sub_val = float(subscription.replace("x", ""))
                if sub_val > 50:
                    sent_score += 20
                elif sub_val > 10:
                    sent_score += 15
                elif sub_val > 1:
                    sent_score += 10
            except (ValueError, AttributeError):
                pass
        sent_score = min(100, max(20, sent_score))

        # ── Listing Gain Potential (5%) ──
        listing_score = 50.0
        if is_upcoming:
            if has_gmp:
                try:
                    gmp_val = float(ipo["gmp"])
                    price = float(ipo.get("priceBandLow", 1) or 1)
                    if price > 0:
                        gmp_pct = (gmp_val / price) * 100
                        if gmp_pct > 50:
                            listing_score += 30
                        elif gmp_pct > 20:
                            listing_score += 20
                        elif gmp_pct > 0:
                            listing_score += 10
                except (ValueError, ZeroDivisionError):
                    pass
            if subscription:
                try:
                    sub_val = float(subscription.replace("x", ""))
                    if sub_val > 10:
                        listing_score += 15
                except (ValueError, AttributeError):
                    pass
        elif is_listed:
            listing_score = 30.0  # Already listed, lower relevance
            if ipo.get("currentPrice") and ipo.get("priceBandLow"):
                try:
                    curr = float(ipo["currentPrice"])
                    low = float(ipo["priceBandLow"])
                    if low > 0 and curr > low:
                        listing_score += 20
                except (ValueError, ZeroDivisionError):
                    pass
        listing_score = min(100, max(20, listing_score))

        return FactorScores(
            business_quality=round(bq_score, 1),
            financial_health=round(fh_score, 1),
            management_quality=round(mgmt_score, 1),
            industry_potential=round(ind_score, 1),
            valuation=round(val_score, 1),
            risk_assessment=round(risk_score, 1),
            growth_potential=round(growth_score, 1),
            corporate_governance=round(gov_score, 1),
            market_sentiment=round(sent_score, 1),
            listing_gain_potential=round(listing_score, 1),
        )

    def _generate_explanation(self, scores: FactorScores, final: float) -> str:
        """Generate a human-readable explanation of the score."""
        parts = []
        cls = ScoreBreakdown._classify(final)
        parts.append(f"Overall AI Score: {final:.0f}/100 — {cls}.")

        # Highlight top and bottom factors
        sd = asdict(scores)
        sorted_factors = sorted(sd.items(), key=lambda x: x[1], reverse=True)
        top = sorted_factors[0]
        bottom = sorted_factors[-1]

        parts.append(f"Strongest factor: {top[0].replace('_', ' ').title()} ({top[1]:.0f}/100).")
        parts.append(f"Weakest factor: {bottom[0].replace('_', ' ').title()} ({bottom[1]:.0f}/100).")

        if final >= 70:
            parts.append("Overall positive assessment with manageable risk profile.")
        elif final >= 50:
            parts.append("Mixed indicators; further due diligence recommended.")
        else:
            parts.append("Significant concerns identified; proceed with caution.")

        return " ".join(parts)


# ─── Convenience Functions ──────────────────────────────────────────

def compute_score(ipo_data: dict) -> ScoreBreakdown:
    """One-shot scoring: pass an IPO data dict, get a complete ScoreBreakdown."""
    engine = ScoringEngine()
    return engine.score_from_data(ipo_data)


def batch_score(ipo_list: List[dict]) -> List[dict]:
    """Score a batch of IPOs and return sorted results."""
    engine = ScoringEngine()
    results = []
    for ipo in ipo_list:
        try:
            breakdown = engine.score_from_data(ipo)
            results.append(breakdown.to_dict())
        except Exception as e:
            results.append({
                "final_score": 0,
                "classification": "Error",
                "error": str(e),
            })
    results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    return results
