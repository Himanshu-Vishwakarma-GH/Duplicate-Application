"""
Ultra-Modern Design System & Qt Stylesheet (QSS) for Duplicate Application Manager.
Features rich obsidian dark surface elevation, neon cyan/emerald accents, high contrast typography,
pill badges, and polished custom widgets.
"""

# Unicode Icons
ICON_DASHBOARD = "📊"
ICON_SCAN = "🔍"
ICON_RESULTS = "👥"
ICON_CATEGORIES = "📁"
ICON_REPORTS = "📄"
ICON_SETTINGS = "⚙️"
ICON_CHECK = "✓"
ICON_WARNING = "⚠️"
ICON_ERROR = "✕"
ICON_TRASH = "🗑️"
ICON_REFRESH = "🔄"
ICON_ADD = "➕"
ICON_REMOVE = "➖"
ICON_FOLDER = "📂"
ICON_FILE = "📄"

DARK_CYBER_OBSIDIAN = {
    "background": "#0B0C10",
    "surface": "#141622",
    "surface_elevated": "#1E2235",
    "surface_hover": "#282E46",
    "border": "#282C40",
    "border_highlight": "#3D4464",
    "primary": "#00E5FF",           # Neon Cyan
    "primary_gradient_start": "#00E5FF",
    "primary_gradient_end": "#7C4DFF",
    "primary_hover": "#33EBFF",
    "primary_pressed": "#00B3CC",
    "emerald": "#10B981",           # Emerald Green
    "emerald_bg": "#0B2D22",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "text_primary": "#FFFFFF",
    "text_secondary": "#CBD5E1",
    "text_muted": "#8A94A6",
    "card_bg": "#141622",
}

LIGHT_STUDIO_COLORS = {
    "background": "#F8FAFC",
    "surface": "#FFFFFF",
    "surface_elevated": "#F1F5F9",
    "surface_hover": "#E2E8F0",
    "border": "#CBD5E1",
    "border_highlight": "#94A3B8",
    "primary": "#0284C7",
    "primary_gradient_start": "#0284C7",
    "primary_gradient_end": "#4F46E5",
    "primary_hover": "#0369A1",
    "primary_pressed": "#075985",
    "emerald": "#059669",
    "emerald_bg": "#ECFDF5",
    "warning": "#D97706",
    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "text_primary": "#0F172A",
    "text_secondary": "#334155",
    "text_muted": "#64748B",
    "card_bg": "#FFFFFF",
}


