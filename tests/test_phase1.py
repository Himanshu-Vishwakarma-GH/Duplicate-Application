"""
Unit tests for Phase 1: DatabaseManager and ConfigManager.
"""

import os
import tempfile
import unittest

from src.config_manager import (
    ConfigError,
    load_config,
    save_config,
    get_default_config,
    load_rules,
    save_rules,
    ConfigManager,
)
from src.database import DatabaseManager


class TestPhase1(unittest.TestCase):
    def test_default_config(self):
        cfg = get_default_config()
        self.assertEqual(cfg["version"], "1.0.0")
        self.assertIn("database_path", cfg)
        self.assertIn("scan_directories", cfg)

    def test_load_save_config_and_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_file = os.path.join(tmpdir, "test_config.json")
            default_cfg = get_default_config()
            save_config(default_cfg, cfg_file)

            loaded = load_config(cfg_file)
            self.assertEqual(loaded, default_cfg)

            # Test validation error on missing required field
            invalid_cfg_file = os.path.join(tmpdir, "invalid_config.json")
            with open(invalid_cfg_file, "w") as f:
                f.write('{"version": "1.0.0"}')

            with self.assertRaises(ConfigError):
                load_config(invalid_cfg_file)

    def test_load_save_rules(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = os.path.join(tmpdir, "test_rules.json")
            rules_data = {
                "version": "1.0.0",
                "categories": [
                    {"name": "TestCat", "description": "Test Category", "priority": 1, "rules": []}
                ],
            }
            save_rules(rules_data, rules_file)
            loaded = load_rules(rules_file)
            self.assertEqual(loaded["version"], "1.0.0")
            self.assertEqual(len(loaded["categories"]), 1)

    def test_database_crud(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = DatabaseManager(db_path=db_path)
            db.init_db()

            # 1. Test Categories CRUD
            cat_id = db.add_category("Dev", "Developer Tools", 1)
            self.assertGreater(cat_id, 0)
            cat = db.get_category(cat_id)
            self.assertEqual(cat["name"], "Dev")
            cat_by_name = db.get_category_by_name("Dev")
            self.assertEqual(cat_by_name["id"], cat_id)

            updated_cat = db.update_category(cat_id, description="Updated Dev Tools")
            self.assertTrue(updated_cat)
            self.assertEqual(db.get_category(cat_id)["description"], "Updated Dev Tools")

            # 2. Test Applications CRUD
            app_id = db.add_application(
                file_path="C:\\App\\app.exe",
                file_name="app.exe",
                file_size=1024,
                content_hash="abc123hash",
                category_id=cat_id,
                is_duplicate=True,
                duplicate_group_id=1,
            )
            self.assertGreater(app_id, 0)
            app = db.get_application(app_id)
            self.assertEqual(app["file_name"], "app.exe")
            self.assertEqual(app["content_hash"], "abc123hash")
            self.assertEqual(app["is_duplicate"], 1)

            dupes = db.get_duplicates()
            self.assertEqual(len(dupes), 1)

            # 3. Test Hash Cache CRUD
            db.add_hash_cache("abc123hash", "C:\\App\\app.exe", 1024)
            cached = db.get_hash_cache("abc123hash")
            self.assertEqual(cached["file_path"], "C:\\App\\app.exe")

            # 4. Test Duplicate Groups CRUD
            grp_id = db.add_duplicate_group("abc123hash", 2048, 2)
            self.assertGreater(grp_id, 0)
            grp = db.get_duplicate_group(grp_id)
            self.assertEqual(grp["content_hash"], "abc123hash")
            self.assertEqual(grp["duplicate_count"], 2)

            # Delete operations
            self.assertTrue(db.delete_application(app_id))
            self.assertIsNone(db.get_application(app_id))
            self.assertTrue(db.delete_category(cat_id))
            self.assertIsNone(db.get_category(cat_id))


if __name__ == "__main__":
    unittest.main()

