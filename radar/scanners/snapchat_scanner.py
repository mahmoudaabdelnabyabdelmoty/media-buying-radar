"""
Snapchat Ads Scanner.
Scans:
- Snap Newsroom RSS Feed
- Snapchat Marketing API Changelog / Developer Releases
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import fetch_response, fetch_rss_feed, clean_html

logger = logging.getLogger("radar.scanners.snapchat")


def scan_snap_newsroom() -> List[Dict[str, Any]]:
    """Scans Snap Newsroom and For Business Blog for advertising updates."""
    updates = []
    feed_url = "https://newsroom.snap.com/rss"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        text = f"{entry['title']} {entry['raw_content']}".lower()
        if any(k in text for k in ["ad", "business", "partner", "sponsor", "lens", "ar", "brand", "commerce", "monetization"]):
            updates.append({
                "platform": "snapchat",
                "title": f"Snapchat: {entry['title']}",
                "original_url": entry["original_url"],
                "published_at": entry["published_at"],
                "category": "ميزات جديدة",
                "raw_content": entry["raw_content"],
                "is_outage": False,
            })

    # If feed is empty or blocked, check Snapchat for Business blog
    if not updates:
        resp = fetch_response("https://forbusiness.snapchat.com/blog")
        if resp:
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.find_all(["h2", "h3", "a"], limit=20)
                for c in cards:
                    text = c.get_text().strip()
                    if len(text) > 25 and any(k in text.lower() for k in ["ad", "business", "audience", "campaign", "grow", "snapchat", "lens", "sales"]):
                        updates.append({
                            "platform": "snapchat",
                            "title": f"Snapchat for Business: {text[:100]}",
                            "original_url": "https://forbusiness.snapchat.com/blog",
                            "published_at": datetime.now(timezone.utc).isoformat(),
                            "category": "ميزات جديدة",
                            "raw_content": text,
                            "is_outage": False,
                        })
                        if len(updates) >= 5:
                            break
            except Exception as e:
                logger.warning(f"Error scraping Snap for Business blog: {e}")
    return updates


def scan_snap_developer_changelog() -> List[Dict[str, Any]]:
    """Scans Snapchat Marketing API developer documentation."""
    updates = []
    url = "https://marketingapi.snapchat.com/docs/"
    resp = fetch_response(url)
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            headers = soup.find_all(["h2", "h3", "a"], limit=10)
            for h in headers:
                text = h.get_text().strip()
                if any(k in text.lower() for k in ["v1.", "v2.", "changelog", "release notes", "conversions api", "cpa", "pixel"]):
                    updates.append({
                        "platform": "snapchat",
                        "title": f"Snapchat Marketing API: {text[:100]}",
                        "original_url": url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": "تحديثات تقنية",
                        "raw_content": f"Snapchat Marketing API doc release: {text}",
                        "is_outage": False,
                    })
        except Exception as e:
            logger.warning(f"Error scraping Snap Marketing API: {e}")
    return updates


def scan_snapchat() -> List[Dict[str, Any]]:
    """Orchestrates all Snapchat scanning endpoints."""
    all_updates = []
    try:
        all_updates.extend(scan_snap_newsroom())
    except Exception as e:
        logger.error(f"Error in scan_snap_newsroom: {e}")

    try:
        all_updates.extend(scan_snap_developer_changelog())
    except Exception as e:
        logger.error(f"Error in scan_snap_developer_changelog: {e}")

    return all_updates
