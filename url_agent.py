import os
import re
import json
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from ddgs import DDGS

# Optional LLM/Agent fallback
from langchain_openai import ChatOpenAI
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# Load environment
load_dotenv()

# ---------------------------
# Configuration
# ---------------------------
USE_LLM_FALLBACK: bool = bool(os.getenv("OPENAI_API_KEY"))
CACHE_FILE = os.path.join(os.path.dirname(__file__), ".foundation_url_cache.json")

STOPWORDS = {
    "the",
    "foundation",
    "foundations",
    "trust",
    "charitable",
    "charity",
    "fund",
    "funds",
    "inc",
    "inc.",
    "llc",
    "ltd",
    "co",
    "company",
    "org",
    "of",
    "for",
    "and",
    "&",
}

BAD_DOMAINS = {
    "wikipedia.org",
    "wikidata.org",
    "linkedin.com",
    "facebook.com",
    "x.com",
    "twitter.com",
    "instagram.com",
    "youtube.com",
    "bloomberg.com",
    "charitynavigator.org",
    "guidestar.org",
    "crunchbase.com",
    "opencorporates.com",
    "glassdoor.com",
    "indeed.com",
    "news.google.com",
    "reddit.com",
    "quora.com",
    "medium.com",
    "blogspot.com",
    "wixsite.com",
    "weebly.com",
    "tumblr.com",
    "zhihu.com",
    "fundsforngos.org",
    "foundationcenter.org",
    "candid.org",
    "insidephilanthropy.com",
    "grantmakers.org",
    "philanthropy.com",
}

# Higher is better
TLD_PRIORITY = {".org": 3, ".foundation": 3, ".edu": 2, ".com": 1, ".net": 0}

# ---------------------------
# Utilities: cache, normalization, URL helpers
# ---------------------------

def _load_persistent_cache() -> Dict[str, str]:
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_persistent_cache(cache: Dict[str, str]) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


_DISK_CACHE = _load_persistent_cache()


def _normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _tokenize(text: str) -> List[str]:
    return [t for t in _normalize_text(text).split(" ") if t and t not in STOPWORDS]


def _domain_from_url(url: str) -> str:
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        return parsed.netloc.lower()
    except Exception:
        return ""


def _root_url(url: str) -> str:
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        scheme = parsed.scheme or "https"
        return f"{scheme}://{parsed.netloc}/"
    except Exception:
        return url


def _tld_score(domain: str) -> int:
    for tld, score in TLD_PRIORITY.items():
        if domain.endswith(tld):
            return score
    return 0


def _is_bad_domain(domain: str) -> bool:
    return any(domain.endswith(bad) for bad in BAD_DOMAINS)


def _token_overlap_score(name_tokens: List[str], text: str) -> float:
    if not text:
        return 0.0
    text_norm = _normalize_text(text)
    found = sum(1 for t in name_tokens if t in text_norm)
    return found / max(len(name_tokens), 1)


def _fetch_head_or_get(url: str, timeout: float = 5.0) -> Optional[str]:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Foundation-URL-Resolver)"}
        with requests.Session() as s:
            # Try a quick HEAD to follow redirects and verify reachability
            try:
                r_head = s.head(url, headers=headers, allow_redirects=True, timeout=timeout)
                if not r_head.ok:
                    # If HEAD fails, try GET directly
                    r_get = s.get(url, headers=headers, timeout=timeout)
                    if r_get.ok and isinstance(r_get.text, str):
                        return r_get.text[:20000]
                    return None
            except Exception:
                # If HEAD raised, try GET
                r_get = s.get(url, headers=headers, timeout=timeout)
                if r_get.ok and isinstance(r_get.text, str):
                    return r_get.text[:20000]
                return None

            # If HEAD succeeded, still fetch a small body to validate content
            r_get = s.get(url, headers=headers, timeout=timeout)
            if r_get.ok and isinstance(r_get.text, str):
                return r_get.text[:20000]
            return None
    except Exception:
        return None


