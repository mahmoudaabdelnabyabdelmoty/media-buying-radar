"""
Base utilities and helper functions for radar scanners.
Includes:
- Robust HTTP request fetching with browser emulation
- RSS/Atom feed parsing with timezone normalization
- HTML cleanup
- Intelligent platform inference (infer_platform) based on ad-tech & media-buying keywords
"""

import re
import logging
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from time import mktime
from typing import List, Dict, Any, Optional

from radar.config import REQUEST_HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger("radar.scanners.base")


def fetch_response(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = REQUEST_TIMEOUT,
    session: Optional[requests.Session] = None,
) -> Optional[requests.Response]:
    """Fetches a URL with realistic browser headers and error handling."""
    req_headers = headers or REQUEST_HEADERS
    client = session or requests
    try:
        resp = client.get(url, headers=req_headers, timeout=timeout)
        if resp.status_code == 200:
            return resp
        logger.warning(f"Failed fetching {url}: HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"Request exception for {url}: {e}")
    return None


def fetch_rss_feed(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = REQUEST_TIMEOUT,
) -> List[Dict[str, Any]]:
    """
    Fetches an RSS/Atom feed safely using requests first (to avoid user-agent blocks),
    then parses with feedparser.
    """
    entries = []
    try:
        resp = fetch_response(url, headers=headers, timeout=timeout)
        if resp and resp.content:
            parsed = feedparser.parse(resp.content)
            for item in parsed.entries:
                pub_date = None
                if hasattr(item, "published_parsed") and item.published_parsed:
                    try:
                        pub_date = datetime.fromtimestamp(mktime(item.published_parsed), tz=timezone.utc).isoformat()
                    except Exception:
                        pass
                elif hasattr(item, "updated_parsed") and item.updated_parsed:
                    try:
                        pub_date = datetime.fromtimestamp(mktime(item.updated_parsed), tz=timezone.utc).isoformat()
                    except Exception:
                        pass

                if not pub_date:
                    pub_date = datetime.now(timezone.utc).isoformat()

                # Extract description / summary / content
                content = ""
                if hasattr(item, "content") and item.content:
                    content = item.content[0].value
                elif hasattr(item, "summary") and item.summary:
                    content = item.summary
                elif hasattr(item, "description") and item.description:
                    content = item.description

                clean_text = clean_html(content)
                link = getattr(item, "link", url)
                title = getattr(item, "title", "No Title").strip()

                entries.append({
                    "title": title,
                    "original_url": link,
                    "published_at": pub_date,
                    "raw_content": clean_text,
                })
    except Exception as e:
        logger.warning(f"Error parsing feed from {url}: {e}")
    return entries


def clean_html(raw_html: str) -> str:
    """Strips HTML tags, scripts, and extra whitespace."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for script_or_style in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        script_or_style.decompose()
    text = soup.get_text(separator=" ")
    return " ".join(text.split()).strip()


def infer_platform(title: str, content: str = "", default: str = "community") -> str:
    """
    Intelligently determines the target media buying platform from an article's
    title and content based on weighted ad-tech keywords.

    Returns one of:
      'meta', 'google_ads', 'tiktok', 'snapchat', 'linkedin', 'x_ads', or default.
    """
    try:
        from radar.platform_router import route_platform
        return route_platform(title, content, default_platform=default)
    except Exception:
        pass

    title_lower = title.lower()
    combined_lower = f"{title_lower} {content.lower()}"


    scores = {
        "meta": 0,
        "google_ads": 0,
        "tiktok": 0,
        "snapchat": 0,
        "linkedin": 0,
        "x_ads": 0,
    }

    # Meta keywords
    meta_primary = [
        "facebook", "instagram", "reels", "advantage+", "advantage plus",
        "meta ads", "meta for business", "capi", "zuckerberg", "threads app",
        "meta verified", "meta pixel", "asc campaigns", "meta ai"
    ]
    meta_secondary = [
        "meta", "whatsapp ads", "ad manager", "ads manager", "lookalike",
        "custom audience", "instant forms", "lead ad", "catalog ads"
    ]
    for term in meta_primary:
        if term in title_lower:
            scores["meta"] += 4
        elif term in combined_lower:
            scores["meta"] += 2
    for term in meta_secondary:
        if term in title_lower:
            scores["meta"] += 2
        elif term in combined_lower:
            scores["meta"] += 1

    # Google Ads keywords
    google_primary = [
        "google ads", "pmax", "performance max", "adwords", "google search ads",
        "smart bidding", "youtube ads", "youtube shorts ads", "google merchant",
        "demand gen", "google shopping", "search engine roundtable"
    ]
    google_secondary = [
        "google", "ga4", "search console", "target cpa", "target roas",
        "broad match", "responsive search ads", "rsa", "quality score"
    ]
    for term in google_primary:
        if term in title_lower:
            scores["google_ads"] += 4
        elif term in combined_lower:
            scores["google_ads"] += 2
    for term in google_secondary:
        if term in title_lower:
            scores["google_ads"] += 2
        elif term in combined_lower:
            scores["google_ads"] += 1

    # TikTok keywords
    tiktok_terms = [
        "tiktok", "tik tok", "bytedance", "spark ads", "tiktok shop",
        "pulse premier", "tiktok ads", "tiktok pixel", "tiktok creator"
    ]
    for term in tiktok_terms:
        if term in title_lower:
            scores["tiktok"] += 4
        elif term in combined_lower:
            scores["tiktok"] += 2

    # Snapchat keywords
    snap_terms = [
        "snapchat", "snap inc", "snap ads", "sponsored lens", "ar lens",
        "snapchat for business", "snap pixel"
    ]
    for term in snap_terms:
        if term in title_lower:
            scores["snapchat"] += 4
        elif term in combined_lower:
            scores["snapchat"] += 2

    # LinkedIn keywords
    li_terms = [
        "linkedin", "matched audiences", "sponsored content", "inmail",
        "linkedin ads", "thought leader ads", "linkedin marketing"
    ]
    for term in li_terms:
        if term in title_lower:
            scores["linkedin"] += 4
        elif term in combined_lower:
            scores["linkedin"] += 2

    # X / Twitter keywords
    x_terms = [
        "x ads", "twitter ads", "twitter", "x premium", "tweet ads",
        "x developer", "x analytics"
    ]
    for term in x_terms:
        if term in title_lower:
            scores["x_ads"] += 4
        elif term in combined_lower:
            scores["x_ads"] += 2

    # Pick the platform with the highest score above threshold
    best_platform = default
    max_score = 0
    for platform_key, score in scores.items():
        if score > max_score and score >= 2:
            max_score = score
            best_platform = platform_key

    return best_platform
