"""
Community & Industry PPC Radar Scanner.
Scans live advertiser communities on Reddit:
- r/facebookads: Active Meta advertisers, bans, delivery glitches, CAPI bugs
- r/ppc: Multi-platform PPC discussions (Google Ads, Meta, TikTok, PMax)
- r/adops: Ad Operations, tracking, DSPs, server-side attribution
- r/ecommerce: DTC media buying, scaling budgets, conversion drops

Enriches each update with `inferred_platform` (e.g. meta, google_ads, tiktok, etc.).
"""

import time
import logging
import requests
import feedparser
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from radar.scanners.base import clean_html, infer_platform
from radar.config import REQUEST_HEADERS

logger = logging.getLogger("radar.scanners.community")

# High-signal media buying keywords
SIGNAL_KEYWORDS = [
    "ban", "disabled", "glitch", "bug", "down", "outage",
    "cpm", "spike", "pixel", "capi", "pmax", "tracking",
    "meta", "facebook", "google ads", "tiktok", "suspension",
    "roas", "attribution", "spend", "scaling", "disapproved",
    "ad account", "cost per click", "cpa", "conversion"
]

OUTAGE_KEYWORDS = [
    "outage", "is meta down", "is facebook down", "ads not delivering",
    "broken", "zero impressions", "spend stopped", "reporting down",
    "manager down", "glitch", "bug"
]


def scan_reddit_sub(
    sub_name: str,
    default_platform: str = "community",
    session: Optional[requests.Session] = None,
    limit: int = 8,
) -> List[Dict[str, Any]]:
    """Scans a specific subreddit RSS feed with session cookies and rate-limit safety."""
    updates = []
    feed_url = f"https://www.reddit.com/r/{sub_name}/new/.rss"
    client = session or requests

    try:
        resp = client.get(
            feed_url,
            headers={
                **REQUEST_HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=10,
        )

        if resp.status_code == 200 and resp.content:
            parsed = feedparser.parse(resp.content)
            for entry in parsed.entries[:limit]:
                title = getattr(entry, "title", "").strip()
                raw_content = ""
                if hasattr(entry, "content") and entry.content:
                    raw_content = clean_html(entry.content[0].value)
                elif hasattr(entry, "summary") and entry.summary:
                    raw_content = clean_html(entry.summary)

                combined_lower = f"{title} {raw_content}".lower()

                # High signal check
                is_high_signal = any(k in combined_lower for k in SIGNAL_KEYWORDS)
                is_outage = any(k in combined_lower for k in OUTAGE_KEYWORDS)

                # Infer specific platform from content or fallback to sub's default
                inferred = infer_platform(title, raw_content, default=default_platform)

                if is_high_signal or sub_name == "facebookads":
                    updates.append({
                        "platform": inferred,
                        "inferred_platform": inferred,
                        "source_name": f"Reddit r/{sub_name}",
                        "title": f"Reddit r/{sub_name}: {title}",
                        "original_url": getattr(entry, "link", feed_url),
                        "published_at": getattr(entry, "published", datetime.now(timezone.utc).isoformat()),
                        "category": "أعطال وسيستم" if is_outage else "مجتمع وميدان",
                        "raw_content": raw_content[:1000],
                        "is_outage": is_outage,
                    })
        elif resp.status_code == 429:
            logger.warning(f"Reddit rate-limited (HTTP 429) for r/{sub_name}. Skipping gracefully.")
        else:
            logger.warning(f"Reddit returned HTTP {resp.status_code} for r/{sub_name}")

    except Exception as e:
        logger.warning(f"Error scanning Reddit r/{sub_name}: {e}")

    return updates


def scan_reddit_communities() -> List[Dict[str, Any]]:
    """Scans all targeted media buying subreddits."""
    all_updates = []
    session = requests.Session()
    # Warm up session
    try:
        session.get("https://www.reddit.com/", headers=REQUEST_HEADERS, timeout=5)
    except Exception:
        pass

    subreddits = [
        ("facebookads", "meta"),
        ("ppc", "google_ads"),
        ("adops", "community"),
        ("ecommerce", "community"),
    ]

    for sub_name, default_plat in subreddits:
        try:
            items = scan_reddit_sub(sub_name, default_platform=default_plat, session=session)
            all_updates.extend(items)
            time.sleep(1.0)  # Safe delay between calls to respect rate-limits
        except Exception as e:
            logger.error(f"Failed scanning r/{sub_name}: {e}")

    return all_updates


def scan_community() -> List[Dict[str, Any]]:
    """Orchestrates community scanner execution."""
    return scan_reddit_communities()
