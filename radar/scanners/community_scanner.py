"""
Community & Industry PPC Radar Scanner.
Scans:
- Reddit r/ppc RSS feed for field alerts, glitches, and discussions
- Search Engine Land PPC feed for industry news and breaking changes
"""

import logging
from typing import List, Dict, Any

from radar.scanners.base import fetch_rss_feed

logger = logging.getLogger("radar.scanners.community")


def scan_reddit_ppc() -> List[Dict[str, Any]]:
    """Scans Reddit r/ppc feed for real-time field reports and glitches."""
    updates = []
    feed_url = "https://www.reddit.com/r/ppc/new/.rss"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:10]:
        title = entry["title"]
        raw_text = f"{title} {entry['raw_content']}".lower()

        # Check for high signal keywords (bug, glitch, banned, down, cpm spike, pixel, outage)
        is_high_signal = any(
            k in raw_text
            for k in [
                "ban", "disabled", "glitch", "bug", "down", "outage",
                "cpm", "spike", "pixel", "capi", "pmax", "tracking",
                "meta", "google ads", "tiktok", "suspension", "roas"
            ]
        )

        is_outage = any(k in raw_text for k in ["outage", "is meta down", "is facebook down", "ads not delivering", "broken"])

        if is_high_signal:
            updates.append({
                "platform": "community",
                "title": f"Reddit r/ppc: {title}",
                "original_url": entry["original_url"],
                "published_at": entry["published_at"],
                "category": "أعطال وسيستم" if is_outage else "مجتمع وميدان",
                "raw_content": entry["raw_content"][:1000],
                "is_outage": is_outage,
            })
    return updates


def scan_search_engine_land() -> List[Dict[str, Any]]:
    """Scans PPC and paid search industry feeds (Search Engine Land, PPC Hero, SEJ)."""
    updates = []
    feed_urls = [
        ("https://www.ppchero.com/feed/", "PPC Hero"),
        ("https://www.searchenginejournal.com/feed/", "Search Engine Journal"),
        ("https://searchengineland.com/channel/paid-search/feed", "Search Engine Land"),
        ("https://searchengineland.com/feed", "Search Engine Land"),
    ]

    for feed_url, source_name in feed_urls:
        entries = fetch_rss_feed(feed_url)
        if entries:
            for entry in entries[:6]:
                title = entry["title"]
                raw_text = f"{title} {entry['raw_content']}".lower()

                if any(k in raw_text for k in ["ad", "ppc", "google", "meta", "search", "campaign", "budget", "pmax", "tiktok", "bidding", "cpm"]):
                    updates.append({
                        "platform": "community",
                        "title": f"{source_name}: {title}",
                        "original_url": entry["original_url"],
                        "published_at": entry["published_at"],
                        "category": "ميزات جديدة",
                        "raw_content": entry["raw_content"][:1000],
                        "is_outage": False,
                    })
            if len(updates) >= 8:
                break
    return updates


def scan_community() -> List[Dict[str, Any]]:
    """Orchestrates community and industry feeds."""
    all_updates = []
    try:
        all_updates.extend(scan_reddit_ppc())
    except Exception as e:
        logger.error(f"Error in scan_reddit_ppc: {e}")

    try:
        all_updates.extend(scan_search_engine_land())
    except Exception as e:
        logger.error(f"Error in scan_search_engine_land: {e}")

    return all_updates
