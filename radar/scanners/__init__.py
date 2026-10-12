"""
Radar Scanners Package.
Exports all platform-specific scanners and multi-source industry scanners.
"""

from radar.scanners.meta_scanner import scan_meta
from radar.scanners.google_scanner import scan_google_ads
from radar.scanners.tiktok_scanner import scan_tiktok
from radar.scanners.snapchat_scanner import scan_snapchat
from radar.scanners.linkedin_scanner import scan_linkedin
from radar.scanners.x_scanner import scan_x
from radar.scanners.community_scanner import scan_community
from radar.scanners.industry_media_scanner import scan_industry_media

ALL_SCANNERS = {
    "meta": scan_meta,
    "google_ads": scan_google_ads,
    "tiktok": scan_tiktok,
    "snapchat": scan_snapchat,
    "linkedin": scan_linkedin,
    "x_ads": scan_x,
    "community": scan_community,
    "industry_media": scan_industry_media,
}

__all__ = [
    "scan_meta",
    "scan_google_ads",
    "scan_tiktok",
    "scan_snapchat",
    "scan_linkedin",
    "scan_x",
    "scan_community",
    "scan_industry_media",
    "ALL_SCANNERS",
]