def get_stylesheet(theme: str = "dark") -> str:
    """Generate comprehensive ultra-modern QSS stylesheet."""
    c = DARK_CYBER_OBSIDIAN if theme.lower() == "dark" else LIGHT_STUDIO_COLORS

    return f"""
    /* Global Base */
    QWidget {{
        background-color: {c["background"]};
        color: {c["text_primary"]};
        font-family: "Segoe UI", "SF Pro Display", "Inter", sans-serif;
        font-size: 13px;
    }}

    QMainWindow {{
        background-color: {c["background"]};
    }}

    /* Sidebar Container */
    QFrame#sidebarFrame {{
        background-color: {c["surface"]};
        border-right: 1px solid {c["border"]};
        min-width: 220px;
        max-width: 220px;
    }}

    /* Sidebar Title Header */
    QLabel#sidebarHeader {{
        font-size: 18px;
        font-weight: 800;
        color: {c["text_primary"]};
        padding: 16px 20px;
        letter-spacing: 0.5px;
    }}

    /* Sidebar Navigation Buttons */
    QPushButton#sidebarBtn {{
        text-align: left;
        padding: 12px 18px;
        border: none;
        border-radius: 8px;
        margin: 3px 12px;
        color: {c["text_muted"]};
        font-size: 13px;
        font-weight: 600;
        background-color: transparent;
    }}

    QPushButton#sidebarBtn:hover {{
        background-color: {c["surface_elevated"]};
        color: {c["text_primary"]};
    }}

    QPushButton#sidebarBtn:checked {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c["primary_gradient_start"]}, stop:1 {c["primary_gradient_end"]});
        color: #FFFFFF;
        font-weight: 700;
    }}

    /* Section Headers */
    QLabel#sectionTitle {{
        font-size: 22px;
        font-weight: 800;
        color: {c["text_primary"]};
        letter-spacing: -0.3px;
    }}

    QLabel#sectionSubtitle {{
        font-size: 13px;
        color: {c["text_muted"]};
        font-weight: 400;
    }}

    /* Cards */
    QFrame#cardFrame {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 12px;
        padding: 20px;
    }}

    QFrame#statCard {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 12px;
        padding: 16px;
    }}

    QFrame#statCard:hover {{
        border: 1px solid {c["border_highlight"]};
        background-color: {c["surface_elevated"]};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {c["surface_elevated"]};
        color: {c["text_primary"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        padding: 9px 18px;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: {c["surface_hover"]};
        border-color: {c["border_highlight"]};
    }}

    QPushButton#primaryBtn {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c["primary_gradient_start"]}, stop:1 {c["primary_gradient_end"]});
        color: #FFFFFF;
        border: none;
        font-weight: 700;
    }}

    QPushButton#primaryBtn:hover {{
        background-color: {c["primary_hover"]};
    }}

    QPushButton#primaryBtn:pressed {{
        background-color: {c["primary_pressed"]};
    }}

    QPushButton#dangerBtn {{
        background-color: {c["danger"]};
        color: #FFFFFF;
        border: none;
        font-weight: 700;
    }}

    QPushButton#dangerBtn:hover {{
        background-color: {c["danger_hover"]};
    }}

    /* Input Controls */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {c["surface_elevated"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        padding: 10px 14px;
        color: {c["text_primary"]};
        font-size: 13px;
    }}

    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {c["primary"]};
    }}

    /* Lists, Tables, Trees */
    QListWidget, QTableWidget, QTreeWidget {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        gridline-color: {c["border"]};
        color: {c["text_primary"]};
        outline: none;
    }}

    QListWidget::item {{
        padding: 10px 12px;
        border-bottom: 1px solid {c["border"]};
        border-radius: 6px;
    }}

    QTableWidget::item, QTreeWidget::item {{
        padding: 10px 12px;
        border-bottom: 1px solid {c["border"]};
    }}

    QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {{
        background-color: {c["surface_elevated"]};
    }}

    QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {c["surface_elevated"]};
        color: {c["primary"]};
        font-weight: 600;
    }}

    QHeaderView::section {{
        background-color: {c["surface_elevated"]};
        color: {c["text_muted"]};
        padding: 12px;
        border: none;
        border-bottom: 1px solid {c["border"]};
        font-weight: 700;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Progress Bar */
    QProgressBar {{
        background-color: {c["surface_elevated"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        text-align: center;
        color: {c["text_primary"]};
        font-weight: 700;
        font-size: 12px;
    }}

    QProgressBar::chunk {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c["primary_gradient_start"]}, stop:1 {c["primary_gradient_end"]});
        border-radius: 7px;
    }}

    /* Checkboxes */
    QCheckBox {{
        spacing: 8px;
        font-size: 13px;
        color: {c["text_secondary"]};
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {c["border_highlight"]};
        background-color: {c["surface_elevated"]};
    }}

    QCheckBox::indicator:checked {{
        background-color: {c["primary"]};
        border-color: {c["primary"]};
        image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path fill='%23000' d='M9.707 3.293a1 1 0 010 1.414l-4.5 4.5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L4.5 7.086l3.793-3.793a1 1 0 011.414 0z'/></svg>");
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {c["surface"]};
        border-top: 1px solid {c["border"]};
        color: {c["text_muted"]};
        font-size: 12px;
        padding: 6px 16px;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {c["background"]};
        width: 10px;
        border: none;
    }}

    QScrollBar::handle:vertical {{
        background-color: {c["border_highlight"]};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {c["primary"]};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
