import os
import sys
import json
import re
import random
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_DIR = Path(__file__).resolve().parent
POSTS_DIR = REPO_DIR / "_posts"
POSTS_DIR.mkdir(exist_ok=True)

HIGH_CPC_KEYWORDS = [
    "insurance", "loan", "credit", "mortgage", "investing", "crypto",
    "refinance", "banking", "tax", "debt", "AI", "cybersecurity",
    "cloud computing", "VPN", "hosting", "SaaS", "SEO", "marketing",
    "lead generation", "small business", "startup", "health insurance",
    "weight loss", "fitness", "DUI", "bankruptcy", "personal injury",
    "online course", "certification", "remote work", "real estate",
    "artificial intelligence", "machine learning", "ChatGPT", "LLM", "robotics",
    "election", "president", "congress", "senate", "supreme court",
    "weather", "hurricane", "climate change", "tornado", "flood",
    "stock market", "forex", "trading", "dividend", "retirement",
    "GDP", "inflation", "recession", "interest rate", "federal reserve",
    "Bitcoin", "Ethereum", "blockchain", "NFT", "DeFi",
    "iPhone", "Android", "Windows", "gaming", "electric vehicle",
    "Samsung Galaxy", "Google Pixel", "OnePlus", "iPhone 16", "iPhone 17",
    "iOS update", "iOS 19", "Android 15", "Android 16",
    "smartphone", "foldable phone", "phone review", "5G phone",
    "iPad", "MacBook", "Apple Watch", "Samsung Watch",
    "tablet", "laptop", "processor", "Qualcomm", "Apple Silicon",
    "M4 chip", "Snapdragon", "solar", "renewable energy", "nuclear", "space", "NASA",
    "earthquake", "tsunami", "drought", "wildfire", "storm",
    "NASDAQ", "S&P 500", "Dow Jones", "IPO", "earnings",
    # Crypto
    "Bitcoin price", "Ethereum price", "Solana", "Ripple", "XRP",
    "cryptocurrency", "altcoin", "mining", "staking", "Web3",
    "Dogecoin", "Cardano", "Polygon", "Chainlink", "Litecoin",
    "crypto regulation", "SEC crypto", "Bitcoin ETF", "crypto market",
    "Binance", "Coinbase", "crypto wallet", "DeFi", "yield farming",
    "stocks", "crypto", "market", "trading", "investor",
    # Stocks
    "stock market today", "Nifty 50", "Sensex", "BSE", "NSE",
    "share market", "Indian stocks", "mutual funds", "SIP",
    "stock analysis", "tech stocks", "bank stocks", "FII", "DII",
    "options trading", "futures trading", "intraday", "swing trading",
    "value investing", "growth stocks", "REITs", "stock split",
    "NVDA", "AAPL", "TSLA", "AMZN", "MSFT", "GOOGL",
    # Sports
    "NFL", "NBA", "soccer", "cricket", "tennis", "F1", "UFC",
    "Olympics", "World Cup", "Super Bowl", "Champions League",
    "baseball", "hockey", "golf", "boxing", "wrestling",
    "football", "basketball", "Premier League", "IPL",
    # Entertainment
    "movies", "music", "TV shows", "streaming", "Netflix",
    "Hollywood", "Bollywood", "celebrity", "Oscars", "Grammy",
    "gaming", "video games", "PlayStation", "Xbox", "Nintendo",
    "PS5", "Xbox Series X", "Nintendo Switch", "PC gaming",
    "game review", "game release", "GTA", "Fortnite", "Call of Duty",
    "Minecraft", "Elden Ring", "game trailer", "gaming laptop",
    "gaming PC", "graphics card", "RTX", "Steam", "Epic Games",
    "anime", "comics", "Marvel", "DC", "Disney",
    "Spotify", "YouTube", "TikTok", "Instagram",
    # Health
    "COVID", "vaccine", "cancer", "diabetes", "heart disease",
    "mental health", "fitness", "nutrition", "yoga", "meditation",
    "sleep", "diet", "weight loss", "supplements",
    "pandemic", "medicine", "surgery", "therapy",
    # Science
    "NASA", "space", "Mars", "moon", "telescope", "quantum",
    "physics", "biology", "chemistry", "genetics", "evolution",
    "climate science", "ocean", "archaeology", "paleontology",
    "nuclear fusion", "particle physics", "dark matter",
    # World News
    "Ukraine", "Russia", "China", "Middle East", "Europe",
    "Asia", "Africa", "diplomacy", "sanctions", "military",
    "border", "refugee", "treaty", "NATO", "UN",
    "earthquake", "tsunami", "wildfire", "flood", "hurricane",
    "drought", "heatwave", "blizzard", "tornado", "volcano",
]

