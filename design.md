# UI/UX Design Document

## Project Name
**Duplicate Application Manager**

## Version
1.0.0

## Date
August 29, 2026

---

## 1. Design Philosophy

### Core Principles
1. **Clarity** - Information hierarchy is obvious
2. **Efficiency** - Minimal clicks to complete tasks
3. **Safety** - Destructive actions require confirmation
4. **Feedback** - Always show progress and results
5. **Professionalism** - Clean, modern aesthetic

### Design System
- **Framework**: PySide6 (Qt6)
- **Style**: Modern flat design with subtle depth
- **Theme**: Dark mode (default), Light mode (option)

---

## 2. Color Palette

### Dark Theme (Default)

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Background | Charcoal | `#1E1E1E` | Main window background |
| Surface | Dark Gray | `#2D2D2D` | Cards, panels |
| Surface Elevated | Medium Gray | `#3D3D3D` | Hover states, elevated cards |
| Primary | Electric Blue | `#007ACC` | Buttons, links, active states |
| Primary Hover | Light Blue | `#1E90FF` | Button hover |
| Success | Green | `#4EC94E` | Success messages, safe actions |
| Warning | Amber | `#FFB800` | Warnings, attention needed |
| Error | Red | `#F44336` | Errors, destructive actions |
| Text Primary | White | `#FFFFFF` | Main text |
| Text Secondary | Light Gray | `#B0B0B0` | Labels, descriptions |
| Text Disabled | Dark Gray | `#6D6D6D` | Disabled text |
| Border | Subtle Gray | `#404040` | Dividers, borders |

### Light Theme

| Role | Color | Hex |
|------|-------|-----|
| Background | White | `#FFFFFF` |
| Surface | Light Gray | `#F5F5F5` |
| Surface Elevated | White | `#FFFFFF` |
| Primary | Blue | `#0066CC` |
| Text Primary | Near Black | `#1E1E1E` |
| Text Secondary | Dark Gray | `#666666` |

---

## 3. Typography

### Font Family
```
Primary: "Segoe UI" (Windows) / "SF Pro Display" (Mac) / "Ubuntu" (Linux)
Fallback: "Arial", "Helvetica", sans-serif
Monospace: "Cascadia Code" / "JetBrains Mono" / "Consolas"
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 - Window Title | 24px | Bold (700) | 32px |
| H2 - Section Header | 20px | SemiBold (600) | 28px |
| H3 - Card Title | 16px | SemiBold (600) | 24px |
| Body - Primary | 14px | Regular (400) | 20px |
| Body - Secondary | 13px | Regular (400) | 18px |
| Caption | 12px | Regular (400) | 16px |
| Button | 14px | Medium (500) | 20px |

---

## 4. Component Design

### 4.1 Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  ⬡ Duplicate App Manager                    ─  □  ✕           │
├────────────┬────────────────────────────────────────────────────┤
│            │                                                    │
│  SIDEBAR   │                  MAIN CONTENT                      │
│            │                                                    │
│ ┌────────┐ │  ┌──────────────────────────────────────────────┐  │
│ │ 📊 Dash│ │  │                                              │  │
│ └────────┘ │  │              (Dynamic Content)               │  │
│ ┌────────┐ │  │                                              │  │
│ │ 🔍 Scan│ │  │                                              │  │
│ └────────┘ │  │                                              │  │
│ ┌────────┐ │  │                                              │  │
│ │ 📋 Resu│ │  │                                              │  │
│ └────────┘ │  │                                              │  │
│ ┌────────┐ │  │                                              │  │
│ │ 📁 Cate│ │  │                                              │  │
│ └────────┘ │  │                                              │  │
│ ┌────────┐ │  └──────────────────────────────────────────────┘  │
│ │ ⚙️ Conf│ │                                                    │
│ └────────┘ │  ┌──────────────────────────────────────────────┐  │
│            │  │  Status Bar: Ready | Files: 1,234 | Dupes: 56│  │
│            │  └──────────────────────────────────────────────┘  │
│            │                                                    │
└────────────┴────────────────────────────────────────────────────┘
```

### 4.2 Sidebar Component

