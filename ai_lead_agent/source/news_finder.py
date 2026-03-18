"""
╔══════════════════════════════════════════════════════════════════╗
║   RWAtify Lead Agent — Signal Finder                            ║
║   Searches the ENTIRE Google internet via Serper.dev            ║
║   Uses 80+ precision queries to find RE tokenization leads      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import requests
import time
import random
import re
import json
import urllib.parse
import os
import sys

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Fix import path so config is found from any working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from config.rwatify_config import (
    SEARCH_QUERIES,
    COMPETITOR_NAMES,
    KNOWN_LEADS,
    SKIP_DOMAINS,
    REAL_ESTATE_KEYWORDS,
    PHASE1_KEYWORDS,
    PHASE2_KEYWORDS,
    HARD_DISQUALIFIERS,
)

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


# ─────────────────────────────────────────────
#  QUICK PRE-FILTER — saves Claude API cost
#  Only passes articles that have BOTH:
#    Layer A = real estate entity keyword
#    Layer B = tokenization / capital signal
# ─────────────────────────────────────────────

def quick_filter(title: str, snippet: str, body: str = "") -> str:
    """
    Returns: 'phase1' | 'phase2' | 'competitor' | 'reject'
    Run before calling Claude to avoid wasting API credits.
    """
    txt = (title + " " + snippet + " " + body[:1500]).lower()

    # Hard disqualifiers — reject immediately
    if any(k in txt for k in HARD_DISQUALIFIERS):
        return "reject"

    # Known real estate leads — always worth checking
    if any(lead in txt for lead in KNOWN_LEADS):
        if any(k in txt for k in PHASE1_KEYWORDS):
            return "phase1"
        if any(k in txt for k in PHASE2_KEYWORDS):
            return "phase2"
        return "phase2"  # known lead company with any mention = worth Claude review

    # Competitor vendor detection
    # Only flag as competitor if vendor appears in title OR 3+ times in body
    # AND no known real estate lead is also mentioned
    for c in COMPETITOR_NAMES:
        in_title = c in title.lower()
        count_in_body = txt.count(c)
        if (in_title or count_in_body >= 3):
            if not any(lead in txt for lead in KNOWN_LEADS):
                return "competitor"

    # Must have real estate layer A keyword
    if not any(w in txt for w in REAL_ESTATE_KEYWORDS):
        return "reject"

    # Check intent layers
    if any(k in txt for k in PHASE1_KEYWORDS):
        return "phase1"
    if any(k in txt for k in PHASE2_KEYWORDS):
        return "phase2"

    return "reject"


# ─────────────────────────────────────────────
#  GOOGLE SEARCH VIA SERPER.DEV
#  Searches the entire internet (not limited sites)
# ─────────────────────────────────────────────

def google_search(query: str, num_results: int = 10) -> list:
    """
    Search Google via Serper.dev API.
    Each call uses 1 Serper credit (2,500 free).
    Returns list of {title, url, snippet, source}
    """
    if not SERPER_API_KEY:
        print("  ❌ SERPER_API_KEY not set in .env file!")
        return []

    try:
        time.sleep(random.uniform(0.3, 0.8))
        r = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY":    SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "q":   query,
                "num": num_results,
                "gl":  "us",       # search as US (most comprehensive index)
                "hl":  "en",       # English results
                "tbs": "qdr:w1",   # Last week (7 days) for catch-up run
            },
            timeout=15,
        )

        if r.status_code == 429:
            print("  ⚠️  Rate limit hit — waiting 15 seconds...")
            time.sleep(15)
            return []
        if r.status_code == 403:
            print("  ❌ Serper API key invalid or quota exhausted.")
            return []

        r.raise_for_status()
        data = r.json()
        organic = data.get("organic", [])
        results = []

        for item in organic:
            url     = item.get("link", "")
            title   = item.get("title", "")
            snippet = item.get("snippet", "")
            source  = urllib.parse.urlparse(url).netloc.replace("www.", "")

            # Skip pure crypto noise sites
            if any(s in source for s in SKIP_DOMAINS):
                continue
            if len(title) > 10:
                results.append({
                    "title":   title,
                    "url":     url,
                    "snippet": snippet,
                    "source":  source,
                })

        return results

    except Exception as e:
        print(f"  ⚠️  Serper error: {str(e)[:80]}")
        return []


# ─────────────────────────────────────────────
#  FETCH FULL ARTICLE TEXT
# ─────────────────────────────────────────────

def fetch_article(url: str) -> tuple:
    """
    Fetch full article text and publish date from a URL.
    Returns: (article_text: str, date: str)
    """
    if not url or not url.startswith("http"):
        return "", ""

    try:
        time.sleep(random.uniform(0.8, 1.8))
        r = requests.get(
            url,
            headers={
                "User-Agent":      random.choice(UA_POOL),
                "Accept":          "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            },
            timeout=14,
            allow_redirects=True,
        )

        if r.status_code in [403, 404, 429, 451, 503]:
            return "", ""
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")

        # Remove noise elements
        for tag in soup(["nav", "footer", "script", "style", "aside",
                          "header", "form", "button", "noscript", "iframe"]):
            tag.decompose()

        # Extract publish date
        date = ""
        for meta in soup.find_all("meta"):
            prop = (meta.get("property", "") + meta.get("name", "")).lower()
            if any(x in prop for x in ["publish", "article:published", "date", "created"]):
                m = re.search(r'\d{4}-\d{2}-\d{2}', meta.get("content", ""))
                if m:
                    date = m.group(0)
                    break
        if not date:
            for t in soup.find_all("time", attrs={"datetime": True}):
                m = re.search(r'\d{4}-\d{2}-\d{2}', t["datetime"])
                if m:
                    date = m.group(0)
                    break
        if not date:
            for s in soup.find_all("script", {"type": "application/ld+json"}):
                try:
                    d = json.loads(s.string or "{}")
                    for k in ["datePublished", "dateModified"]:
                        if k in d:
                            m = re.search(r'\d{4}-\d{2}-\d{2}', str(d[k]))
                            if m:
                                date = m.group(0)
                                break
                except Exception:
                    pass

        # Extract article body
        body = (
            soup.find("article") or
            soup.find("div", class_=re.compile(
                r"article[-_]?body|content[-_]?body|post[-_]?content|"
                r"entry[-_]?content|story[-_]?body|article[-_]?text", re.I)) or
            soup.find("main")
        )
        text = body.get_text(" ", strip=True) if body else soup.get_text(" ", strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:5000], date

    except Exception:
        return "", ""


# ─────────────────────────────────────────────
#  DEDUPLICATE BY URL
# ─────────────────────────────────────────────

def remove_duplicates(articles: list) -> list:
    """Remove duplicate articles by URL."""
    seen = set()
    unique = []
    for art in articles:
        url = art.get("url", "")[:100]
        if url and url not in seen:
            seen.add(url)
            unique.append(art)
    return unique


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT — called by LangGraph node
# ─────────────────────────────────────────────

def monitor_signals() -> list:
    """
    Run all 80+ Google searches via Serper.dev.
    Pre-filter results with quick_filter.
    Return unique articles ready for Claude qualification.

    Each article dict contains:
      title, url, snippet, source, query, full_text, date, quick_label
    """
    all_articles = []
    total_queries = len(SEARCH_QUERIES)

    print(f"\n{'═'*65}")
    print(f"  RWAtify Lead Agent — Serper.dev Google Search")
    print(f"  Running {total_queries} queries across the entire internet")
    print(f"  Serper credits this run: {total_queries}")
    print(f"{'═'*65}\n")

    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i:2d}/{total_queries}] {query[:65]}", end="  ")
        results = google_search(query, num_results=10)

        relevant = []
        for r in results:
            label = quick_filter(r["title"], r["snippet"])
            if label != "reject":
                r["query"]       = query
                r["quick_label"] = label
                r["full_text"]   = ""
                r["date"]        = ""
                relevant.append(r)

        print(f"→ {len(relevant)} relevant / {len(results)} total")
        all_articles.extend(relevant)

    # Deduplicate
    unique = remove_duplicates(all_articles)
    print(f"\n  ✅ {len(unique)} unique articles to qualify with Claude\n")

    # Fetch full text for each (helps Claude make better decisions)
    print("  📄 Fetching full article text...")
    for j, art in enumerate(unique, 1):
        url = art.get("url", "")
        if url.startswith("http"):
            full_text, date = fetch_article(url)
            if full_text:
                art["full_text"] = full_text
            if date:
                art["date"] = date
        if j % 10 == 0:
            print(f"  ... fetched {j}/{len(unique)}")

    print(f"  ✅ Full text fetched for {sum(1 for a in unique if a.get('full_text'))} articles\n")
    return unique