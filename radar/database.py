"""
Database Engine for Media Buying Platform Updates Radar.
Handles SQLite storage, SHA-256 deduplication, queries, and JSON export for the frontend dashboard.
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from radar.config import DB_PATH, EXPORT_JSON_PATH


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates and returns a SQLite database connection with row factory enabled."""
    target_path = db_path or DB_PATH
    Path(target_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the updates table and necessary indexes."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    title TEXT NOT NULL,
                    original_url TEXT NOT NULL,
                    published_at TEXT,
                    category TEXT,
                    raw_content TEXT,
                    egyptian_summary TEXT,
                    media_buyer_impact TEXT,
                    hash_sha256 TEXT UNIQUE NOT NULL,
                    is_outage INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now', 'utc'))
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_updates_hash ON updates(hash_sha256);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_updates_platform ON updates(platform);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_updates_published ON updates(published_at);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_updates_outage ON updates(is_outage);"
            )
    finally:
        conn.close()


def generate_content_hash(platform: str, title: str, original_url: str) -> str:
    """
    Computes a deterministic SHA-256 hash for deduplication based on platform, title, and url.
    Normalizes whitespace and casing.
    """
    normalized_raw = f"{platform.strip().lower()}|{title.strip().lower()}|{original_url.strip()}"
    return hashlib.sha256(normalized_raw.encode("utf-8")).hexdigest()


def is_duplicate(hash_sha256: str, db_path: Optional[str] = None) -> bool:
    """Checks whether an update with the given SHA-256 hash already exists in the database."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM updates WHERE hash_sha256 = ? LIMIT 1", (hash_sha256,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def save_update(update_data: Dict[str, Any], db_path: Optional[str] = None) -> Optional[int]:
    """
    Inserts a new update record into the database.
    Returns the inserted ID, or None if already exists (deduplicated).
    """
    platform = update_data.get("platform", "general").strip()
    title = update_data.get("title", "").strip()
    original_url = update_data.get("original_url", "").strip()

    hash_sha256 = update_data.get("hash_sha256") or generate_content_hash(platform, title, original_url)

    if is_duplicate(hash_sha256, db_path):
        return None

    published_at = update_data.get("published_at")
    if not published_at:
        published_at = datetime.now(timezone.utc).isoformat()

    created_at = update_data.get("created_at") or datetime.now(timezone.utc).isoformat()
    is_outage = 1 if update_data.get("is_outage") else 0

    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO updates (
                    platform, title, original_url, published_at, category,
                    raw_content, egyptian_summary, media_buyer_impact,
                    hash_sha256, is_outage, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    platform,
                    title,
                    original_url,
                    published_at,
                    update_data.get("category", platform),
                    update_data.get("raw_content", ""),
                    update_data.get("egyptian_summary", ""),
                    update_data.get("media_buyer_impact", ""),
                    hash_sha256,
                    is_outage,
                    created_at,
                ),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_recent_updates(limit: int = 150, platform: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves the latest updates sorted by published_at / created_at descending."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        if platform:
            cursor.execute(
                """
                SELECT * FROM updates
                WHERE platform = ?
                ORDER BY datetime(COALESCE(published_at, created_at)) DESC, id DESC
                LIMIT ?
                """,
                (platform, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM updates
                ORDER BY datetime(COALESCE(published_at, created_at)) DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_stats(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Computes total counts, per-platform counts, and active outages."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM updates")
        total_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM updates WHERE is_outage = 1")
        total_outages = cursor.fetchone()[0]

        cursor.execute("SELECT platform, COUNT(*) as count FROM updates GROUP BY platform")
        by_platform = {row["platform"]: row["count"] for row in cursor.fetchall()}

        return {
            "total_updates": total_count,
            "total_outages": total_outages,
            "platforms": by_platform,
        }
    finally:
        conn.close()


def export_to_json(filepath: Optional[str] = None, limit: int = 200, db_path: Optional[str] = None) -> str:
    """
    Exports recent updates cleanly to JSON format to be read directly
    by the web dashboard (`web/data/updates.json`).
    Enriches each record with frontend-friendly keys (platformName, categoryLabel, summary_egyptian, etc.)
    """
    target_path = Path(filepath or EXPORT_JSON_PATH)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    updates = get_recent_updates(limit=limit, db_path=db_path)
    stats = get_stats(db_path=db_path)

    platform_display_map = {
        "meta": "Meta Ads",
        "google": "Google Ads",
        "google_ads": "Google Ads",
        "tiktok": "TikTok Ads",
        "snapchat": "Snapchat Ads",
        "linkedin": "LinkedIn Ads",
        "x": "X Ads",
        "x_ads": "X Ads",
        "community": "مجتمعات المسوقين",
    }

    category_slug_map = {
        "outage": ("outage", "🚨 عطل فني"),
        "أعطال وسيستم": ("outage", "🚨 عطل فني"),
        "feature": ("feature", "🚀 ميزة جديدة"),
        "ميزات جديدة": ("feature", "🚀 ميزة جديدة"),
        "تحديثات تقنية": ("feature", "⚙️ تحديث تقني"),
        "policy": ("policy", "⚠️ سياسات وحظر"),
        "سياسات وحظر": ("policy", "⚠️ سياسات وحظر"),
        "algorithm": ("algorithm", "⚡ تعديل خوارزمي"),
        "تعديلات خوارزمية": ("algorithm", "⚡ تعديل خوارزمي"),
        "تتبع وبيكسل": ("algorithm", "🎯 تتبع وبيكسل"),
        "مزادات وCPM": ("algorithm", "💰 مزادات وCPM"),
        "استهداف وجمهور": ("feature", "👥 استهداف وجمهور"),
    }

    enriched_updates = []
    for item in updates:
        row = dict(item)
        plat = row.get("platform", "")
        clean_plat = "google" if plat == "google_ads" else ("x" if plat == "x_ads" else plat)

        is_out = bool(row.get("is_outage"))
        cat_raw = row.get("category", "feature")
        cat_slug, cat_label = category_slug_map.get(cat_raw, ("feature", cat_raw or "💡 تحديث منصة"))
        if is_out:
            cat_slug = "outage"
            cat_label = "🚨 عطل فني"

        # Provide frontend-compatible keys alongside raw db keys
        row["platform"] = clean_plat
        row["raw_platform"] = plat
        row["platformName"] = platform_display_map.get(plat, clean_plat)
        row["category"] = cat_slug
        row["categoryLabel"] = cat_label
        row["summary_egyptian"] = row.get("egyptian_summary", "")
        row["buyer_impact"] = row.get("media_buyer_impact", "")
        row["source_url"] = row.get("original_url", "")
        row["source_name"] = platform_display_map.get(plat, "المصدر الرسمي")
        row["timestamp"] = row.get("published_at") or row.get("created_at") or datetime.now(timezone.utc).isoformat()
        row["is_outage"] = is_out
        enriched_updates.append(row)

    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_updates": stats["total_updates"],
            "total_outages": stats["total_outages"],
            "platform_breakdown": stats["platforms"],
            "engine_version": "1.0.0",
        },
        "updates": enriched_updates,
    }

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return str(target_path)

