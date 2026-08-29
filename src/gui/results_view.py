"""
Results View module for Duplicate Application Manager.
Implements dense, readable tree table with pill badges and batch action controls.
"""

import os
import time
from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidgetItem,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

import src.duplicate_detector as duplicate_detector
from src.gui.styles import ICON_REFRESH, ICON_TRASH


class ResultsView(QWidget):
    """View displaying duplicate groups in an interactive tree widget matching Nordic Studio UI."""

    request_removal = Signal(list)  # list of file paths selected for removal
    request_rescan = Signal()

    def __init__(self, db_manager: Any = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_groups: List[Dict[str, Any]] = []

        self._init_ui()
        self.refresh_results()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header bar
        header_layout = QHBoxLayout()
        header_title = QLabel("Duplicate Groups Overview")
        header_title.setObjectName("sectionHeader")
        header_title.setStyleSheet("font-size: 22px; font-weight: 700; color: #10B981;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        refresh_btn = QPushButton(f"{ICON_REFRESH} Refresh")
        refresh_btn.clicked.connect(self.refresh_results)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # Search and Sort Bar
        filter_card = QFrame()
        filter_card.setObjectName("cardFrame")
        filter_h = QHBoxLayout(filter_card)

        filter_h.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by file path or name...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_h.addWidget(self.search_input)

        filter_h.addWidget(QLabel("Sort:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Total Size (Descending)", "Duplicate Count (Descending)", "File Name"])
        self.sort_combo.currentIndexChanged.connect(self._apply_filters)
        filter_h.addWidget(self.sort_combo)

        main_layout.addWidget(filter_card)

        # Tree Widget for Groups and Files
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size", "Type", "Modified Date", "Actions"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.tree)

        # Action Bar at Bottom
        action_card = QFrame()
        action_card.setObjectName("cardFrame")
        action_h = QHBoxLayout(action_card)

        self.summary_label = QLabel("0 duplicate groups found.")
        self.summary_label.setStyleSheet("color: #9CA3AF;")
        action_h.addWidget(self.summary_label)
        action_h.addStretch()

        select_dupes_btn = QPushButton("Select All Duplicates")
        select_dupes_btn.clicked.connect(self._auto_select_duplicates)
        action_h.addWidget(select_dupes_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all)
        action_h.addWidget(deselect_all_btn)

        self.remove_btn = QPushButton(f"{ICON_TRASH} Remove Selected")
        self.remove_btn.setObjectName("dangerBtn")
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        action_h.addWidget(self.remove_btn)

        main_layout.addWidget(action_card)

    def refresh_results(self):
        """Fetch duplicate groups from DB and update tree view."""
        if not self.db_manager:
            return

        try:
            self.current_groups = duplicate_detector.get_duplicate_groups(self.db_manager)
            self._apply_filters()
        except Exception as e:
            print(f"Error refreshing results view: {e}")

    def _apply_filters(self):
        self.tree.clear()
        search_query = self.search_input.text().lower().strip()
        sort_mode = self.sort_combo.currentIndex()

        groups = list(self.current_groups)

        # Sort groups
        if sort_mode == 0:  # Size Descending
            groups.sort(key=lambda g: g.get("total_size", 0), reverse=True)
        elif sort_mode == 1:  # Count Descending
            groups.sort(key=lambda g: g.get("duplicate_count", 0), reverse=True)
        elif sort_mode == 2:  # Name
            groups.sort(key=lambda g: g["files"][0].get("file_name", "") if g.get("files") else "")

        total_groups_shown = 0
        total_files_shown = 0

        for grp in groups:
            files = grp.get("files", [])

            # Filter files by search query
            if search_query:
                matching_files = [
                    f for f in files if search_query in f.get("file_path", "").lower() or search_query in f.get("file_name", "").lower()
                ]
            else:
                matching_files = files

            if not matching_files:
                continue

            total_groups_shown += 1
            total_files_shown += len(matching_files)

            # Create Group Top Item
            total_mb = (grp.get("total_size") or 0) / (1024 * 1024)
            first_name = matching_files[0].get("file_name", "Group") if matching_files else "Group"
            group_item = QTreeWidgetItem(self.tree)
            group_item.setText(0, f"📂 {first_name}  [{len(matching_files)} copies]")
            group_item.setText(1, f"{total_mb:.1f} MB")
            group_item.setText(2, "Executable Group")
            group_item.setText(3, "-")
            group_item.setText(4, "Group")
            group_item.setExpanded(True)

            # Create Child File Items
            for f in matching_files:
                file_item = QTreeWidgetItem(group_item)
                file_item.setFlags(file_item.flags() | Qt.ItemIsUserCheckable)
                file_item.setCheckState(0, Qt.Unchecked)

                f_path = f.get("file_path", "")
                f_size_mb = f.get("file_size", 0) / (1024 * 1024)

                mtime_str = "-"
                if os.path.exists(f_path):
                    mtime = os.path.getmtime(f_path)
                    mtime_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))

                ext = f.get("extension", "").upper().replace(".", "") or "FILE"

                file_item.setText(0, f_path)
                file_item.setText(1, f"{f_size_mb:.1f} MB")
                file_item.setText(2, ext)
                file_item.setText(3, mtime_str)
                file_item.setText(4, "Duplicate" if f.get("is_duplicate") else "Original")
                file_item.setData(0, Qt.UserRole, f_path)

        self.summary_label.setText(
            f"Showing {total_groups_shown} duplicate groups ({total_files_shown} files)."
        )

    def _auto_select_duplicates(self):
        """Auto check all file items in each group except the first one."""
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            group_item = root.child(i)
            for j in range(group_item.childCount()):
                child = group_item.child(j)
                if j > 0:
                    child.setCheckState(0, Qt.Checked)
                else:
                    child.setCheckState(0, Qt.Unchecked)

    def _deselect_all(self):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            group_item = root.child(i)
            for j in range(group_item.childCount()):
                group_item.child(j).setCheckState(0, Qt.Unchecked)

    def _on_remove_clicked(self):
        selected_paths = []
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            group_item = root.child(i)
            for j in range(group_item.childCount()):
                child = group_item.child(j)
                if child.checkState(0) == Qt.Checked:
                    fpath = child.data(0, Qt.UserRole)
                    if fpath:
                        selected_paths.append(fpath)

        if selected_paths:
            self.request_removal.emit(selected_paths)
