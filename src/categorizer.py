"""
Categorizer module for Duplicate Application Manager.
Applies priority-ordered rules (path_contains, extension, size_range, path_matches) to categorize applications.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def load_rules(rules_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load rules from JSON file and return category rules list sorted by priority.
    
    Args:
        rules_path: Path to rules.json file.
        
    Returns:
        List of category dictionaries ordered by priority ascending.
    """
    path = rules_path or "config/rules.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        categories = data.get("categories", [])
        # Sort categories by priority ascending (lower number = higher priority)
        return sorted(categories, key=lambda c: c.get("priority", 999))
    except Exception as e:
        logger.warning(f"Failed to load rules from {path}: {e}")
        return []


def matches_rule(file_info: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """
    Evaluate a single rule against file metadata.
    
    Rule types supported:
    - path_contains: value (str), case_sensitive (bool)
    - extension: values (List[str]) or value (str)
    - size_range: min_mb (float), max_mb (float)
    - path_matches: pattern (str)
    """
    rule_type = rule.get("type")
    file_path = file_info.get("file_path", "")
    extension = file_info.get("extension", "").lower()
    file_size = file_info.get("file_size", 0)

    if rule_type == "path_contains":
        val = rule.get("value", "")
        if not val:
            return False
        case_sensitive = rule.get("case_sensitive", False)
        if case_sensitive:
            return val in file_path
        return val.lower() in file_path.lower()

    elif rule_type == "extension":
        values = rule.get("values", [])
        if not values and "value" in rule:
            values = [rule["value"]]
        lowers = [v.lower() if v.startswith(".") else f".{v.lower()}" for v in values]
        return extension in lowers

    elif rule_type == "size_range":
        min_mb = rule.get("min_mb")
        max_mb = rule.get("max_mb")
        size_mb = file_size / (1024 * 1024)

        if min_mb is not None and size_mb < min_mb:
            return False
        if max_mb is not None and max_mb > 0 and size_mb > max_mb:
            return False
        return True

    elif rule_type == "path_matches":
        pattern = rule.get("pattern") or rule.get("value", "")
        if not pattern:
            return False
        try:
            return bool(re.search(pattern, file_path, re.IGNORECASE))
        except re.error as e:
            logger.warning(f"Invalid regex pattern in rule {pattern}: {e}")
            return False

    return False


def categorize_app(file_info: Dict[str, Any], categories: List[Dict[str, Any]]) -> str:
    """
    Determine the category name for a given file based on priority-sorted rules.
    
    Args:
        file_info: Metadata dictionary containing file_path, extension, file_size, etc.
        categories: List of category rule dicts sorted by priority.
        
    Returns:
        Matching category name, or "Uncategorized" if no rule matches.
    """
    if not categories:
        return "Uncategorized"

    # Sort categories by priority ascending if not already sorted
    sorted_cats = sorted(categories, key=lambda c: c.get("priority", 999))

    for category in sorted_cats:
        cat_name = category.get("name", "Uncategorized")
        rules = category.get("rules", [])

        # Skip Uncategorized fallback category during matching phase
        if cat_name.lower() == "uncategorized" or not rules:
            continue

        for rule in rules:
            if matches_rule(file_info, rule):
                return cat_name

    return "Uncategorized"


def assign_category_to_app(
    file_info: Dict[str, Any],
    categories: List[Dict[str, Any]],
    db_manager: Any = None,
) -> str:
    """
    Categorize a file and optionally update database category link.
    
    Args:
        file_info: File metadata dictionary.
        categories: Category rules list.
        db_manager: Instance of DatabaseManager.
        
    Returns:
        Category name.
    """
    cat_name = categorize_app(file_info, categories)
    file_info["category_name"] = cat_name

    if db_manager:
        try:
            cat_record = db_manager.get_category_by_name(cat_name)
            cat_id = cat_record["id"] if cat_record else None
            file_info["category_id"] = cat_id

            # Upsert application record in database
            existing = db_manager.get_application_by_path(file_info["file_path"])
            if existing:
                app_id = existing["id"]
                file_info["id"] = app_id
                if cat_id:
                    db_manager.update_application(app_id, category_id=cat_id)
            else:
                app_id = db_manager.add_application(
                    file_path=file_info["file_path"],
                    file_name=file_info["file_name"],
                    file_size=file_info.get("file_size", 0),
                    content_hash=file_info.get("content_hash", ""),
                    category_id=cat_id,
                    is_duplicate=file_info.get("is_duplicate", False),
                    duplicate_group_id=file_info.get("duplicate_group_id"),
                )
                file_info["id"] = app_id
        except Exception as e:
            logger.warning(f"Error updating category in database for {file_info.get('file_path')}: {e}")

    return cat_name

