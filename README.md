# Duplicate Application Manager

A desktop application and CLI tool built with Python and PySide6 that detects and organizes duplicate applications using **content-based cryptographic hashing** (SHA-256) rather than filenames. It features automated rule-based categorization, safe trash removal, interactive statistics dashboards, and customizable JSON rules.

---

## Key Features

- **Content-Based Duplicate Detection**: Uses SHA-256 hashing to identify identical files regardless of file names or installation locations.
- **Partial Hashing for Large Files**: Fast hashing of large files (>100 MB) by sampling file headers, footers, and size metadata.
- **Hash Caching**: SQLite database cache avoids re-hashing unchanged files during subsequent scans.
- **Rule-Based Categorization**: Prioritized category assignment based on file paths, file extensions, size ranges, and regex rules configured in `config/rules.json`.
- **Safe Removal**: Uses `send2trash` to safely move selected duplicate files to the system Recycle Bin/Trash rather than permanent deletion.
- **Modern PySide6 Desktop GUI**: Modern, dark-themed responsive interface with Dashboard, Scan Config, Duplicate Results tree, and Category Browser.
- **Headless / CLI Mode**: Command-line interface support for automated environment scans and report exports.
- **Reporting & Exporting**: Comprehensive summary stats with JSON and formatted Text report export capabilities.

---

## Project Structure

```
duplicate_app_manager/
├── config/
│   ├── default_config.json   # Default scanner & app configuration
│   └── rules.json            # Prioritized categorization rules
├── data/
│   └── app_manager.db        # SQLite database (applications, categories, hash cache, groups)
├── logs/
│   └── app_manager.log       # Application logs
├── src/
│   ├── config_manager.py     # Config and rules loading/saving
│   ├── database.py           # SQLite connection & CRUD operations
│   ├── hasher.py             # SHA-256 full/partial hashing & cache
│   ├── scanner.py            # Recursive directory scanning & filtering
│   ├── duplicate_detector.py # Duplicate grouping & savings calculation
│   ├── categorizer.py        # Rule matching engine
│   ├── remover.py            # Safe trash removal via send2trash
│   ├── reporter.py           # Summary generation & report export
│   └── gui/
│       ├── main_window.py    # Main window with sidebar navigation
│       ├── dashboard.py      # Dashboard cards & breakdown charts
│       ├── scan_view.py      # Scan configuration & background worker
│       ├── results_view.py   # Hierarchical duplicate groups tree
│       ├── category_view.py  # Category browser & app move dialog
│       └── styles.py         # QSS design system & dark/light themes
├── tests/
│   ├── test_phase1.py        # Database & Config manager tests
│   ├── test_phase2.py        # Core logic tests
│   ├── test_phase3.py        # PySide6 GUI unit tests
│   └── test_phase4.py        # Remover, Reporter, and E2E integration tests
├── main.py                   # Application entry point
├── requirements.txt          # Dependencies
└── README.md                 # Project documentation
```

---

## Prerequisites & Installation

### Requirements
- Python 3.10+

### Installation Steps

1. Clone or download the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. GUI Desktop Interface (Default)

Launch the PySide6 desktop interface:
```bash
python main.py
```

### 2. Command Line Arguments

You can pass optional arguments to `main.py`:

```bash
# Specify custom configuration and rules files
python main.py --config config/default_config.json --rules config/rules.json

# Auto-start scan on launch in GUI mode
python main.py --scan "C:\Program Files"

# Run in Headless CLI mode without GUI and export report to JSON
python main.py --headless --scan "D:\Applications" --report "data/report.json"

# Run in Headless CLI mode and export plain text summary report
python main.py --headless --scan "D:\Applications" --report "data/report.txt"
```

---

## Running Unit & Integration Tests

Run the complete automated test suite (Phase 1 to Phase 4):
```bash
python -m unittest discover tests -v
```

---

## License

MIT License. Designed and implemented for the Duplicate Application Manager project.