RSS_FEEDS = [
    # ── Google News (global + topic-specific) ──
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en",
    "https://news.google.com/rss/search?q=cryptocurrency+Bitcoin&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=stock+market+investing&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=artificial+intelligence+tech&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=politics+election&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=weather+climate&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=business+finance&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=sports+football+cricket&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=entertainment+movies+music&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=health+fitness+medical&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=science+space+research&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=gaming+esports&hl=en-US&gl=US&ceid=US:en",

    # ── BBC ──
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "https://feeds.bbci.co.uk/news/entertainment_arts/rss.xml",
    "https://feeds.bbci.co.uk/sport/rss.xml",
    "https://feeds.bbci.co.uk/news/health/rss.xml",

    # ── New York Times ──
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Arts.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",

    # ── Reuters ──
    "https://www.reutersagency.com/feed/",
    "https://www.reutersagency.com/feed/?best-topics=business-finance",
    "https://www.reutersagency.com/feed/?best-topics=tech",
    "https://www.reutersagency.com/feed/?best-topics=politics",
    "https://www.reutersagency.com/feed/?best-topics=health",
    "https://www.reutersagency.com/feed/?best-topics=lifestyle",

    # ── Associated Press ──
    "https://rsshub.app/apnews/topics/apf-topnews",
    "https://rsshub.app/apnews/topics/technology",
    "https://rsshub.app/apnews/topics/business",
    "https://rsshub.app/apnews/topics/politics",
    "https://rsshub.app/apnews/topics/science",
    "https://rsshub.app/apnews/topics/health",
    "https://rsshub.app/apnews/topics/sports",
    "https://rsshub.app/apnews/topics/entertainment",

    # ── NPR ──
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.npr.org/1014/rss.xml",
    "https://feeds.npr.org/1003/rss.xml",
    "https://feeds.npr.org/1007/rss.xml",
    "https://feeds.npr.org/1008/rss.xml",
    "https://feeds.npr.org/1019/rss.xml",

    # ── CNBC ──
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "https://www.cnbc.com/id/100727362/device/rss/rss.html",

    # ── Bloomberg ──
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.bloomberg.com/technology/news.rss",
    "https://feeds.bloomberg.com/politics/news.rss",

    # ── The Guardian ──
    "https://www.theguardian.com/world/rss",
    "https://www.theguardian.com/technology/rss",
    "https://www.theguardian.com/business/rss",
    "https://www.theguardian.com/politics/rss",
    "https://www.theguardian.com/sport/rss",
    "https://www.theguardian.com/culture/rss",
    "https://www.theguardian.com/science/rss",

    # ── Newsweek / Independent / Telegraph ──
    "https://www.newsweek.com/rss",
    "https://www.independent.co.uk/news/world/rss",
    "https://www.telegraph.co.uk/rss",
    "https://www.huffpost.com/section/front-page/feed",

    # ── Weather ──
    "https://rss.weather.com/weather/rss/news",
    "https://feeds.a.dj.com/rss/RSSWeather.xml",
    "https://www.accuweather.com/rss/news.rss",

    # ── Crypto ──
    "https://cointelegraph.com/rss",
    "https://coindesk.com/feed",
    "https://cryptonews.com/rss.xml",
    "https://cryptopotato.com/feed/",
    "https://www.newsbtc.com/feed/",
    "https://u.today/rss",
    "https://cryptobriefing.com/feed/",
    "https://www.reddit.com/r/CryptoCurrency/hot/.rss",
    "https://www.reddit.com/r/bitcoin/hot/.rss",
    "https://www.reddit.com/r/altcoin/hot/.rss",
    "https://www.reddit.com/r/ethereum/hot/.rss",
    "https://www.reddit.com/r/defi/hot/.rss",

    # ── Stocks & Markets ──
    "https://finance.yahoo.com/news/rss/index",
    "https://www.marketwatch.com/rss/news",
    "https://www.investing.com/rss/news.rss",
    "https://www.investing.com/rss/market_overview.rss",
    "https://seekingalpha.com/feed.xml",
    "https://www.fool.com/feed/",
    "https://www.barrons.com/feed/rss",
    "https://www.reddit.com/r/stocks/hot/.rss",
    "https://www.reddit.com/r/investing/hot/.rss",
    "https://www.reddit.com/r/wallstreetbets/hot/.rss",

    # ── India ──
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "https://www.ndtv.com/rss/all",
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://www.hindustantimes.com/feeds/rss/top-news/rssfeed.xml",
    "https://indianexpress.com/feed/",
    "https://www.business-standard.com/rss/latest.rss",
    "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://www.livemint.com/rss/latest",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://www.reddit.com/r/india/hot/.rss",

    # ── Tech ──
    "https://www.wired.com/feed/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/feed/",
    "https://techcrunch.com/feed/",
    "https://www.engadget.com/rss.xml",
    "https://www.zdnet.com/news/rss.xml",
    "https://www.cnet.com/rss/news/",
    "https://www.reddit.com/r/technology/hot/.rss",
    "https://www.reddit.com/r/artificial/hot/.rss",
    "https://www.reddit.com/r/MachineLearning/hot/.rss",
    "https://www.reddit.com/r/Futurology/hot/.rss",

    # ── Science & Space ──
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://www.space.com/feed",
    "https://www.nature.com/nature.rss",
    "https://www.scientificamerican.com/feed/",
    "https://www.newscientist.com/feed/home",
    "https://www.reddit.com/r/science/hot/.rss",
    "https://www.reddit.com/r/space/hot/.rss",

    # ── Sports ──
    "https://www.espn.com/espn/rss/news",
    "https://www.skysports.com/rss/12040",
    "https://www.skysports.com/rss/12041",
    "https://sports.yahoo.com/rss",
    "https://www.reddit.com/r/sports/hot/.rss",
    "https://www.reddit.com/r/nfl/hot/.rss",
    "https://www.reddit.com/r/nba/hot/.rss",
    "https://www.reddit.com/r/soccer/hot/.rss",
    "https://www.reddit.com/r/Cricket/hot/.rss",

    # ── Entertainment ──
    "https://variety.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://www.billboard.com/articles/rss",
    "https://www.rollingstone.com/feed/",
    "https://pitchfork.com/feed/feed-news/rss",
    "https://www.reddit.com/r/movies/hot/.rss",
    "https://www.reddit.com/r/television/hot/.rss",
    "https://www.reddit.com/r/Music/hot/.rss",
    "https://www.reddit.com/r/gaming/hot/.rss",
    "https://www.reddit.com/r/esports/hot/.rss",
    "https://www.reddit.com/r/GameDeals/hot/.rss",
    "https://www.reddit.com/r/truegaming/hot/.rss",

    # ── Gaming ──
    "https://www.ign.com/rss/articles/feed",
    "https://www.gamespot.com/feeds/news/",
    "https://www.pcgamer.com/rss/",
    "https://kotaku.com/rss",
    "https://www.eurogamer.net/feed",
    "https://www.videogameschronicle.com/feed/",
    "https://www.gamerevolution.com/feed",
    "https://www.destructoid.com/feed/",
    "https://www.nintendolife.com/feed/",
    "https://www.pushsquare.com/feed/",
    "https://www.gematsu.com/feed/",
    "https://www.rockpapershotgun.com/feed",
    "https://www.polygon.com/rss/index.xml",
    "https://www.reddit.com/r/PS5/hot/.rss",
    "https://www.reddit.com/r/XboxSeriesX/hot/.rss",
    "https://www.reddit.com/r/NintendoSwitch/hot/.rss",
    "https://www.reddit.com/r/pcgaming/hot/.rss",

    # ── Mobile / Android / iOS ──
    "https://www.androidauthority.com/feed/",
    "https://www.androidcentral.com/feed",
    "https://9to5google.com/feed/",
    "https://9to5mac.com/feed/",
    "https://www.gsmarena.com/rss-news-reviews.php",
    "https://www.phonearena.com/rss",
    "https://www.xda-developers.com/feed/",
    "https://www.reddit.com/r/Android/hot/.rss",
    "https://www.reddit.com/r/iphone/hot/.rss",
    "https://www.reddit.com/r/GooglePixel/hot/.rss",
    "https://www.reddit.com/r/samsung/hot/.rss",
    "https://www.reddit.com/r/oneplus/hot/.rss",
    "https://www.reddit.com/r/apple/hot/.rss",

    # ── Health ──
    "https://www.webmd.com/rss/all.xml",
    "https://www.medicalnewstoday.com/feed",
    "https://www.healthline.com/rss/all",
    "https://www.cdc.gov/rss/health.xml",
    "https://www.who.int/rss-feeds/news-english.xml",
    "https://www.reddit.com/r/health/hot/.rss",
    "https://www.reddit.com/r/Fitness/hot/.rss",

    # ── Business & Startups ──
    "https://www.inc.com/rss/",
    "https://www.forbes.com/entrepreneurs/feed/",
    "https://www.businessinsider.com/rss",
    "https://hbr.org/feed/latest",
    "https://www.reddit.com/r/startups/hot/.rss",
    "https://www.reddit.com/r/Entrepreneur/hot/.rss",
    "https://www.reddit.com/r/business/hot/.rss",
    "https://www.reddit.com/r/finance/hot/.rss",
    "https://www.reddit.com/r/Economics/hot/.rss",

    # ── Politics ──
    "https://www.reddit.com/r/politics/hot/.rss",
    "https://www.reddit.com/r/worldnews/hot/.rss",
    "https://www.reddit.com/r/geopolitics/hot/.rss",

    # ── Europe ──
    "https://www.dw.com/en/top-stories/rss",
    "https://www.euronews.com/rss",
    "https://www.france24.com/en/rss",

    # ── Asia Pacific ──
    "https://www.scmp.com/rss/this_just_in/feed.xml",
    "https://www.straitstimes.com/news/asia/rss.xml",
    "https://www.japantimes.co.jp/feed/",

    # ── Middle East / Africa ──
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.africanews.com/feed/",

    # ── Weather ──
    "https://www.reddit.com/r/weather/hot/.rss",
    "https://www.reddit.com/r/climate/hot/.rss",
    "https://www.reddit.com/r/ClimateCrisis/hot/.rss",
    "https://www.reddit.com/r/tropicalweather/hot/.rss",
]

