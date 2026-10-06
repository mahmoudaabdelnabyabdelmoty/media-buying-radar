"""
Configuration and Data Sources for Media Buying Platform Updates Radar.
Contains RSS feeds, Changelog endpoints, headers, and system paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
RADAR_DIR = BASE_DIR / "radar"
WEB_DIR = BASE_DIR / "web"
WEB_DATA_DIR = WEB_DIR / "data"

# Database & Output paths
DB_PATH = os.getenv("RADAR_DB_PATH", str(BASE_DIR / "radar.db"))
EXPORT_JSON_PATH = os.getenv("RADAR_EXPORT_PATH", str(WEB_DATA_DIR / "updates.json"))

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Request configuration
REQUEST_TIMEOUT = 15  # seconds
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (Compatible; MediaBuyingRadar/1.0; +https://github.com/media-buying-radar)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

# Platform Categories
PLATFORM_CATEGORIES = {
    "meta": "Meta (Facebook & Instagram)",
    "google_ads": "Google Ads",
    "tiktok": "TikTok Ads",
    "snapchat": "Snapchat Ads",
    "linkedin": "LinkedIn Ads",
    "x_ads": "X Ads (Twitter)",
    "community": "Community & Industry",
}

# Platform Source Definitions
SOURCES = {
    "meta": {
        "name": "Meta Ads",
        "category": "meta",
        "endpoints": [
            {
                "type": "rss",
                "name": "Meta Official News Feed",
                "url": "https://about.fb.com/news/feed/",
            },
            {
                "type": "status_html",
                "name": "MetaStatus Dashboard",
                "url": "https://metastatus.com/",
            },
            {
                "type": "html_changelog",
                "name": "Meta Graph API & Marketing API Changelog",
                "url": "https://developers.facebook.com/docs/graph-api/changelog/",
            },
        ],
    },
    "google_ads": {
        "name": "Google Ads",
        "category": "google_ads",
        "endpoints": [
            {
                "type": "rss",
                "name": "Google Ads Developer Blog",
                "url": "https://ads-developers.googleblog.com/feeds/posts/default?alt=rss",
            },
            {
                "type": "rss",
                "name": "Google Keyword Ads Feed",
                "url": "https://blog.google/products/ads-commerce/rss/",
            },
            {
                "type": "html_announcements",
                "name": "Google Ads Announcements",
                "url": "https://support.google.com/google-ads/announcements/9095107",
            },
        ],
    },
    "tiktok": {
        "name": "TikTok Ads",
        "category": "tiktok",
        "endpoints": [
            {
                "type": "rss",
                "name": "TikTok Newsroom Business",
                "url": "https://newsroom.tiktok.com/en-us/feed",
            },
            {
                "type": "html_changelog",
                "name": "TikTok Marketing API Changelog",
                "url": "https://ads.tiktok.com/marketing_api/docs?id=1701890906231810",
            },
        ],
    },
    "snapchat": {
        "name": "Snapchat Ads",
        "category": "snapchat",
        "endpoints": [
            {
                "type": "rss",
                "name": "Snap Newsroom Feed",
                "url": "https://newsroom.snap.com/rss",
            },
            {
                "type": "html_changelog",
                "name": "Snapchat Marketing API Releases",
                "url": "https://marketingapi.snapchat.com/docs/",
            },
        ],
    },
    "linkedin": {
        "name": "LinkedIn Ads",
        "category": "linkedin",
        "endpoints": [
            {
                "type": "rss",
                "name": "LinkedIn Marketing Solutions Blog",
                "url": "https://www.linkedin.com/business/marketing/blog/rss",
            },
            {
                "type": "html_changelog",
                "name": "LinkedIn Marketing Developer Changelog",
                "url": "https://learn.microsoft.com/en-us/linkedin/marketing/versioning",
            },
        ],
    },
    "x_ads": {
        "name": "X Ads",
        "category": "x_ads",
        "endpoints": [
            {
                "type": "html_changelog",
                "name": "X Developer Changelog",
                "url": "https://developer.x.com/en/updates/changelog",
            },
            {
                "type": "rss",
                "name": "X Ads Blog Feed",
                "url": "https://blog.x.com/en_us/topics/product/rss",
            },
        ],
    },
    "community": {
        "name": "PPC Communities & News",
        "category": "community",
        "endpoints": [
            {
                "type": "rss",
                "name": "PPC Hero Industry Feed",
                "url": "https://www.ppchero.com/feed/",
            },
            {
                "type": "rss",
                "name": "Search Engine Journal Paid Media Feed",
                "url": "https://www.searchenginejournal.com/feed/",
            },
            {
                "type": "rss",
                "name": "Search Engine Land PPC Feed",
                "url": "https://searchengineland.com/channel/paid-search/feed",
            },
            {
                "type": "rss",
                "name": "Reddit r/ppc Feed",
                "url": "https://www.reddit.com/r/ppc/new/.rss",
            },
        ],
    },
}
