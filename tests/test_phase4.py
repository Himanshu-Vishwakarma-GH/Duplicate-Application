"""
Unit and Integration tests for Phase 4: Remover, Reporter, CLI arguments, and End-to-End workflow.
"""

import json
import os
import tempfile
import unittest

from src.config_manager import ConfigManager
from src.database import DatabaseManager
import src.remover as remover
import src.reporter as reporter
import src.scanner as scanner
import src.hasher as hasher
import src.duplicate_detector as duplicate_detector
import src.categorizer as categorizer


class TestRemover(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.file1 = os.path.join(self.tmpdir.name, "test1.txt")
        self.file2 = os.path.join(self.tmpdir.name, "test2.txt")
        with open(self.file1, "w") as f:
            f.write("content 1")
        with open(self.file2, "w") as f:
            f.write("content 2")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_remove_file(self):
        res = remover.remove_file(self.file1)
        self.assertTrue(res)
        self.assertFalse(os.path.exists(self.file1))

    def test_remove_non_existent(self):
        res = remover.remove_file(os.path.join(self.tmpdir.name, "non_existent.txt"))
        self.assertFalse(res)

    def test_batch_remove(self):
        res = remover.batch_remove([self.file1, self.file2])
        self.assertEqual(res["total"], 2)
        self.assertEqual(res["success_count"], 2)
        self.assertEqual(res["failed_count"], 0)
        self.assertFalse(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()

        # Seed data
        cat_id = self.db.add_category("Development", "Dev tools", 1)
        grp_id = self.db.add_duplicate_group("hash123", 2048, 2)
        self.db.add_application("C:\\app1.exe", "app1.exe", 1024, "hash123", cat_id, True, grp_id)
        self.db.add_application("C:\\app2.exe", "app2.exe", 1024, "hash123", cat_id, True, grp_id)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_generate_summary(self):
        summary = reporter.generate_summary(self.db)
        self.assertEqual(summary["total_applications"], 2)
        self.assertEqual(summary["duplicate_applications"], 2)
        self.assertEqual(summary["duplicate_groups_count"], 1)
        self.assertEqual(summary["potential_savings_bytes"], 1024)

    def test_export_json_and_text(self):
        summary = reporter.generate_summary(self.db)
        json_path = os.path.join(self.tmpdir.name, "report.json")
        txt_path = os.path.join(self.tmpdir.name, "report.txt")

        reporter.export_json(summary, json_path)
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data["total_applications"], 2)

        reporter.export_text(summary, txt_path)
        self.assertTrue(os.path.exists(txt_path))
        with open(txt_path, "r") as f:
            content = f.read()
            self.assertIn("SUMMARY REPORT", content)
            self.assertIn("Development", content)


class TestEndToEndWorkflow(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        base = self.tmpdir.name

        self.db_path = os.path.join(base, "e2e.db")
        self.db = DatabaseManager(self.db_path)
        self.db.init_db()

        # Seed categories
        self.cat_dev = self.db.add_category("Development Tools", "IDEs and SDKs", 1)
        self.cat_games = self.db.add_category("Games", "Gaming software", 2)

        # Create directory layout with duplicate files
        self.scan_dir = os.path.join(base, "scan_target")
        self.sub_dir = os.path.join(self.scan_dir, "dev")
        os.makedirs(self.sub_dir, exist_ok=True)

        self.file1 = os.path.join(self.scan_dir, "game_copy1.exe")
        self.file2 = os.path.join(self.sub_dir, "game_copy2.exe")
        self.file3 = os.path.join(self.sub_dir, "unique_dev.py")

        dupe_bytes = b"BINARY_GAME_PAYLOAD_1234567890"
        with open(self.file1, "wb") as f:
            f.write(dupe_bytes)
        with open(self.file2, "wb") as f:
            f.write(dupe_bytes)
        with open(self.file3, "wb") as f:
            f.write(b"print('Hello World')")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_full_e2e_pipeline(self):
        # 1. Scan directory
        scanned = scanner.scan_directory(self.scan_dir, recursive=True)
        self.assertEqual(len(scanned), 3)

        # 2. Categorize applications
        rules = [
            {"name": "Development Tools", "priority": 1, "rules": [{"type": "extension", "values": [".py"]}]},
            {"name": "Games", "priority": 2, "rules": [{"type": "path_contains", "value": "game"}]},
        ]
        for f in scanned:
            categorizer.assign_category_to_app(f, rules, db_manager=self.db)

        # 3. Detect duplicates
        dupes = duplicate_detector.find_duplicates(scanned, hasher_module=hasher, db_manager=self.db)
        self.assertEqual(len(dupes), 1)
        self.assertEqual(dupes[0]["duplicate_count"], 2)

        # 4. Generate summary report
        summary = reporter.generate_summary(self.db)
        self.assertEqual(summary["total_applications"], 3)
        self.assertEqual(summary["duplicate_applications"], 2)

        # 5. Remove redundant copy
        res = remover.remove_file(self.file2)
        self.assertTrue(res)
        self.assertFalse(os.path.exists(self.file2))
        self.assertTrue(os.path.exists(self.file1))


if __name__ == "__main__":
    unittest.main()