OPENROUTER_MODELS = [
    "microsoft/phi-3-mini-128k-instruct",
    "meta-llama/llama-3-8b-instruct",
    "mistralai/mistral-7b-instruct",
    "google/gemma-2-9b-it",
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
]

NVIDIA_MODEL = "meta/llama-3.1-8b-instruct"

AD_SLOT_MARKER_START = "<!-- AD_TOP -->"
AD_SLOT_MARKER_MID = "<!-- AD_MID -->"
AD_SLOT_MARKER_END = "<!-- AD_BOTTOM -->"


def load_env_api_keys():
    keys = {}
    for i in range(1, 5):
        val = os.environ.get(f"OPENROUTER_API_KEY_{i}")
        if val:
            keys[f"openrouter_{i}"] = val
    nv = os.environ.get("NVIDIA_API_KEY_1")
    if nv:
        keys["nvidia_1"] = nv
    keys["unsplash"] = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    keys["newsapi"] = os.environ.get("NEWSAPI_KEY", "")
    return keys


def fetch_trends_rss():
    topics = []
    for url in RSS_FEEDS:
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                continue
            root = ElementTree.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"} if not root.tag.startswith("rss") else {}
            for item in root.iter("item"):
                title = item.findtext("title", "")
                desc = item.findtext("description", "")
                link = item.findtext("link", "")
                text = f"{title} {desc}"
                topics.append({"title": title, "text": text, "source": url, "link": link})
            if "feed" in root.tag.lower():
                for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                    title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                    link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                    link = link_el.attrib.get("href", "") if link_el is not None else ""
                    topics.append({"title": title, "text": title, "source": url, "link": link})
        except Exception as e:
            log.warning(f"RSS failed for {url}: {e}")
    return topics


