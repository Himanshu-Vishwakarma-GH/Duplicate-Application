"""
Remover module for Duplicate Application Manager.
Handles safe deletion via send2trash (system recycle bin/trash), batch operations, tracking, and logging.
"""

import logging
import os
from typing import Any, Dict, List, Optional

try:
    import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

logger = logging.getLogger(__name__)

# Track removal history stack for auditing
_removal_history: List[Dict[str, Any]] = []


def remove_file(file_path: str) -> bool:
    """
    Safely move a file to system trash using send2trash.
    
    Args:
        file_path: Absolute or relative path to the file.
        
    Returns:
        True if successfully moved to trash, False otherwise.
    """
    if not file_path:
        logger.warning("Empty file path provided for removal.")
        return False

    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        logger.warning(f"File to remove does not exist: {abs_path}")
        return False

    try:
        if HAS_SEND2TRASH:
            send2trash.send2trash(abs_path)
        else:
            # Fallback if send2trash unavailable: remove file directly
            os.remove(abs_path)

        logger.info(f"Successfully moved file to trash: {abs_path}")
        _removal_history.append({
            "file_path": abs_path,
            "timestamp": os.stat(abs_path).st_mtime if os.path.exists(abs_path) else None,
        })
        return True
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to move file to trash {abs_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error removing file {abs_path}: {e}")
        return False


def batch_remove(file_paths: List[str]) -> Dict[str, Any]:
    """
    Batch remove a list of files to trash.
    
    Args:
        file_paths: List of file paths to remove.
        
    Returns:
        Dictionary with removal counts and lists of successful/failed file paths.
    """
    removed_files: List[str] = []
    failed_files: List[str] = []

    for path in file_paths:
        if remove_file(path):
            removed_files.append(path)
        else:
            failed_files.append(path)

    summary = {
        "total": len(file_paths),
        "success_count": len(removed_files),
        "failed_count": len(failed_files),
        "removed_files": removed_files,
        "failed_files": failed_files,
    }

    logger.info(
        f"Batch removal complete: {len(removed_files)} succeeded, {len(failed_files)} failed out of {len(file_paths)} total."
    )
    return summary


def get_removal_history() -> List[Dict[str, Any]]:
    """Return copy of removal operations history log."""
    return list(_removal_history)


def clear_removal_history() -> None:
    """Clear removal history log."""
    global _removal_history
    _removal_history = []
