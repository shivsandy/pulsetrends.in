"""
Duplicate Prevention System — Multi-Field Deduplication

Checks across 7 fields before allowing a new IPO to be added:
1. Company Name (fuzzy match)
2. Exchange
3. Ticker Symbol
4. ISIN
5. Filing Number / Prospectus ID
6. Source ID
7. Filing Date (within 90-day window)

Records are matched if ANY of these composite checks succeed.
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set, Tuple


# ─── Fuzzy Matching Utility ─────────────────────────────────────────

def _normalize_name(name: str) -> str:
    """Normalize company name for comparison."""
    n = name.lower().strip()
    # Remove common suffixes
    n = re.sub(r'\b(ltd|limited|inc|corp|corporation|plc|sa|ag|nv|gmbh|spa|as|ab|oy)\b\.?', '', n)
    n = re.sub(r'\b(holdings|group|industries|technologies|international|global)\b', '', n)
    n = re.sub(r'[^a-z0-9\s]', '', n)
    return re.sub(r'\s+', ' ', n).strip()


def _name_similarity(name1: str, name2: str) -> float:
    """Compute fuzzy name similarity (0.0 to 1.0)."""
    n1 = _normalize_name(name1)
    n2 = _normalize_name(name2)
    if not n1 or not n2:
        return 0.0
    # Exact match after normalization
    if n1 == n2:
        return 1.0
    # Token-based matching
    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    token_score = len(intersection) / len(union) if union else 0
    # Sequence matching
    seq_score = SequenceMatcher(None, n1, n2).ratio()
    return max(token_score, seq_score)


# ─── Duplicate Check ────────────────────────────────────────────────

class DuplicateDetector:
    """
    Multi-field duplicate detector for IPO records.

    Maintains a lookup index from existing records and checks new
    records against multiple fields before allowing insertion.
    """

    def __init__(self, existing_records: Optional[List[dict]] = None):
        self.name_threshold = 0.85  # Fuzzy name match threshold
        self.filing_window_days = 90  # Max days for filing date match

        # Indexes
        self._ticker_index: Dict[str, List[dict]] = {}       # ticker -> records
        self._exchange_ticker_index: Dict[str, dict] = {}     # exch:ticker -> record
        self._name_index: Dict[str, List[dict]] = {}          # normalized name -> records
        self._source_id_index: Dict[str, dict] = {}           # source_id -> record
        self._filing_id_index: Dict[str, dict] = {}           # filing_id -> record
        self._isin_index: Dict[str, dict] = {}                 # isin -> record
        self._all_records: List[dict] = []

        if existing_records:
            self.build_index(existing_records)

    def build_index(self, records: List[dict]):
        """Build lookup indexes from existing records."""
        self._all_records = records
        self._ticker_index.clear()
        self._exchange_ticker_index.clear()
        self._name_index.clear()
        self._source_id_index.clear()
        self._filing_id_index.clear()
        self._isin_index.clear()

        for rec in records:
            # Ticker index
            ticker = (rec.get("ticker") or rec.get("symbol") or "").strip().upper()
            if ticker:
                self._ticker_index.setdefault(ticker, []).append(rec)

            # Exchange:Ticker composite
            exchange = (rec.get("exchange") or "").strip().upper()
            if ticker and exchange:
                self._exchange_ticker_index[f"{exchange}:{ticker}"] = rec

            # Name index
            name = (rec.get("name") or rec.get("company_name") or "").strip()
            if name:
                norm = _normalize_name(name)
                self._name_index.setdefault(norm, []).append(rec)

            # Source ID
            sid = rec.get("id") or rec.get("source_id") or ""
            if sid:
                self._source_id_index[sid] = rec

            # Filing ID
            fid = rec.get("filing_id") or rec.get("prospectus_id") or ""
            if fid:
                self._filing_id_index[fid] = rec

            # ISIN
            isin = rec.get("isin", "")
            if isin:
                self._isin_index[isin] = rec

    def check(self, new_ipo: dict) -> Optional[dict]:
        """
        Check a new IPO record against all existing records.

        Returns the matched existing record if a duplicate is found,
        or None if the record appears to be new.

        Performs checks in order of reliability (fastest/most reliable first):
        1. Source ID match
        2. Exchange:Ticker composite match
        3. ISIN match
        4. Filing ID / Prospectus ID match
        5. Ticker-only match (within same exchange group)
        6. Fuzzy name match (with exchange similarity)
        7. Filing date proximity (within 90 days)
        """
        new_ticker = (new_ipo.get("ticker") or new_ipo.get("symbol") or "").strip().upper()
        new_exchange = (new_ipo.get("exchange") or "").strip().upper()
        new_name = (new_ipo.get("name") or new_ipo.get("company_name") or "").strip()
        new_sid = new_ipo.get("id") or new_ipo.get("source_id") or ""
        new_fid = new_ipo.get("filing_id") or new_ipo.get("prospectus_id") or ""
        new_isin = new_ipo.get("isin", "")
        new_date = (new_ipo.get("openDate") or new_ipo.get("listingDate") or
                    new_ipo.get("ipo_date") or new_ipo.get("filing_date") or "")

        # 1. Source ID match (exact)
        if new_sid and new_sid in self._source_id_index:
            return self._source_id_index[new_sid]

        # 2. Exchange:Ticker composite (exact)
        if new_ticker and new_exchange:
            key = f"{new_exchange}:{new_ticker}"
            if key in self._exchange_ticker_index:
                return self._exchange_ticker_index[key]

        # 3. ISIN match (exact)
        if new_isin and new_isin in self._isin_index:
            return self._isin_index[new_isin]

        # 4. Filing ID / Prospectus ID (exact)
        if new_fid and new_fid in self._filing_id_index:
            return self._filing_id_index[new_fid]

        # 5. Ticker match within exchange group
        if new_ticker and new_ticker in self._ticker_index:
            candidates = self._ticker_index[new_ticker]
            if new_exchange:
                # Prefer same exchange
                for cand in candidates:
                    cand_exch = (cand.get("exchange") or "").strip().upper()
                    if cand_exch == new_exchange:
                        return cand
            # Return first ticker match if no exchange context
            return candidates[0]

        # 6. Fuzzy name match
        if new_name:
            best_match = None
            best_score = 0.0
            for norm, records in self._name_index.items():
                for cand in records:
                    cand_name = (cand.get("name") or cand.get("company_name") or "").strip()
                    if not cand_name:
                        continue
                    score = _name_similarity(new_name, cand_name)
                    # Bonus if exchanges match
                    cand_exch = (cand.get("exchange") or "").strip().upper()
                    if new_exchange and cand_exch and new_exchange == cand_exch:
                        score += 0.1
                    if score > best_score:
                        best_score = score
                        best_match = cand

            if best_match and best_score >= self.name_threshold:
                return best_match

        # 7. Filing date proximity (within 90 days) + partial name match
        if new_date and new_name:
            try:
                new_dt = datetime.fromisoformat(new_date.replace("Z", "+00:00"))
                window_start = new_dt - timedelta(days=self.filing_window_days)
                window_end = new_dt + timedelta(days=self.filing_window_days)

                for rec in self._all_records:
                    rec_date = (rec.get("openDate") or rec.get("listingDate") or
                                rec.get("ipo_date") or rec.get("filing_date") or "")
                    if not rec_date:
                        continue
                    try:
                        rec_dt = datetime.fromisoformat(rec_date.replace("Z", "+00:00"))
                        if window_start <= rec_dt <= window_end:
                            rec_name = (rec.get("name") or rec.get("company_name") or "").strip()
                            if new_name and rec_name:
                                if _name_similarity(new_name, rec_name) >= 0.6:
                                    return rec
                    except (ValueError, AttributeError):
                        continue
            except (ValueError, AttributeError):
                pass

        return None

    def is_duplicate(self, new_ipo: dict) -> bool:
        """Simple boolean check: returns True if duplicate found."""
        return self.check(new_ipo) is not None

    def get_duplicates(self, new_ipos: List[dict]) -> Tuple[List[dict], List[dict]]:
        """
        Batch check: returns (unique_records, duplicate_records).
        Preserves the first occurrence of each duplicate.
        """
        unique: List[dict] = []
        duplicates: List[dict] = []
        seen_keys: Set[str] = set()

        for ipo in new_ipos:
            matched = self.check(ipo)
            if matched:
                duplicates.append(ipo)
            else:
                # Generate a quick lookup key to avoid re-checking within batch
                ticker = (ipo.get("ticker") or "").strip().upper()
                name = (ipo.get("name") or ipo.get("company_name") or "").strip()
                exch = (ipo.get("exchange") or "").strip().upper()
                key = f"{exch}:{ticker}:{_normalize_name(name)}" if ticker else f"name:{_normalize_name(name)}"

                if key not in seen_keys:
                    seen_keys.add(key)
                    unique.append(ipo)
                    # Temporarily add to our index for within-batch dedup
                    self._add_to_index(ipo)

        return unique, duplicates

    def _add_to_index(self, rec: dict):
        """Add a single record to the lookup indexes."""
        self._all_records.append(rec)
        ticker = (rec.get("ticker") or rec.get("symbol") or "").strip().upper()
        exchange = (rec.get("exchange") or "").strip().upper()
        name = (rec.get("name") or rec.get("company_name") or "").strip()
        sid = rec.get("id") or rec.get("source_id") or ""

        if ticker:
            self._ticker_index.setdefault(ticker, []).append(rec)
        if ticker and exchange:
            self._exchange_ticker_index[f"{exchange}:{ticker}"] = rec
        if name:
            self._name_index.setdefault(_normalize_name(name), []).append(rec)
        if sid:
            self._source_id_index[sid] = rec


# ─── Convenience Functions ──────────────────────────────────────────

def deduplicate_list(ipos: List[dict]) -> Tuple[List[dict], List[dict]]:
    """Deduplicate a list of IPO records. Returns (unique, duplicates)."""
    detector = DuplicateDetector()
    return detector.get_duplicates(ipos)


def merge_with_dedup(
    existing: List[dict],
    incoming: List[dict],
) -> Tuple[List[dict], int, int]:
    """
    Merge incoming records into existing, deduplicating as we go.

    Returns: (merged_records, new_count, updated_count)
    """
    detector = DuplicateDetector(existing)
    new_count = 0
    updated_count = 0
    merged = list(existing)

    for ipo in incoming:
        match = detector.check(ipo)
        if match:
            # Update existing fields if new data is available
            updated = False
            for field, value in ipo.items():
                if value and not match.get(field):
                    match[field] = value
                    updated = True
            if updated:
                match["last_updated"] = datetime.now(timezone.utc).isoformat()
                updated_count += 1
        else:
            if not ipo.get("last_updated"):
                ipo["last_updated"] = datetime.now(timezone.utc).isoformat()
            merged.append(ipo)
            detector._add_to_index(ipo)
            new_count += 1

    return merged, new_count, updated_count