def fetch_trends_google():
    results = []
    for geo in ["united_states"]:
        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl="en-US", tz=300, timeout=10)
            trending = pytrends.trending_searches(pn=geo)
            if not trending.empty:
                for title in trending[0].head(8).tolist():
                    results.append({"title": title, "text": title, "source": f"google_trends_{geo}", "link": ""})
        except Exception as e:
            log.warning(f"Google Trends ({geo}) failed: {e}")
            continue
    return results


def fetch_trends_newsapi(api_key):
    if not api_key:
        return []
    results = []
    topics = ["AI", "politics", "weather", "stock market", "technology", "climate",
               "cryptocurrency", "Bitcoin", "stocks", "sports", "entertainment",
               "movies", "music", "health", "fitness", "science", "space",
               "gaming", "business", "startup", "IPO", "cricket", "soccer",
               "iPhone", "Android", "smartphone", "video games", "PlayStation"]
    for topic in topics:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={"q": topic, "pageSize": 5, "language": "en", "sortBy": "popularity", "apiKey": api_key},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                for article in data.get("articles", []):
                    title = article.get("title", "")
                    desc = article.get("description", "") or ""
                    text = f"{title} {desc}"
                    results.append({"title": title, "text": text, "source": f"newsapi/{topic}", "link": article.get("url", "")})
        except Exception as e:
            log.warning(f"NewsAPI {topic} failed: {e}")
            continue
    return results


