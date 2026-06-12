"""
Airdrops Scraper — Enhanced pipeline for scraping airdrop data from multiple sources.

Scrapes:
  - airdrops.io (listing + detail pages)
  - airdropalert.com (listing)

Output: clean JSON array of airdrop objects with participation steps, chain, status, etc.
"""

import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup, Tag

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
AIRDROP_IO_FILE = os.path.join(DATA_DIR, "airdrops_data.json")
# ── Configuration ────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

BASE_URL = "https://airdrops.io"
AIRDROPALERT_URL = "https://airdropalert.com"

# Section-header names to skip (these aren't real airdrops)
SKIP_NAMES = {
    "latest airdrops",
    "hottest airdrops",
    "updated airdrops",
    "potential airdrops",
    "hot airdrops",
    "new airdrops",
    "trending airdrops",
    "browse airdrops effortlessly with easy search & filter options",
}

# ── Helpers ──────────────────────────────────────────────────────


def _id_from_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _html_text(el: Tag | None) -> str:
    if el is None:
        return ""
    return _clean_text(el.get_text(separator=" ", strip=True))


def _href(el: Tag | None) -> str:
    if el is None:
        return ""
    href = el.get("href", "")
    if isinstance(href, str) and href.startswith("/"):
        href = BASE_URL + href
    return href


def _is_valid_name(name: str) -> bool:
    name_lower = name.strip().lower()
    if not name_lower or len(name_lower) < 2:
        return False
    if name_lower in SKIP_NAMES:
        return False
    # Skip names that look like page sections (e.g. "Browse airdrops effortlessly...")
    if len(name_lower) > 40:
        return False
    return True


def _parse_heat_score(text: str) -> int:
    match = re.search(r"(\d+)°", text)
    return int(match.group(1)) if match else 0


def _parse_status(text: str) -> str:
    tl = text.lower()
    if "confirmed" in tl:
        return "confirmed"
    return "active"


def _parse_chain(text: str) -> str:
    """Extract chain from text snippets like 'Solana What is X' or 'Own chain, Arbitrum, Ethereum, Hyperliquid'."""
    # Common chains (ordered by specificity)
    known_chains = [
        "Ethereum", "Solana", "Arbitrum", "Base", "Hyperliquid", "Bitcoin", "BNB Chain",
        "BSC", "Polygon", "Optimism", "Cosmos", "Avalanche", "Celestia", "Sui", "Aptos",
        "Monad", "Berachain", "TON", "StarkNet", "zkSync", "Scroll", "Linea", "Fuel",
        "Polyhedra", "Movement", "Eclipse", "Initia", "Saga", "Dymension", "Neutron",
        "Nibiru", "Archway", "Canto", "Kamino", "Parcl", "ApeX", "Penumbra", "Tenet",
        "Injective", "Sei", "Kaspa", "MegaETH", "Story", "Swan", "Aethir", "Hemi",
        "Ink", "Citrea", "Zora", "Blast", "Mode", "Taiko", "Pyth", "Ainn",
        "Scroll", "Citrea", "Solstice",
    ]
    
    # Remove filler phrases first
    cleaned = re.sub(r"\s*(What is|Claim Live|Chain|Network)\s*.*", "", text, flags=re.I).strip()
    
    # Handle "Own chain" -> extract the actual chain name from comma-separated values
    if "own chain" in cleaned.lower():
        # Look for known chains in the full text (including after commas)
        for chain in known_chains:
            if chain.lower() in text.lower():
                return chain
        # Extract the last chain name before "What is" or 
        parts = re.split(r"[,;]|\s+(?:What is|Ongoing|Confirmed)\s+", text, flags=re.I)
        for p in reversed(parts):
            p = p.strip()
            if p and len(p) > 2 and p.lower() not in ("own chain", "chain"):
                return p
        return ""
    
    # Check for known chains in cleaned text
    for chain in known_chains:
        if chain.lower() in cleaned.lower():
            return chain
    # Fallback: check comma-separated values
    parts = [p.strip() for p in re.split(r"[,;]", text) if p.strip()]
    for p in parts:
        for chain in known_chains:
            if chain.lower() in p.lower():
                return chain
    # Last resort: first word with length > 1
    words = cleaned.split()
    if words and len(words[0]) > 1:
        return words[0]
    return ""


