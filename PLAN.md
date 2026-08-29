# Python Duplicate Application Manager - Brainstorming & Plan

## 1. PROJECT OVERVIEW

**Goal**: Build an intelligent application management tool that detects duplicate applications using content-based hashing (not filename/type/timestamp) and categorizes them using rule-based systems.

**Tech Stack**: Python 3.x, hashlib, json/yaml, os, shutil, sqlite3, argparse

---

## 2. ARCHITECTURE DESIGN

```
┌─────────────────────────────────────────────────────┐
│                    CLI Interface                     │
│              (argparse + rich for display)           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Application Manager Core               │
├─────────────┬─────────────┬─────────────┬───────────┤
│  Scanner    │   Hasher    │  Categorizer│  Remover  │
│  Module     │   Module    │  Engine     │  Module   │
└──────┬──────┴──────┬──────┴──────┬──────┴─────┬─────┘
       │             │             │             │
┌──────▼─────────────▼─────────────▼─────────────▼─────┐
│                    Data Layer                        │
│         (SQLite DB + JSON Config + Logs)             │
└─────────────────────────────────────────────────────┘
```

---

## 3. CORE MODULES

### 3.1 Scanner Module (`scanner.py`)
- Recursively scan configured directories
- Collect file metadata (path, size, extension)
- Support filtering by file extensions
- Handle symlinks and permission errors gracefully
- Memory-efficient iteration for large directories

### 3.2 Hasher Module (`hasher.py`)
- Generate SHA-256 hashes for file content
- Support partial hashing for large files (first + last chunks + size)
- Progress tracking for hash generation
- Hash caching to avoid re-hashing unchanged files

### 3.3 Duplicate Detector (`duplicate_detector.py`)
- Group files by hash values
- Identify duplicate clusters
- Calculate space savings potential
- Store results in SQLite database

### 3.4 Categorizer Engine (`categorizer.py`)
- Load rules from JSON configuration
- Apply rules based on:
  - File path patterns
  - File extensions
  - File size ranges
  - Keyword matching in paths
- Support priority-based rule ordering
- Handle multiple category assignment

### 3.5 Remover Module (`remover.py`)
- Safe deletion (move to trash by default)
- Batch removal support
- Confirmation prompts
- Undo capability
- Backup creation before removal

### 3.6 Reporter Module (`reporter.py`)
- Generate summary reports
- Show duplicate statistics
- Categorization breakdown
- Export to text/JSON format

### 3.7 Config Manager (`config_manager.py`)
- Manage scan directories
- Manage categorization rules
- Store preferences
- Default configuration loading

---

## 4. DATA MODELS

### Application Record
```python
{
    "id": int,
    "file_path": str,
    "file_name": str,
    "file_size": int,
    "content_hash": str,
    "category": str,
    "is_duplicate": bool,
    "duplicate_group_id": int,
    "last_scanned": datetime
}
```

### Categorization Rule
```python
{
    "category_name": str,
    "rules": [
        {"type": "path_contains", "value": str, "case_sensitive": bool},
        {"type": "path_matches", "pattern": str},  # regex
        {"type": "extension", "values": [str]},
        {"type": "size_range", "min": int, "max": int}
    ],
    "priority": int
}
```

---

## 5. CLI COMMANDS

```bash
# Initialize configuration
python app_manager.py init

# Scan directories
python app_manager.py scan [--dir /path/to/scan] [--recursive]

# Detect duplicates
python app_manager.py detect [--hash-algo sha256]

# Categorize applications
python app_manager.py categorize [--rules rules.json]

# List all applications (by category)
python app_manager.py list [--category "Games"] [--duplicates-only]

# Remove duplicates
python app_manager.py remove [--interactive] [--dry-run]

# Generate report
python app_manager.py report [--output report.txt] [--format json|text]

# Manage configuration
python app_manager.py config --add-dir /path
python app_manager.py config --add-rule rules.json
python app_manager.py config --show
```

---

## 6. PROJECT STRUCTURE