def score_topic(topic):
    title_lower = topic["title"].lower()
    full_text = topic["text"].lower()
    score = 0
    matched = []
    for kw in HIGH_CPC_KEYWORDS:
        if kw.lower() in title_lower:
            score += 20
            matched.append(kw)
        elif kw.lower() in full_text:
            score += 5
            matched.append(kw)
    words = full_text.split()
    if len(words) > 10:
        score += 5
    if any(c.isdigit() for c in full_text):
        score += 3
    return score, matched


def pick_best_topic(candidates):
    scored = []
    for c in candidates:
        s, matched = score_topic(c)
        if s > 0:
            scored.append((s, c, matched))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored:
        best = scored[0]
        log.info(f"Best topic: {best[1]['title']} (score={best[0]}, keywords={best[2]})")
        return best[1], best[2]
    if candidates:
        log.info(f"No high-CPC match, using first topic: {candidates[0]['title']}")
        return candidates[0], []
    return None, []


def get_existing_titles():
    titles = set()
    for f in POSTS_DIR.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            m = re.search(r'title:\s*["\']?(.+?)["\']?\n', content)
            if m:
                titles.add(m.group(1).strip().lower())
        except Exception:
            pass
    return titles


def is_duplicate(title, existing):
    t = title.lower().strip()
    if t in existing:
        return True
    t_clean = re.sub(r'[^a-z0-9\s]', '', t)
    for e in existing:
        e_clean = re.sub(r'[^a-z0-9\s]', '', e)
        if t_clean == e_clean:
            return True
    return False


def call_openrouter(api_key, prompt, model=None):
    if not model:
        model = random.choice(OPENROUTER_MODELS)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional content writer. Write well-researched, engaging articles in natural English. Vary sentence structure. Use a professional but accessible tone."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 8192,
        "top_p": 0.95,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=300,
    )
    if resp.status_code != 200:
        raise Exception(f"OpenRouter error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"]


def call_nvidia(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional content writer. Write well-researched, engaging articles in natural English."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 8192,
        "top_p": 0.95,
    }
    resp = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=300,
    )
    if resp.status_code != 200:
        raise Exception(f"NVIDIA error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"]


