"""
Unit tests for Phase 2: Hasher, Scanner, DuplicateDetector, and Categorizer modules.
"""

import os
import tempfile
import unittest

from src.database import DatabaseManager
from src.hasher import (
    hash_file,
    partial_hash,
    get_cached_hash,
    cache_hash,
    compute_file_hash,
)
from src.scanner import (
    scan_directory,
    apply_filters,
    get_scan_stats,
)
from src.duplicate_detector import (
    find_duplicates,
    get_duplicate_groups,
    calculate_savings,
)
from src.categorizer import (
    matches_rule,
    categorize_app,
    assign_category_to_app,
)


class TestHasherModule(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.tmpdir.name, "test.db")
        self.db = DatabaseManager(self.db_file)
        self.db.init_db()

        # Create a sample test file
        self.sample_file = os.path.join(self.tmpdir.name, "sample.txt")
        with open(self.sample_file, "wb") as f:
            f.write(b"Hello World! This is a test file content.")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_hash_file(self):
        h1 = hash_file(self.sample_file)
        h2 = hash_file(self.sample_file)
        self.assertIsNotNone(h1)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)  # SHA-256 hex length

    def test_partial_hash(self):
        ph = partial_hash(self.sample_file, chunk_size=10)
        self.assertIsNotNone(ph)
        self.assertEqual(len(ph), 64)

    def test_non_existent_file(self):
        bad_path = os.path.join(self.tmpdir.name, "non_existent.bin")
        self.assertIsNone(hash_file(bad_path))
        self.assertIsNone(partial_hash(bad_path))

    def test_caching(self):
        h = hash_file(self.sample_file)
        size = os.path.getsize(self.sample_file)

        # Cache it
        cache_hash(self.sample_file, h, size, self.db)
        cached = get_cached_hash(self.sample_file, self.db)
        self.assertEqual(cached, h)

        # Invalidate cache by changing file content/size
        with open(self.sample_file, "wb") as f:
            f.write(b"Different content with different length!")

        invalidated = get_cached_hash(self.sample_file, self.db)
        self.assertIsNone(invalidated)

    def test_compute_file_hash(self):
        h = compute_file_hash(self.sample_file, threshold_mb=100, db_manager=self.db)
        self.assertIsNotNone(h)


class TestScannerModule(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        base = self.tmpdir.name

        # Structure:
        # base/
        # ├── app1.exe
        # ├── file2.txt
        # ├── node_modules/
        # │   └── script.exe
        # └── sub/
        #     └── app2.exe

        self.app1 = os.path.join(base, "app1.exe")
        self.file2 = os.path.join(base, "file2.txt")
        self.sub_dir = os.path.join(base, "sub")
        self.app2 = os.path.join(self.sub_dir, "app2.exe")
        self.excl_dir = os.path.join(base, "node_modules")
        self.excl_app = os.path.join(self.excl_dir, "script.exe")

        os.makedirs(self.sub_dir, exist_ok=True)
        os.makedirs(self.excl_dir, exist_ok=True)

        for p in [self.app1, self.file2, self.app2, self.excl_app]:
            with open(p, "w") as f:
                f.write("content")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_scan_directory_all(self):
        results = scan_directory(self.tmpdir.name, config={}, recursive=True)
        paths = [r["file_path"] for r in results]
        self.assertEqual(len(results), 4)

    def test_scan_directory_with_filters_and_exclusions(self):
        cfg = {
            "file_extensions": [".exe"],
            "excluded_directories": ["node_modules"],
        }
        results = scan_directory(self.tmpdir.name, config=cfg, recursive=True)
        filenames = [r["file_name"] for r in results]
        self.assertIn("app1.exe", filenames)
        self.assertIn("app2.exe", filenames)
        self.assertNotIn("file2.txt", filenames)
        self.assertNotIn("script.exe", filenames)

    def test_apply_filters_and_stats(self):
        raw = scan_directory(self.tmpdir.name, config={}, recursive=True)
        filtered = apply_filters(raw, {"extensions": [".exe"]})
        self.assertEqual(len(filtered), 3)

        stats = get_scan_stats(filtered)
        self.assertEqual(stats["total_files"], 3)
        self.assertIn(".exe", stats["extension_breakdown"])


class TestDuplicateDetectorModule(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.tmpdir.name, "test.db")
        self.db = DatabaseManager(self.db_file)
        self.db.init_db()

        base = self.tmpdir.name
        self.file1 = os.path.join(base, "copy1.exe")
        self.file2 = os.path.join(base, "copy2.exe")
        self.file3 = os.path.join(base, "unique.exe")

        with open(self.file1, "wb") as f:
            f.write(b"IDENTICAL_CONTENT_12345")
        with open(self.file2, "wb") as f:
            f.write(b"IDENTICAL_CONTENT_12345")
        with open(self.file3, "wb") as f:
            f.write(b"UNIQUE_CONTENT_67890")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_find_duplicates(self):
        import src.hasher as hasher

        files = [
            {"file_path": self.file1, "file_name": "copy1.exe", "file_size": os.path.getsize(self.file1)},
            {"file_path": self.file2, "file_name": "copy2.exe", "file_size": os.path.getsize(self.file2)},
            {"file_path": self.file3, "file_name": "unique.exe", "file_size": os.path.getsize(self.file3)},
        ]

        dupe_groups = find_duplicates(files, hasher_module=hasher, db_manager=self.db)
        self.assertEqual(len(dupe_groups), 1)
        self.assertEqual(dupe_groups[0]["duplicate_count"], 2)

        # Check DB updates
        db_dupes = self.db.get_duplicates()
        self.assertEqual(len(db_dupes), 2)

        # Savings calculation
        savings = calculate_savings(dupe_groups)
        self.assertEqual(savings["total_groups"], 1)
        self.assertEqual(savings["redundant_files_count"], 1)
        self.assertEqual(savings["potential_savings_bytes"], os.path.getsize(self.file1))


class TestCategorizerModule(unittest.TestCase):
    def setUp(self):
        self.categories = [
            {
                "name": "Development",
                "priority": 1,
                "rules": [
                    {"type": "path_contains", "value": "dev", "case_sensitive": False},
                    {"type": "extension", "values": [".py", ".cpp"]},
                ],
            },
            {
                "name": "Games",
                "priority": 2,
                "rules": [
                    {"type": "path_contains", "value": "games", "case_sensitive": False},
                ],
            },
            {
                "name": "Uncategorized",
                "priority": 999,
                "rules": [],
            },
        ]

    def test_matches_rule(self):
        info_dev = {"file_path": "C:\\Dev\\script.py", "extension": ".py", "file_size": 100}
        self.assertTrue(matches_rule(info_dev, {"type": "path_contains", "value": "dev"}))
        self.assertTrue(matches_rule(info_dev, {"type": "extension", "values": [".py"]}))

    def test_categorize_app_priority(self):
        # Path matches dev (priority 1) and games (priority 2) -> should pick Development
        info = {"file_path": "C:\\dev\\games\\launcher.exe", "extension": ".exe", "file_size": 100}
        cat = categorize_app(info, self.categories)
        self.assertEqual(cat, "Development")

    def test_categorize_app_uncategorized(self):
        info = {"file_path": "C:\\random\\tool.xyz", "extension": ".xyz", "file_size": 100}
        cat = categorize_app(info, self.categories)
        self.assertEqual(cat, "Uncategorized")


if __name__ == "__main__":
    unittest.main()
