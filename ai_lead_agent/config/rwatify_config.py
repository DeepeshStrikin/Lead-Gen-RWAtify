"""
╔══════════════════════════════════════════════════════════════════╗
║   RWAtify Lead Agent — Central Configuration                    ║
║   Edit this file to add/remove queries, keywords, companies     ║
╚══════════════════════════════════════════════════════════════════╝

All search queries, keyword filters, competitor lists and known leads
are managed here. The rest of the agent reads from this file.
"""

# ═══════════════════════════════════════════════════════════
#  OUTPUT
# ═══════════════════════════════════════════════════════════

OUTPUT_FILE = "data/rwatify_leads.xlsx"

# ═══════════════════════════════════════════════════════════
#  SERPER SEARCH — 50+ PRECISION GOOGLE QUERIES
#  These target BUYERS of RWAtify, not vendors.
# ═══════════════════════════════════════════════════════════

SEARCH_QUERIES = [

    # ── DIRECT TOKENIZATION INTENT (PHASE 1 PRIORITY) ────
    '"real estate" "tokenize our assets" CEO OR founder OR director 2025',
    '"property developer" "we are tokenizing" real estate 2025',
    '"real estate fund" "tokenization" "our own platform" 2025',
    '"we are building" "tokenization platform" real estate developer',
    '"fractional ownership" "our platform" real estate developer CEO quote',
    '"tokenized real estate" developer "we launched" 2025',
    '"tokenize" "our properties" real estate developer CEO OR MD',
    '"digital securities" "real estate" "our investors" CEO 2025',
    '"real estate tokenization" "own infrastructure" developer 2025',
    '"tokenized property" fund "investment vehicle" launch 2025',

    # ── UAE / DUBAI / ABU DHABI ──────────────────────────
    '"real estate developer" tokenization Dubai 2025',
    '"property developer" "blockchain" announcement Dubai OR "Abu Dhabi" 2025',
    '"tokenized real estate" UAE developer launch 2025',
    '"real estate fund" tokenization "Abu Dhabi" 2025',
    '"fractional property" investment platform UAE launch 2025',
    '"real estate" "digital assets" "RWA" developer UAE 2025',
    'Ellington OR DAMAC OR Azizi tokenization platform 2025',
    'DAMAC OR "Dar Global" OR Emaar tokenization blockchain 2025',
    '"Omniyat" OR "Select Group" OR "MAG" tokenization blockchain 2025',
    '"Danube Properties" OR "Sobha" OR "Nshama" blockchain real estate 2025',

    # ── SAUDI ARABIA / MENA / MEA ─────────────────────────
    '"real estate fund" tokenization "Saudi Arabia" 2025',
    '"real estate developer" tokenization Riyadh OR Jeddah 2025',
    '"property developer" blockchain "Saudi Arabia" announcement 2025',
    '"real estate" "RWA tokenization" Saudi OR Kuwait OR Bahrain 2025',
    '"real estate" tokenization Egypt OR Qatar OR Bahrain 2025',
    '"real estate" "digital investment" Africa Nigeria OR Kenya 2025',

    # ── UNITED STATES ─────────────────────────────────────
    '"real estate developer" "tokenized" fund launch USA 2025',
    '"multifamily" "real estate fund" tokenization platform launch 2025',
    '"commercial real estate" tokenization "investment platform" 2025',
    '"real estate private equity" tokenization "own platform" 2025',
    '"family office" "real estate" tokenization platform 2025',
    '"real estate developer" Texas OR Florida OR California tokenization 2025',
    '"real estate fund" "Fund I" OR "Fund II" OR "Fund III" tokenization 2025',
    '"opportunity zone" "real estate" tokenization "investment platform" 2025',

    # ── UK / EUROPE ───────────────────────────────────────
    '"real estate" "tokenization" developer launch UK OR Europe 2025',
    '"property developer" blockchain "digital securities" UK 2025',
    '"real estate fund" tokenization Germany OR Netherlands OR France 2025',
    '"property investment" blockchain tokenization London 2025',

    # ── ASIA / SINGAPORE / HONG KONG ────────────────────
    '"real estate" tokenization Singapore developer launch 2025',
    '"property fund" tokenization blockchain Singapore OR "Hong Kong" 2025',
    '"real estate" "digital asset" tokenization India OR Indonesia 2025',

    # ── GLOBAL REAL ESTATE FUNDS ─────────────────────────
    '"real estate fund" tokenization blockchain platform 2025',
    '"private equity real estate" tokenization "own infrastructure" 2025',
    '"asset manager" "real estate" tokenization platform launch 2025',
    '"real estate investment" "tokenized" fund launch 2025',

    # ── PROPTECH BUYERS ──────────────────────────────────
    '"proptech" "tokenization" "investment platform" launch 2025',
    '"real estate crowdfunding" blockchain tokenization platform 2025',
    '"fractional real estate" platform launch blockchain 2025',

    # ── CAPITAL / FUND STRUCTURE SIGNALS ─────────────────
    '"real estate" "SPV" "capital raise" "digital" 2025',
    '"real estate fund" "co-investment" OR "JV" tokenization 2025',
    '"real estate" "private placement" tokenization investors 2025',
    '"real estate" "investor portal" "blockchain" developer 2025',
    '"real estate developer" "capital partners" tokenization blockchain 2025',

    # ── KNOWN HIGH-INTENT COMPANIES ───────────────────────
    '"Dar Global" tokenization blockchain real estate',
    '"MAG Lifestyle" OR "MAG Group" tokenization real estate platform',
    '"Seazen Group" tokenization RWA digital asset',
    '"Ellington Properties" tokenization platform 2025',
    '"Azizi Developments" tokenization blockchain',
    '"Al Habtoor" real estate tokenization digital',
    '"Omniyat" tokenization blockchain platform',
    '"Select Group" Dubai tokenization platform',
    '"DAMAC Properties" tokenization blockchain 2025',
    '"Aldar Properties" digital assets tokenization 2025',
    '"Meraas" OR "Emaar" tokenization digital investment 2025',
    '"Tishman Speyer" OR "Brookfield" tokenization digital 2025',
    '"Related Group" tokenization real estate 2025',
    '"Greystar" OR "Hines" tokenization platform 2025',

    # ── SWITCHING ANGLE (using competitor but should switch) ──
    '"real estate" "DigiShares" OR "Tokeny" OR "Securitize" developer 2025',
    '"real estate" "tokenization platform" "partnership" developer 2025',
    '"MANTRA" OR "Chainlink" real estate tokenization developer 2025',

    # ── CONFERENCE / ANNOUNCEMENT SIGNALS ────────────────
    '"real estate" tokenization announced CEO interview 2025',
    '"real estate developer" "digital assets" RWA platform 2025',
    '"property" "tokenization" "we have built" OR "we are building" 2025',
    'MIPIM OR "EXPO REAL" OR "Cityscape" real estate tokenization 2025',
    '"ULI" OR "IMN" real estate tokenization blockchain speaker 2025',

    # ── CAREERS PAGE INTENT (hiring = budget + mandate) ──
    '"real estate" "head of tokenization" OR "digital assets lead" job 2025',
    '"real estate developer" "blockchain engineer" OR "digital assets" hiring 2025',
    '"real estate fund" "investment platform" product manager hiring 2025',

    # ── RWA INFRASTRUCTURE INTENT ─────────────────────────
    '"real world asset" tokenization real estate developer 2025',
    '"RWA" real estate platform "own infrastructure" developer 2025',
    '"on-chain real estate" developer investment platform 2025',
    '"tokenized real estate" "investor portal" OR "cap table" 2025',
    '"digital investment platform" real estate developer 2025',
]


