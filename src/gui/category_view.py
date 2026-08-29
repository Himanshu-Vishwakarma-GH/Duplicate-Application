"""
Category Browser View module for Duplicate Application Manager.
Lists categories, views assigned applications, and allows moving apps between categories.
"""

from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CategoryView(QWidget):
    """Category Browser View displaying category list and categorized application files."""

    def __init__(self, db_manager: Any = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.categories: List[Dict[str, Any]] = []
        self.applications: List[Dict[str, Any]] = []
        self.selected_category_id: Optional[int] = None

        self._init_ui()
        self.refresh_categories()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header
        header = QLabel("Category Browser")
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(header)

        # Splitter layout
        splitter = QSplitter(Qt.Horizontal)

        # Left Panel: Category List
        left_card = QFrame()
        left_card.setObjectName("cardFrame")
        left_v = QVBoxLayout(left_card)

        left_title = QLabel("Categories")
        left_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_v.addWidget(left_title)

        self.category_list = QListWidget()
        self.category_list.currentItemChanged.connect(self._on_category_selected)
        left_v.addWidget(self.category_list)

        splitter.addWidget(left_card)

        # Right Panel: App List for selected category
        right_card = QFrame()
        right_card.setObjectName("cardFrame")
        right_v = QVBoxLayout(right_card)

        right_header = QHBoxLayout()
        self.cat_header_label = QLabel("Applications")
        self.cat_header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_header.addWidget(self.cat_header_label)
        right_header.addStretch()

        right_header.addWidget(QLabel("Move to Category:"))
        self.target_cat_combo = QComboBox()
        right_header.addWidget(self.target_cat_combo)

        move_btn = QPushButton("Move App")
        move_btn.clicked.connect(self._move_selected_app)
        right_header.addWidget(move_btn)

        right_v.addLayout(right_header)

        self.app_table = QTableWidget()
        self.app_table.setColumnCount(4)
        self.app_table.setHorizontalHeaderLabels(["File Name", "File Path", "Size", "Duplicate?"])
        self.app_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        right_v.addWidget(self.app_table)

        splitter.addWidget(right_card)
        splitter.setSizes([250, 650])

        main_layout.addWidget(splitter)

    def refresh_categories(self):
        """Fetch categories and applications from database."""
        if not self.db_manager:
            return

        try:
            self.categories = self.db_manager.get_all_categories()
            self.applications = self.db_manager.get_all_applications()

            # Populate Left Category List
            self.category_list.clear()
            self.target_cat_combo.clear()

            cat_counts = {}
            for a in self.applications:
                cid = a.get("category_id")
                if cid:
                    cat_counts[cid] = cat_counts.get(cid, 0) + 1

            for cat in self.categories:
                cid = cat["id"]
                cname = cat["name"]
                cnt = cat_counts.get(cid, 0)
                item_text = f"{cname} ({cnt} apps)"

                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, cid)
                self.category_list.addItem(item)
                self.target_cat_combo.addItem(cname, cid)

            if self.category_list.count() > 0:
                self.category_list.setCurrentRow(0)

        except Exception as e:
            print(f"Error loading categories: {e}")

    def _on_category_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]):
        if not current:
            return

        cat_id = current.data(Qt.UserRole)
        self.selected_category_id = cat_id

        cat_name = "Category"
        for c in self.categories:
            if c["id"] == cat_id:
                cat_name = c["name"]
                break

        self.cat_header_label.setText(f"Applications in '{cat_name}'")

        # Filter applications
        cat_apps = [a for a in self.applications if a.get("category_id") == cat_id]

        self.app_table.setRowCount(len(cat_apps))
        for row, app in enumerate(cat_apps):
            size_mb = app.get("file_size", 0) / (1024 * 1024)

            name_item = QTableWidgetItem(app.get("file_name", ""))
            name_item.setData(Qt.UserRole, app.get("id"))
            self.app_table.setItem(row, 0, name_item)
            self.app_table.setItem(row, 1, QTableWidgetItem(app.get("file_path", "")))
            self.app_table.setItem(row, 2, QTableWidgetItem(f"{size_mb:.1f} MB"))
            self.app_table.setItem(row, 3, QTableWidgetItem("Yes" if app.get("is_duplicate") else "No"))

    def _move_selected_app(self):
        curr_row = self.app_table.currentRow()
        if curr_row < 0 or not self.db_manager:
            return

        app_id = self.app_table.item(curr_row, 0).data(Qt.UserRole)
        target_cat_id = self.target_cat_combo.currentData()

        if app_id and target_cat_id:
            try:
                self.db_manager.update_application(app_id, category_id=target_cat_id)
                self.refresh_categories()
            except Exception as e:
                print(f"Error moving app category: {e}")
