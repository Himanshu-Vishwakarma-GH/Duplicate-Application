"""
Scan Configuration View module for Duplicate Application Manager.
Configures scan directories, extension filters, exclusions, and runs background scan threads.
"""

from typing import Any, Dict, List, Optional
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import src.scanner as scanner
import src.hasher as hasher
import src.duplicate_detector as duplicate_detector
import src.categorizer as categorizer
from src.gui.styles import ICON_ADD, ICON_REMOVE, ICON_SCAN


class ScanWorker(QThread):
    """Background worker thread for performing scanning, hashing, detection, and categorization."""

    progress_updated = Signal(int, str)
    scan_finished = Signal(dict)

    def __init__(
        self,
        scan_dirs: List[str],
        config: Dict[str, Any],
        db_manager: Any,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.scan_dirs = scan_dirs
        self.config = config
        self.db_manager = db_manager

    def run(self):
        try:
            self.progress_updated.emit(5, "Scanning directories...")
            all_files: List[Dict[str, Any]] = []

            total_dirs = len(self.scan_dirs)
            for idx, dpath in enumerate(self.scan_dirs):
                self.progress_updated.emit(
                    10 + int((idx / max(1, total_dirs)) * 30),
                    f"Scanning directory: {dpath}...",
                )
                scanned = scanner.scan_directory(dpath, config=self.config, recursive=True)
                all_files.extend(scanned)

            self.progress_updated.emit(45, f"Found {len(all_files)} files. Categorizing applications...")
            rules = self.config.get("rules", [])
            for f in all_files:
                categorizer.assign_category_to_app(f, rules, db_manager=self.db_manager)

            self.progress_updated.emit(65, "Computing content hashes & detecting duplicates...")
            threshold_mb = self.config.get("large_file_threshold_mb", 100)
            dupe_groups = duplicate_detector.find_duplicates(
                files=all_files,
                hasher_module=hasher,
                db_manager=self.db_manager,
                threshold_mb=threshold_mb,
            )

            self.progress_updated.emit(100, "Scan completed successfully!")
            stats = {
                "total_files": len(all_files),
                "duplicate_groups": len(dupe_groups),
                "duplicate_files": sum(g.get("duplicate_count", 0) for g in dupe_groups),
            }
            self.scan_finished.emit(stats)

        except Exception as e:
            self.progress_updated.emit(0, f"Error during scan: {e}")
            self.scan_finished.emit({"error": str(e)})


class ScanView(QWidget):
    """Scan Configuration and Progress View."""

    scan_completed = Signal()

    def __init__(self, config_manager: Any = None, db_manager: Any = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.worker: Optional[ScanWorker] = None

        self._init_ui()
        self._load_config_values()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 20)
        main_layout.setSpacing(14)

        # Header Title
        header_v = QVBoxLayout()
        header_v.setSpacing(2)

        header_title = QLabel("Scan Configuration")
        header_title.setObjectName("sectionTitle")
        header_v.addWidget(header_title)

        header_sub = QLabel("Select scan directories, configure file extension filters, and adjust hashing parameters.")
        header_sub.setObjectName("sectionSubtitle")
        header_v.addWidget(header_sub)
        main_layout.addLayout(header_v)

        # Card 1: Scan Directories
        dirs_card = QFrame()
        dirs_card.setObjectName("cardFrame")
        dirs_v = QVBoxLayout(dirs_card)
        dirs_v.setContentsMargins(14, 14, 14, 14)
        dirs_v.setSpacing(8)

        dirs_header = QLabel("Scan Directories")
        dirs_header.setStyleSheet("font-size: 14px; font-weight: 700;")
        dirs_v.addWidget(dirs_header)

        self.dirs_list = QListWidget()
        self.dirs_list.setFixedHeight(85)
        dirs_v.addWidget(self.dirs_list)

        dirs_btn_layout = QHBoxLayout()
        add_dir_btn = QPushButton(f"{ICON_ADD}  Add Directory")
        add_dir_btn.clicked.connect(self._add_directory)
        dirs_btn_layout.addWidget(add_dir_btn)

        rem_dir_btn = QPushButton(f"{ICON_REMOVE}  Remove Selected")
        rem_dir_btn.clicked.connect(self._remove_directory)
        dirs_btn_layout.addWidget(rem_dir_btn)
        dirs_btn_layout.addStretch()

        dirs_v.addLayout(dirs_btn_layout)
        main_layout.addWidget(dirs_card)

        # Card 2: Filters & Exclusions
        filter_card = QFrame()
        filter_card.setObjectName("cardFrame")
        filter_layout = QFormLayout(filter_card)
        filter_layout.setContentsMargins(14, 14, 14, 14)
        filter_layout.setSpacing(10)

        filter_header = QLabel("File Filters & Exclusions")
        filter_header.setStyleSheet("font-size: 14px; font-weight: 700;")
        filter_layout.addRow(filter_header)

        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText(".exe, .msi, .app, .dmg, .deb, .rpm")
        filter_layout.addRow("File Extensions:", self.ext_input)

        self.excl_input = QLineEdit()
        self.excl_input.setPlaceholderText("node_modules, .git, __pycache__")
        filter_layout.addRow("Excluded Directories:", self.excl_input)

        main_layout.addWidget(filter_card)

        # Card 3: Options
        options_card = QFrame()
        options_card.setObjectName("cardFrame")
        options_v = QVBoxLayout(options_card)
        options_v.setContentsMargins(14, 14, 14, 14)
        options_v.setSpacing(8)

        opts_header = QLabel("Scan Options")
        opts_header.setStyleSheet("font-size: 14px; font-weight: 700;")
        options_v.addWidget(opts_header)

        self.chk_cache = QCheckBox("Use cached hashes for faster re-scans")
        self.chk_cache.setChecked(True)
        options_v.addWidget(self.chk_cache)

        self.chk_partial = QCheckBox("Use partial hashing for large files (> 100 MB)")
        self.chk_partial.setChecked(True)
        options_v.addWidget(self.chk_partial)

        self.chk_symlinks = QCheckBox("Follow symbolic links")
        self.chk_symlinks.setChecked(False)
        options_v.addWidget(self.chk_symlinks)

        main_layout.addWidget(options_card)

        # Progress & Control Section (Always Visible)
        control_card = QFrame()
        control_card.setObjectName("cardFrame")
        control_v = QVBoxLayout(control_card)
        control_v.setContentsMargins(14, 14, 14, 14)
        control_v.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(22)
        control_v.addWidget(self.progress_bar)

        ctrl_bottom_h = QHBoxLayout()
        self.status_label = QLabel("Ready to scan.")
        self.status_label.setStyleSheet("color: #8A94A6; font-size: 12px;")
        ctrl_bottom_h.addWidget(self.status_label)
        ctrl_bottom_h.addStretch()

        self.start_scan_btn = QPushButton(f"{ICON_SCAN}  Start Scan Now")
        self.start_scan_btn.setObjectName("primaryBtn")
        self.start_scan_btn.setFixedHeight(38)
        self.start_scan_btn.clicked.connect(self._start_scan)
        ctrl_bottom_h.addWidget(self.start_scan_btn)

        control_v.addLayout(ctrl_bottom_h)
        main_layout.addWidget(control_card)

    def _load_config_values(self):
        if not self.config_manager:
            return

        cfg = self.config_manager.config
        dirs = cfg.get("scan_directories", [])
        self.dirs_list.clear()
        for d in dirs:
            self.dirs_list.addItem(QListWidgetItem(d))

        exts = cfg.get("file_extensions", [])
        self.ext_input.setText(", ".join(exts))

        excls = cfg.get("excluded_directories", [])
        self.excl_input.setText(", ".join(excls))

    def _add_directory(self):
        dpath = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if dpath:
            self.dirs_list.addItem(QListWidgetItem(dpath))

    def _remove_directory(self):
        selected = self.dirs_list.selectedItems()
        for item in selected:
            self.dirs_list.takeItem(self.dirs_list.row(item))

    def _start_scan(self):
        scan_dirs = [self.dirs_list.item(i).text() for i in range(self.dirs_list.count())]
        if not scan_dirs:
            self.status_label.setText("Please add at least one directory to scan.")
            return

        ext_text = self.ext_input.text()
        exts = [e.strip() for e in ext_text.split(",") if e.strip()]

        excl_text = self.excl_input.text()
        excls = [e.strip() for e in excl_text.split(",") if e.strip()]

        scan_config = {
            "file_extensions": exts,
            "excluded_directories": excls,
            "large_file_threshold_mb": 100 if self.chk_partial.isChecked() else 999999,
            "rules": self.config_manager.rules.get("categories", []) if self.config_manager else [],
        }

        if self.config_manager:
            self.config_manager.config["scan_directories"] = scan_dirs
            self.config_manager.config["file_extensions"] = exts
            self.config_manager.config["excluded_directories"] = excls
            self.config_manager.save()

        self.start_scan_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting scan...")

        self.worker = ScanWorker(
            scan_dirs=scan_dirs,
            config=scan_config,
            db_manager=self.db_manager,
            parent=self,
        )
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.scan_finished.connect(self._on_scan_finished)
        self.worker.start()

    def _on_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.status_label.setText(msg)

    def _on_scan_finished(self, stats: Dict[str, Any]):
        self.start_scan_btn.setEnabled(True)
        if "error" in stats:
            self.status_label.setText(f"Scan failed: {stats['error']}")
        else:
            self.status_label.setText(
                f"Scan finished! Found {stats.get('total_files', 0)} files in {stats.get('duplicate_groups', 0)} duplicate groups."
            )
            self.scan_completed.emit()