# ═══════════════════════════════════════════════════════════
#  COMPETITOR LIST — never qualify these as leads
#  These SELL tokenization infra — they are vendors not buyers
# ═══════════════════════════════════════════════════════════

COMPETITOR_NAMES = [
    "digishares", "tokeny", "securitize", "polymath", "smartlands",
    "zoniqx", "tokinvest", "tzero", "blocksquare", "brickken",
    "multibank.io", "prypco", "harbor", "bitbond", "cashlink",
    "stokr", "tokensoft", "vertalo", "ddx global", "inovartic",
    "tokenscope", "fortexchain", "ctrl alt", "fasset",
    "lara on the block", "binaryx", "world liberty financial",
    "stobox", "chainbull", "homecubes", "nomyx", "digift",
    "realt ", "metawealth", "honeybricks", "landshare", "realio",
    "slices.estate", "mantra chain", "mavryk", "digift",
    "republic", "fundrise", "yieldstreet",  # these are platforms/portals
]


# ═══════════════════════════════════════════════════════════
#  KNOWN REAL ESTATE LEADS — always valid leads
#  Even if currently using a competitor platform
# ═══════════════════════════════════════════════════════════

KNOWN_LEADS = [
    "dar global", "damac", "emaar", "ellington properties", "azizi",
    "mag lifestyle", "mag group", "seazen", "al habtoor", "omniyat",
    "select group", "danube", "nshama", "sobha", "aldar", "deyaar",
    "meraas", "dubai properties", "union properties", "imkan",
    "bloom holding", "masaar", "reportage", "pantheon",
    "tishman speyer", "brookfield real estate", "blackstone real estate",
    "prologis", "lendlease", "hines", "greystar", "related group",
    "kin capital", "crowdstreet", "roofstock",
    "pwfo", "arada",  # mentioned by client as recent prospects
]


