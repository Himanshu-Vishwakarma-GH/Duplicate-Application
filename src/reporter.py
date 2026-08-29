"""
Reporter module for Duplicate Application Manager.
Compiles summary statistics and exports report to JSON or plain Text format.
"""

import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def generate_summary(db_manager: Any) -> Dict[str, Any]:
    """
    Compile a complete summary dictionary from the database.
    
    Args:
        db_manager: Instance of DatabaseManager.
        
    Returns:
        Summary statistics dictionary.
    """
    if not db_manager:
        return {
            "total_applications": 0,
            "duplicate_applications": 0,
            "duplicate_groups_count": 0,
            "categories_count": 0,
            "total_space_bytes": 0,
            "potential_savings_bytes": 0,
            "category_breakdown": [],
            "top_duplicates": [],
        }

    apps = db_manager.get_all_applications()
    dupes = db_manager.get_duplicates()
    groups = db_manager.get_all_duplicate_groups()
    categories = db_manager.get_all_categories()

    total_apps = len(apps)
    total_dupes = len(dupes)
    total_groups = len(groups)

    total_space = sum(a.get("file_size", 0) for a in apps)

    # Compute potential savings
    potential_savings = 0
    for g in groups:
        grp_id = g["id"]
        grp_apps = [a for a in apps if a.get("duplicate_group_id") == grp_id]
        if grp_apps:
            single_size = grp_apps[0].get("file_size", 0)
            cnt = len(grp_apps)
            potential_savings += max(0, (cnt - 1) * single_size)

    # Category breakdown
    cat_stats = []
    cat_map = {c["id"]: c["name"] for c in categories}

    for c in categories:
        cid = c["id"]
        capps = [a for a in apps if a.get("category_id") == cid]
        cat_stats.append({
            "id": cid,
            "name": c["name"],
            "count": len(capps),
            "total_size_bytes": sum(a.get("file_size", 0) for a in capps),
        })

    # Uncategorized count
    uncat_apps = [a for a in apps if a.get("category_id") is None]
    if uncat_apps:
        cat_stats.append({
            "id": None,
            "name": "Uncategorized",
            "count": len(uncat_apps),
            "total_size_bytes": sum(a.get("file_size", 0) for a in uncat_apps),
        })

    # Top duplicate groups list
    top_dupes = []
    for g in groups[:10]:
        grp_id = g["id"]
        grp_apps = [a for a in apps if a.get("duplicate_group_id") == grp_id]
        if grp_apps:
            top_dupes.append({
                "group_id": grp_id,
                "content_hash": g.get("content_hash"),
                "file_count": len(grp_apps),
                "file_name": grp_apps[0].get("file_name"),
                "single_file_size": grp_apps[0].get("file_size"),
                "files": [a.get("file_path") for a in grp_apps],
            })

    return {
        "total_applications": total_apps,
        "duplicate_applications": total_dupes,
        "duplicate_groups_count": total_groups,
        "categories_count": len(categories),
        "total_space_bytes": total_space,
        "total_space_mb": round(total_space / (1024 * 1024), 2),
        "potential_savings_bytes": potential_savings,
        "potential_savings_mb": round(potential_savings / (1024 * 1024), 2),
        "category_breakdown": cat_stats,
        "top_duplicates": top_dupes,
    }


def export_json(stats: Dict[str, Any], output_path: str) -> None:
    """Export summary dictionary to a JSON file."""
    parent_dir = os.path.dirname(output_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Summary report exported to JSON: {output_path}")
    except Exception as e:
        logger.error(f"Failed to export JSON report to {output_path}: {e}")
        raise


def export_text(stats: Dict[str, Any], output_path: str) -> None:
    """Export summary report to plain formatted text file."""
    parent_dir = os.path.dirname(output_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    lines = [
        "=" * 60,
        "DUPLICATE APPLICATION MANAGER - SUMMARY REPORT",
        "=" * 60,
        f"Total Applications Scanned: {stats.get('total_applications', 0)}",
        f"Duplicate Applications Found: {stats.get('duplicate_applications', 0)}",
        f"Duplicate Groups: {stats.get('duplicate_groups_count', 0)}",
        f"Total Space Consumed: {stats.get('total_space_mb', 0)} MB",
        f"Potential Space Savings: {stats.get('potential_savings_mb', 0)} MB",
        "-" * 60,
        "CATEGORY BREAKDOWN:",
    ]

    for cat in stats.get("category_breakdown", []):
        size_mb = round(cat.get("total_size_bytes", 0) / (1024 * 1024), 2)
        lines.append(f"  • {cat.get('name')}: {cat.get('count')} apps ({size_mb} MB)")

    lines.append("-" * 60)
    lines.append("TOP DUPLICATE GROUPS:")

    for g in stats.get("top_duplicates", []):
        lines.append(
            f"  [Group #{g.get('group_id')}] Hash: {g.get('content_hash')} ({g.get('file_count')} copies)"
        )
        for fp in g.get("files", []):
            lines.append(f"    - {fp}")

    lines.append("=" * 60)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"Summary report exported to Text: {output_path}")
    except Exception as e:
        logger.error(f"Failed to export Text report to {output_path}: {e}")
        raise
