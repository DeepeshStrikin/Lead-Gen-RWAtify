"""
╔══════════════════════════════════════════════════════════════════╗
║   RWAtify Lead Agent — AI Lead Qualifier                        ║
║   Uses Claude (Anthropic) with the RWAtify Master Prompt        ║
║   Detects competitors, qualifies leads, assigns phase tags      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import json
import time
import random
import requests
from typing import Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from config.rwatify_config import COMPETITOR_NAMES, KNOWN_LEADS

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# ─────────────────────────────────────────────
#  OUTPUT SCHEMA — full RWAtify required fields
# ─────────────────────────────────────────────

class IntentSchema(BaseModel):
    """RWAtify lead qualification result."""

    # Core qualification flags
    is_valid_lead:  bool = Field(description="True if company is a real estate buyer (not a vendor)")
    is_competitor:  bool = Field(description="True if company SELLS tokenization infrastructure")
    reject_reason:  str  = Field(default="", description="Why rejected — empty if valid lead")

    # Lead identity
    company_name:    str = Field(description="Exact name of main real estate company discussed")
    company_type:    str = Field(description="Real Estate Developer | Fund / Investment Manager | Family Office | PropTech | Asset Operator | Real Estate Crowdfunding | Other")
    country:         str = Field(default="", description="Country where company is based")
    city:            str = Field(default="", description="City where company is based")
    company_website: str = Field(default="", description="Company website URL if found in article")

    # Decision maker
    decision_maker_name:  str = Field(default="", description="Full name of exec quoted or mentioned")
    decision_maker_title: str = Field(default="", description="Exact title of that exec")
    exact_quote:          str = Field(default="", description="Their actual quoted words about tokenization/digital assets")

    # RWAtify qualification
    signal_type: str = Field(default="", description="e.g. tokenization intent, fractional ownership, digital securities, capital raise")
    fit_tag:     str = Field(default="", description="Strong RWAtify Fit | Potential RWAtify Fit")
    why_rwatify: str = Field(default="", description="One specific sentence why RWAtify fits this company's actual situation")
    digital_ready: bool = Field(default=False, description="True if company publicly mentions tokenization, digital securities, blockchain, or on-chain investment")

    # Phase
    phase_tag:       str = Field(description="Phase 1 — Contact Now | Phase 2 — Nurture | Competitor | Reject")
    article_summary: str = Field(default="", description="Two sentences: what company announced and what the RWAtify signal is")

    # Legacy urgency field for compatibility
    intent:   str = Field(default="NO", description="YES | NO | MAYBE — for routing")
    urgency:  int = Field(default=0, ge=0, le=10, description="Priority 0-10")
    signal_summary: str = Field(default="", description="Short summary of signal")


# ─────────────────────────────────────────────
#  RWATIFY MASTER PROMPT
# ─────────────────────────────────────────────

MASTER_PROMPT = """You are a lead qualification agent for RWAtify — a build-to-own real estate capital & investor infrastructure platform.

RWAtify is for real estate developers, fund managers and portfolio operators who want to OWN their investor infrastructure (cap tables, SPVs, distributions, reporting, onboarding) — not rent SaaS tools.

═══════════════════════════════════════════════════════
STEP 1 — IDENTIFY THE MAIN COMPANY IN THE ARTICLE
═══════════════════════════════════════════════════════
Read the article and identify the ONE main company being discussed.
Ask: What does this company's PRIMARY BUSINESS do?

═══════════════════════════════════════════════════════
STEP 2 — IS IT A COMPETITOR OR A LEAD?
═══════════════════════════════════════════════════════

A COMPETITOR = a company whose product IS the tokenization platform itself.
They SELL the infrastructure. Do NOT target them.

COMPETITORS (is_competitor: true, is_valid_lead: false):
DigiShares, Tokeny, Securitize, Polymath, Smartlands, Zoniqx,
tZERO, Blocksquare, Brickken, MultiBank.io, PRYPCO, PRYPCO Mint,
DDX Global, Inovartic, Tokenscope, ForteXchain, Ctrl Alt, Fasset,
Binaryx, Stobox, MANTRA (blockchain), Mavryk, DigiFT, Harbor,
any company whose main product is: "tokenization platform", "STO platform",
"digital securities issuance", "RWA protocol", "tokenization-as-a-service"

A LEAD = a company that OWNS or DEVELOPS real estate or runs funds/SPVs.
They are BUYERS. These are RWAtify targets.

ALWAYS LEADS (is_valid_lead: true, is_competitor: false):
Any real estate developer, real estate fund, family office, proptech
investment platform, REIT, real estate crowdfunding platform, or asset operator.

CRITICAL RULE:
If a real estate developer (e.g. DAMAC) is using a competitor tool (e.g. MANTRA) —
THE DEVELOPER IS STILL A LEAD. They currently rent tools. RWAtify gives them ownership.
company_name = DAMAC, is_valid_lead = true, is_competitor = false.

