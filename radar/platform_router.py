"""
radar/platform_router.py
Intelligent Semantic Platform Router for Media Buying Radar.

Directs incoming industry news, community field alerts, and PPC articles to the correct
advertising platform tab:
- TikTok Ads (tiktok): TikTok, Spark Ads, TikTok Shop, ByteDance, FilmTok, BookTok, etc.
- Meta Ads (meta): Meta, Facebook, Instagram, Reels, Advantage+, CAPI, Threads, WhatsApp, etc.
- Google Ads (google_ads): Google Ads, PMax, YouTube, Performance Max, Search Ads, Merchant Center, etc.
- Snapchat Ads (snapchat): Snapchat, Snap, Spotlight, Lenses, AR Lenses, Spectacles, etc.
- LinkedIn Ads (linkedin): LinkedIn, B2B, InMail, Thought Leader, Matched Audiences, etc.
- X Ads (x_ads): X Ads, Twitter, Grok, Amplify, Tweets, X Developer, etc.
- Community (community): General PPC industry news, WordPress, broader SEO/web tools without platform focus.
"""

import re
import logging
import sqlite3
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger("radar.platform_router")

# Core platform detection rules and weighted lexicons
PLATFORM_RULES = {
    "tiktok": {
        "primary_keywords": [
            "tiktok", "tik tok", "spark ads", "tiktok shop", "bytedance",
            "filmtok", "booktok", "tt shop", "douyin", "tiktok ads",
            "tiktok pixel", "tiktok events api", "capcut", "tiktok marketing",
            "tiktok lead generation", "tiktok partner", "tiktok creator"
        ],
        "secondary_keywords": [
            "short-form video", "vertical video format", "sound-on"
        ],
        "patterns": [
            r"\btik\s*tok\b",
            r"\bspark\s+ads?\b",
            r"\bbytedance\b",
            r"\btiktok\s+shop\b",
            r"\bfilmtok\b",
            r"\bbooktok\b",
        ],
    },
    "meta": {
        "primary_keywords": [
            "meta", "facebook", "instagram", "reels", "advantage+", "advantage plus",
            "capi", "conversions api", "threads", "meta ads", "fb ads", "ig ads",
            "whatsapp", "click-to-whatsapp", "ray-ban meta", "meta horizon",
            "meta quest", "llama", "connect 2026", "facebook groups",
            "business manager", "commerce manager", "meta pixel", "meta verified",
            "meta status", "metastatus", "mark zuckerberg", "instagram reels",
            "teen accounts", "instant forms", "meta enterprise"
        ],
        "secondary_keywords": [
            "messenger", "whatsapp business", "meta graph api"
        ],
        "patterns": [
            r"\bmeta\b",
            r"\bfacebook\b",
            r"\binstagram\b",
            r"\breels\b",
            r"\badvantage\+\b",
            r"\badvantage\s+plus\b",
            r"\bcapi\b",
            r"\bthreads\b",
            r"\bwhatsapp\b",
        ],
    },
    "google_ads": {
        "primary_keywords": [
            "google ads", "pmax", "youtube", "performance max", "search ads",
            "merchant center", "google keyword", "google shopping", "demand gen",
            "admob", "dv360", "display & video 360", "google ads api", "ga4",
            "google analytics", "troas", "smart bidding", "search console",
            "google search", "ad words", "google tags", "google tag manager",
            "google ad", "paid search", "google target bid"
        ],
        "secondary_keywords": [
            "google", "helpful content"
        ],
        "patterns": [
            r"\bgoogle\s+ads?\b",
            r"\bpmax\b",
            r"\bperformance\s+max\b",
            r"\byoutube\b",
            r"\bmerchant\s+center\b",
            r"\bsearch\s+ads?\b",
            r"\bdemand\s+gen\b",
            r"\btroas\b",
            r"\bgoogle\s+shopping\b",
        ],
    },
    "microsoft": {
        "primary_keywords": [
            "microsoft advertising", "bing ads", "bing", "microsoft", "bing places",
            "microsoft ads", "copilot", "msft", "bing webmaster", "bing search"
        ],
        "secondary_keywords": [
            "edge browser", "msn"
        ],
        "patterns": [
            r"\bbing\b",
            r"\bmicrosoft\b",
            r"\bbing\s+ads?\b",
            r"\bmicrosoft\s+advertising\b",
        ],
    },
    "snapchat": {
        "primary_keywords": [
            "snapchat", "spotlight", "lenses", "ar lens", "ar lenses",
            "snap ads", "snap pixel", "spectacles", "snap for business",
            "snap inc", "snapchat marketing", "story ads", "snap status",
            "snapchat lenses", "snap audience", "snapchat ads"
        ],
        "secondary_keywords": [
            "snap map", "bitmoji"
        ],
        "patterns": [
            r"\bsnapchat\b",
            r"\bsnap\s+ads?\b",
            r"\bspotlight\b",
            r"\bar\s+lens(es)?\b",
            r"\bsnap\s+inc\b",
            r"\bsnap\s+for\s+business\b",
            r"\bsnap\s+marketing\b",
        ],
    },
    "linkedin": {
        "primary_keywords": [
            "linkedin", "b2b", "inmail", "thought leader", "thought leader ads",
            "linkedin ads", "matched audiences", "campaign manager",
            "linkedin marketing", "sales navigator", "b2b marketing",
            "sponsored content", "linkedin lead", "b2b campaign", "b2b campaigns"
        ],
        "secondary_keywords": [
            "lead gen forms", "professional network", "pipeline number"
        ],
        "patterns": [
            r"\blinkedin\b",
            r"\binmail\b",
            r"\bthought\s+leader(\s+ads)?\b",
            r"\bb2b\b",
            r"\blinkedin\s+marketing\b",
        ],
    },
    "x_ads": {
        "primary_keywords": [
            "x ads", "twitter", "grok", "amplify", "x developer", "tweet",
            "tweets", "x ad", "twitter ads", "x premium", "x analytics",
            "tweetdeck", "elon musk", "x platform", "x activity api"
        ],
        "secondary_keywords": [
            "retweet", "x subscriptions"
        ],
        "patterns": [
            r"\bx\s+ads?\b",
            r"\btwitter\b",
            r"\bgrok\b",
            r"\bamplify\b",
            r"\btweet(s)?\b",
            r"\bx\s+developer\b",
            r"\bx\s+(launches|re-builds|adds|rolls|tests|updates|announces|unveils|partners|expands)\b",
            r"\bx['’]s\b",
            r"\bx\s+platform\b",
        ],
    },
}

