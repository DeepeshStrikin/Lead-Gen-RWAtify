"""
╔══════════════════════════════════════════════════════════════════╗
║   RWAtify Lead Agent — Contact Finder v2                        ║
║   Uses Serper.dev (Google) to find real linkedin.com/in/ URLs   ║
║   DuckDuckGo kept as fallback only                              ║
╚══════════════════════════════════════════════════════════════════╝
"""

import re
import os
import sys
import time
import random
import requests
import urllib.parse

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from dotenv import load_dotenv
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

from config.rwatify_config import TARGET_TITLES

BLOCKED_DOMAINS = [
    "wikipedia.org", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "crunchbase.com", "bloomberg.com",
    "glassdoor.com", "indeed.com", "ziprecruiter.com",
]


# ═══════════════════════════════════════════════════════════
#  LINKEDIN URL BUILDERS (search links — used as fallback)
# ═══════════════════════════════════════════════════════════

def li_company_search(company: str) -> str:
    """LinkedIn company search URL."""
    if not company:
        return ""
    return (
        "https://www.linkedin.com/search/results/companies/?keywords="
        + urllib.parse.quote(company)
    )


def li_person_search(name: str, company: str) -> str:
    """LinkedIn people search URL for a specific person + company."""
    query = f"{name} {company}" if name and company else (name or company or "")
    if not query.strip():
        return ""
    return (
        "https://www.linkedin.com/search/results/people/?keywords="
        + urllib.parse.quote(query.strip())
    )


# ═══════════════════════════════════════════════════════════
#  NAME CLEANER
# ═══════════════════════════════════════════════════════════

def clean_name(title: str) -> str:
    """Extract person name from a LinkedIn result title string."""
    name = title.split(" - ")[0].strip()
    name = name.replace("| LinkedIn", "").replace("LinkedIn", "").strip()
    name = re.sub(r"[^\w\s\-\']", "", name).strip()
    return name


# ═══════════════════════════════════════════════════════════
#  SERPER LINKEDIN PROFILE SEARCH (PRIMARY)
#  Uses Google site: search to find real linkedin.com/in/ URLs
# ═══════════════════════════════════════════════════════════

def serper_linkedin_search(company: str, role: str) -> list:
    """
    Search Google via Serper for a specific role at a company on LinkedIn.
    Returns list of dicts with 'url', 'title', 'snippet'.
    These are REAL linkedin.com/in/ profile URLs from Google index.
    """
    if not SERPER_API_KEY:
        return []

    queries = [
        f'site:linkedin.com/in "{company}" "{role}"',
        f'site:linkedin.com/in {company} {role} real estate',
    ]

    found = []
    for query in queries:
        try:
            time.sleep(random.uniform(0.3, 0.7))
            r = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": SERPER_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": 5, "gl": "us", "hl": "en"},
                timeout=12,
            )
            if r.status_code != 200:
                continue

            for item in r.json().get("organic", []):
                url     = item.get("link", "")
                title   = item.get("title", "")
                snippet = item.get("snippet", "")
                if "linkedin.com/in/" in url and title:
                    found.append({"url": url, "title": title, "snippet": snippet})

            if found:
                break   # stop after first successful query

        except Exception:
            continue

    return found


# ═══════════════════════════════════════════════════════════
#  DDGS LINKEDIN SEARCH (FALLBACK)
# ═══════════════════════════════════════════════════════════

def ddgs_linkedin_search(company: str, role: str) -> list:
    """DuckDuckGo fallback for LinkedIn profile search."""
    if not DDGS:
        return []
    queries = [
        f'site:linkedin.com/in "{company}" "{role}"',
        f'site:linkedin.com/in {company} {role} real estate',
    ]
    results = []
    try:
        with DDGS() as ddgs:
            for query in queries:
                found = list(ddgs.text(query, max_results=5))
                results.extend(found)
                if results:
                    break
    except Exception:
        pass
    # Normalise to same format as serper results
    return [{"url": r.get("href", ""), "title": r.get("title", ""), "snippet": r.get("body", "")} for r in results]


