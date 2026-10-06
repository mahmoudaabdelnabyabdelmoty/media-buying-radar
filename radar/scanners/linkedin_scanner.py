"""
LinkedIn Ads Scanner.
Scans:
- LinkedIn Marketing Solutions Blog RSS
- LinkedIn Marketing Developer Changelog & Versioning
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import fetch_response, fetch_rss_feed, clean_html

logger = logging.getLogger("radar.scanners.linkedin")


def scan_linkedin_marketing_blog() -> List[Dict[str, Any]]:
    """Scans LinkedIn Marketing Solutions Blog RSS."""
    updates = []
    feed_url = "https://www.linkedin.com/business/marketing/blog/rss"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        updates.append({
            "platform": "linkedin",
            "title": f"LinkedIn Ads: {entry['title']}",
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "ميزات جديدة",
            "raw_content": entry["raw_content"],
            "is_outage": False,
        })
    return updates


def scan_linkedin_developer_changelog() -> List[Dict[str, Any]]:
    """Scans Microsoft Learn LinkedIn Marketing API versioning & changelog."""
    updates = []
    url = "https://learn.microsoft.com/en-us/linkedin/marketing/versioning"
    resp = fetch_response(url)
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            versions = soup.find_all(["h2", "h3"], limit=10)
            for v in versions:
                text = v.get_text().strip()
                if any(k in text.lower() for k in ["version", "202", "changelog", "breaking change"]):
                    next_p = v.find_next(["p", "ul"])
                    desc = next_p.get_text().strip() if next_p else "LinkedIn Marketing API versioning update"
                    updates.append({
                        "platform": "linkedin",
                        "title": f"LinkedIn Marketing API: {text}",
                        "original_url": url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": "تحديثات تقنية",
                        "raw_content": desc,
                        "is_outage": False,
                    })
        except Exception as e:
            logger.warning(f"Error scraping LinkedIn API versioning: {e}")
    return updates


def scan_linkedin() -> List[Dict[str, Any]]:
    """Orchestrates all LinkedIn scanning endpoints."""
    all_updates = []
    try:
        all_updates.extend(scan_linkedin_marketing_blog())
    except Exception as e:
        logger.error(f"Error in scan_linkedin_marketing_blog: {e}")

    try:
        all_updates.extend(scan_linkedin_developer_changelog())
    except Exception as e:
        logger.error(f"Error in scan_linkedin_developer_changelog: {e}")

    return all_updates
