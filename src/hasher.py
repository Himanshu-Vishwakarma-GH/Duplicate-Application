"""
Hasher module for Duplicate Application Manager.
Handles full SHA-256 hashing, partial hashing for large files, hash caching, and graceful error handling.
"""

import hashlib
import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def hash_file(file_path: str) -> Optional[str]:
    """
    Compute full SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file to hash.
        
    Returns:
        Hexadecimal SHA-256 hash string, or None if reading fails.
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        logger.warning(f"File does not exist or is not a file: {file_path}")
        return None

    sha256 = hashlib.sha256()
    chunk_size = 64 * 1024  # 64KB chunks

    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (PermissionError, OSError, FileNotFoundError) as e:
        logger.warning(f"Failed to read/hash file {file_path}: {e}")
        return None


def partial_hash(file_path: str, chunk_size: int = 1024 * 1024) -> Optional[str]:
    """
    Compute partial SHA-256 hash for large files (> threshold).
    Hashes the first chunk_size bytes + last chunk_size bytes + file_size representation.
    
    Args:
        file_path: Path to the file.
        chunk_size: Size of header and footer chunks to hash (default 1MB).
        
    Returns:
        Hexadecimal SHA-256 hash string, or None if reading fails.
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        logger.warning(f"File does not exist or is not a file: {file_path}")
        return None

    try:
        file_size = os.path.getsize(file_path)
        sha256 = hashlib.sha256()
        
        # Include file size to differentiate files of different lengths
        sha256.update(f"SIZE:{file_size}".encode("utf-8"))

        with open(file_path, "rb") as f:
            # First chunk
            first_chunk = f.read(chunk_size)
            sha256.update(first_chunk)

            # Last chunk if file is larger than chunk_size
            if file_size > chunk_size:
                f.seek(max(0, file_size - chunk_size), os.SEEK_SET)
                last_chunk = f.read(chunk_size)
                sha256.update(last_chunk)

        return sha256.hexdigest()
    except (PermissionError, OSError, FileNotFoundError) as e:
        logger.warning(f"Failed partial hash for file {file_path}: {e}")
        return None


def get_cached_hash(file_path: str, db_manager: Any = None) -> Optional[str]:
    """
    Check if a valid cached hash exists in the database.
    Invalidated if file size has changed.
    
    Args:
        file_path: Absolute or relative file path.
        db_manager: Instance of DatabaseManager.
        
    Returns:
        Cached hash string if valid, else None.
    """
    if not db_manager:
        return None

    try:
        cached = db_manager.get_hash_cache_by_path(file_path)
        if not cached:
            return None

        if os.path.exists(file_path):
            current_size = os.path.getsize(file_path)
            if cached.get("file_size") == current_size:
                return cached.get("hash")
        return None
    except Exception as e:
        logger.warning(f"Error reading hash cache for {file_path}: {e}")
        return None


def cache_hash(file_path: str, hash_value: str, file_size: int, db_manager: Any = None) -> None:
    """
    Store or update a file hash in the database cache.
    
    Args:
        file_path: File path.
        hash_value: Computed hash.
        file_size: File size in bytes.
        db_manager: Instance of DatabaseManager.
    """
    if not db_manager or not hash_value:
        return

    try:
        db_manager.add_hash_cache(hash_value, file_path, file_size)
    except Exception as e:
        logger.warning(f"Failed to cache hash for {file_path}: {e}")


def compute_file_hash(
    file_path: str,
    threshold_mb: int = 100,
    db_manager: Any = None,
    use_cache: bool = True,
) -> Optional[str]:
    """
    High-level function to compute hash for a file.
    Uses hash caching if available, and selects partial vs full hashing based on file size.
    
    Args:
        file_path: File path.
        threshold_mb: Threshold in MB above which partial hashing is used.
        db_manager: Instance of DatabaseManager.
        use_cache: Whether to use cached hash.
        
    Returns:
        SHA-256 hash string, or None if error.
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return None

    try:
        file_size = os.path.getsize(file_path)
    except (PermissionError, OSError):
        return None

    if use_cache and db_manager:
        cached_hash = get_cached_hash(file_path, db_manager)
        if cached_hash:
            return cached_hash

    threshold_bytes = threshold_mb * 1024 * 1024
    if file_size > threshold_bytes:
        computed = partial_hash(file_path)
    else:
        computed = hash_file(file_path)

    if computed and db_manager:
        cache_hash(file_path, computed, file_size, db_manager)

    return computed
