"""
X Ads Scanner (Twitter).
Scans:
- X Developer Platform Changelog
- X Ads Product & Updates Blog
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import fetch_response, fetch_rss_feed, clean_html

logger = logging.getLogger("radar.scanners.x")


def scan_x_developer_changelog() -> List[Dict[str, Any]]:
    """Scans X Developer platform changelog."""
    updates = []
    url = "https://developer.x.com/en/updates/changelog"
    resp = fetch_response(url)
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.find_all(["h2", "h3", "article"], limit=10)
            for it in items:
                title_text = it.get_text().strip()
                if len(title_text) > 10 and any(k in title_text.lower() for k in ["api", "ads", "v2", "endpoint", "metric", "update", "202"]):
                    next_el = it.find_next("p")
                    desc = next_el.get_text().strip() if next_el else "X Developer Platform update notice"
                    updates.append({
                        "platform": "x_ads",
                        "title": f"X Developer: {title_text[:100]}",
                        "original_url": url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": "تحديثات تقنية",
                        "raw_content": desc,
                        "is_outage": False,
                    })
        except Exception as e:
            logger.warning(f"Error scraping X Developer Changelog: {e}")
    return updates


def scan_x_blog() -> List[Dict[str, Any]]:
    """Scans X product blog RSS feed."""
    updates = []
    feed_url = "https://blog.x.com/en_us/topics/product/rss"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        text = f"{entry['title']} {entry['raw_content']}".lower()
        if any(k in text for k in ["ad", "revenue", "creator", "monetization", "targeting", "analytics", "business"]):
            updates.append({
                "platform": "x_ads",
                "title": f"X Ads: {entry['title']}",
                "original_url": entry["original_url"],
                "published_at": entry["published_at"],
                "category": "ميزات جديدة",
                "raw_content": entry["raw_content"],
                "is_outage": False,
            })
    return updates


def scan_x() -> List[Dict[str, Any]]:
    """Orchestrates all X Ads scanning endpoints."""
    all_updates = []
    try:
        all_updates.extend(scan_x_developer_changelog())
    except Exception as e:
        logger.error(f"Error in scan_x_developer_changelog: {e}")

    try:
        all_updates.extend(scan_x_blog())
    except Exception as e:
        logger.error(f"Error in scan_x_blog: {e}")

    return all_updates