def _is_official_site(root_url: str, name_tokens: List[str]) -> bool:
    html = _fetch_head_or_get(root_url)
    if html is None:
        return False
    html_lower = (html or "").lower()
    if "wikipedia" in html_lower or "linkedin" in html_lower:
        return False
    score = _token_overlap_score(name_tokens, html_lower)
    # Require modest overlap, allowing single-token match (e.g., surname)
    return score >= 0.3


def _score_candidate(url: str, title: str, snippet: str, name_tokens: List[str]) -> float:
    domain = _domain_from_url(url)
    if not domain or _is_bad_domain(domain):
        return -1.0

    base = 0.0
    base += 0.6 * _token_overlap_score(name_tokens, domain)
    base += 0.3 * _token_overlap_score(name_tokens, title or "")
    base += 0.2 * _token_overlap_score(name_tokens, snippet or "")
    base += 0.2 * _tld_score(domain)

    # Prefer homepages
    if url.rstrip("/").count("/") <= 2:
        base += 0.2

    # Prefer domains that explicitly include 'foundation' (modest bonus)
    if "foundation" in domain:
        base += 0.25

    # Strongly prefer domains that include any key name token
    if any(t in domain for t in name_tokens):
        base += 0.8

    # Penalize likely non-homepage sections
    if any(p in url for p in ["/jobs", "/careers", "/news", "/press", "/about-us/jobs", "/wikipedia.", "/linkedin."]):
        base -= 0.2

    return base


def _generate_domain_candidates(name_tokens: List[str]) -> List[str]:
    """Generate plausible official domains from name tokens.

    Heuristics attempt with and without the word 'foundation', and with hyphenated/concatenated forms.
    """
    tokens = [t for t in name_tokens if t != "foundation"]
    if not tokens:
        tokens = name_tokens

    joined = "".join(tokens)
    hyphened = "-".join(tokens)

    bases = [joined, hyphened]
    # Include versions that add 'foundation'
    bases += [
        f"{joined}foundation",
        f"{hyphened}-foundation" if hyphened else "foundation",
        f"{joined}-foundation" if joined else "foundation",
    ]

    tlds = [".org", ".foundation", ".edu", ".com"]
    domains = []
    for base in bases:
        if not base:
            continue
        for tld in tlds:
            domains.append(f"{base}{tld}")
            domains.append(f"www.{base}{tld}")
    # Deduplicate preserving order
    seen: set = set()
    unique = []
    for d in domains:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    return unique[:16]


def _ddg_search(name: str, max_results: int = 12) -> List[Dict[str, str]]:
    queries = [
        f"{name} official website",
        f"{name} foundation",
        f"{name} grants",
        f"{name} .org",
    ]
    seen = set()
    results: List[Dict[str, str]] = []
    with DDGS(timeout=5) as ddgs:
        for q in queries:
            for item in ddgs.text(q, region="us-en", max_results=max_results):
                url = item.get("href") or item.get("url") or item.get("link")
                if not url:
                    continue
                domain = _domain_from_url(url)
                if not domain or domain in seen:
                    continue
                seen.add(domain)
                results.append(
                    {
                        "url": url,
                        "title": item.get("title") or "",
                        "snippet": item.get("body") or item.get("snippet") or "",
                    }
                )
            if len(results) >= max_results:
                break
    return results[:max_results]