KNOWN_SPECIFIC_PLATFORMS = {"tiktok", "meta", "google_ads", "microsoft", "snapchat", "linkedin", "x_ads"}


def calculate_platform_scores(
    title: str,
    content: str = "",
    current_platform: str = "community"
) -> Dict[str, float]:
    """
    Computes weighted semantic scores for all advertising platforms based on title and content.
    Title matches are weighted 3.5x over body matches.
    Regex boundary matches receive extra high confidence scores.
    """
    title_norm = (title or "").lower()
    content_norm = (content or "").lower()
    combined_text = f"{title_norm} {content_norm}"

    scores: Dict[str, float] = {p: 0.0 for p in PLATFORM_RULES}

    # Baseline bias: if incoming item was already from a dedicated scanner, grant modest retention bias
    if current_platform in KNOWN_SPECIFIC_PLATFORMS:
        scores[current_platform] += 2.0

    for platform, rule in PLATFORM_RULES.items():
        # 1. Regex pattern matches (High precision)
        for pat in rule.get("patterns", []):
            if re.search(pat, title_norm, re.IGNORECASE):
                scores[platform] += 6.0
            elif re.search(pat, content_norm, re.IGNORECASE):
                scores[platform] += 3.0

        # 2. Primary keyword matches
        for kw in rule.get("primary_keywords", []):
            if kw in title_norm:
                scores[platform] += 4.5
            elif kw in content_norm:
                scores[platform] += 1.5

        # 3. Secondary keyword matches
        for kw in rule.get("secondary_keywords", []):
            if kw in title_norm:
                scores[platform] += 2.0
            elif kw in content_norm:
                scores[platform] += 0.8

    return scores


