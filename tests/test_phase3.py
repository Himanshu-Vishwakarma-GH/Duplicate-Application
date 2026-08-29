"""
Unit tests for Phase 3: GUI components (MainWindow, Dashboard, ScanView, ResultsView, CategoryView).
Executed in offscreen mode.
"""

import os
import sys
import tempfile
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from src.config_manager import ConfigManager
from src.database import DatabaseManager
from src.gui.styles import get_stylesheet
from src.gui.main_window import MainWindow
from src.gui.dashboard import DashboardView
from src.gui.scan_view import ScanView
from src.gui.results_view import ResultsView
from src.gui.category_view import CategoryView

app = QApplication.instance() or QApplication(sys.argv)


class TestPhase3GUI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.cfg_path = os.path.join(self.tmpdir.name, "config.json")
        self.rules_path = os.path.join(self.tmpdir.name, "rules.json")

        self.db = DatabaseManager(self.db_path)
        self.db.init_db()

        self.cfg_mgr = ConfigManager(self.cfg_path, self.rules_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_styles(self):
        qss_dark = get_stylesheet("dark")
        qss_light = get_stylesheet("light")
        self.assertIn("#0B0C10", qss_dark)
        self.assertIn("#F8FAFC", qss_light)




    def test_dashboard_view(self):
        view = DashboardView(db_manager=self.db)
        self.assertIsNotNone(view)
        view.refresh_data()
        self.assertEqual(view.card_total_apps.value_label.text(), "0")

    def test_scan_view(self):
        view = ScanView(config_manager=self.cfg_mgr, db_manager=self.db)
        self.assertIsNotNone(view)
        self.assertTrue(view.start_scan_btn.isEnabled())

    def test_results_view(self):
        view = ResultsView(db_manager=self.db)
        self.assertIsNotNone(view)
        view.refresh_results()
        self.assertEqual(view.tree.topLevelItemCount(), 0)

    def test_category_view(self):
        view = CategoryView(db_manager=self.db)
        self.assertIsNotNone(view)
        view.refresh_categories()

    def test_main_window(self):
        win = MainWindow(config_manager=self.cfg_mgr, db_manager=self.db)
        self.assertIsNotNone(win)
        self.assertEqual(win.stacked_widget.count(), 4)

        # Test switching views
        win._switch_page(1)
        self.assertEqual(win.stacked_widget.currentIndex(), 1)
        win._switch_page(2)
        self.assertEqual(win.stacked_widget.currentIndex(), 2)


if __name__ == "__main__":
    unittest.main()
