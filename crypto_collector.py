import json
import os
import sys
from datetime import datetime, timezone

import requests

try:
    from airdrops_scraper import scrape as scrape_airdrops, load_cache as load_airdrop_cache
except ImportError:
    scrape_airdrops = None
    load_airdrop_cache = None

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CRYPTO_FILE = os.path.join(DATA_DIR, "crypto_data.json")
AIRDROP_FILE = os.path.join(DATA_DIR, "airdrops_data.json")

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE = "https://api.llama.fi"


def fetch_coingecko_top_coins(limit: int = 60) -> list[dict]:
    coins = []
    try:
        resp = requests.get(
            f"{COINGECKO_BASE}/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": min(limit, 250),
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h",
            },
            headers={"Accept": "application/json"},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data:
                coins.append({
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "ticker": (item.get("symbol") or "").upper(),
                    "category": "coin",
                    "chain": item.get("id", ""),
                    "description": f"{item.get('name', '')} ({item.get('symbol', '').upper()}) - Market Cap: ${item.get('market_cap', 0):,.0f}" if item.get('market_cap') else "",
                    "price": f"${item.get('current_price', 0)}" if item.get('current_price') else "",
                    "market_cap": f"${item.get('market_cap', 0):,.0f}" if item.get('market_cap') else "",
                    "volume_24h": f"${item.get('total_volume', 0):,.0f}" if item.get('total_volume') else "",
                    "status": "active",
                    "estimated_value": "",
                    "eligibility": "",
                    "farming_guide": "",
                    "tge_date": "",
                    "source": "coingecko",
                })
            print(f"[Collector] CoinGecko: {len(coins)} coins")
        else:
            print(f"[Collector] CoinGecko error: {resp.status_code}")
    except Exception as e:
        print(f"[Collector] CoinGecko failed: {e}")
    return coins


