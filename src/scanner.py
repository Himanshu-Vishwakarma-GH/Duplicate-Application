"""
Scanner module for Duplicate Application Manager.
Recursively scans directories, collects metadata, applies filters, and handles errors gracefully.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def should_exclude_dir(dir_name: str, excluded_dirs: List[str]) -> bool:
    """Check if a directory name matches any excluded directory rule."""
    if not excluded_dirs:
        return False
    lower_dir = dir_name.lower()
    for excl in excluded_dirs:
        if excl and excl.lower() == lower_dir:
            return True
    return False


def is_extension_allowed(ext: str, allowed_extensions: List[str]) -> bool:
    """Check if file extension is allowed by configuration."""
    if not allowed_extensions:
        return True
    lower_ext = ext.lower()
    allowed_lowers = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in allowed_extensions]
    return lower_ext in allowed_lowers


def scan_directory(
    path: str,
    config: Optional[Dict[str, Any]] = None,
    recursive: bool = True,
) -> List[Dict[str, Any]]:
    """
    Recursively or flatly scan a directory for files and collect metadata.
    
    Args:
        path: Path to directory to scan.
        config: Configuration dictionary containing file_extensions and excluded_directories.
        recursive: Whether to scan subdirectories recursively.
        
    Returns:
        List of file metadata dictionaries with keys:
        - file_path (str)
        - file_name (str)
        - file_size (int)
        - extension (str)
    """
    results: List[Dict[str, Any]] = []

    if not path or not os.path.exists(path) or not os.path.isdir(path):
        logger.warning(f"Scan directory does not exist or is not a directory: {path}")
        return results

    config = config or {}
    allowed_extensions = config.get("file_extensions", [])
    excluded_directories = config.get("excluded_directories", [])

    abs_base = os.path.abspath(path)

    if not recursive:
        try:
            with os.scandir(abs_base) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            ext = os.path.splitext(entry.name)[1]
                            if is_extension_allowed(ext, allowed_extensions):
                                stat = entry.stat(follow_symlinks=False)
                                results.append({
                                    "file_path": os.path.abspath(entry.path),
                                    "file_name": entry.name,
                                    "file_size": stat.st_size,
                                    "extension": ext.lower(),
                                })
                    except (PermissionError, OSError) as e:
                        logger.warning(f"Error reading file entry {entry.path}: {e}")
        except (PermissionError, OSError) as e:
            logger.warning(f"Error scanning directory {abs_base}: {e}")
        return results

    # Recursive scan using os.walk
    for root, dirs, files in os.walk(abs_base, topdown=True, followlinks=False):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if not should_exclude_dir(d, excluded_directories)]

        for file_name in files:
            full_path = os.path.join(root, file_name)
            ext = os.path.splitext(file_name)[1]

            if not is_extension_allowed(ext, allowed_extensions):
                continue

            try:
                stat = os.stat(full_path, follow_symlinks=False)
                results.append({
                    "file_path": os.path.abspath(full_path),
                    "file_name": file_name,
                    "file_size": stat.st_size,
                    "extension": ext.lower(),
                })
            except (PermissionError, OSError, FileNotFoundError) as e:
                logger.warning(f"Skipping inaccessible file {full_path}: {e}")

    return results


def apply_filters(
    files: List[Dict[str, Any]],
    filters: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Apply secondary filtering to an existing list of file metadata dicts.
    
    Filters supported:
    - extensions: List[str]
    - min_size: int (bytes)
    - max_size: int (bytes)
    """
    filtered = []
    allowed_extensions = filters.get("extensions")
    min_size = filters.get("min_size")
    max_size = filters.get("max_size")

    for f in files:
        if allowed_extensions and not is_extension_allowed(f.get("extension", ""), allowed_extensions):
            continue
        size = f.get("file_size", 0)
        if min_size is not None and size < min_size:
            continue
        if max_size is not None and max_size > 0 and size > max_size:
            continue
        filtered.append(f)

    return filtered


def get_scan_stats(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics for scanned files."""
    total_files = len(files)
    total_size = sum(f.get("file_size", 0) for f in files)
    ext_breakdown: Dict[str, int] = {}

    for f in files:
        ext = f.get("extension", "unknown").lower()
        ext_breakdown[ext] = ext_breakdown.get(ext, 0) + 1

    return {
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "extension_breakdown": ext_breakdown,
    }
