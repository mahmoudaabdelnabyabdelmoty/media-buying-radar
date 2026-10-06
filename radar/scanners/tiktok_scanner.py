"""
TikTok Ads Scanner.
Scans:
- TikTok Newsroom RSS Feed
- TikTok Marketing API Changelog & Business Updates
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import fetch_response, fetch_rss_feed, clean_html

logger = logging.getLogger("radar.scanners.tiktok")


def scan_tiktok_newsroom() -> List[Dict[str, Any]]:
    """Scans TikTok official Newsroom via RSS and HTML scraping."""
    updates = []
    feed_url = "https://newsroom.tiktok.com/en-us/feed"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        text = f"{entry['title']} {entry['raw_content']}".lower()
        if any(k in text for k in ["ad", "business", "creator", "partner", "commercial", "shopping", "brand", "feature", "campaign"]):
            updates.append({
                "platform": "tiktok",
                "title": f"TikTok: {entry['title']}",
                "original_url": entry["original_url"],
                "published_at": entry["published_at"],
                "category": "ميزات جديدة",
                "raw_content": entry["raw_content"],
                "is_outage": False,
            })

    # If RSS returned no business items, scrape newsroom HTML
    if not updates:
        resp = fetch_response("https://newsroom.tiktok.com/en-us/")
        if resp:
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", limit=25):
                    href = a.get("href", "")
                    title = a.get_text().strip()
                    if title and len(title) > 25 and not title.startswith("Watch"):
                        full_url = href if href.startswith("http") else f"https://newsroom.tiktok.com{href}"
                        updates.append({
                            "platform": "tiktok",
                            "title": f"TikTok Newsroom: {title}",
                            "original_url": full_url,
                            "published_at": datetime.now(timezone.utc).isoformat(),
                            "category": "ميزات جديدة",
                            "raw_content": f"TikTok Newsroom update: {title}",
                            "is_outage": False,
                        })
                        if len(updates) >= 5:
                            break
            except Exception as e:
                logger.warning(f"Error scraping TikTok newsroom HTML: {e}")
    return updates


def scan_tiktok_marketing_api() -> List[Dict[str, Any]]:
    """Scans TikTok Marketing API Changelog."""
    updates = []
    url = "https://ads.tiktok.com/marketing_api/docs"
    resp = fetch_response(url)
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            elements = soup.find_all(["h2", "h3", "a"], limit=10)
            for el in elements:
                text = el.get_text().strip()
                if any(k in text.lower() for k in ["v1.", "v2.", "changelog", "update", "pixel", "catalog", "events api"]):
                    updates.append({
                        "platform": "tiktok",
                        "title": f"TikTok Marketing API: {text[:100]}",
                        "original_url": url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": "تحديثات تقنية",
                        "raw_content": f"TikTok Marketing API update documentation notice: {text}",
                        "is_outage": False,
                    })
        except Exception as e:
            logger.warning(f"Error scraping TikTok Marketing API docs: {e}")
    return updates


def scan_tiktok() -> List[Dict[str, Any]]:
    """Orchestrates all TikTok scanning endpoints."""
    all_updates = []
    try:
        all_updates.extend(scan_tiktok_newsroom())
    except Exception as e:
        logger.error(f"Error in scan_tiktok_newsroom: {e}")

    try:
        all_updates.extend(scan_tiktok_marketing_api())
    except Exception as e:
        logger.error(f"Error in scan_tiktok_marketing_api: {e}")

    return all_updates
