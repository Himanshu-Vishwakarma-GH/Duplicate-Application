"""
Main entry point for Duplicate Application Manager.
Handles CLI options, logging configuration, headless execution, and PySide6 Desktop GUI launch.
"""

import argparse
import logging
import os
import sys

# Ensure src directory is in sys.path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.config_manager import ConfigManager, load_config, load_rules
from src.database import DatabaseManager
import src.scanner as scanner
import src.hasher as hasher
import src.duplicate_detector as duplicate_detector
import src.categorizer as categorizer
import src.reporter as reporter


def setup_logging(log_level_name: str = "INFO") -> None:
    """Configure logging to file (logs/app_manager.log) and console."""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir, "app_manager.log")
    numeric_level = getattr(logging, log_level_name.upper(), logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(numeric_level)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def run_headless_scan(scan_dir: str, config_mgr: ConfigManager, db_mgr: DatabaseManager, report_path: str = None) -> None:
    """Run scanning and duplicate detection in headless CLI mode without GUI."""
    logging.info(f"Starting headless scan on directory: {scan_dir}")
    
    cfg = config_mgr.config
    rules = config_mgr.rules.get("categories", [])

    # 1. Scan
    scanned_files = scanner.scan_directory(scan_dir, config=cfg, recursive=True)
    logging.info(f"Scanned {len(scanned_files)} files in {scan_dir}.")

    # 2. Categorize
    for f in scanned_files:
        categorizer.assign_category_to_app(f, rules, db_manager=db_mgr)

    # 3. Detect duplicates
    dupe_groups = duplicate_detector.find_duplicates(
        files=scanned_files,
        hasher_module=hasher,
        db_manager=db_mgr,
        threshold_mb=cfg.get("large_file_threshold_mb", 100),
    )
    logging.info(f"Duplicate detection finished. Found {len(dupe_groups)} duplicate groups.")

    # 4. Generate summary report
    summary = reporter.generate_summary(db_mgr)
    print("\n" + "=" * 60)
    print("HEADLESS SCAN SUMMARY REPORT")
    print("=" * 60)
    print(f"Total Applications: {summary['total_applications']}")
    print(f"Duplicate Applications: {summary['duplicate_applications']}")
    print(f"Duplicate Groups: {summary['duplicate_groups_count']}")
    print(f"Potential Space Savings: {summary['potential_savings_mb']} MB")
    print("=" * 60)

    if report_path:
        if report_path.endswith(".json"):
            reporter.export_json(summary, report_path)
        else:
            reporter.export_text(summary, report_path)
        print(f"Report exported to: {report_path}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Duplicate Application Manager")
    parser.add_argument("--config", type=str, default="config/default_config.json", help="Path to config.json")
    parser.add_argument("--rules", type=str, default="config/rules.json", help="Path to rules.json")
    parser.add_argument("--scan", type=str, default=None, help="Directory to scan immediately on launch")
    parser.add_argument("--report", type=str, default=None, help="Path to export report (JSON or TXT)")
    parser.add_argument("--headless", action="store_true", help="Run in headless CLI mode without GUI")

    args = parser.parse_args()

    # Load configuration
    try:
        config_mgr = ConfigManager(config_path=args.config, rules_path=args.rules)
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Setup Logging
    setup_logging(config_mgr.config.get("log_level", "INFO"))
    logging.info("Initializing Duplicate Application Manager...")

    # Database setup
    db_path = config_mgr.config.get("database_path", "data/app_manager.db")
    db_mgr = DatabaseManager(db_path=db_path)
    db_mgr.init_db()

    # Seed categories if DB empty
    existing_cats = db_mgr.get_all_categories()
    if not existing_cats:
        rules = config_mgr.rules.get("categories", [])
        for cat in rules:
            db_mgr.add_category(
                name=cat["name"],
                description=cat.get("description", ""),
                priority=cat.get("priority", 0),
            )

    # Headless execution mode
    if args.headless:
        scan_target = args.scan or (config_mgr.config.get("scan_directories") and config_mgr.config.get("scan_directories")[0])
        if not scan_target:
            print("Error: Headless mode requires --scan <directory> or scan_directories in config.")
            sys.exit(1)
        run_headless_scan(scan_target, config_mgr, db_mgr, report_path=args.report)
        return

    # PySide6 Desktop GUI Mode
    from PySide6.QtWidgets import QApplication
    from src.gui.main_window import MainWindow

    logging.info("Launching PySide6 Desktop Interface...")
    app = QApplication(sys.argv)

    window = MainWindow(config_manager=config_mgr, db_manager=db_mgr)
    window.show()

    # If --scan arg provided, trigger scan immediately
    if args.scan:
        window.scan_view.dirs_list.clear()
        window.scan_view.dirs_list.addItem(args.scan)
        window._switch_page(1)  # switch to Scan view

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