# ═══════════════════════════════════════════════════════════
#  CRYPTO / NOISE DOMAINS — skip articles from these sites
# ═══════════════════════════════════════════════════════════

SKIP_DOMAINS = [
    "cointelegraph.com", "decrypt.co", "theblock.co", "coindesk.com",
    "crypto.news", "beincrypto.com", "ambcrypto.com", "coingape.com",
    "newsbtc.com", "dailyhodl.com", "bitcoinist.com", "coinquora.com",
    "coinpedia.org", "zycrypto.com", "u.today", "cryptopotato.com",
    "cryptoslate.com", "cryptobriefing.com", "cryptonews.com",
]


# ═══════════════════════════════════════════════════════════
#  KEYWORD FILTERS — pre-filter before expensive Claude call
# ═══════════════════════════════════════════════════════════

# Layer A — Real Estate entity words (must be present)
REAL_ESTATE_KEYWORDS = [
    "real estate", "property", "developer", "fund", "reit", "landlord",
    "asset manager", "proptech", "residential", "commercial", "hospitality",
    "multifamily", "mixed-use", "industrial", "office building",
    "real estate developer", "investment manager", "capital market",
    "private equity real estate", "real estate fund",
]

# Layer B — Tokenization / intent signals (must be present alongside Layer A)
PHASE1_KEYWORDS = [
    "real estate tokenization", "tokenized real estate", "property tokenization",
    "rwa real estate", "tokenize our assets", "tokenizing property",
    "fractional real estate blockchain", "tokenized property fund",
    "digital real estate securities", "on-chain real estate",
    "blockchain real estate investment", "fractional property investment",
    "build our own platform", "proprietary investment platform",
    "replace fund administrator", "cap table digitization",
    "digital securities real estate", "asset tokenization real estate",
    "blockchain-based real estate", "tokenized investment platform",
    "own investor infrastructure", "investor lifecycle platform",
    "we are tokenizing", "we launched tokenization", "tokenization platform launch",
    "real world asset", "rwa tokenization", "digital ownership", "on-chain",
    "programmable ownership", "digital securities",
]

PHASE2_KEYWORDS = [
    "exploring tokenization", "digital transformation real estate",
    "web3 real estate", "blockchain property", "digital investment platform",
    "fractional ownership", "digital property investment",
    "blockchain capital markets", "rwa", "tokenization",
    "spv", "special purpose vehicle", "co-investment", "family office",
    "fund I", "fund II", "fund III", "investor portal", "private placement",
    "capital partners", "jv structure", "alternative investment",
]

# Hard disqualifiers — auto-reject if ONLY about these
HARD_DISQUALIFIERS = [
    "mortgage broker", "real estate agent", "property listing",
    "home for sale", "buy a home", "sell your home", "mls listing",
    "brokerage ranking", "realtor awards", "proptech awards",
    "nft marketplace", "crypto exchange", "defi protocol",
    "play-to-earn", "metaverse land", "virtual real estate",
]


