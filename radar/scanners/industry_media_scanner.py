"""
Industry Media & Professional Publications Scanner.
Ingests:
- Social Media Today (Daily social advertising coverage: TikTok, Meta, Snap, X, LinkedIn)
- Search Engine Roundtable (Google Ads & search algorithm radar)
- Jon Loomer Digital (Specialized Meta Ads strategy and changes)
- MarTech (AdTech platforms, marketing automation, data privacy)
- Search Engine Land (Paid Search and digital media)
- Marketing Dive (Advertising agency and platform spend shifts)
- Modern Retail (E-commerce media buying, DTC performance marketing)
- PPC Hero & Search Engine Journal (Tactical PPC & Paid Media)

Enriches all articles with `inferred_platform`:
Routes each article into 'meta', 'google_ads', 'tiktok', 'snapchat', 'linkedin', 'x_ads', or 'community'.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from radar.scanners.base import (
    fetch_response,
    fetch_rss_feed,
    clean_html,
    infer_platform,
)

logger = logging.getLogger("radar.scanners.industry_media")


def scan_social_media_today() -> List[Dict[str, Any]]:
    """Scans Social Media Today for daily platform news and social ad developments."""
    updates = []
    feed_url = "https://www.socialmediatoday.com/feeds/news/"
    entries = fetch_rss_feed(feed_url)

    if not entries:
        # Fallback to direct HTML scrape if RSS unavailable
        resp = fetch_response("https://www.socialmediatoday.com/")
        if resp:
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    title = link.get_text().strip()
                    if "/news/" in href and len(title) > 25:
                        full_url = href if href.startswith("http") else f"https://www.socialmediatoday.com{href}"
                        entries.append({
                            "title": title,
                            "original_url": full_url,
                            "published_at": datetime.now(timezone.utc).isoformat(),
                            "raw_content": f"Social Media Today report: {title}",
                        })
                        if len(entries) >= 10:
                            break
            except Exception as e:
                logger.warning(f"Error scraping Social Media Today HTML: {e}")

    for entry in entries[:12]:
        title = entry["title"]
        content = entry["raw_content"]
        inferred = infer_platform(title, content, default="community")
        is_outage = any(k in f"{title} {content}".lower() for k in ["outage", "glitch", "down", "bug", "reporting delay"])

        updates.append({
            "platform": inferred,
            "inferred_platform": inferred,
            "source_name": "Social Media Today",
            "title": f"Social Media Today: {title}",
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "أعطال وسيستم" if is_outage else "ميزات جديدة",
            "raw_content": content,
            "is_outage": is_outage,
        })
    return updates


def scan_seroundtable() -> List[Dict[str, Any]]:
    """Scans Search Engine Roundtable for Google Ads and search algorithm shifts."""
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

                    inferred = infer_platform(title, desc, default="google_ads")
                    is_outage = any(k in raw.lower() for k in ["bug", "glitch", "delayed", "outage", "down", "issue"])
                    is_algo = any(k in raw.lower() for k in ["update", "algorithm", "ranking", "volatility", "spam update", "pmax"])

                    cat = "أعطال وسيستم" if is_outage else ("تعديلات خوارزمية" if is_algo else "ميزات جديدة")

                    updates.append({
                        "platform": inferred,
                        "inferred_platform": inferred,
                        "source_name": "Search Engine Roundtable",
                        "title": f"Search Engine Roundtable: {title}",
                        "original_url": full_url,
                        "published_at": datetime.now(timezone.utc).isoformat(),
                        "category": cat,
                        "raw_content": raw,
                        "is_outage": is_outage,
                    })
                    if len(updates) >= 8:
                        break
        except Exception as e:
            logger.warning(f"Error scraping Search Engine Roundtable HTML: {e}")
    return updates


def scan_jon_loomer() -> List[Dict[str, Any]]:
    """Scans Jon Loomer Digital for expert Meta Ads tutorials and platform changes."""
    updates = []
    feed_url = "https://www.jonloomer.com/feed/"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:10]:
        title = entry["title"]
        content = entry["raw_content"]
        inferred = infer_platform(title, content, default="meta")
        updates.append({
            "platform": inferred,
            "inferred_platform": inferred,
            "source_name": "Jon Loomer Digital",
            "title": f"Jon Loomer: {title}",
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "ميزات جديدة",
            "raw_content": content,
            "is_outage": False,
        })
    return updates


def scan_martech() -> List[Dict[str, Any]]:
    """Scans MarTech for enterprise ad-tech, identity solutions, and platform news."""
    updates = []
    feed_url = "https://martech.org/feed/"
    entries = fetch_rss_feed(feed_url)
    for entry in entries[:8]:
        title = entry["title"]
        content = entry["raw_content"]
        inferred = infer_platform(title, content, default="community")
        updates.append({
            "platform": inferred,
            "inferred_platform": inferred,
            "source_name": "MarTech",
            "title": f"MarTech: {title}",
            "original_url": entry["original_url"],
            "published_at": entry["published_at"],
            "category": "تحديثات تقنية",
            "raw_content": content,
            "is_outage": False,
        })
    return updates


def scan_additional_media() -> List[Dict[str, Any]]:
    """Scans Marketing Dive, Modern Retail, PPC Hero, and Search Engine Journal."""
    updates = []
    media_sources = [
        ("Marketing Dive", "https://www.marketingdive.com/feeds/news/"),
        ("Modern Retail", "https://www.modernretail.co/feed/"),
        ("PPC Hero", "https://www.ppchero.com/feed/"),
        ("Search Engine Journal", "https://www.searchenginejournal.com/feed/"),
        ("Search Engine Land", "https://searchengineland.com/channel/paid-search/feed"),
    ]

    for name, feed_url in media_sources:
        try:
            entries = fetch_rss_feed(feed_url)
            for entry in entries[:5]:
                title = entry["title"]
                content = entry["raw_content"]
                # Filter for advertising relevance
                combined = f"{title} {content}".lower()
                is_ad_related = any(
                    k in combined
                    for k in [
                        "ad", "ppc", "meta", "google", "tiktok", "amazon", "budget",
                        "retail media", "cpm", "roas", "campaign", "search", "pmax",
                        "creative", "social media", "shopping", "ecommerce"
                    ]
                )
                if not is_ad_related:
                    continue

                inferred = infer_platform(title, content, default="community")
                is_outage = any(k in combined for k in ["outage", "glitch", "down", "suspended", "ban wave"])

                updates.append({
                    "platform": inferred,
                    "inferred_platform": inferred,
                    "source_name": name,
                    "title": f"{name}: {title}",
                    "original_url": entry["original_url"],
                    "published_at": entry["published_at"],
                    "category": "أعطال وسيستم" if is_outage else "ميزات جديدة",
                    "raw_content": content,
                    "is_outage": is_outage,
                })
        except Exception as e:
            logger.warning(f"Error fetching {name} ({feed_url}): {e}")

    return updates


def scan_industry_media() -> List[Dict[str, Any]]:
    """Orchestrates all industry media scanners."""
    all_updates = []
    try:
        all_updates.extend(scan_social_media_today())
    except Exception as e:
        logger.error(f"Error in scan_social_media_today: {e}")

    try:
        all_updates.extend(scan_seroundtable())
    except Exception as e:
        logger.error(f"Error in scan_seroundtable: {e}")

    try:
        all_updates.extend(scan_jon_loomer())
    except Exception as e:
        logger.error(f"Error in scan_jon_loomer: {e}")

    try:
        all_updates.extend(scan_martech())
    except Exception as e:
        logger.error(f"Error in scan_martech: {e}")

    try:
        all_updates.extend(scan_additional_media())
    except Exception as e:
        logger.error(f"Error in scan_additional_media: {e}")

    return all_updates