def fetch_defillama_protocols(limit: int = 30) -> list[dict]:
    protocols = []
    try:
        resp = requests.get(f"{DEFILLAMA_BASE}/protocols", timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            count = 0
            for item in data:
                if count >= limit:
                    break
                name = item.get("name", "")
                symbol = item.get("symbol", "") or name[:4].upper()
                protocols.append({
                    "id": item.get("id", ""),
                    "name": name,
                    "ticker": symbol,
                    "category": "defi",
                    "chain": (item.get("chain") or "Multi-chain").replace(",", ", "),
                    "description": item.get("description", "") or f"{name} is a DeFi protocol on {item.get('chain', 'multiple chains')} with TVL of ${item.get('tvl', 0):,.0f}.",
                    "price": "",
                    "market_cap": f"${item.get('tvl', 0):,.0f}" if item.get('tvl') else "",
                    "volume_24h": "",
                    "status": "active",
                    "estimated_value": "",
                    "eligibility": "",
                    "farming_guide": "",
                    "tge_date": "",
                    "source": "defillama",
                })
                count += 1
            print(f"[Collector] DefiLlama: {len(protocols)} protocols")
    except Exception as e:
        print(f"[Collector] DefiLlama failed: {e}")
    return protocols


def fetch_scraped_airdrops() -> list[dict]:
    if scrape_airdrops:
        try:
            scrape_airdrops()
        except Exception as e:
            print(f"[Collector] Airdrops scraper run failed: {e}")

    try:
        with open(AIRDROP_FILE, encoding="utf-8") as f:
            data = json.load(f)
        airdrops = data.get("airdrops", [])
        print(f"[Collector] Scraped airdrops: {len(airdrops)}")
        return airdrops
    except (FileNotFoundError, json.JSONDecodeError):
        print("[Collector] No airdrops_data.json found, using empty airdrop list")
        return []


def fetch_manual_projects() -> list[dict]:
    projects = [
        {"id": "uniswap", "name": "Uniswap", "ticker": "UNI", "category": "defi", "chain": "Ethereum", "description": "Leading DEX with AMM model. v4 introduces hooks for custom liquidity pools."},
        {"id": "aave", "name": "Aave", "ticker": "AAVE", "category": "defi", "chain": "Ethereum", "description": "Decentralized lending and borrowing protocol. Supports flash loans and credit delegation."},
        {"id": "makerdao", "name": "MakerDAO", "ticker": "MKR", "category": "defi", "chain": "Ethereum", "description": "DAO governing DAI stablecoin. Endgame plan underway for subDAO launch."},
        {"id": "compound", "name": "Compound", "ticker": "COMP", "category": "defi", "chain": "Ethereum", "description": "Algorithmic money market protocol for lending and borrowing."},
        {"id": "curve", "name": "Curve Finance", "ticker": "CRV", "category": "defi", "chain": "Ethereum", "description": "Stablecoin exchange DEX optimized for low-slippage stable swaps."},
        {"id": "lido", "name": "Lido DAO", "ticker": "LDO", "category": "defi", "chain": "Ethereum", "description": "Liquid staking solution for ETH, SOL, MATIC. stETH is leading LST."},
        {"id": "eigenlayer", "name": "EigenLayer", "ticker": "EIGEN", "category": "defi", "chain": "Ethereum", "description": "Restaking protocol securing AVS networks with re-staked ETH."},
        {"id": "pendle", "name": "Pendle", "ticker": "PENDLE", "category": "defi", "chain": "Ethereum", "description": "Yield tokenization protocol. Separates future yield into tradable PT/YT tokens."},
        {"id": "ethena", "name": "Ethena", "ticker": "ENA", "category": "defi", "chain": "Ethereum", "description": "Synthetic dollar protocol with 'Internet Bonds' via delta-neutral hedging."},
        {"id": "ondo", "name": "Ondo Finance", "ticker": "ONDO", "category": "defi", "chain": "Ethereum", "description": "Tokenized real-world assets and DeFi protocols bridging TradFi with crypto."},
        {"id": "chainlink", "name": "Chainlink", "ticker": "LINK", "category": "defi", "chain": "Ethereum", "description": "Leading oracle network providing tamper-proof data feeds to smart contracts."},
        {"id": "solana", "name": "Solana", "ticker": "SOL", "category": "l1", "chain": "Solana", "description": "High-performance L1 with Proof-of-History and parallel transaction processing."},
        {"id": "avalanche", "name": "Avalanche", "ticker": "AVAX", "category": "l1", "chain": "Avalanche", "description": "L1 platform with subnets for custom app-chain deployment."},
        {"id": "polygon", "name": "Polygon", "ticker": "POL", "category": "l2", "chain": "Ethereum", "description": "Aggregation layer for Ethereum scaling. zkEVM, CDK, and POS chain."},
        {"id": "arbitrum", "name": "Arbitrum", "ticker": "ARB", "category": "l2", "chain": "Ethereum", "description": "Optimistic rollup L2 with largest TVL. Orbit chain for custom L3s."},
        {"id": "optimism", "name": "Optimism", "ticker": "OP", "category": "l2", "chain": "Ethereum", "description": "Optimistic rollup L2 and Superchain ecosystem. OP Stack powers many L2s."},
        {"id": "base", "name": "Base", "ticker": "BASE", "category": "l2", "chain": "Ethereum", "description": "Coinbase-built L2 on OP Stack. Growing rapidly with Onchain Summer campaigns."},
        {"id": "celestia", "name": "Celestia", "ticker": "TIA", "category": "l1", "chain": "Celestia", "description": "Modular data availability network. First DA layer for rollups."},
        {"id": "near", "name": "NEAR Protocol", "ticker": "NEAR", "category": "l1", "chain": "NEAR", "description": "L1 with sharding, human-readable accounts, and Chain Signatures."},
        {"id": "cosmos", "name": "Cosmos", "ticker": "ATOM", "category": "l1", "chain": "Cosmos", "description": "IBC-enabled ecosystem of interconnected app-chains."},
        {"id": "polkadot", "name": "Polkadot", "ticker": "DOT", "category": "l1", "chain": "Polkadot", "description": "Multi-chain framework with shared security. Parachains for specialized app chains."},
        {"id": "bnbchain", "name": "BNB Chain", "ticker": "BNB", "category": "l1", "chain": "BNB Chain", "description": "EVM-compatible L1 with low fees. opBNB L2 and Greenfield for data."},
        {"id": "ton", "name": "TON", "ticker": "TON", "category": "l1", "chain": "TON", "description": "Telegram-integrated L1 with fast transactions and mini-app ecosystem."},
        {"id": "sei", "name": "Sei", "ticker": "SEI", "category": "l1", "chain": "Sei", "description": "Trading-focused L1 with parallel order execution and native order book."},
        {"id": "saga", "name": "Saga", "ticker": "SAGA", "category": "l1", "chain": "Saga", "description": "Infrastructure for launching dedicated app-chains (chainlets) with shared security."},
        {"id": "dymension", "name": "Dymension", "ticker": "DYM", "category": "l1", "chain": "Cosmos", "description": "Network of modular rollups (RollApps) using IBC for settlement."},
        {"id": "injective", "name": "Injective", "ticker": "INJ", "category": "l1", "chain": "Injective", "description": "DeFi L1 with native order book, derivatives, and cross-chain trading."},
        {"id": "kaspa", "name": "Kaspa", "ticker": "KAS", "category": "l1", "chain": "Kaspa", "description": "DAG-based PoW L1 with GHOSTDAG protocol. Sub-second block times."},
        {"id": "dogecoin", "name": "Dogecoin", "ticker": "DOGE", "category": "meme", "chain": "Dogecoin", "description": "Original meme coin with active community. Used for micro-tipping and payments."},
        {"id": "shibainu", "name": "Shiba Inu", "ticker": "SHIB", "category": "meme", "chain": "Ethereum", "description": "Ecosystem including Shibarium L2, LEASH, BONE, and ShibaSwap DEX."},
        {"id": "worldcoin", "name": "Worldcoin", "ticker": "WLD", "category": "coin", "chain": "Optimism", "description": "Digital identity project with World ID orb verification and universal basic income."},
    ]
    for p in projects:
        p.setdefault("price", "")
        p.setdefault("market_cap", "")
        p.setdefault("volume_24h", "")
        p.setdefault("status", "active")
        p.setdefault("estimated_value", "")
        p.setdefault("eligibility", "")
        p.setdefault("farming_guide", "")
        p.setdefault("tge_date", "")
        p.setdefault("source", "manual")
    print(f"[Collector] Manual projects: {len(projects)}")
    return projects


def needs_data_refresh() -> bool:
    try:
        with open(CRYPTO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        last = data.get("last_updated", "")
        if last:
            updated = datetime.fromisoformat(last)
            age = datetime.now(timezone.utc).astimezone() - updated
            if age.days < 2:
                print(f"[Collector] Data is {age.days}d old, skipping collection")
                return False
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        pass
    return True


def collect_all() -> list[dict]:
    if not needs_data_refresh():
        cached = load_cached()
        if cached:
            return cached

    all_projects = {}

    def add_projects(proj_list: list[dict]):
        for p in proj_list:
            pid = p.get("id", "")
            if pid and pid not in all_projects:
                all_projects[pid] = p

    add_projects(fetch_coingecko_top_coins(60))
    add_projects(fetch_defillama_protocols(30))
    add_projects(fetch_scraped_airdrops())
    add_projects(fetch_manual_projects())

    result = list(all_projects.values())
    print(f"[Collector] Total unique projects: {len(result)}")
    return result


def load_cached() -> list[dict]:
    try:
        with open(CRYPTO_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("projects", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save(data: list[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    output = {
        "last_updated": datetime.now(timezone.utc).astimezone().isoformat(),
        "total": len(data),
        "projects": data,
    }
    with open(CRYPTO_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[Collector] Saved {len(data)} projects to {CRYPTO_FILE}")


if __name__ == "__main__":
    data = collect_all()
    save(data)
