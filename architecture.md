# System Architecture Document

## Project Name
**Duplicate Application Manager**

## Version
1.0.0

## Date
August 29, 2026

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                       │
│                     PySide6 (Qt6) Desktop GUI                   │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard  │  Scan Config  │  Results View  │  Category Browser │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                        BUSINESS LOGIC LAYER                     │
├─────────────┬──────────────┬──────────────┬─────────────────────┤
│   Scanner   │   Hasher     │  Detector    │   Categorizer       │
│   Module    │   Module     │  Module      │   Engine            │
└──────┬──────┴──────┬───────┴──────┬───────┴──────────┬──────────┘
       │             │              │                  │
┌──────▼─────────────▼──────────────▼──────────────────▼──────────┐
│                         DATA ACCESS LAYER                       │
├─────────────────────────┬───────────────────────────────────────┤
│     SQLite Database     │      JSON Configuration              │
│   (app_manager.db)     │      (rules.json, config.json)        │
└─────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Module Architecture

### 2.1 Module Dependency Graph

```
                    ┌─────────────┐
                    │     CLI     │
                    │  (entry)    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Config    │
                    │   Manager   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│    Scanner    │  │   Database    │  │   Logger      │
│    Module     │  │   Manager     │  │   Module      │
└───────┬───────┘  └───────────────┘  └───────────────┘
        │
┌───────▼───────┐
│    Hasher     │
│    Module     │
└───────┬───────┘
        │
┌───────▼───────┐
│   Duplicate   │
│   Detector    │
└───────┬───────┘
        │
┌───────▼───────┐
│  Categorizer  │
│    Engine     │
└───────┬───────┘
        │
┌───────▼───────┐
│   Remover     │
│    Module     │
└───────────────┘
```

### 2.2 Module Responsibilities

| Module | Responsibility | Key Methods |
|--------|----------------|-------------|
| **Scanner** | Recursively scan directories | `scan_directory()`, `get_file_info()` |
| **Hasher** | Generate content hashes | `hash_file()`, `partial_hash()`, `cache_hash()` |
| **Detector** | Group duplicates by hash | `find_duplicates()`, `create_groups()` |
| **Categorizer** | Apply rules to categorize | `load_rules()`, `categorize_app()` |
| **Remover** | Safe deletion | `move_to_trash()`, `batch_remove()` |
| **Database** | Persistent storage | `save_app()`, `get_duplicates()` |
| **Config** | Configuration management | `load_config()`, `save_config()` |
| **GUI** | User interface | `show_dashboard()`, `show_results()` |

---

## 3. Data Flow

### 3.1 Scan & Detect Flow

```
User Clicks "Scan"
        │
        ▼
┌─────────────────┐
│ Scanner.scan()  │
│ - Walk directory│
│ - Get file info │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hasher.hash()   │
│ - Read file     │
│ - SHA-256 hash  │
│ - Cache result  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DB.save()       │
│ - Store record  │
│ - Link to hash  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Detector.find() │
│ - Group by hash │
│ - Mark dupes    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GUI.update()    │
│ - Show results  │
│ - Show groups   │
└─────────────────┘
```

### 3.2 Categorization Flow

```
┌─────────────────┐
│ Load rules.json │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ For each app:   │
│ - Check rules   │
│ - Match pattern │
│ - Assign cat    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DB.update()     │
│ - Store category│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GUI.refresh()   │
│ - Group by cat  │
└─────────────────┘
```

### 3.3 Removal Flow

```
┌─────────────────┐
│ User selects    │
│ duplicates      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Confirmation    │
│ Dialog          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Remover.remove()│
│ - Move to trash │
│ - Log action    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DB.delete()     │
│ - Remove record │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GUI.show_report │
│ - Show savings  │
└─────────────────┘
```

---

## 4. Database Schema

### 4.1 ER Diagram

```
┌──────────────────────┐       ┌──────────────────────┐
│     applications     │       │    categories        │
├──────────────────────┤       ├──────────────────────┤
│ id (PK)              │       │ id (PK)              │
│ file_path            │       │ name                 │
│ file_name            │       │ description          │
│ file_size            │       │ priority             │
│ content_hash (FK)    │──────▶│ created_at           │
│ category_id (FK)     │──────▶│                      │
│ is_duplicate         │       └──────────────────────┘
│ duplicate_group_id   │
│ created_at           │       ┌──────────────────────┐
│ updated_at           │       │    hash_cache        │
└──────────────────────┘       ├──────────────────────┤
                               │ hash (PK)            │
                               │ file_path            │
                               │ file_size            │
                               │ computed_at          │
                               └──────────────────────┘
```

### 4.2 SQL Schema

```sql
-- Applications table
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    category_id INTEGER,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_group_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Categories table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hash cache for performance
CREATE TABLE hash_cache (
    hash TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Duplicate groups
CREATE TABLE duplicate_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT NOT NULL,
    total_size INTEGER,
    duplicate_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_app_hash ON applications(content_hash);
CREATE INDEX idx_app_category ON applications(category_id);
CREATE INDEX idx_app_duplicate ON applications(is_duplicate);
CREATE INDEX idx_hash_cache_path ON hash_cache(file_path);
```

---

## 5. Configuration Schema

### 5.1 config.json