def route_platform(
    title: str,
    content: str = "",
    default_platform: str = "community",
    min_confidence: float = 3.0
) -> str:
    """
    Analyzes title and content to determine the most accurate target platform.
    Returns one of: 'tiktok', 'meta', 'google_ads', 'snapchat', 'linkedin', 'x_ads', or 'community'.
    """
    scores = calculate_platform_scores(title, content, current_platform=default_platform)

    # Sort descending by score
    sorted_platforms = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_platform, best_score = sorted_platforms[0]

    # If the highest score exceeds confidence threshold, route to it
    if best_score >= min_confidence:
        return best_platform

    # If current_platform is already a verified specific platform and no competitor has higher score
    if default_platform in KNOWN_SPECIFIC_PLATFORMS and best_score > 0:
        return default_platform

    # Fallback to default (usually 'community')
    return default_platform if default_platform else "community"


def route_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches and mutates a single update item with its routed platform and inferred_platform.
    """
    title = item.get("title", "")
    content = item.get("raw_content", "")
    current_plat = item.get("platform", "community")

    routed_plat = route_platform(title, content, default_platform=current_plat)
    item["platform"] = routed_plat
    item["inferred_platform"] = routed_plat

    # Auto-adjust category if not set or generic
    if item.get("category") in (None, "", "general", "community"):
        item["category"] = routed_plat

    return item


def reroute_database_records(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Audits and re-routes existing records in SQLite database (`radar.db`).
    Categorizes items originally marked as 'community' or imprecise platforms into their
    true platforms (TikTok, Meta, Google, Snapchat, LinkedIn, X).
    """
    from radar.config import DB_PATH
    target_db = db_path or DB_PATH

    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, platform, title, raw_content, original_url FROM updates")
        rows = cursor.fetchall()

        stats = {
            "total_examined": len(rows),
            "re_routed": 0,
            "breakdown_before": {},
            "breakdown_after": {},
            "transitions": []
        }

        for row in rows:
            old_p = row["platform"]
            stats["breakdown_before"][old_p] = stats["breakdown_before"].get(old_p, 0) + 1

            new_p = route_platform(row["title"], row["raw_content"], default_platform=old_p)
            
            # If changed, update the row in database
            if new_p != old_p:
                try:
                    cursor.execute(
                        "UPDATE updates SET platform = ?, inferred_platform = ? WHERE id = ?",
                        (new_p, new_p, row["id"])
                    )
                except Exception:
                    cursor.execute(
                        "UPDATE updates SET platform = ? WHERE id = ?",
                        (new_p, row["id"])
                    )
                stats["re_routed"] += 1
                stats["transitions"].append({
                    "id": row["id"],
                    "from": old_p,
                    "to": new_p,
                    "title": row["title"][:70]
                })

            stats["breakdown_after"][new_p] = stats["breakdown_after"].get(new_p, 0) + 1

        conn.commit()
        logger.info(f"Platform Router DB Audit Completed: {stats['re_routed']} records re-routed.")
        return stats

    finally:
        conn.close()


def get_platform_metrics(db_path: Optional[str] = None) -> Dict[str, int]:
    """Returns the current breakdown of updates per platform in SQLite."""
    from radar.config import DB_PATH
    target_db = db_path or DB_PATH

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT platform, COUNT(*) FROM updates GROUP BY platform")
        results = dict(cursor.fetchall())
        return results
    finally:
        conn.close()