def _parse_actions_from_card(text: str) -> list[str]:
    """Extract actionable steps from card description text.
    Input like: 'Trade, Interact with Chain, Stake HYPE, Provide LP & Refer Friends'
    """
    # Remove heat score prefix
    text = re.sub(r"^\d+°\s*", "", text)
    # Remove status words
    text = re.sub(r"\b(Ongoing|Confirmed|Active|Claim Live)\b", "", text, flags=re.I)
    # Remove trailing "CLAIM AIRDROP" etc
    text = re.sub(r"\s*CLAIM AIRDROP.*", "", text, flags=re.I)
    text = _clean_text(text)

    if not text or len(text) < 5:
        return []

    # Split by comma, &, or bullets
    parts = re.split(r"\s*[,&]\s*|•\s*", text)
    steps = []
    for p in parts:
        p = p.strip().strip(".").strip()
        if p and len(p) > 3 and p.lower() not in ("actions", "actions:"):
            steps.append(p)
    return steps


# ── airdrops.io Scraping ────────────────────────────────────────


def _scrape_single_page(url: str, seen_ids: set[str]) -> list[dict]:
    """Scrape a single airdrops.io page and return valid airdrop cards."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"[Airdrops Scraper] Page {url} returned HTTP {resp.status_code}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"[Airdrops Scraper] Error fetching {url}: {e}")
        return []

    results: list[dict] = []
    # Find all article-like cards
    cards = soup.select("article, div.post, div.entry, [class*=airdrop], [class*=item]")
    if not cards:
        cards = soup.find_all("div", class_=re.compile(r"airdrop|item|card|post", re.I))

    for card in cards:
        try:
            name_el = card.select_one("h2, h3, h4, .entry-title, .title, strong")
            if not name_el:
                continue
            name = _clean_text(name_el.get_text(strip=True))
            if not _is_valid_name(name):
                continue

            aid = _id_from_name(name)
            if aid in seen_ids:
                continue
            seen_ids.add(aid)

            # Link
            link_el = card.select_one("a[href*='airdrops.io']") or name_el.find_parent("a")
            card_url = _href(link_el) if link_el else ""

            # Get full card text
            full_text = _clean_text(card.get_text(separator=" ", strip=True))

            heat = _parse_heat_score(full_text)
            status = _parse_status(full_text)

            # Chain from card
            chain_text = _clean_text(card.get_text(separator=" ", strip=True))
            chain = _parse_chain(chain_text)

            # Description / actions
            actions = _parse_actions_from_card(full_text) if heat > 0 else []
            description = full_text[:400] if len(full_text) > 400 else full_text

            results.append({
                "id": aid,
                "name": name,
                "url": card_url,
                "heat": heat,
                "status": status,
                "chain": chain,
                "actions": actions,
                "description": description,
                "source": "airdrops.io",
            })
        except Exception:
            continue

    return results


def scrape_airdrops_io_listing(max_pages: int = 5) -> list[dict]:
    """Scrape airdrops.io listing cards across multiple pages."""
    print(f"[Airdrops Scraper] Fetching airdrops.io listing (up to {max_pages} pages)...")
    
    all_airdrops: list[dict] = []
    seen_ids: set[str] = set()

    for page_num in range(1, max_pages + 1):
        url = f"{BASE_URL}/page/{page_num}/" if page_num > 1 else BASE_URL
        page_results = _scrape_single_page(url, seen_ids)
        if not page_results:
            print(f"[Airdrops Scraper] No more results after page {page_num - 1}, stopping")
            break
        all_airdrops.extend(page_results)
        print(f"[Airdrops Scraper] Page {page_num}: +{len(page_results)} airdrops (total: {len(all_airdrops)})")
        time.sleep(1.0)  # Be polite

    print(f"[Airdrops Scraper] Found {len(all_airdrops)} valid airdrops from listing")
    return all_airdrops

    airdrops: list[dict] = []
    seen_ids: set[str] = set()

    # Find all article-like cards
    cards = soup.select("article, div.post, div.entry, [class*=airdrop], [class*=item]")
    if not cards:
        cards = soup.find_all("div", class_=re.compile(r"airdrop|item|card|post", re.I))

    for card in cards:
        try:
            name_el = card.select_one("h2, h3, h4, .entry-title, .title, strong")
            if not name_el:
                continue
            name = _clean_text(name_el.get_text(strip=True))
            if not _is_valid_name(name):
                continue

            aid = _id_from_name(name)
            if aid in seen_ids:
                continue
            seen_ids.add(aid)

            # Link
            link_el = card.select_one("a[href*='airdrops.io']") or name_el.find_parent("a")
            url = _href(link_el) if link_el else ""

            # Get full card text
            full_text = _clean_text(card.get_text(separator=" ", strip=True))

            heat = _parse_heat_score(full_text)
            status = _parse_status(full_text)

            # Chain from card
            chain_text = _clean_text(card.get_text(separator=" ", strip=True))
            chain = _parse_chain(chain_text)

            # Description / actions
            actions = _parse_actions_from_card(full_text) if heat > 0 else []
            description = full_text[:400] if len(full_text) > 400 else full_text

            airdrops.append({
                "id": aid,
                "name": name,
                "url": url,
                "heat": heat,
                "status": status,
                "chain": chain,
                "actions": actions,
                "description": description,
                "source": "airdrops.io",
            })
        except Exception as e:
            continue

    print(f"[Airdrops Scraper] Found {len(airdrops)} valid airdrops from listing")
    return airdrops


def scrape_airdrops_io_detail(url: str, name: str) -> dict:
    """Scrape a detail page for richer data: about, steps, chain, social links, value."""
    result: dict = {}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = _clean_text(soup.get_text(separator=" ", strip=True))

        # ── Chain ──
        chain_match = re.search(
            r"Chain\s*:?\s*([A-Za-z, \n]+?)(?:What is|Ongoing|Confirmed|Airdrop)",
            text, re.I
        )
        if chain_match:
            chain = chain_match.group(1).strip().rstrip(",").strip()
            result["chain"] = _parse_chain(chain) or chain

        # ── Estimated value ──
        value_match = re.search(
            r"(?:Estimated\s*(?:Value|Reward|Airdrop)\s*:?\s*"
            r"|Value\s*:?\s*)"
            r"(\$[\d,]+(?:\s*[–-]\s*\$?[\d,]+)?(?:\s*-\s*\$?[\d,]+)?)",
            text, re.I
        )
        if value_match:
            result["estimated_value"] = value_match.group(1).strip()

        # ── TGE / Launch date ──
        tge_match = re.search(
            r"(?:TGE|Token\s*(?:Generation|Launch)|Launch\s*Date)\s*:?\s*(.+?)(?:\.|$)",
            text, re.I
        )
        if tge_match:
            result["tge_date"] = tge_match.group(1).strip()

        # ── How to Participate steps ──
        steps = _extract_participation_steps(soup, text)
        if steps:
            result["steps"] = steps

        # ── About / description (first real paragraph) ──
        about = _extract_about(soup, text, name)
        if about:
            result["about"] = about

        # ── Social links ──
        social_links = _extract_social_links(soup, text)
        if social_links:
            result["social_links"] = social_links

        # ── Eligibility ──
        elig_match = re.search(
            r"(?:Eligibility|Who is eligible|Requirements)\s*:?\s*(.+?)(?:\.|$)",
            text, re.I
        )
        if elig_match:
            result["eligibility"] = elig_match.group(1).strip()

        # ── Difficulty ──
        diff_match = re.search(
            r"(Difficulty|Estimated Difficulty)\s*:?\s*(Easy|Medium|Hard)",
            text, re.I
        )
        if diff_match:
            result["difficulty"] = diff_match.group(2)

        # ── Cost ──
        cost_match = re.search(
            r"(?:Estimated\s*)?Cost\s*:?\s*(.+?)(?:\.|$)",
            text, re.I
        )
        if cost_match:
            result["estimated_cost"] = cost_match.group(1).strip()

        time.sleep(0.3)

    except Exception as e:
        print(f"[Airdrops Scraper] Detail scrape fail for {name}: {e}")

    return result


def _extract_participation_steps(soup: BeautifulSoup, text: str) -> list[str]:
    """Extract numbered participation steps from the detail page."""
    steps: list[str] = []

    # Look for "How to Participate" or "How to Join" sections
    for heading_text in ["How to Participate", "How to Join", "How to Farm",
                         "How to Claim", "Step-by-Step Guide", "Steps",
                         "Participation Guide"]:
        heading = soup.find(["h2", "h3", "h4", "strong"],
                            string=re.compile(re.escape(heading_text), re.I))
        if heading:
            # Get all list items after this heading
            parent = heading.find_parent(["section", "div", "article"])
            if not parent:
                parent = heading.parent
            if parent:
                lis = parent.find_all("li")
                if lis:
                    steps = [_clean_text(li.get_text()) for li in lis if _clean_text(li.get_text())]
                    if len(steps) >= 2:
                        return steps

    # Fallback: look for numbered patterns like "1. Do X 2. Do Y"
    numbered = re.findall(r"(?:^|\s)(\d+[.)]\s*)([A-Z][^.!?\n]+[.!?])", text)
    if numbered and len(numbered) >= 2:
        steps = [n[1].strip() for n in numbered[:10]]
        return steps

    # Fallback: look for "Actions:" or bullet points
    actions_match = re.search(
        r"(?:Actions?|Steps|What to do)\s*:?\s*(.+?)(?:How to|What is|$)",
        text, re.I
    )
    if actions_match:
        action_text = actions_match.group(1)
        parts = re.split(r"[•·-]\s*", action_text)
        steps = [p.strip() for p in parts if len(p.strip()) > 5][:10]

    return steps


def _extract_about(soup: BeautifulSoup, text: str, name: str) -> str:
    """Extract the project description/about section."""
    # Look for "What Is X" or "About" section
    for heading_text in [f"What is {name}", "About", "Overview", "What Is"]:
        heading = soup.find(["h2", "h3", "strong"],
                            string=re.compile(re.escape(heading_text), re.I))
        if heading:
            parent = heading.find_parent(["section", "div", "article"]) or heading.parent
            if parent:
                # Get the paragraph right after
                for sibling in parent.find_all(["p", "div"], recursive=True):
                    # Only first meaningful paragraph
                    if _html_text(sibling) and len(_html_text(sibling)) > 80:
                        return _html_text(sibling)[:1000]

    # Fallback: get the first large paragraph
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        txt = _html_text(p)
        if len(txt) > 100 and "cookie" not in txt.lower() and "menu" not in txt.lower():
            return txt[:1000]

    return ""


def _extract_social_links(soup: BeautifulSoup, text: str) -> dict:
    """Extract Twitter/X, Discord, Telegram links from the main content area."""
    links: dict = {}
    # Scope to main article content to avoid nav/footer links
    content_area = soup.find("article") or soup.find("main") or soup.find(".entry-content") or soup
    if not isinstance(content_area, Tag):
        content_area = soup
    for a_tag in content_area.find_all("a", href=True):
        href = a_tag.get("href", "")
        if not isinstance(href, str):
            continue
        hl = href.lower()
        if "x.com" in hl or "twitter.com" in hl:
            if not links.get("twitter"):
                links["twitter"] = href
        elif "discord.gg" in hl or "discord.com" in hl:
            if not links.get("discord"):
                links["discord"] = href
        elif "t.me" in hl or "telegram" in hl:
            if not links.get("telegram"):
                links["telegram"] = href
        elif "github.com" in hl:
            if not links.get("github"):
                links["github"] = href
    return links


# ── airdropalert.com Scraping ───────────────────────────────────


def scrape_airdropalert() -> list[dict]:
    """Scrape airdropalert.com for additional airdrop listings."""
    print("[Airdrops Scraper] Fetching airdropalert.com listing...")
    try:
        resp = requests.get(AIRDROPALERT_URL, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"[Airdrops Scraper] airdropalert fetch failed: HTTP {resp.status_code}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        items: list[dict] = []
        seen_names: set[str] = set()

        cards = soup.select(".airdrop-card, .airdrop-item, article, [class*=airdrop]")
        if not cards:
            cards = soup.find_all("div", class_=re.compile(r"airdrop|card|item", re.I))

        for card in cards:
            name_el = card.select_one("h2, h3, .airdrop-name, .title")
            if not name_el:
                continue
            name = _clean_text(name_el.get_text(strip=True))
            if not _is_valid_name(name):
                continue
            if name.lower() in seen_names:
                continue
            seen_names.add(name.lower())

            link_el = card.select_one("a[href]")
            url = _href(link_el) if link_el else ""

            desc_el = card.select_one("p, .airdrop-desc, .description")
            description = _html_text(desc_el) if desc_el else ""

            items.append({
                "id": _id_from_name(name),
                "name": name,
                "url": url,
                "description": description or name,
                "status": "active",
                "chain": "",
                "actions": [],
                "source": "airdropalert",
            })

        print(f"[Airdrops Scraper] Found {len(items)} airdrops from airdropalert")
        return items
    except Exception as e:
        print(f"[Airdrops Scraper] airdropalert scrape error: {e}")
        return []


# ── Merge & Normalize ────────────────────────────────────────────


def _normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def merge_sources(sources: list[list[dict]]) -> list[dict]:
    """Merge multiple scraped sources, deduplicating by name."""
    seen: dict[str, dict] = {}
    for batch in sources:
        for ad in batch:
            key = _normalize_name(ad.get("name", ""))
            if not key:
                continue
            if key in seen:
                existing = seen[key]
                # Merge fields, preferring non-empty values
                for field in ["chain", "description", "estimated_value", "url",
                              "status"]:
                    new_val = ad.get(field)
                    old_val = existing.get(field)
                    if new_val and not old_val:
                        existing[field] = new_val
                # Merge steps (longer wins)
                existing_steps = existing.get("steps") or existing.get("actions") or []
                new_steps = ad.get("steps") or ad.get("actions") or []
                if len(new_steps) > len(existing_steps):
                    existing["steps"] = new_steps
                # Merge social links
                existing_social = existing.get("social_links", {}) or {}
                new_social = ad.get("social_links", {}) or {}
                if isinstance(existing_social, dict) and isinstance(new_social, dict):
                    for k, v in new_social.items():
                        if v and not existing_social.get(k):
                            existing_social[k] = v
                    existing["social_links"] = existing_social
                # Heat score (max)
                existing["heat"] = max(existing.get("heat", 0) or 0, ad.get("heat", 0) or 0)
                # About (prefer longer)
                existing_about = existing.get("about", "")
                new_about = ad.get("about", "")
                if len(str(new_about)) > len(str(existing_about)):
                    existing["about"] = new_about
            else:
                entry = dict(ad)
                # Normalize actions -> steps
                if entry.get("actions") and not entry.get("steps"):
                    entry["steps"] = entry["actions"]
                seen[key] = entry

    merged = list(seen.values())
    print(f"[Airdrops Scraper] Merged: {len(merged)} unique airdrops")
    return merged


# ── Main orchestrator ────────────────────────────────────────────


def scrape(force_refresh: bool = False) -> list[dict]:
    """Run the full scraping pipeline and return merged results."""
    # Check cache freshness
    if not force_refresh and os.path.exists(AIRDROP_IO_FILE):
        try:
            with open(AIRDROP_IO_FILE, encoding="utf-8") as f:
                cached = json.load(f)
            last = cached.get("last_updated", "")
            if last:
                updated = datetime.fromisoformat(last.replace("Z", "+00:00"))
                age_hours = (datetime.now(timezone.utc) - updated).total_seconds() / 3600
                if age_hours < 12:
                    print(f"[Airdrops Scraper] Data is {age_hours:.1f}h old, using cache ({len(cached.get('airdrops', []))} airdrops)")
                    return cached.get("airdrops", [])
        except Exception:
            pass    # 1. Scrape airdrops.io listing
    airdrops_io = scrape_airdrops_io_listing()

    # 2. Scrape detail pages for each (skip if too many, limit to top by heat)
    airdrops_io.sort(key=lambda x: x.get("heat", 0) or 0, reverse=True)
    print(f"[Airdrops Scraper] Scraping detail pages for top {len(airdrops_io)} airdrops...")
    enriched = []
    for i, ad in enumerate(airdrops_io):
        if ad.get("url"):
            detail = scrape_airdrops_io_detail(ad["url"], ad["name"])
            ad.update(detail)
            enriched.append(ad)
        if (i + 1) % 10 == 0:
            print(f"[Airdrops Scraper] Detail pages: {i + 1}/{len(airdrops_io)}")

    # 3. Scrape airdropalert as supplementary
    airdropalert = scrape_airdropalert()

    # 4. Merge
    merged = merge_sources([enriched, airdropalert])

    return merged


def save(airdrops: list[dict]):
    """Save merged results to JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total": len(airdrops),
        "airdrops": airdrops,
    }
    with open(AIRDROP_IO_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[Airdrops Scraper] Saved {len(airdrops)} airdrops to {AIRDROP_IO_FILE}")


if __name__ == "__main__":
    data = scrape()
    save(data)
    print(f"[Airdrops Scraper] Done — {len(data)} airdrops collected")
