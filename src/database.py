"""
Database manager for Duplicate Application Manager.
Handles SQLite connection context, table creation, indexes, and CRUD operations.
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union


class DatabaseManager:
    """Manages SQLite database connections and CRUD operations."""

    def __init__(self, db_path: str = "data/app_manager.db"):
        self.db_path = db_path
        self._ensure_db_dir()

    def _ensure_db_dir(self) -> None:
        """Ensure parent directory for database file exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """Context manager for obtaining a database connection."""
        self._ensure_db_dir()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def connection(self):
        """Alias for get_connection for convenience."""
        with self.get_connection() as conn:
            yield conn

    def init_db(self) -> None:
        """Create tables and indexes if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Categories table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 2. Applications table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    content_hash TEXT NOT NULL,
                    category_id INTEGER,
                    is_duplicate BOOLEAN DEFAULT FALSE,
                    duplicate_group_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );
                """
            )

            # 3. Hash cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS hash_cache (
                    hash TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 4. Duplicate groups table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_hash TEXT NOT NULL,
                    total_size INTEGER,
                    duplicate_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_hash ON applications(content_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_category ON applications(category_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_duplicate ON applications(is_duplicate);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash_cache_path ON hash_cache(file_path);")

    # -------------------------------------------------------------------------
    # Applications CRUD
    # -------------------------------------------------------------------------

    def add_application(
        self,
        file_path: str,
        file_name: str,
        file_size: int,
        content_hash: str,
        category_id: Optional[int] = None,
        is_duplicate: bool = False,
        duplicate_group_id: Optional[int] = None,
    ) -> int:
        """Insert a new application record."""
        sql = """
            INSERT INTO applications (file_path, file_name, file_size, content_hash, category_id, is_duplicate, duplicate_group_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (file_path, file_name, file_size, content_hash, category_id, is_duplicate, duplicate_group_id))
            return cursor.lastrowid

    def get_application(self, app_id: int) -> Optional[Dict[str, Any]]:
        """Fetch an application by ID."""
        sql = "SELECT * FROM applications WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (app_id,)).fetchone()
            return dict(row) if row else None

    def get_application_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Fetch an application by file_path."""
        sql = "SELECT * FROM applications WHERE file_path = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (file_path,)).fetchone()
            return dict(row) if row else None

    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Fetch all application records."""
        sql = "SELECT * FROM applications ORDER BY id ASC"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(sql).fetchall()
            return [dict(row) for row in rows]

    def update_application(self, app_id: int, **kwargs) -> bool:
        """Update fields of an application record dynamically."""
        if not kwargs:
            return False
        kwargs["updated_at"] = sqlite3.connect(":memory:").execute("SELECT CURRENT_TIMESTAMP").fetchone()[0]
        set_clauses = [f"{key} = ?" for key in kwargs.keys()]
        sql = f"UPDATE applications SET {', '.join(set_clauses)} WHERE id = ?"
        values = list(kwargs.values()) + [app_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            return cursor.rowcount > 0

    def delete_application(self, app_id: int) -> bool:
        """Delete an application record by ID."""
        sql = "DELETE FROM applications WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (app_id,))
            return cursor.rowcount > 0

    def get_duplicates(self) -> List[Dict[str, Any]]:
        """Fetch all application records marked as duplicates."""
        sql = "SELECT * FROM applications WHERE is_duplicate = 1 ORDER BY content_hash, file_name"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(sql).fetchall()
            return [dict(row) for row in rows]

    # -------------------------------------------------------------------------
    # Categories CRUD
    # -------------------------------------------------------------------------

    def add_category(self, name: str, description: Optional[str] = "", priority: int = 0) -> int:
        """Insert a new category."""
        sql = "INSERT INTO categories (name, description, priority) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (name, description, priority))
            return cursor.lastrowid

    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a category by ID."""
        sql = "SELECT * FROM categories WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (category_id,)).fetchone()
            return dict(row) if row else None

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Fetch a category by name."""
        sql = "SELECT * FROM categories WHERE name = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (name,)).fetchone()
            return dict(row) if row else None

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Fetch all categories ordered by priority ascending."""
        sql = "SELECT * FROM categories ORDER BY priority ASC, id ASC"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(sql).fetchall()
            return [dict(row) for row in rows]

    def update_category(self, category_id: int, **kwargs) -> bool:
        """Update category fields."""
        if not kwargs:
            return False
        set_clauses = [f"{key} = ?" for key in kwargs.keys()]
        sql = f"UPDATE categories SET {', '.join(set_clauses)} WHERE id = ?"
        values = list(kwargs.values()) + [category_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            return cursor.rowcount > 0

    def delete_category(self, category_id: int) -> bool:
        """Delete a category by ID."""
        sql = "DELETE FROM categories WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (category_id,))
            return cursor.rowcount > 0

    # -------------------------------------------------------------------------
    # Hash Cache CRUD
    # -------------------------------------------------------------------------

    def add_hash_cache(self, hash_val: str, file_path: str, file_size: int) -> None:
        """Insert or replace a hash cache entry."""
        sql = """
            INSERT OR REPLACE INTO hash_cache (hash, file_path, file_size, computed_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (hash_val, file_path, file_size))

    def get_hash_cache(self, hash_val: str) -> Optional[Dict[str, Any]]:
        """Fetch hash cache entry by hash."""
        sql = "SELECT * FROM hash_cache WHERE hash = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (hash_val,)).fetchone()
            return dict(row) if row else None

    def get_hash_cache_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Fetch hash cache entry by file_path."""
        sql = "SELECT * FROM hash_cache WHERE file_path = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (file_path,)).fetchone()
            return dict(row) if row else None

    def get_all_hash_cache(self) -> List[Dict[str, Any]]:
        """Fetch all cached hash records."""
        sql = "SELECT * FROM hash_cache"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(sql).fetchall()
            return [dict(row) for row in rows]

    def delete_hash_cache(self, hash_val: str) -> bool:
        """Delete a hash cache entry."""
        sql = "DELETE FROM hash_cache WHERE hash = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (hash_val,))
            return cursor.rowcount > 0

    def clear_hash_cache(self) -> None:
        """Clear all entries from hash_cache."""
        sql = "DELETE FROM hash_cache"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)

    # -------------------------------------------------------------------------
    # Duplicate Groups CRUD
    # -------------------------------------------------------------------------

    def add_duplicate_group(self, content_hash: str, total_size: int = 0, duplicate_count: int = 0) -> int:
        """Insert a new duplicate group."""
        sql = "INSERT INTO duplicate_groups (content_hash, total_size, duplicate_count) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (content_hash, total_size, duplicate_count))
            return cursor.lastrowid

    def get_duplicate_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a duplicate group by ID."""
        sql = "SELECT * FROM duplicate_groups WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (group_id,)).fetchone()
            return dict(row) if row else None

    def get_duplicate_group_by_hash(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Fetch a duplicate group by content_hash."""
        sql = "SELECT * FROM duplicate_groups WHERE content_hash = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(sql, (content_hash,)).fetchone()
            return dict(row) if row else None

    def get_all_duplicate_groups(self) -> List[Dict[str, Any]]:
        """Fetch all duplicate groups."""
        sql = "SELECT * FROM duplicate_groups ORDER BY id ASC"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(sql).fetchall()
            return [dict(row) for row in rows]

    def update_duplicate_group(self, group_id: int, **kwargs) -> bool:
        """Update fields of a duplicate group record."""
        if not kwargs:
            return False
        set_clauses = [f"{key} = ?" for key in kwargs.keys()]
        sql = f"UPDATE duplicate_groups SET {', '.join(set_clauses)} WHERE id = ?"
        values = list(kwargs.values()) + [group_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            return cursor.rowcount > 0

    def delete_duplicate_group(self, group_id: int) -> bool:
        """Delete a duplicate group by ID."""
        sql = "DELETE FROM duplicate_groups WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (group_id,))
            return cursor.rowcount > 0

    def clear_duplicate_groups(self) -> None:
        """Clear all entries from duplicate_groups."""
        sql = "DELETE FROM duplicate_groups"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)

    def clear_all_scan_data(self, clear_cache: bool = False) -> None:
        """
        Clear all application records, duplicate groups, and optionally hash cache from the database.
        
        Args:
            clear_cache: If True, also clears the hash_cache table.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM applications;")
            cursor.execute("DELETE FROM duplicate_groups;")
            if clear_cache:
                cursor.execute("DELETE FROM hash_cache;")