# ═══════════════════════════════════════════════════════════
#  TARGET DECISION MAKER TITLES (RWAtify buyers)
# ═══════════════════════════════════════════════════════════

TARGET_TITLES = [
    "Founder",
    "Co-Founder",
    "Managing Partner",
    "General Partner",
    "Chief Executive Officer",
    "Chief Investment Officer",
    "Head of Investments",
    "Managing Director",
    "Principal",
    "Partner",
    "Head of Real Estate",
    "Fund Director",
    "Head of Capital Markets",
    "Chief Financial Officer",
]


# ═══════════════════════════════════════════════════════════
#  PRE-SEEDED LEADS
#  Companies already identified by the client / known to have intent.
#  These are ALWAYS included in the Excel (Phase 2 minimum),
#  even if no fresh article is found for them during the web search.
#
#  Fields:
#    company_name     → exact name
#    company_type     → developer / fund / operator etc.
#    country / city   → geography
#    company_website  → official website
#    why_rwatify      → why they need RWAtify
#    fit_tag          → "Strong RWAtify Fit" or "Potential RWAtify Fit"
#    phase_tag        → "Phase 1 — Contact Now" or "Phase 2 — Nurture"
#    signal_type      → what signal makes them a lead
#    source           → "Pre-Seeded — Client Identified"
# ═══════════════════════════════════════════════════════════