@lru_cache(maxsize=4096)
def resolve_official_foundation_url(foundation_name: str) -> Optional[str]:
    if not foundation_name or not foundation_name.strip():
        return None

    norm_key = _normalize_text(foundation_name)
    if norm_key in _DISK_CACHE:
        cached = _DISK_CACHE.get(norm_key)
        if cached:
            domain = _domain_from_url(cached)
            # Drop cached entries that are no longer considered good
            if domain and not _is_bad_domain(domain):
                return _root_url(cached)
            else:
                try:
                    del _DISK_CACHE[norm_key]
                    _save_persistent_cache(_DISK_CACHE)
                except Exception:
                    pass

    name_tokens = _tokenize(foundation_name)
    if not name_tokens:
        return None

    # Search candidates via free DuckDuckGo backend
    candidates = _ddg_search(foundation_name, max_results=20)
    if not candidates:
        return None

    # Score and sort candidates
    scored: List[Tuple[float, Dict[str, str]]] = []
    for c in candidates:
        score = _score_candidate(c["url"], c.get("title", ""), c.get("snippet", ""), name_tokens)
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Try direct domain guesses first (often fastest and most accurate for well-known orgs)
    for candidate_domain in _generate_domain_candidates(name_tokens):
        root = _root_url(candidate_domain)
        if _is_official_site(root, name_tokens):
            _DISK_CACHE[norm_key] = root
            _save_persistent_cache(_DISK_CACHE)
            return root

    # Validate top-N via lightweight fetch
    for _, c in scored[:5]:
        root = _root_url(c["url"])
        if _is_official_site(root, name_tokens):
            _DISK_CACHE[norm_key] = root
            _save_persistent_cache(_DISK_CACHE)
            return root

    # As a fallback, return the highest-scoring homepage candidate even if validation failed
    if scored:
        root = _root_url(scored[0][1]["url"])
        _DISK_CACHE[norm_key] = root
        _save_persistent_cache(_DISK_CACHE)
        return root

    return None


# ---------------------------
# Lightweight validator tool for the LLM fallback
# ---------------------------

@tool
def validate_url(url: str) -> str:
    """Return the URL if the page appears to be an official foundation site; otherwise empty string."""
    try:
        html = _fetch_head_or_get(url, timeout=5)
        if not html:
            return ""
        # Minimal signals
        if ("foundation" in html.lower() or "grants" in html.lower() or "our mission" in html.lower()):
            return _root_url(url)
        return ""
    except Exception:
        return ""


# ---------------------------
# LLM fallback setup (optional)
# ---------------------------

llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini") if USE_LLM_FALLBACK else None
search_tool = DuckDuckGoSearchRun(max_results=10) if USE_LLM_FALLBACK else None

SYSTEM_PROMPT = """
You are a highly reliable assistant that returns the official homepage URL for a foundation. Your output must be a single URL.

Robust strategy:
- Normalize the name (treat case/accents/& as 'and').
- Try search queries: "<name> official website", "<name> foundation", "<name> .org".
- Prefer homepages and domains ending with .org or .foundation, then .edu, then .com.
- Avoid aggregator/social/news sites (e.g., Wikipedia, LinkedIn, Candid, Foundation Center, Charity Navigator).
- Use validate_url on the candidate homepage to confirm foundation/grant signals.
- If multiple candidates exist, choose the one whose domain best matches the foundation name tokens.

Output: ONLY the final URL. No extra text.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent_executor: Optional[AgentExecutor] = None
if USE_LLM_FALLBACK and llm is not None and search_tool is not None:
    tools = [search_tool, validate_url]
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
        verbose=False,
        max_iterations=6,
        max_execution_time=25,
    )


# ---------------------------
# Public API
# ---------------------------

def find_foundation_url(name: str) -> str:
    """Resolve the official foundation homepage URL.

    Strategy:
    1) Deterministic resolver via DuckDuckGo + heuristic scoring + validation (with disk+memory caching).
    2) Optional LLM fallback using tools if available.
    """
    try:
        url = resolve_official_foundation_url(name)
        if url:
            return url

        if USE_LLM_FALLBACK and agent_executor is not None:
            prompt_variations = [
                f"Find the official homepage URL for '{name}'. Return only the URL.",
                f"Return only the official website URL for '{name}' foundation. Prefer .org.",
            ]
            for prompt_text in prompt_variations:
                try:
                    response = agent_executor.invoke({"input": prompt_text})
                    result = (response.get("output") or "").strip()
                    if result.startswith("http"):
                        return _root_url(result)
                except Exception:
                    continue
    
        return f"Unable to find URL for {name} after multiple attempts"
    except Exception as ex:
        return f"Unable to find URL for {name}: {str(ex)}"


if __name__ == "__main__":
    examples = [
        "BILL & MELINDA GATES FOUNDATION",
        "The William Penn Foundation",
        "The William and Flora Hewlett Foundation",
    ]
    for ex in examples:
        print(f"Query: {ex}")
        print(f"URL:   {find_foundation_url(ex)}\n")
 