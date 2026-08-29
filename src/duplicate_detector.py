"""
Duplicate detector module for Duplicate Application Manager.
Identifies duplicate file groups by content hash, updates database, and calculates space savings.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def find_duplicates(
    files: List[Dict[str, Any]],
    hasher_module: Any = None,
    db_manager: Any = None,
    threshold_mb: int = 100,
) -> List[Dict[str, Any]]:
    """
    Find duplicate files based on content hash.
    Computes hashes if missing, groups duplicates, updates database, and returns group statistics.
    
    Args:
        files: List of file metadata dicts (must contain file_path, file_size, etc.).
        hasher_module: Module or object providing compute_file_hash or hash_file.
        db_manager: Instance of DatabaseManager.
        threshold_mb: Large file threshold in MB for partial hashing.
        
    Returns:
        List of duplicate group dictionaries:
        - id (int, optional)
        - content_hash (str)
        - total_size (int)
        - duplicate_count (int)
        - potential_savings_bytes (int)
        - files (List[Dict])
    """
    if not files:
        return []

    # Step 1: Pre-group by file_size to avoid hashing unique file sizes
    size_groups: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for f in files:
        size_groups[f.get("file_size", 0)].append(f)

    # Candidates are files whose file_size is shared by at least 2 files
    candidates = [f for size, group in size_groups.items() if len(group) >= 2 for f in group]

    # Step 2: Compute/fetch hashes for candidates
    hash_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for f in candidates:
        file_path = f["file_path"]
        content_hash = f.get("content_hash")

        if not content_hash:
            if hasher_module and hasattr(hasher_module, "compute_file_hash"):
                content_hash = hasher_module.compute_file_hash(
                    file_path=file_path,
                    threshold_mb=threshold_mb,
                    db_manager=db_manager,
                    use_cache=True,
                )
            elif hasher_module and hasattr(hasher_module, "hash_file"):
                content_hash = hasher_module.hash_file(file_path)

        if content_hash:
            f["content_hash"] = content_hash
            hash_groups[content_hash].append(f)

    # Filter groups with at least 2 duplicates
    duplicate_results: List[Dict[str, Any]] = []

    for content_hash, group_files in hash_groups.items():
        if len(group_files) < 2:
            continue

        count = len(group_files)
        total_size = sum(gf.get("file_size", 0) for gf in group_files)
        # Potential savings = space that can be freed by keeping 1 file
        single_file_size = group_files[0].get("file_size", 0)
        potential_savings = (count - 1) * single_file_size

        group_record = {
            "content_hash": content_hash,
            "total_size": total_size,
            "duplicate_count": count,
            "potential_savings_bytes": potential_savings,
            "files": group_files,
        }

        # Step 3: Persist to database if db_manager provided
        if db_manager:
            try:
                # Add duplicate group record
                group_id = db_manager.add_duplicate_group(
                    content_hash=content_hash,
                    total_size=total_size,
                    duplicate_count=count,
                )
                group_record["id"] = group_id

                # Upsert applications and link to duplicate group
                for gf in group_files:
                    path = gf["file_path"]
                    name = gf["file_name"]
                    size = gf["file_size"]
                    cat_id = gf.get("category_id")

                    existing = db_manager.get_application_by_path(path)
                    if existing:
                        app_id = existing["id"]
                        db_manager.update_application(
                            app_id,
                            content_hash=content_hash,
                            is_duplicate=True,
                            duplicate_group_id=group_id,
                            category_id=cat_id or existing.get("category_id"),
                        )
                        gf["id"] = app_id
                    else:
                        app_id = db_manager.add_application(
                            file_path=path,
                            file_name=name,
                            file_size=size,
                            content_hash=content_hash,
                            category_id=cat_id,
                            is_duplicate=True,
                            duplicate_group_id=group_id,
                        )
                        gf["id"] = app_id

            except Exception as e:
                logger.warning(f"Error persisting duplicate group to database: {e}")

        duplicate_results.append(group_record)

    return duplicate_results


def get_duplicate_groups(db_manager: Any) -> List[Dict[str, Any]]:
    """
    Fetch all duplicate groups from database alongside their associated application records.
    
    Args:
        db_manager: Instance of DatabaseManager.
        
    Returns:
        List of group dictionaries.
    """
    if not db_manager:
        return []

    groups = db_manager.get_all_duplicate_groups()
    all_apps = db_manager.get_all_applications()

    # Index apps by duplicate_group_id
    apps_by_group = defaultdict(list)
    for app in all_apps:
        grp_id = app.get("duplicate_group_id")
        if grp_id:
            apps_by_group[grp_id].append(app)

    result = []
    for g in groups:
        g_id = g["id"]
        group_apps = apps_by_group.get(g_id, [])
        count = len(group_apps)
        total_size = g.get("total_size") or sum(a.get("file_size", 0) for a in group_apps)
        single_size = group_apps[0]["file_size"] if group_apps else 0
        potential_savings = max(0, (count - 1) * single_size)

        result.append({
            "id": g_id,
            "content_hash": g.get("content_hash"),
            "total_size": total_size,
            "duplicate_count": count or g.get("duplicate_count", 0),
            "potential_savings_bytes": potential_savings,
            "files": group_apps,
        })

    return result


def calculate_savings(duplicate_groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate summary statistics for space savings across duplicate groups.
    """
    total_groups = len(duplicate_groups)
    total_duplicate_files = sum(g.get("duplicate_count", 0) for g in duplicate_groups)
    redundant_files_count = sum(max(0, g.get("duplicate_count", 0) - 1) for g in duplicate_groups)
    total_space_bytes = sum(g.get("total_size", 0) for g in duplicate_groups)
    potential_savings_bytes = sum(g.get("potential_savings_bytes", 0) for g in duplicate_groups)

    return {
        "total_groups": total_groups,
        "total_duplicate_files": total_duplicate_files,
        "redundant_files_count": redundant_files_count,
        "total_space_bytes": total_space_bytes,
        "potential_savings_bytes": potential_savings_bytes,
        "potential_savings_mb": round(potential_savings_bytes / (1024 * 1024), 2),
        "potential_savings_gb": round(potential_savings_bytes / (1024 * 1024 * 1024), 2),
    }
