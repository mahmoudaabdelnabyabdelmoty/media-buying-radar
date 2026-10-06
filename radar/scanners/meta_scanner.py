"""
Meta Ads Scanner (Facebook & Instagram).
Scans:
- MetaStatus for service disruptions / outages
- Meta Business Newsroom RSS
- Meta Developer Graph API / Marketing API Changelog
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import fetch_response, fetch_rss_feed, clean_html

logger = logging.getLogger("radar.scanners.meta")


def scan_metastatus() -> List[Dict[str, Any]]:
    """Checks MetaStatus API for active outages or recent incidents."""
    updates = []
    url = "https://metastatus.com/api/v2/summary.json"
    resp = fetch_response(url)
    if resp:
        try:
            data = resp.json()
            # Incidents check
            incidents = data.get("incidents", [])
            for inc in incidents[:5]:
                name = inc.get("name", "Meta Service Incident")
                status = inc.get("status", "investigating")
                updated_at = inc.get("updated_at") or datetime.now(timezone.utc).isoformat()
                incident_updates = inc.get("incident_updates", [])
                body = incident_updates[0].get("body", "") if incident_updates else "Incident reported on Meta Status."
                link = inc.get("shortlink") or "https://metastatus.com"

                updates.append({
                    "platform": "meta",
                    "title": f"[عطل في السيستم] Meta Status: {name} ({status})",
                    "original_url": link,
                    "published_at": updated_at,
                    "category": "أعطال وسيستم",
                    "raw_content": f"Status: {status}. Details: {body}",
                    "is_outage": True,
                })

            # Check status of specific components
            components = data.get("components", [])
            for comp in components:
                c_name = comp.get("name", "")
                c_status = comp.get("status", "")
                if c_status != "operational" and any(k in c_name.lower() for k in ["ads", "graph api", "instagram", "marketing"]):
                    updates.append({
                        "platform": "meta",
                        "title": f"[خلل تقني] خلل في خدمة {c_name} بشركة ميتا",
                        "original_url": "https://metastatus.com",
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": "أعطال وسيستم",
                        "raw_content": f"Component {c_name} status is currently {c_status}.",
                        "is_outage": True,
                    })
        except Exception as e:
            logger.warning(f"Failed parsing MetaStatus JSON: {e}")
    return updates


def scan_meta_business_news() -> List[Dict[str, Any]]:
    """Scans Meta official news feed (about.fb.com)."""
    updates = []
    feed_urls = [
        "https://about.fb.com/news/feed/",
        "https://about.fb.com/news/category/business/feed/",
    ]
    for feed_url in feed_urls:
        entries = fetch_rss_feed(feed_url)
        if entries:
            for entry in entries[:10]:
                text = f"{entry['title']} {entry['raw_content']}".lower()
                # Categorize based on business, AI, or advertising relevance
                cat = "ميزات جديدة"
                if any(k in text for k in ["ad", "business", "advertis", "monetiz", "partner", "commerce"]):
                    cat = "ميزات جديدة"
                updates.append({
                    "platform": "meta",
                    "title": f"Meta: {entry['title']}",
                    "original_url": entry["original_url"],
                    "published_at": entry["published_at"],
                    "category": cat,
                    "raw_content": entry["raw_content"],
                    "is_outage": False,
                })
            break
    return updates


def scan_meta_developer_changelog() -> List[Dict[str, Any]]:
    """Scans Meta Graph API and Marketing API changelog."""
    updates = []
    url = "https://developers.facebook.com/docs/graph-api/changelog/"
    resp = fetch_response(url)
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Look for version sections or headers
            sections = soup.find_all(["h2", "h3", "section"], limit=10)
            for sec in sections:
                title_text = sec.get_text().strip()
                if any(v in title_text.lower() for v in ["v2", "v1", "version", "marketing api", "changelog"]):
                    # Grab sibling text
                    next_p = sec.find_next("p")
                    content = next_p.get_text().strip() if next_p else "تحديث في إصدارات Meta Marketing API"
                    updates.append({
                        "platform": "meta",
                        "title": f"Meta Marketing API Changelog: {title_text}",
                        "original_url": url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": "تحديثات تقنية",
                        "raw_content": content,
                        "is_outage": False,
                    })
        except Exception as e:
            logger.warning(f"Error scraping Meta Developer Changelog: {e}")
    return updates


def scan_meta() -> List[Dict[str, Any]]:
    """Orchestrates all Meta scanning endpoints."""
    all_updates = []
    try:
        all_updates.extend(scan_metastatus())
    except Exception as e:
        logger.error(f"Error in scan_metastatus: {e}")

    try:
        all_updates.extend(scan_meta_business_news())
    except Exception as e:
        logger.error(f"Error in scan_meta_business_news: {e}")

    try:
        all_updates.extend(scan_meta_developer_changelog())
    except Exception as e:
        logger.error(f"Error in scan_meta_developer_changelog: {e}")

    return all_updates