═══════════════════════════════════════════════════════
STEP 3 — DOES THE COMPANY QUALIFY AS A RWATIFY BUYER?
═══════════════════════════════════════════════════════

A company qualifies if it shows at least ONE of:
• Multiple active/completed real estate projects
• Fund or investment vehicle structure
• SPV or co-investment structures
• Repeated capital raises
• Institutional/family office backing
• External investors or investor reporting
• JV or operating partner language

AUTO-REJECT if the company ONLY does:
• Consumer home sales (brokers, realtors, listing portals)
• Mortgage lending / lending intermediary
• Architecture or construction only
• Single custom home building
• Property management only
• NFT/metaverse/gaming (not real physical real estate)

═══════════════════════════════════════════════════════
STEP 4 — PHASE TAG
═══════════════════════════════════════════════════════

"Phase 1 — Contact Now":
  A NAMED EXECUTIVE from the real estate company was directly quoted
  about tokenization, digital assets, blockchain, OR the company made
  a specific named tokenization announcement with verifiable exec attribution.
  → intent = "YES", urgency = 8-10

"Phase 2 — Nurture":
  The company clearly has tokenization/digital intent BUT no specific
  exec was quoted. General company mention or passing reference.
  → intent = "YES", urgency = 4-7

"Competitor":
  Article is primarily about a tokenization vendor/infrastructure company.
  → intent = "NO", urgency = 0

"Reject":
  No real qualifying signal. Generic article, consumer real estate,
  educational content, or government announcement only.
  → intent = "NO", urgency = 0

═══════════════════════════════════════════════════════
STEP 5 — FIT TAG
═══════════════════════════════════════════════════════

"Strong RWAtify Fit":
  Company shows PHASE 1 intent (exec quoted + active tokenization)
  OR shows multiple capital/SPV/fund signals.

"Potential RWAtify Fit":
  Company shows Phase 2 intent — tokenization interest but no exec quote,
  OR shows fund/capital structure without yet mentioning tokenization.

═══════════════════════════════════════════════════════
EXAMPLES (learn from these):
═══════════════════════════════════════════════════════

Example 1:
Article: "DAMAC Properties launches $1B tokenization deal with MANTRA blockchain"
→ company_name = "DAMAC Properties"
→ is_valid_lead = true, is_competitor = false
→ phase_tag = "Phase 1 — Contact Now", fit_tag = "Strong RWAtify Fit"
→ why_rwatify = "DAMAC is tokenizing $1B in assets via a rented platform — RWAtify gives them ownership and control of that infrastructure"
→ intent = "YES", urgency = 9

Example 2:
Article: "PRYPCO launches tokenization marketplace for UAE properties"
→ company_name = "PRYPCO"
→ is_valid_lead = false, is_competitor = true
→ phase_tag = "Competitor", intent = "NO", urgency = 0

Example 3:
Article: "Ellington Properties tokenizes Dubai apartment, partners with Ctrl Alt"
→ company_name = "Ellington Properties"
→ is_valid_lead = true, is_competitor = false
→ phase_tag = "Phase 1 — Contact Now", fit_tag = "Strong RWAtify Fit"

Example 4:
Article: "Real estate funds are exploring tokenization strategies"
→ No specific company named → phase_tag = "Reject", intent = "NO"

Example 5:
Article: "MAG Lifestyle signs $3B tokenization deal with MultiBank.io"
→ company_name = "MAG Lifestyle"
→ is_valid_lead = true, is_competitor = false
→ phase_tag = "Phase 1 — Contact Now"

═══════════════════════════════════════════════════════
NOW QUALIFY THIS ARTICLE:
═══════════════════════════════════════════════════════
ARTICLE TITLE: {title}
SOURCE WEBSITE: {source}
SEARCH QUERY: {query}
URL: {url}
ARTICLE TEXT:
{text}