PRE_SEEDED_LEADS = [

    # ── CLIENT-FLAGGED RECENT PROSPECTS ─────────────────
    {
        "company_name":    "PWFO",
        "company_type":    "Real Estate Developer / Fund",
        "country":         "UAE",
        "city":            "Dubai",
        "company_website": "",
        "why_rwatify":     "Flagged by client as showing direct interest in RWAtify infrastructure",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "Client-identified prospect with direct intent signal",
        "digital_ready":   "Yes",
    },
    {
        "company_name":    "Arada",
        "company_type":    "Real Estate Developer",
        "country":         "UAE",
        "city":            "Sharjah / Dubai",
        "company_website": "https://www.arada.com",
        "why_rwatify":     "Flagged by client as showing interest in RWAtify; large-scale master-planned developer with investor capital needs",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "Client-identified prospect with direct intent signal",
        "digital_ready":   "Yes",
    },

    # ── UAE — HIGH INTENT DEVELOPERS ────────────────────
    {
        "company_name":    "DAMAC Properties",
        "company_type":    "Real Estate Developer",
        "country":         "UAE",
        "city":            "Dubai",
        "company_website": "https://www.damacproperties.com",
        "why_rwatify":     "DAMAC is tokenizing $1B+ in assets via rented blockchain platforms — RWAtify gives them owned infrastructure and full control",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "Tokenization announcement, digital securities, blockchain",
        "digital_ready":   "Yes",
    },
    {
        "company_name":    "Dar Global",
        "company_type":    "Real Estate Developer",
        "country":         "UAE / UK (Listed London)",
        "city":            "Dubai / London",
        "company_website": "https://www.darglobal.com",
        "why_rwatify":     "Dar Global is exploring tokenized fundraising for large resort projects — RWAtify is the infrastructure layer they need",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "Tokenized funding exploration, blockchain-based capital raising",
        "digital_ready":   "Yes",
    },
    {
        "company_name":    "MAG Lifestyle Development",
        "company_type":    "Real Estate Developer",
        "country":         "UAE",
        "city":            "Dubai",
        "company_website": "https://www.magleisure.com",
        "why_rwatify":     "MAG signed $3B tokenization deal via third-party platform — replacing that with owned RWAtify infrastructure would eliminate vendor dependency",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "Tokenization deal announced, digital real estate securities",
        "digital_ready":   "Yes",
    },
    {
        "company_name":    "Ellington Properties",
        "company_type":    "Real Estate Developer",
        "country":         "UAE",
        "city":            "Dubai",
        "company_website": "https://www.ellingtonproperties.com",
        "why_rwatify":     "Ellington tokenized a Dubai apartment via Ctrl Alt — they are active tokenization buyers needing owned infrastructure",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "Tokenization live, digital ownership, fractional real estate",
        "digital_ready":   "Yes",
    },
    {
        "company_name":    "Azizi Developments",
        "company_type":    "Real Estate Developer",
        "country":         "UAE",
        "city":            "Dubai",
        "company_website": "https://www.azizidevelopments.com",
        "why_rwatify":     "Azizi runs large-scale residential developments with external capital — RWAtify replaces fragmented investor ops",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 2 — Nurture",
        "signal_type":     "Multi-project developer, capital partners, investor onboarding need",
        "digital_ready":   "No",
    },
    {
        "company_name":    "Omniyat",
        "company_type":    "Real Estate Developer",
        "country":         "UAE",
        "city":            "Dubai",
        "company_website": "https://www.omniyat.com",
        "why_rwatify":     "Omniyat develops ultra-luxury branded residences with complex investor structures needing modern infrastructure",
        "fit_tag":         "Potential RWAtify Fit",
        "phase_tag":       "Phase 2 — Nurture",
        "signal_type":     "Luxury developer, complex ownership structures, capital partners",
        "digital_ready":   "No",
    },
    {
        "company_name":    "Select Group",
        "company_type":    "Real Estate Developer",
        "country":         "UAE",
        "city":            "Dubai",
        "company_website": "https://www.selectgroup.me",
        "why_rwatify":     "Select Group is a multi-project Dubai developer with institutional capital — RWAtify modernises their investor operations",
        "fit_tag":         "Potential RWAtify Fit",
        "phase_tag":       "Phase 2 — Nurture",
        "signal_type":     "Multi-project developer, institutional backing",
        "digital_ready":   "No",
    },
    {
        "company_name":    "Aldar Properties",
        "company_type":    "Real Estate Developer / Fund",
        "country":         "UAE",
        "city":            "Abu Dhabi",
        "company_website": "https://www.aldar.com",
        "why_rwatify":     "Aldar operates large portfolios with institutional investors across Abu Dhabi — needs owned infrastructure for distributions and investor reporting",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 2 — Nurture",
        "signal_type":     "Portfolio operator, institutional capital, investor reporting",
        "digital_ready":   "No",
    },
    {
        "company_name":    "Seazen Group",
        "company_type":    "Real Estate Developer",
        "country":         "China (Global)",
        "city":            "Shanghai",
        "company_website": "https://www.seazen.com",
        "why_rwatify":     "Seazen announced digital asset and RWA tokenization initiative for converting tangible assets to blockchain tokens",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "RWA tokenization initiative, corporate digital asset unit",
        "digital_ready":   "Yes",
    },

    # ── USA — HIGH INTENT OPERATORS ───────────────────────
    {
        "company_name":    "Related Group",
        "company_type":    "Real Estate Developer",
        "country":         "USA",
        "city":            "Miami, FL",
        "company_website": "https://www.relatedgroup.com",
        "why_rwatify":     "Related Group is a major US developer with complex JV and co-investment structures requiring modern investor infrastructure",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 2 — Nurture",
        "signal_type":     "Co-investment structures, JV vehicles, capital partners",
        "digital_ready":   "No",
    },
    {
        "company_name":    "Tishman Speyer",
        "company_type":    "Real Estate Fund / Developer",
        "country":         "USA",
        "city":            "New York, NY",
        "company_website": "https://www.tishmanspeyer.com",
        "why_rwatify":     "Tishman Speyer manages multiple funds and SPVs globally — RWAtify replaces fragmented fund admin and reporting stack",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 2 — Nurture",
        "signal_type":     "Fund manager, SPV structures, institutional investors",
        "digital_ready":   "No",
    },

    # ── ELEVATED RETURNS (PIONEER) ─────────────────────────
    {
        "company_name":    "Elevated Returns",
        "company_type":    "Real Estate Fund / Operator",
        "country":         "USA",
        "city":            "New York, NY",
        "company_website": "https://www.elevatedreturns.com",
        "why_rwatify":     "Elevated Returns pioneered tokenized real estate with blockchain-based ownership — needs owned infrastructure to scale their model",
        "fit_tag":         "Strong RWAtify Fit",
        "phase_tag":       "Phase 1 — Contact Now",
        "signal_type":     "Tokenized real estate ownership, blockchain-based investment model",
        "digital_ready":   "Yes",
    },
]