```json
{
  "version": "1.0.0",
  "scan_directories": [
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "D:\\Applications"
  ],
  "excluded_directories": [
    "node_modules",
    ".git",
    "__pycache__"
  ],
  "file_extensions": [
    ".exe", ".msi", ".app", ".dmg", ".deb", ".rpm"
  ],
  "hash_algorithm": "sha256",
  "large_file_threshold_mb": 100,
  "database_path": "data/app_manager.db",
  "log_level": "INFO",
  "theme": "dark"
}
```

### 5.2 rules.json

```json
{
  "version": "1.0.0",
  "categories": [
    {
      "name": "Development Tools",
      "description": "Programming IDEs, SDKs, and development utilities",
      "priority": 1,
      "rules": [
        {"type": "path_contains", "value": "dev", "case_sensitive": false},
        {"type": "path_contains", "value": "development", "case_sensitive": false},
        {"type": "path_contains", "value": "sdk", "case_sensitive": false},
        {"type": "path_contains", "value": "ide", "case_sensitive": false},
        {"type": "extension", "values": [".py", ".js", ".java", ".cpp"]}
      ]
    },
    {
      "name": "Games",
      "description": "Gaming applications and platforms",
      "priority": 2,
      "rules": [
        {"type": "path_contains", "value": "games", "case_sensitive": false},
        {"type": "path_contains", "value": "steam", "case_sensitive": false},
        {"type": "path_contains", "value": "epic", "case_sensitive": false},
        {"type": "path_contains", "value": "gaming", "case_sensitive": false}
      ]
    },
    {
      "name": "Productivity",
      "description": "Office suites, document editors, and productivity tools",
      "priority": 3,
      "rules": [
        {"type": "path_contains", "value": "office", "case_sensitive": false},
        {"type": "path_contains", "value": "microsoft", "case_sensitive": false},
        {"type": "path_contains", "value": "productivity", "case_sensitive": false},
        {"type": "extension", "values": [".docx", ".xlsx", ".pptx"]}
      ]
    },
    {
      "name": "Utilities",
      "description": "System utilities and helper tools",
      "priority": 4,
      "rules": [
        {"type": "path_contains", "value": "tools", "case_sensitive": false},
        {"type": "path_contains", "value": "utilities", "case_sensitive": false},
        {"type": "path_contains", "value": "system", "case_sensitive": false}
      ]
    },
    {
      "name": "Media",
      "description": "Audio, video, and image processing applications",
      "priority": 5,
      "rules": [
        {"type": "path_contains", "value": "media", "case_sensitive": false},
        {"type": "path_contains", "value": "video", "case_sensitive": false},
        {"type": "path_contains", "value": "audio", "case_sensitive": false},
        {"type": "extension", "values": [".mp3", ".mp4", ".avi", ".wav"]}
      ]
    },
    {
      "name": "Uncategorized",
      "description": "Applications that don't match any rule",
      "priority": 999,
      "rules": []
    }
  ]
}
```

---

## 6. Technology Stack

### 6.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.10+ | Core runtime |
| GUI | PySide6 | 6.5+ | Desktop interface |
| Database | SQLite3 | Built-in | Data persistence |
| Hashing | hashlib | Built-in | Content hashing |
| Config | json | Built-in | Configuration |
| Logging | logging | Built-in | Application logs |

### 6.2 External Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| PySide6 | 6.5+ | Qt6 GUI framework |
| send2trash | 1.8+ | Cross-platform trash |
| pytest | 7.0+ | Testing framework |

### 6.3 Development Tools

| Tool | Purpose |
|------|---------|
| VS Code / Antigravity | IDE |
| Git | Version control |
| pytest | Unit testing |
| mypy | Type checking |
| black | Code formatting |

---

## 7. Security Considerations

| Concern | Mitigation |
|---------|------------|
| File system access | User explicitly selects directories |
| Permanent deletion | Use trash, not permanent delete |
| Data privacy | No network calls, local-only |
| Database integrity | WAL mode, atomic operations |
| Error handling | No sensitive data in logs |

---

## 8. Performance Considerations

| Optimization | Implementation |
|--------------|----------------|
| Hash caching | SQLite cache table |
| Partial hashing | First/last 1MB for large files |
| Async operations | QThread for background tasks |
| Lazy loading | Virtual model for large lists |
| Progress feedback | Signal/slot updates |

---

## 9. Error Handling Strategy

```
┌─────────────────────────────────────────┐
│           Error Handling Flow           │
├─────────────────────────────────────────┤
│ 1. Catch specific exceptions            │
│ 2. Log error with context               │
│ 3. Show user-friendly message           │
│ 4. Continue or gracefully degrade       │
│ 5. Never crash silently                 │
└─────────────────────────────────────────┘
```

### Exception Hierarchy

```python
class AppManagerError(Exception):
    """Base exception"""
    
class ScanError(AppManagerError):
    """Directory scanning errors"""
    
class HashError(AppManagerError):
    """Hashing errors"""
    
class DatabaseError(AppManagerError):
    """Database operation errors"""
    
class ConfigError(AppManagerError):
    """Configuration errors"""
```

---

## 10. Testing Strategy

| Level | Scope | Tools |
|-------|-------|-------|
| Unit | Individual modules | pytest |
| Integration | Module interactions | pytest |
| GUI | User interface | Qt Test |
| E2E | Full workflows | Manual |

---

*Document Version: 1.0 | Author: AI Agent | Date: 2026-08-29*
