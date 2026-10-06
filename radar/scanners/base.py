"""
Base utilities and helper functions for radar scanners.
"""

import logging
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from time import mktime
from typing import List, Dict, Any, Optional

from radar.config import REQUEST_HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger("radar.scanners.base")


def fetch_response(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[requests.Response]:
    """Fetches a URL with realistic browser headers and error handling."""
    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout)
        if resp.status_code == 200:
            return resp
        logger.warning(f"Failed fetching {url}: HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"Request exception for {url}: {e}")
    return None


def fetch_rss_feed(url: str, timeout: int = REQUEST_TIMEOUT) -> List[Dict[str, Any]]:
    """
    Fetches an RSS/Atom feed safely using requests first (to avoid user-agent blocks),
    then parses with feedparser.
    """
    entries = []
    try:
        resp = fetch_response(url, timeout=timeout)
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
    for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
        script_or_style.decompose()
    text = soup.get_text(separator=" ")
    return " ".join(text.split()).strip()
