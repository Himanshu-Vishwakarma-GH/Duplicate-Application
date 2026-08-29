"""
Dashboard view module for Duplicate Application Manager.
Implements the Nordic Studio Graphite & Mint Emerald UI layout.
"""

from typing import Any, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.gui.styles import (
    ICON_CATEGORIES,
    ICON_DASHBOARD,
    ICON_RESULTS,
    ICON_SCAN,
    ICON_TRASH,
)


class StatCard(QFrame):
    """Nordic Studio Stat Card widget with emerald numbers and graphite surface."""

    def __init__(self, icon: str, title: str, value: str = "0", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("statCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 22px; color: #10B981; background: transparent;")
        layout.addWidget(icon_label)
        layout.addSpacing(10)

        v_layout = QVBoxLayout()
        v_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #9CA3AF; font-weight: 500; background: transparent;")
        v_layout.addWidget(title_label)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #10B981; background: transparent;")
        v_layout.addWidget(self.value_label)

        layout.addLayout(v_layout)
        layout.addStretch()


class DashboardView(QWidget):
    """Dashboard Overview using the Nordic Studio Graphite & Mint Emerald design."""

    request_scan = Signal()
    request_results = Signal()

    def __init__(self, db_manager: Any = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.db_manager = db_manager

        self._init_ui()
        self.refresh_data()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header section
        header_layout = QHBoxLayout()
        header_title = QLabel("Duplicate Groups Overview")
        header_title.setObjectName("sectionHeader")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        scan_btn = QPushButton(f"{ICON_SCAN} Start Scan")
        scan_btn.setObjectName("primaryBtn")
        scan_btn.setFixedHeight(38)
        scan_btn.clicked.connect(self.request_scan.emit)
        header_layout.addWidget(scan_btn)

        main_layout.addLayout(header_layout)

        # Stat Cards Grid (Horizontal row)
        cards_layout = QGridLayout()
        cards_layout.setSpacing(14)

        self.card_total_apps = StatCard(ICON_DASHBOARD, "Total Apps Scanned", "0")
        self.card_groups = StatCard(ICON_RESULTS, "Duplicate Groups", "0")
        self.card_duplicates = StatCard(ICON_RESULTS, "Total Duplicates", "0")
        self.card_space_saved = StatCard(ICON_TRASH, "Disk Space Saved", "0 MB")

        cards_layout.addWidget(self.card_total_apps, 0, 0)
        cards_layout.addWidget(self.card_groups, 0, 1)
        cards_layout.addWidget(self.card_duplicates, 0, 2)
        cards_layout.addWidget(self.card_space_saved, 0, 3)

        main_layout.addLayout(cards_layout)

        # Lower section: Duplicate groups summary + Category breakdown
        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        # Left: Duplicate Groups List
        dupes_card = QFrame()
        dupes_card.setObjectName("cardFrame")
        dupes_v = QVBoxLayout(dupes_card)

        dupes_header = QHBoxLayout()
        dupes_title = QLabel("Duplicate Groups")
        dupes_title.setStyleSheet("font-size: 15px; font-weight: 700;")
        dupes_header.addWidget(dupes_title)
        dupes_header.addStretch()

        view_all_btn = QPushButton("View All")
        view_all_btn.clicked.connect(self.request_results.emit)
        dupes_header.addWidget(view_all_btn)
        dupes_v.addLayout(dupes_header)

        self.dupes_list = QListWidget()
        dupes_v.addWidget(self.dupes_list)

        content_layout.addWidget(dupes_card, stretch=1)

        # Right: Category Breakdown
        cats_card = QFrame()
        cats_card.setObjectName("cardFrame")
        self.cats_v = QVBoxLayout(cats_card)

        cats_title = QLabel("Categories Breakdown")
        cats_title.setStyleSheet("font-size: 15px; font-weight: 700;")
        self.cats_v.addWidget(cats_title)

        self.cats_container = QVBoxLayout()
        self.cats_v.addLayout(self.cats_container)
        self.cats_v.addStretch()

        content_layout.addWidget(cats_card, stretch=1)

        main_layout.addLayout(content_layout)

    def refresh_data(self):
        """Fetch latest database stats and refresh UI."""
        if not self.db_manager:
            return

        try:
            apps = self.db_manager.get_all_applications()
            dupes = self.db_manager.get_duplicates()
            groups = self.db_manager.get_all_duplicate_groups()
            categories = self.db_manager.get_all_categories()

            total_apps_count = len(apps)
            total_dupes_count = len(dupes)

            # Potential savings
            total_savings_bytes = 0
            for g in groups:
                grp_id = g["id"]
                grp_apps = [a for a in apps if a.get("duplicate_group_id") == grp_id]
                if grp_apps:
                    single_size = grp_apps[0].get("file_size", 0)
                    cnt = len(grp_apps)
                    total_savings_bytes += max(0, (cnt - 1) * single_size)

            savings_mb = total_savings_bytes / (1024 * 1024)
            savings_str = f"{savings_mb:.1f} MB" if savings_mb < 1024 else f"{savings_mb / 1024:.2f} GB"

            # Update Stat Cards
            self.card_total_apps.value_label.setText(str(total_apps_count))
            self.card_groups.value_label.setText(str(len(groups)))
            self.card_duplicates.value_label.setText(str(total_dupes_count))
            self.card_space_saved.value_label.setText(savings_str)

            # Update Top Duplicate Groups list
            self.dupes_list.clear()
            for idx, g in enumerate(groups[:5], 1):
                grp_id = g["id"]
                grp_apps = [a for a in apps if a.get("duplicate_group_id") == grp_id]
                file_count = len(grp_apps)
                if file_count > 0:
                    first_name = grp_apps[0].get("file_name", "App")
                    size_mb = grp_apps[0].get("file_size", 0) / (1024 * 1024)
                    item_text = f"{first_name} [{file_count} copies]  —  {size_mb:.1f} MB each"
                    self.dupes_list.addItem(QListWidgetItem(item_text))

            if not groups:
                self.dupes_list.addItem(QListWidgetItem("No duplicate groups found. Run a scan!"))

            # Update Category Breakdown Progress Bars
            while self.cats_container.count():
                child = self.cats_container.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            cat_counts = {}
            for a in apps:
                cid = a.get("category_id")
                if cid:
                    cat_counts[cid] = cat_counts.get(cid, 0) + 1

            for cat in categories:
                cid = cat["id"]
                cname = cat["name"]
                count = cat_counts.get(cid, 0)
                pct = int((count / total_apps_count * 100)) if total_apps_count > 0 else 0

                cat_row = QWidget()
                row_l = QVBoxLayout(cat_row)
                row_l.setContentsMargins(0, 4, 0, 4)

                lbl_l = QHBoxLayout()
                c_lbl = QLabel(cname)
                c_lbl.setStyleSheet("font-weight: 600;")
                lbl_l.addWidget(c_lbl)
                lbl_l.addStretch()

                cnt_lbl = QLabel(f"{count} apps ({pct}%)")
                cnt_lbl.setStyleSheet("color: #9CA3AF; font-size: 12px;")
                lbl_l.addWidget(cnt_lbl)
                row_l.addLayout(lbl_l)

                pbar = QProgressBar()
                pbar.setValue(pct)
                pbar.setFixedHeight(8)
                pbar.setTextVisible(False)
                row_l.addWidget(pbar)

                self.cats_container.addWidget(cat_row)

        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
