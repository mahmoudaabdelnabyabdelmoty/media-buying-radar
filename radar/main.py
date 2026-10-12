"""
Main Radar Engine Runner.
Orchestrates:
1. Intelligent Platform Router auditing existing records & newly scanned items
2. Running all platform scanners
3. Deduplication check via SHA-256
4. Summarization cascade (Gemini -> Groq -> Smart Egyptian Rule-Based)
5. SQLite persistence (radar.db)
6. Exporting clean JSON for web dashboard (web/data/updates.json)
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from radar.config import DB_PATH, EXPORT_JSON_PATH
from radar.database import (
    init_db,
    save_update,
    is_duplicate,
    generate_content_hash,
    export_to_json,
    get_stats,
)
from radar.llm_summarizer import summarize_update
from radar.platform_router import route_platform, reroute_database_records
from radar.scanners import ALL_SCANNERS

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("radar.engine")


def run_radar_cycle(
    target_platform: str = None,
    export_path: str = None,
    db_path: str = None,
    dry_run: bool = False,
) -> dict:
    """
    Executes one complete radar scan cycle.
    Returns summary metrics of the cycle.
    """
    logger.info("=" * 60)
    logger.info("🛰️ تشغيل رادار تحديثات منصات الإعلانات الممولة (Media Buying Radar)")
    logger.info(f"⏰ وقت البدء: {datetime.now(timezone.utc).isoformat()}")
    logger.info("=" * 60)

    # 1. Initialize Database & Audit existing records with Intelligent Platform Router
    init_db(db_path=db_path)
    if not dry_run:
        audit_stats = reroute_database_records(db_path=db_path)
        if audit_stats["re_routed"] > 0:
            logger.info(f"🧭 تم فحص القاعدة وإعادة توجيه {audit_stats['re_routed']} خبراً عبر الموجه الذكي.")

    scanners_to_run = {}
    if target_platform:
        if target_platform in ALL_SCANNERS:
            scanners_to_run[target_platform] = ALL_SCANNERS[target_platform]
        else:
            logger.error(f"Platform '{target_platform}' not found in registered scanners.")
            return {"error": "Invalid platform"}
    else:
        scanners_to_run = ALL_SCANNERS

    total_scanned = 0
    total_new = 0
    total_skipped = 0
    total_routed = 0

    # 2. Run Scanners
    for platform_key, scanner_func in scanners_to_run.items():
        logger.info(f"🔍 جاري فحص مصادر: [{platform_key}] ...")
        try:
            items = scanner_func()
            logger.info(f"   رصد {len(items)} عنصر من مصادر [{platform_key}].")
            total_scanned += len(items)

            for item in items:
                title = item.get("title", "").strip()
                url = item.get("original_url", "").strip()
                raw_content = item.get("raw_content", "")
                incoming_platform = item.get("platform", platform_key)

                # Intelligent Platform Routing
                platform = route_platform(title, raw_content, default_platform=incoming_platform)
                item["platform"] = platform
                item["inferred_platform"] = item.get("inferred_platform") or platform
                if platform != incoming_platform:
                    total_routed += 1
                    logger.info(f"   🧭 توجيه ذكي: تحويل المنصة من [{incoming_platform}] إلى [{platform}] | {title[:50]}")

                # Deduplication check
                content_hash = generate_content_hash(platform, title, url)
                if is_duplicate(content_hash, db_path=db_path):
                    total_skipped += 1
                    continue

                logger.info(f"✨ تحديث جديد تم رصده [{platform}]: [{title[:60]}...]")

                # Summarize via LLM cascade (Gemini -> Groq -> Smart Rule-based Egyptian)
                summary_data = summarize_update(title, raw_content, platform)

                # Merge processed data
                item["hash_sha256"] = content_hash
                item["egyptian_summary"] = summary_data.get("egyptian_summary", "")
                item["media_buyer_impact"] = summary_data.get("media_buyer_impact", "")
                item["category"] = summary_data.get("category", item.get("category", platform))
                # If scanner or LLM flagged outage, mark as outage
                item["is_outage"] = bool(item.get("is_outage") or summary_data.get("is_outage"))

                if not dry_run:
                    row_id = save_update(item, db_path=db_path)
                    if row_id:
                        total_new += 1
                        logger.info(f"   💾 تم الحفظ بنجاح (ID: {row_id} - [{platform}])")
                else:
                    total_new += 1
                    logger.info("   [Dry Run] تخطي الحفظ الفعلي.")

        except Exception as e:
            logger.error(f"❌ خطأ أثناء فحص المصادر [{platform_key}]: {e}", exc_info=True)

    # 3. Export to JSON for frontend dashboard
    json_dest = export_path or EXPORT_JSON_PATH
    if not dry_run:
        saved_file = export_to_json(filepath=json_dest, db_path=db_path)
        logger.info(f"📄 تم تصدير بيانات الرادار إلى: {saved_file}")
    else:
        logger.info("[Dry Run] تخطي تصدير ملف الـ JSON.")

    # 4. Final Stats
    stats = get_stats(db_path=db_path)
    logger.info("=" * 60)
    logger.info("📊 تقرير دورة الرادار:")
    logger.info(f"   - إجمالي العناصر المفحوصة: {total_scanned}")
    logger.info(f"   - عناصر جديدة تمت معالجتها وحفظها: {total_new}")
    logger.info(f"   - عناصر متكررة تم تجاهلها: {total_skipped}")
    logger.info(f"   - عناصر أعيد توجيهها بالذكاء الدلالي: {total_routed}")
    logger.info(f"   - إجمالي التحديثات المخزنة في القاعدة: {stats['total_updates']}")
    logger.info(f"   - الأعطال النشطة المرصودة: {stats['total_outages']}")
    logger.info("   - توزيع المنصات في القاعدة الآن:")
    for p_name, count in stats["platforms"].items():
        logger.info(f"     * {p_name}: {count} تحديث")
    logger.info("=" * 60)

    return {
        "scanned": total_scanned,
        "new": total_new,
        "skipped": total_skipped,
        "routed": total_routed,
        "stats": stats,
        "export_path": json_dest,
    }


def main():
    parser = argparse.ArgumentParser(description="Media Buying Radar Engine")
    parser.add_argument("--platform", type=str, help="Filter scan to a specific platform (e.g. meta, google_ads)")
    parser.add_argument("--export-path", type=str, help="Custom path for updates.json export")
    parser.add_argument("--db-path", type=str, help="Custom SQLite db path")
    parser.add_argument("--dry-run", action="store_true", help="Perform scan and summarization without saving to database")
    parser.add_argument("--export-only", action="store_true", help="Only export current database to JSON without scanning")

    args = parser.parse_args()

    if args.export_only:
        init_db(db_path=args.db_path)
        out = export_to_json(filepath=args.export_path, db_path=args.db_path)
        print(f"Exported to {out}")
        sys.exit(0)

    result = run_radar_cycle(
        target_platform=args.platform,
        export_path=args.export_path,
        db_path=args.db_path,
        dry_run=args.dry_run,
    )

    if "error" in result:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