# ═══════════════════════════════════════════════════════════
#  FIND COMPANY WEBSITE
# ═══════════════════════════════════════════════════════════

def find_company_website(company: str) -> str:
    """Find official company website using Serper (Google), DDGS as fallback."""
    if not company:
        return ""

    queries = [
        f'"{company}" official website real estate',
        f'{company} real estate developer official site',
    ]

    # Try Serper first
    if SERPER_API_KEY:
        for query in queries:
            try:
                time.sleep(random.uniform(0.3, 0.6))
                r = requests.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
                    json={"q": query, "num": 5},
                    timeout=12,
                )
                if r.status_code == 200:
                    for item in r.json().get("organic", []):
                        url = item.get("link", "")
                        if url and not any(d in url for d in BLOCKED_DOMAINS + ["linkedin.com"]):
                            return url
            except Exception:
                continue

    # DDGS fallback
    if DDGS:
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = list(ddgs.text(query, max_results=5))
                    for r in results:
                        url = r.get("href", "")
                        if url and not any(d in url for d in BLOCKED_DOMAINS + ["linkedin.com"]):
                            return url
        except Exception:
            pass

    return ""


# ═══════════════════════════════════════════════════════════
#  MAIN CONTACT FINDER
# ═══════════════════════════════════════════════════════════

def find_linkedin_contact(company: str) -> dict:
    """
    Find the best decision maker LinkedIn profile for this company.
    Uses Serper (Google site: search) as primary, DDGS as fallback.
    Returns direct linkedin.com/in/ profile URL whenever possible.
    """
    print(f"\n  🔎 Searching decision maker for: {company}")

    website = find_company_website(company)

    roles = [
        "Founder",
        "Co-Founder",
        "Managing Partner",
        "General Partner",
        "Managing Director",
        "Chief Investment Officer",
        "Head of Investments",
        "Fund Director",
        "Principal",
        "Chief Executive Officer",
        "CEO",
        "Head of Capital Markets",
        "Chief Financial Officer",
        "Head of Real Estate",
    ]

    # Build short keywords from the company name for snippet matching
    # e.g. "DAMAC Properties" → ["damac", "properties"]
    co_keywords = [w.lower() for w in company.split() if len(w) > 2]

    for role in roles:
        # Try Serper first (Google), then DDGS
        results = serper_linkedin_search(company, role)
        if not results:
            results = ddgs_linkedin_search(company, role)

        for r in results:
            url     = r.get("url", "")
            title   = r.get("title", "")
            snippet = r.get("snippet", "")

            if not url or "linkedin.com/in/" not in url:
                continue

            name = clean_name(title)

            # Must look like a real person (at least 2 words)
            if len(name.split()) < 2:
                continue

            skip_words = ["linkedin", "profile", "view", "connect", "member", "jobs"]
            if any(w in name.lower() for w in skip_words):
                continue

            # ── KEY VALIDATION ──────────────────────────────────────
            # Confirm the company name appears in the Google snippet.
            # Snippet is like: "Hussain Sajwani · Founder & CEO at DAMAC Properties"
            # If company keyword NOT in snippet or title → wrong person → skip.
            combined = (title + " " + snippet).lower()
            if co_keywords and not any(kw in combined for kw in co_keywords):
                print(f"  ⚠️  Skipping '{name}' — company name not found in their profile snippet")
                continue
            # ────────────────────────────────────────────────────────

            print(f"  ✅ Found: {name} ({role}) — {url}")

            return {
                "name":             name,
                "title":            role,
                "linkedin":         url,              # ← REAL linkedin.com/in/ URL
                "linkedin_search":  li_person_search(name, company),
                "company_linkedin": li_company_search(company),
                "website":          website,
            }

    # No specific person found — fallback to company-level links
    print(f"  ⚠️  No decision maker found for {company} — using company search links")

    return {
        "name":             "",
        "title":            "",
        "linkedin":         "",
        "linkedin_search":  li_company_search(company),
        "company_linkedin": li_company_search(company),
        "website":          website,
    }