def generate_article(topic, keywords, api_keys):
    kw_str = ", ".join(keywords[:5]) if keywords else topic["title"]
    prompt = f"""Write a comprehensive, well-researched article about the following topic.

Topic: {topic['title']}
Source reference: {topic.get('link', '')}

CRITICAL: Write strictly about the TOPIC above, not about the keywords.
Naturally include these keywords where relevant: {kw_str}

Requirements:
- Write at least 1200 words
- Use a natural, engaging, professional tone
- Vary sentence length and structure
- Include specific examples, data points, or statistics where relevant
- Structure with clear H2 and H3 subheadings
- Include a FAQ section with at least 4 questions and answers at the end
- Write in markdown format
- Start with a compelling introduction paragraph
- End with a conclusion paragraph
- Do NOT include any meta-commentary or notes about the writing process
- Write directly as if you are an expert in this field

Return only the article content in markdown format with no additional commentary."""

    errors = []
    for i in range(1, 5):
        key = api_keys.get(f"openrouter_{i}")
        if not key:
            continue
        try:
            log.info(f"Trying OpenRouter key {i}...")
            content = call_openrouter(key, prompt)
            if len(content) > 500:
                return content
            errors.append(f"OpenRouter key {i}: content too short ({len(content)} chars)")
        except Exception as e:
            errors.append(f"OpenRouter key {i}: {e}")
            continue

    nv_key = api_keys.get("nvidia_1")
    if nv_key:
        try:
            log.info("Trying NVIDIA...")
            content = call_nvidia(nv_key, prompt)
            if len(content) > 500:
                return content
            errors.append(f"NVIDIA: content too short ({len(content)} chars)")
        except Exception as e:
            errors.append(f"NVIDIA: {e}")

    raise Exception(f"All LLM APIs failed: {'; '.join(errors)}")


def fetch_image(query, api_key, used_urls=None):
    if not api_key:
        log.warning("No Unsplash API key")
        return ""
    if used_urls is None:
        used_urls = set()
    try:
        page = random.randint(1, 10)
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 5, "page": page, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {api_key}"},
            timeout=15,
        )
        if resp.status_code != 200:
            log.warning(f"Unsplash HTTP {resp.status_code}: {resp.text[:100]}")
            return ""
        data = resp.json()
        if data.get("results"):
            for img in data["results"]:
                url = img["urls"]["regular"]
                if url not in used_urls:
                    used_urls.add(url)
                    return f"{url}?w=1200"
            fallback = data["results"][0]
            url = fallback["urls"]["regular"]
            return f"{url}?w=1200"
        log.warning(f"Unsplash: no results for '{query[:50]}'")
        return ""
    except Exception as e:
        log.warning(f"Unsplash failed: {e}")
        return ""


def slugify(title):
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    s = s[:80].strip('-')
    return s


def build_post(content, topic, keywords, image_url, existing_titles):
    title = topic["title"]
    if len(title) > 100:
        title = title[:97] + "..."

    if is_duplicate(title, existing_titles):
        log.warning(f"Duplicate title: {title}")
        return None

    slug = slugify(title)
    date = datetime.utcnow()
    filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
    filepath = POSTS_DIR / filename

    excerpt = content[:300].replace("\n", " ").strip()
    excerpt = re.sub(r'^#+\s*', '', excerpt)
    excerpt = re.sub(r'\s+', ' ', excerpt).strip()
    excerpt = excerpt[:150] + "..." if len(excerpt) > 150 else excerpt

    kw_tags = ", ".join(keywords[:5]) if keywords else topic["title"].lower().replace(" ", ", ")
    tag_list = re.sub(r'[^\w,\s]', '', kw_tags).strip().lower()

    image_line = f'image: "{image_url}"\n' if image_url else ""
    frontmatter = f"""---
title: "{title}"
date: {date.strftime('%Y-%m-%d %H:%M:%S')}
excerpt: "{excerpt}"
{image_line}tags: [{tag_list}]
categories: [{tag_list}]
---

"""

    content_clean = re.sub(r'^```markdown\s*', '', content)
    content_clean = re.sub(r'^```\s*$', '', content_clean, flags=re.MULTILINE)
    content_clean = re.sub(r'^---.*?---\s*', '', content_clean, flags=re.DOTALL)
    # Remove the first h1 heading since we render title from front matter
    content_clean = re.sub(r'^#\s+.+?\n=+\s*\n*', '', content_clean, count=1)
    content_clean = re.sub(r'^#\s+.+?\n', '', content_clean, count=1)

    final_content = frontmatter + content_clean.strip()
    filepath.write_text(final_content, encoding="utf-8")
    log.info(f"Post saved: {filepath.name}")
    return filepath