```python
# Sidebar styling
SIDEBAR_STYLE = """
QFrame {
    background-color: #252526;
    border-right: 1px solid #404040;
    min-width: 200px;
    max-width: 200px;
}

QPushButton {
    text-align: left;
    padding: 12px 16px;
    border: none;
    border-radius: 4px;
    margin: 2px 8px;
    color: #B0B0B0;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #3D3D3D;
    color: #FFFFFF;
}

QPushButton:checked {
    background-color: #007ACC;
    color: #FFFFFF;
}
"""
```

### 4.3 Dashboard View

```
┌─────────────────────────────────────────────────────────────────┐
│                         DASHBOARD                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ 📁 1,234    │ │ 🔴 56       │ │ 💾 2.3 GB   │ │ 📊 45%    │ │
│  │ Total Apps  │ │ Duplicates  │ │ Space Saved │ │ Organized │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────┐ ┌────────────────────────────┐  │
│  │    DUPLICATE GROUPS        │ │    CATEGORIES BREAKDOWN    │  │
│  │                            │ │                            │  │
│  │  Group 1: 3 files (450MB) │ │  ████████ Development 34%  │  │
│  │  Group 2: 2 files (1.2GB) │ │  ██████   Games       28%  │  │
│  │  Group 3: 4 files (89MB)  │ │  ████     Productivity 18% │  │
│  │  ...                      │ │  ███      Utilities   12%  │  │
│  │                            │ │  ██       Media        8%  │  │
│  │  [View All Duplicates]     │ │                            │  │
│  └────────────────────────────┘ └────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  RECENT SCANS                                              │ │
│  │                                                            │ │
│  │  Aug 29, 14:32 - C:\Program Files - 1,234 apps - 56 dupes│ │
│  │  Aug 28, 10:15 - D:\Applications - 892 apps - 23 dupes   │ │
│  │                                                            │ │
│  │  [Start New Scan]                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Scan Configuration View

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCAN CONFIGURATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SCAN DIRECTORIES                                        │   │
│  │                                                          │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ ☑ C:\Program Files                                │  │   │
│  │  │ ☑ C:\Program Files (x86)                          │  │   │
│  │  │ ☐ D:\Games                                        │  │   │
│  │  │ ☑ D:\Development                                  │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                          │   │
│  │  [Add Directory]  [Remove Selected]  [Scan Now]         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FILE FILTERS                                            │   │
│  │                                                          │   │
│  │  Include Extensions: [ .exe  .msi  .app  .dmg  ]        │   │
│  │                                                          │   │
│  │  Exclude Directories: [ node_modules  .git  __pycache__]│   │
│  │                                                          │   │
│  │  Maximum File Size: [ 1000 ] MB  (0 = unlimited)        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SCAN OPTIONS                                            │   │
│  │                                                          │   │
│  │  ☑ Use cached hashes (faster re-scans)                 │   │
│  │  ☑ Partial hashing for files > 100MB                   │   │
│  │  ☑ Follow symbolic links                               │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5 Results View

```
┌─────────────────────────────────────────────────────────────────┐
│                     DUPLICATE RESULTS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Filter: [All ▾]  Sort: [Size ▾]  Search: [_______________]   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ☐ Select All (56 duplicates found)     [Remove Selected]│  │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  GROUP 1 - Hash: a1b2c3d4... (3 copies, 450 MB total)  │   │
│  │  ─────────────────────────────────────────────────────── │   │
│  │  ☑ C:\Program Files\App\v1.0\app.exe          150 MB   │   │
│  │  ☐ C:\Program Files\App\v2.0\app.exe          150 MB   │   │
│  │  ☐ D:\Backup\App\app.exe                       150 MB   │   │
│  │                                          [Keep] [Remove] │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  GROUP 2 - Hash: e5f6g7h8... (2 copies, 1.2 GB total)  │   │
│  │  ─────────────────────────────────────────────────────── │   │
│  │  ☑ D:\Games\GameXYZ\game.exe                  600 MB   │   │
│  │  ☐ C:\Games\GameXYZ\game.exe                  600 MB   │   │
│  │                                          [Keep] [Remove] │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ◀ 1 2 3 ... 12 ▶                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.6 Category Browser View