Return ONLY valid JSON matching this exact structure, nothing else:
{{
  "is_valid_lead": true,
  "is_competitor": false,
  "reject_reason": "",
  "company_name": "exact company name",
  "company_type": "Real Estate Developer",
  "country": "UAE",
  "city": "Dubai",
  "company_website": "https://...",
  "decision_maker_name": "First Last",
  "decision_maker_title": "CEO",
  "exact_quote": "their actual words",
  "signal_type": "tokenization intent",
  "fit_tag": "Strong RWAtify Fit",
  "why_rwatify": "one specific sentence",
  "digital_ready": true,
  "phase_tag": "Phase 1 — Contact Now",
  "article_summary": "two sentences",
  "intent": "YES",
  "urgency": 9,
  "signal_summary": "short summary"
}}"""


# ─────────────────────────────────────────────
#  CALL CLAUDE API
# ─────────────────────────────────────────────

def _call_claude(title: str, source: str, url: str, query: str, text: str) -> Optional[dict]:
    """Send article to Claude for RWAtify qualification. Returns parsed JSON dict."""

    if not CLAUDE_API_KEY:
        print("  [ERROR] CLAUDE_API_KEY not set in .env file!")
        return None

    prompt = MASTER_PROMPT.format(
        title=title,
        source=source,
        query=query,
        url=url,
        text=text[:4500],
    )

    for attempt in range(3):
        try:
            time.sleep(random.uniform(0.5, 1.2))
            r = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key":         CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type":      "application/json",
                },
                json={
                    "model":      "claude-3-haiku-20240307",
                    "max_tokens": 900,
                    "messages":   [{"role": "user", "content": prompt}],
                },
                timeout=35,
            )

            if r.status_code == 529:
                print(f"  [WAIT] Claude overloaded - waiting 20s (attempt {attempt+1}/3)...")
                time.sleep(20)
                continue
            if r.status_code == 429:
                print(f"  [WAIT] Rate limit - waiting 30s (attempt {attempt+1}/3)...")
                time.sleep(30)
                continue

            if r.status_code != 200:
                print(f"  [ERROR] Claude API Error {r.status_code}: {r.text}")
            
            r.raise_for_status()

            raw = "".join(
                b.get("text", "")
                for b in r.json().get("content", [])
                if b.get("type") == "text"
            ).strip()

            # Strip markdown code fences if present
            raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'^```\s*',     '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$',     '', raw, flags=re.MULTILINE)
            raw = raw.strip()

            return json.loads(raw)

        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON parse error (attempt {attempt+1}/3): {str(e)[:50]}")
            if attempt < 2:
                time.sleep(3)
            continue

        except Exception as e:
            print(f"  [ERROR] Claude error (attempt {attempt+1}/3): {str(e)[:60]}")
            if attempt < 2:
                time.sleep(5)
            continue

    return None


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT — called by LangGraph node
# ─────────────────────────────────────────────

def classify_signal(text: str, article: dict = None) -> Optional[IntentSchema]:
    """
    Classify an article/signal using Claude with the RWAtify Master Prompt.
    
    Args:
        text: Combined title + summary text (for backward compat)
        article: Full article dict from news_finder (preferred)
    
    Returns:
        IntentSchema object or None on failure
    """
    if article:
        title   = article.get("title", "")
        source  = article.get("source", "unknown")
        url     = article.get("url", "")
        query   = article.get("query", "")
        content = article.get("full_text") or article.get("snippet", "") or text
    else:
        # Backward compat: parse title/summary from combined text
        lines  = text.strip().split("\n")
        title  = lines[0].replace("Title:", "").strip() if lines else text[:100]
        source = "unknown"
        url    = ""
        query  = ""
        content = text

    ai = _call_claude(title, source, url, query, content)

    if not ai or not isinstance(ai, dict):
        # Return a reject result rather than None
        return IntentSchema(
            is_valid_lead=False,
            is_competitor=False,
            reject_reason="Claude API failed or returned invalid response",
            company_name="UNKNOWN",
            company_type="Unknown",
            phase_tag="Reject",
            fit_tag="",
            intent="NO",
            urgency=0,
            signal_summary="AI processing failed",
        )

    # Post-process: enforce known lead / competitor rules
    company_lower = (ai.get("company_name") or "").lower()

    if any(lead in company_lower for lead in KNOWN_LEADS):
        ai["is_valid_lead"]  = True
        ai["is_competitor"]  = False

    if ai.get("is_competitor") and not any(lead in company_lower for lead in KNOWN_LEADS):
        ai["phase_tag"] = "Competitor"
        ai["intent"]    = "NO"
        ai["urgency"]   = 0

    if not ai.get("is_valid_lead"):
        ai["phase_tag"] = ai.get("phase_tag", "Reject")
        ai["intent"]    = "NO"

    # Map phase to intent for router
    if ai.get("phase_tag") == "Phase 1 — Contact Now":
        ai["intent"]  = "YES"
        if ai.get("urgency", 0) < 7:
            ai["urgency"] = 8
    elif ai.get("phase_tag") == "Phase 2 — Nurture":
        ai["intent"]  = "YES"
        if ai.get("urgency", 0) < 4:
            ai["urgency"] = 5

    try:
        return IntentSchema(**ai)
    except Exception as e:
        print(f"  [WARN] Schema parse error: {e}")
        return IntentSchema(
            is_valid_lead=ai.get("is_valid_lead") or False,
            is_competitor=ai.get("is_competitor") or False,
            reject_reason=ai.get("reject_reason") or "Schema error",
            company_name=ai.get("company_name") or "UNKNOWN",
            company_type=ai.get("company_type") or "Unknown",
            phase_tag=ai.get("phase_tag") or "Reject",
            fit_tag=ai.get("fit_tag") or "",
            intent=ai.get("intent") or "NO",
            urgency=ai.get("urgency") or 0,
            signal_summary=ai.get("signal_summary") or "AI processing failed",
        )