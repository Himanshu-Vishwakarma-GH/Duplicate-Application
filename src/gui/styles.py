"""
Design system and Qt Stylesheet (QSS) for Duplicate Application Manager.
Implements the Nordic Graphite & Mint Emerald design system (minimalist dark studio aesthetic).
"""

# Unicode Icons
ICON_DASHBOARD = "🏠"
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

GRAPHITE_MINT_COLORS = {
    "background": "#121316",
    "surface": "#18191C",
    "surface_elevated": "#1F2128",
    "border": "#2B2E38",
    "border_highlight": "#3F4352",
    "primary": "#10B981",          # Vibrant Mint / Emerald Green
    "primary_hover": "#34D399",
    "primary_pressed": "#059669",
    "accent_mint": "#00E676",
    "accent_blue": "#3B82F6",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "text_primary": "#F3F4F6",
    "text_secondary": "#9CA3AF",
    "text_muted": "#6B7280",
    "badge_bg": "#102E23",
    "badge_text": "#10B981",
}

LIGHT_STUDIO_COLORS = {
    "background": "#F8FAFC",
    "surface": "#FFFFFF",
    "surface_elevated": "#F1F5F9",
    "border": "#E2E8F0",
    "border_highlight": "#CBD5E1",
    "primary": "#059669",
    "primary_hover": "#10B981",
    "primary_pressed": "#047857",
    "accent_mint": "#10B981",
    "accent_blue": "#2563EB",
    "warning": "#D97706",
    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "badge_bg": "#E6F4EA",
    "badge_text": "#059669",
}


def get_stylesheet(theme: str = "dark") -> str:
    """Generate Nordic Graphite & Mint Emerald QSS stylesheet."""
    c = GRAPHITE_MINT_COLORS if theme.lower() == "dark" else LIGHT_STUDIO_COLORS

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
        min-width: 210px;
        max-width: 210px;
    }}

    /* Sidebar Title */
    QLabel#sidebarHeader {{
        font-size: 16px;
        font-weight: 700;
        color: {c["primary"]};
        padding: 14px 18px;
        letter-spacing: 0.5px;
    }}

    /* Sidebar Navigation Buttons */
    QPushButton#sidebarBtn {{
        text-align: left;
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        margin: 2px 10px;
        color: {c["text_secondary"]};
        font-size: 13px;
        font-weight: 500;
        background-color: transparent;
    }}

    QPushButton#sidebarBtn:hover {{
        background-color: {c["surface_elevated"]};
        color: {c["text_primary"]};
    }}

    QPushButton#sidebarBtn:checked {{
        background-color: {c["surface_elevated"]};
        color: {c["primary"]};
        font-weight: 600;
        border-left: 3px solid {c["primary"]};
    }}

    /* Cards */
    QFrame#cardFrame {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        padding: 16px;
    }}

    QFrame#statCard {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        padding: 14px;
    }}

    QFrame#statCard:hover {{
        border: 1px solid {c["border_highlight"]};
    }}

    /* Section Headers */
    QLabel#sectionHeader {{
        font-size: 22px;
        font-weight: 700;
        color: {c["primary"]};
        letter-spacing: -0.3px;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {c["surface_elevated"]};
        color: {c["text_primary"]};
        border: 1px solid {c["border"]};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {c["border"]};
        border-color: {c["border_highlight"]};
    }}

    QPushButton#primaryBtn {{
        background-color: {c["primary"]};
        color: #FFFFFF;
        border: none;
        font-weight: 600;
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
        font-weight: 600;
    }}

    QPushButton#dangerBtn:hover {{
        background-color: {c["danger_hover"]};
    }}

    /* Inputs */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {c["surface_elevated"]};
        border: 1px solid {c["border"]};
        border-radius: 6px;
        padding: 8px 12px;
        color: {c["text_primary"]};
    }}

    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {c["primary"]};
    }}

    /* Tree & Tables */
    QListWidget, QTableWidget, QTreeWidget {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        gridline-color: {c["border"]};
        color: {c["text_primary"]};
        outline: none;
    }}

    QListWidget::item, QTableWidget::item, QTreeWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {c["border"]};
    }}

    QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {c["surface_elevated"]};
        color: {c["primary"]};
        border-radius: 4px;
    }}

    QHeaderView::section {{
        background-color: {c["surface_elevated"]};
        color: {c["text_secondary"]};
        padding: 10px;
        border: none;
        border-bottom: 1px solid {c["border"]};
        font-weight: 600;
        font-size: 12px;
    }}

    /* Progress Bar */
    QProgressBar {{
        background-color: {c["surface_elevated"]};
        border: 1px solid {c["border"]};
        border-radius: 6px;
        text-align: center;
        color: {c["text_primary"]};
        font-weight: 600;
    }}

    QProgressBar::chunk {{
        background-color: {c["primary"]};
        border-radius: 5px;
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {c["surface"]};
        border-top: 1px solid {c["border"]};
        color: {c["text_secondary"]};
        padding: 4px 12px;
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
        min-height: 25px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {c["primary"]};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
