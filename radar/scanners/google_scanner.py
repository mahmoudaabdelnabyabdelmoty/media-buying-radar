"""
Google Ads Scanner.
Scans:
- Search Engine Roundtable (Google Ads & Algorithm Updates)
- Google Ads & Commerce Official Blog RSS (blog.google/products/ads-commerce/)
- Google Ads Developer Blog RSS
- Google Ads Official Announcements
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import fetch_response, fetch_rss_feed, clean_html

logger = logging.getLogger("radar.scanners.google")


def scan_seroundtable_google() -> List[Dict[str, Any]]:
    """Scans Search Engine Roundtable specifically for Google Ads, PMax, and search updates."""
    updates = []
    resp = fetch_response("https://www.seroundtable.com/")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            seen_links = set()
            for header in soup.find_all(["h2", "h3"], limit=20):
                a = header.find("a")
                if a and a.get("href"):
                    href = a["href"]
                    title = a.get_text().strip()
                    if not title or href in seen_links:
                        continue
                    seen_links.add(href)

                    full_url = href if href.startswith("http") else f"https://www.seroundtable.com{href}"
                    p_tag = header.find_next("p")
                    desc = clean_html(p_tag.get_text()) if p_tag else ""
                    raw = f"{title}. {desc}"

                    # Filter for Google / Search / Ads / Ranking / Algo
                    is_google_relevant = any(
                        k in raw.lower()
                        for k in [
                            "google", "ads", "search console", "pmax", "adwords",
                            "algorithm", "ranking", "update", "merchant", "youtube", "cpc"
                        ]
                    )
                    if not is_google_relevant:
                        continue

                    is_outage = any(k in raw.lower() for k in ["bug", "glitch", "delayed", "outage", "down", "issue"])
                    is_algo = any(k in raw.lower() for k in ["update", "algorithm", "ranking", "volatility", "core update"])

                    cat = "أعطال وسيستم" if is_outage else ("تعديلات خوارزمية" if is_algo else "ميزات جديدة")

                    updates.append({
                        "platform": "google_ads",
                        "inferred_platform": "google_ads",
                        "source_name": "Search Engine Roundtable",
                        "title": f"SERoundtable: {title}",
                        "original_url": full_url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": cat,
                        "raw_content": raw,
                        "is_outage": is_outage,
                    })
                    if len(updates) >= 6:
                        break
        except Exception as e:
            logger.warning(f"Error scraping Search Engine Roundtable in google_scanner: {e}")
    return updates


def scan_google_keyword_ads() -> List[Dict[str, Any]]:
    """Scans Google official Ads & Commerce Blog feed."""
    updates = []
    feed_url = "https://blog.google/products/ads-commerce/rss/"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:10]:
        updates.append({
            "platform": "google_ads",
            "inferred_platform": "google_ads",
            "source_name": "Google Ads & Commerce Blog",
            "title": f"Google Ads: {entry['title']}",
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "ميزات جديدة",
            "raw_content": entry["raw_content"],
            "is_outage": False,
        })
    return updates


def scan_google_ads_dev_blog() -> List[Dict[str, Any]]:
    """Scans Google Ads Developer Blog feed."""
    updates = []
    feed_url = "https://ads-developers.googleblog.com/feeds/posts/default?alt=rss"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        updates.append({
            "platform": "google_ads",
            "inferred_platform": "google_ads",
            "source_name": "Google Ads Developer Blog",
            "title": f"Google Ads Dev: {entry['title']}",
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "تحديثات تقنية",
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
            articles = soup.find_all(["h2", "h3", "li"], limit=12)
            for item in articles:
                text = item.get_text().strip()
                if len(text) > 20 and any(k in text.lower() for k in ["ads", "policy", "campaign", "smart bidding", "pmax", "update", "202"]):
                    updates.append({
                        "platform": "google_ads",
                        "inferred_platform": "google_ads",
                        "source_name": "Google Ads Announcements",
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
        all_updates.extend(scan_google_keyword_ads())
    except Exception as e:
        logger.error(f"Error in scan_google_keyword_ads: {e}")

    try:
        all_updates.extend(scan_seroundtable_google())
    except Exception as e:
        logger.error(f"Error in scan_seroundtable_google: {e}")

    try:
        all_updates.extend(scan_google_ads_dev_blog())
    except Exception as e:
        logger.error(f"Error in scan_google_ads_dev_blog: {e}")

    try:
        all_updates.extend(scan_google_ads_announcements())
    except Exception as e:
        logger.error(f"Error in scan_google_ads_announcements: {e}")

    return all_updates