```
duplicate_app_manager/
├── src/
│   ├── __init__.py
│   ├── scanner.py          # Directory scanning
│   ├── hasher.py           # Content hashing
│   ├── duplicate_detector.py # Duplicate detection
│   ├── categorizer.py      # Rule-based categorization
│   ├── remover.py          # Safe duplicate removal
│   ├── reporter.py         # Report generation
│   ├── config_manager.py   # Configuration handling
│   ├── database.py         # SQLite operations
│   └── cli.py              # CLI interface
├── config/
│   ├── default_config.json # Default configuration
│   └── rules.json          # Categorization rules
├── data/
│   └── app_manager.db      # SQLite database
├── logs/
│   └── app_manager.log     # Application logs
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py
│   ├── test_hasher.py
│   ├── test_duplicate_detector.py
│   └── test_categorizer.py
├── requirements.txt
├── setup.py
└── README.md
```

---

## 7. IMPLEMENTATION PHASES

### Phase 1: Foundation (Day 1)
- [ ] Project setup and structure
- [ ] Configuration manager
- [ ] SQLite database schema and operations
- [ ] Basic CLI framework

### Phase 2: Core Detection (Day 1-2)
- [ ] Scanner module
- [ ] Hasher module with progress tracking
- [ ] Duplicate detector
- [ ] Hash caching mechanism

### Phase 3: Categorization (Day 2)
- [ ] Rule parser (JSON)
- [ ] Categorizer engine
- [ ] Multiple rule type support
- [ ] Priority handling

### Phase 4: User Interface (Day 2-3)
- [ ] Interactive CLI with rich library
- [ ] Application listing with categories
- [ ] Duplicate group display
- [ ] Selection interface for removal

### Phase 5: Removal & Safety (Day 3)
- [ ] Safe deletion (trash support)
- [ ] Confirmation dialogs
- [ ] Backup mechanism
- [ ] Undo capability

### Phase 6: Reporting & Polish (Day 3)
- [ ] Report generation
- [ ] Logging implementation
- [ ] Error handling
- [ ] Documentation

---

## 8. DEFAULT CATEGORIZATION RULES

```json
{
  "categories": [
    {
      "name": "Development Tools",
      "priority": 1,
      "rules": [
        {"type": "path_contains", "value": "dev"},
        {"type": "path_contains", "value": "development"},
        {"type": "path_contains", "value": "sdk"},
        {"type": "extension", "values": [".py", ".js", ".java", ".cpp", ".go"]}
      ]
    },
    {
      "name": "Games",
      "priority": 2,
      "rules": [
        {"type": "path_contains", "value": "games"},
        {"type": "path_contains", "value": "steam"},
        {"type": "path_contains", "value": "epic games"}
      ]
    },
    {
      "name": "Productivity",
      "priority": 3,
      "rules": [
        {"type": "path_contains", "value": "office"},
        {"type": "path_contains", "value": "microsoft"},
        {"type": "extension", "values": [".docx", ".xlsx", ".pptx"]}
      ]
    },
    {
      "name": "Utilities",
      "priority": 4,
      "rules": [
        {"type": "path_contains", "value": "tools"},
        {"type": "path_contains", "value": "utilities"}
      ]
    },
    {
      "name": "Uncategorized",
      "priority": 999,
      "rules": []
    }
  ]
}
```

---

## 9. KEY FEATURES CHECKLIST

- [ ] Content-based duplicate detection (SHA-256)
- [ ] Support for partial hashing (large files)
- [ ] SQLite database for persistence
- [ ] JSON-based rule configuration
- [ ] Interactive CLI with rich output
- [ ] Safe deletion with trash support
- [ ] Batch operations
- [ ] Progress bars for long operations
- [ ] Detailed logging
- [ ] Report generation (text/JSON)
- [ ] Configuration management
- [ ] Error handling and recovery

---

## 10. DEPENDENCIES

```
# requirements.txt
rich>=13.0.0          # Beautiful terminal output
send2trash>=1.8.0     # Cross-platform trash support
pyyaml>=6.0           # YAML support (optional)
sqlite3               # Built-in database
hashlib               # Built-in hashing
argparse              # Built-in CLI parsing
```

---

## 11. NEXT STEPS

1. Confirm project structure and approach
2. Begin Phase 1 implementation
3. Set up development environment
4. Create initial codebase
