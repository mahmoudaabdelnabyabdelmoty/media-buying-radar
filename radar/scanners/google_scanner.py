"""
Google Ads Scanner.
Scans:
- Google Ads Developer Blog RSS
- Google Ads & Commerce Official Blog RSS
- Google Ads Official Announcements
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import fetch_response, fetch_rss_feed, clean_html

logger = logging.getLogger("radar.scanners.google")


def scan_google_ads_dev_blog() -> List[Dict[str, Any]]:
    """Scans Google Ads Developer Blog feed."""
    updates = []
    feed_url = "https://ads-developers.googleblog.com/feeds/posts/default?alt=rss"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        updates.append({
            "platform": "google_ads",
            "title": f"Google Ads Dev: {entry['title']}",
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "تحديثات تقنية",
            "raw_content": entry["raw_content"],
            "is_outage": False,
        })
    return updates


def scan_google_keyword_ads() -> List[Dict[str, Any]]:
    """Scans Google official Ads & Commerce Blog feed."""
    updates = []
    feed_url = "https://blog.google/products/ads-commerce/rss/"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        updates.append({
            "platform": "google_ads",
            "title": entry["title"],
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "ميزات جديدة",
            "raw_content": entry["raw_content"],
            "is_outage": False,
        })
    return updates


def scan_google_ads_announcements() -> List[Dict[str, Any]]:
    """Scans Google Ads support announcements page."""
    updates = []
    url = "https://support.google.com/google-ads/announcements/9095107"
    resp = fetch_response(url)
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.find_all(["h2", "h3", "li"], limit=10)
            for item in articles:
                text = item.get_text().strip()
                if len(text) > 20 and any(k in text.lower() for k in ["ads", "policy", "campaign", "smart bidding", "pmax", "update", "202"]):
                    updates.append({
                        "platform": "google_ads",
                        "title": f"Google Ads Announcement: {text[:100]}",
                        "original_url": url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": "سياسات وحظر" if "policy" in text.lower() else "ميزات جديدة",
                        "raw_content": text,
                        "is_outage": False,
                    })
        except Exception as e:
            logger.warning(f"Error scraping Google Ads Announcements: {e}")
    return updates


def scan_google_ads() -> List[Dict[str, Any]]:
    """Orchestrates all Google Ads scanning endpoints."""
    all_updates = []
    try:
        all_updates.extend(scan_google_ads_dev_blog())
    except Exception as e:
        logger.error(f"Error in scan_google_ads_dev_blog: {e}")

    try:
        all_updates.extend(scan_google_keyword_ads())
    except Exception as e:
        logger.error(f"Error in scan_google_keyword_ads: {e}")

    try:
        all_updates.extend(scan_google_ads_announcements())
    except Exception as e:
        logger.error(f"Error in scan_google_ads_announcements: {e}")

    return all_updates