def git_commit_push(filepath):
    try:
        import subprocess
        repo_dir = str(REPO_DIR)
        subprocess.run(["git", "config", "user.name", "AutoPublisher"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bot@yoursite.com"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "pull", "--rebase"], cwd=repo_dir, capture_output=True)
        r = subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True)
        if r.returncode != 0:
            log.error(f"git add failed: {r.stderr.decode()}")
            return False
        r = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_dir, capture_output=True,
        )
        if r.returncode == 0:
            log.info("No changes to commit")
            return True
        r = subprocess.run(
            ["git", "commit", "-m", f"Auto: {filepath.name.replace('.md', '').replace('-', ' ')[11:]}"],
            cwd=repo_dir, capture_output=True,
        )
        if r.returncode != 0:
            log.error(f"git commit failed: {r.stderr.decode()}")
            return False
        r = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True)
        if r.returncode != 0:
            log.error(f"git push failed: {r.stderr.decode()}")
            return False
        log.info("Pushed to GitHub successfully")
        return True
    except Exception as e:
        log.error(f"Git operation failed: {e}")
        return False


def main():
    log.info("=" * 50)
    log.info("Starting daily content generation")
    log.info("=" * 50)

    api_keys = load_env_api_keys()
    key_count = sum(1 for k in api_keys if k.startswith("openrouter") or k.startswith("nvidia"))
    log.info(f"LLM API keys loaded: {key_count}")

    log.info("Fetching trends...")
    all_candidates = []

    trends_rss = fetch_trends_rss()
    log.info(f"RSS feeds returned: {len(trends_rss)} items")
    all_candidates.extend(trends_rss)

    trends_google = fetch_trends_google()
    log.info(f"Google Trends returned: {len(trends_google)} items")
    all_candidates.extend(trends_google)

    trends_news = fetch_trends_newsapi(api_keys.get("newsapi", ""))
    log.info(f"NewsAPI returned: {len(trends_news)} items")
    all_candidates.extend(trends_news)

    if not all_candidates:
        log.error("No trends found from any source")
        sys.exit(1)

    topic, keywords = pick_best_topic(all_candidates)
    if not topic:
        log.error("No suitable topic found")
        sys.exit(1)

    existing_titles = get_existing_titles()
    log.info(f"Existing posts: {len(existing_titles)}")

    if is_duplicate(topic["title"], existing_titles):
        log.info(f"Topic already covered: {topic['title']}")
        candidates_no_dup = [c for c in all_candidates if not is_duplicate(c["title"], existing_titles)]
        if candidates_no_dup:
            topic, keywords = pick_best_topic(candidates_no_dup)
            if not topic:
                log.error("No non-duplicate topic found")
                sys.exit(1)
        else:
            log.error("All topics already covered")
            sys.exit(0)

    log.info(f"Generating article for: {topic['title']}")
    try:
        article = generate_article(topic, keywords, api_keys)
    except Exception as e:
        log.error(f"Article generation failed: {e}")
        sys.exit(1)

    log.info(f"Article generated: {len(article)} characters")

    used_images = set()
    for old_post in POSTS_DIR.glob("*.md"):
        try:
            content = old_post.read_text(encoding="utf-8")
            m = re.search(r'image:\s*"(.+?)"', content)
            if m:
                used_images.add(m.group(1))
        except Exception:
            pass

    image_keywords = keywords[:3] if keywords else topic["title"].split()[:5]
    image_queries = [
        " ".join(image_keywords),
        topic["title"],
    ]
    image_url = ""
    for q in image_queries:
        image_url = fetch_image(q, api_keys.get("unsplash", ""), used_images)
        if image_url:
            break

    if not image_url:
        fallback_pool = [
            "business", "technology", "finance", "office", "success",
            "nature", "city", "global", "digital", "future",
            "data", "network", "innovation", "growth", "strategy",
        ]
        random.shuffle(fallback_pool)
        for q in fallback_pool[:5]:
            image_url = fetch_image(q, api_keys.get("unsplash", ""), used_images)
            if image_url:
                break

    post_file = build_post(article, topic, keywords, image_url, existing_titles)
    if not post_file:
        sys.exit(0)

    success = git_commit_push(post_file)
    if success:
        log.info("Done! Article published successfully.")
    else:
        log.error("Article saved locally but git push failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
