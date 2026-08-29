"""
Main Window module for Duplicate Application Manager.
Implements the main layout with fixed sidebar navigation, QStackedWidget content pages, and status bar.
"""

from typing import Any, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

import src.remover as remover
from src.gui.category_view import CategoryView
from src.gui.dashboard import DashboardView
from src.gui.results_view import ResultsView
from src.gui.scan_view import ScanView
from src.gui.styles import (
    ICON_CATEGORIES,
    ICON_DASHBOARD,
    ICON_RESULTS,
    ICON_SCAN,
    ICON_SETTINGS,
    get_stylesheet,
)


class MainWindow(QMainWindow):
    """Main Application Window with sidebar navigation and stacked content views."""

    def __init__(self, config_manager: Any = None, db_manager: Any = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.current_theme = "dark"

        self.setWindowTitle("Duplicate Application Manager")
        self.resize(1200, 800)

        self._init_ui()
        self._apply_theme(self.current_theme)
        self._update_statusbar()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # ---------------------------------------------------------------------
        # Sidebar Frame (200px fixed width)
        # ---------------------------------------------------------------------
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebarFrame")
        sidebar_v_layout = QVBoxLayout(sidebar_frame)
        sidebar_v_layout.setContentsMargins(0, 16, 0, 16)
        sidebar_v_layout.setSpacing(8)

        # App Title
        app_title = QLabel("⬡ App Manager")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 8px 16px;")
        sidebar_v_layout.addWidget(app_title)

        # Navigation Buttons
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)

        self.btn_dashboard = self._create_sidebar_btn(f"{ICON_DASHBOARD}  Dashboard", 0)
        self.btn_scan = self._create_sidebar_btn(f"{ICON_SCAN}  Scan Config", 1)
        self.btn_results = self._create_sidebar_btn(f"{ICON_RESULTS}  Results", 2)
        self.btn_categories = self._create_sidebar_btn(f"{ICON_CATEGORIES}  Categories", 3)

        sidebar_v_layout.addWidget(self.btn_dashboard)
        sidebar_v_layout.addWidget(self.btn_scan)
        sidebar_v_layout.addWidget(self.btn_results)
        sidebar_v_layout.addWidget(self.btn_categories)
        sidebar_v_layout.addStretch()

        # Theme Toggle Button
        theme_btn = QPushButton(f"{ICON_SETTINGS}  Toggle Theme")
        theme_btn.setObjectName("sidebarBtn")
        theme_btn.clicked.connect(self._toggle_theme)
        sidebar_v_layout.addWidget(theme_btn)

        main_h_layout.addWidget(sidebar_frame)

        # ---------------------------------------------------------------------
        # Main Content Stack
        # ---------------------------------------------------------------------
        self.stacked_widget = QStackedWidget()

        # Views
        self.dashboard_view = DashboardView(db_manager=self.db_manager)
        self.scan_view = ScanView(config_manager=self.config_manager, db_manager=self.db_manager)
        self.results_view = ResultsView(db_manager=self.db_manager)
        self.category_view = CategoryView(db_manager=self.db_manager)

        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.scan_view)
        self.stacked_widget.addWidget(self.results_view)
        self.stacked_widget.addWidget(self.category_view)

        main_h_layout.addWidget(self.stacked_widget)

        # ---------------------------------------------------------------------
        # Status Bar
        # ---------------------------------------------------------------------
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Connect Navigation Signals
        self.btn_dashboard.setChecked(True)
        self.dashboard_view.request_scan.connect(lambda: self._switch_page(1))
        self.dashboard_view.request_results.connect(lambda: self._switch_page(2))
        self.scan_view.scan_completed.connect(self._on_scan_completed)
        self.results_view.request_removal.connect(self._on_request_removal)

    def _create_sidebar_btn(self, text: str, page_index: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("sidebarBtn")
        btn.setCheckable(True)
        self.nav_button_group.addButton(btn, page_index)
        btn.clicked.connect(lambda: self._switch_page(page_index))
        return btn

    def _switch_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        btn = self.nav_button_group.button(index)
        if btn:
            btn.setChecked(True)
        self._update_statusbar()

    def _toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._apply_theme(self.current_theme)

    def _apply_theme(self, theme: str):
        qss = get_stylesheet(theme)
        self.setStyleSheet(qss)

    def _update_statusbar(self):
        if not self.db_manager:
            self.statusbar.showMessage("Ready.")
            return

        try:
            apps = self.db_manager.get_all_applications()
            dupes = self.db_manager.get_duplicates()
            msg = f"Ready  |  Total Applications: {len(apps)}  |  Duplicates Found: {len(dupes)}"
            self.statusbar.showMessage(msg)
        except Exception:
            self.statusbar.showMessage("Ready.")

    def _on_scan_completed(self):
        # Refresh views
        self.dashboard_view.refresh_data()
        self.results_view.refresh_results()
        self.category_view.refresh_categories()
        self._update_statusbar()
        # Switch to Results view
        self._switch_page(2)

    def _on_request_removal(self, file_paths: list):
        if not file_paths:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to move {len(file_paths)} selected files to trash?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            removed_count = 0
            for path in file_paths:
                if remover.remove_file(path):
                    removed_count += 1
                    # Remove from DB if exists
                    if self.db_manager:
                        app = self.db_manager.get_application_by_path(path)
                        if app:
                            self.db_manager.delete_application(app["id"])

            QMessageBox.information(
                self,
                "Removal Complete",
                f"Successfully moved {removed_count} of {len(file_paths)} files to trash.",
            )
            self._on_scan_completed()