```
┌─────────────────────────────────────────────────────────────────┐
│                   CATEGORY BROWSER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌────────────────────────────────────────┐   │
│  │ CATEGORIES   │  │  DEVELOPMENT TOOLS (34 apps)           │   │
│  │              │  │  ───────────────────────────────────── │   │
│  │ ▶ Development│  │                                        │   │
│  │ ▼ Games      │  │  ┌──────────────────────────────────┐  │   │
│  │   Productivity│  │  │ VS Code.exe           120 MB    │  │   │
│  │   Utilities  │  │  │ Python.exe             45 MB     │  │   │
│  │   Media      │  │  │ Node.js.exe            32 MB     │  │   │
│  │   Uncategorized│ │  │ Git.exe                28 MB     │  │   │
│  │              │  │  └──────────────────────────────────┘  │   │
│  │ [+ Add Cat]  │  │                                        │   │
│  │              │  │  [Edit Rules]  [Move to Category]      │   │
│  └──────────────┘  └────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.7 Confirmation Dialog

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  Confirm Removal                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  You are about to move 3 files to trash:                        │
│                                                                 │
│  • C:\Program Files\App\v1.0\app.exe (150 MB)                  │
│  • D:\Games\GameXYZ\game.exe (600 MB)                          │
│  • D:\Backup\App\app.exe (150 MB)                              │
│                                                                 │
│  Total: 900 MB will be freed                                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ☐ I understand these files will be moved to trash       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│                          [Cancel]  [Move to Trash]              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Iconography

### Icon Style
- **Type**: Outlined (stroke-based)
- **Size**: 24x24px (sidebar), 16x16px (inline)
- **Color**: Inherit from text color

### Icon Set

| Icon | Usage | Unicode/SVG |
|------|-------|-------------|
| Dashboard | Sidebar nav | 📊 |
| Scan | Sidebar nav | 🔍 |
| Results | Sidebar nav | 📋 |
| Categories | Sidebar nav | 📁 |
| Settings | Sidebar nav | ⚙️ |
| Check | Success | ✓ |
| Warning | Warning | ⚠️ |
| Error | Error | ✕ |
| Trash | Delete | 🗑️ |
| Refresh | Re-scan | 🔄 |
| Export | Export report | 📤 |

---

## 6. Interaction Patterns

### 6.1 Loading States

```
┌─────────────────────────────────────┐
│  ⏳ Scanning directories...         │
│  ████████████░░░░░░░░ 65%           │
│  Processing: C:\Program Files\...   │
└─────────────────────────────────────┘
```

### 6.2 Empty States

```
┌─────────────────────────────────────┐
│                                     │
│         📁                          │
│                                     │
│   No duplicates found!              │
│                                     │
│   [Start New Scan]                  │
│                                     │
└─────────────────────────────────────┘
```

### 6.3 Toast Notifications

```
┌─────────────────────────────────────┐
│  ✓ 3 files moved to trash           │
│                  900 MB freed        │
│                        [Dismiss]    │
└─────────────────────────────────────┘
```

---

## 7. Responsive Behavior

| Window Size | Layout |
|-------------|--------|
| > 1200px | Full sidebar + content |
| 900-1200px | Collapsed sidebar (icons only) |
| < 900px | Hidden sidebar (hamburger menu) |

---

## 8. Accessibility

| Requirement | Implementation |
|-------------|----------------|
| Keyboard navigation | Tab order, shortcuts |
| Screen reader | Accessible names on all controls |
| High contrast | Theme support |
| Font scaling | Respect system settings |

---

## 9. Qt Stylesheet (QSS)

```css
/* Global Styles */
* {
    font-family: "Segoe UI", "SF Pro Display", sans-serif;
}

QMainWindow {
    background-color: #1E1E1E;
}

/* Cards */
QCard {
    background-color: #2D2D2D;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 16px;
}

/* Primary Button */
QPushButton#primary {
    background-color: #007ACC;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton#primary:hover {
    background-color: #1E90FF;
}

QPushButton#primary:pressed {
    background-color: #005A9E;
}

/* Danger Button */
QPushButton#danger {
    background-color: #F44336;
    color: white;
}

QPushButton#danger:hover {
    background-color: #D32F2F;
}

/* Table */
QTableWidget {
    background-color: #2D2D2D;
    border: 1px solid #404040;
    gridline-color: #404040;
}

QTableWidget::item:selected {
    background-color: #007ACC;
}

/* Scrollbar */
QScrollBar:vertical {
    background-color: #1E1E1E;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #404040;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #505050;
}
```

---

*Document Version: 1.0 | Author: AI Agent | Date: 2026-08-29*
