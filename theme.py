"""
Theme and stylesheet generator for the NAS Camera Viewer application.
"""

LIGHT_THEME = {
    "bg": "#f2f2eb",
    "text-primary": "#1c1c1c",
    "text-secondary": "#4a4a42",
    "text-muted": "#7a7a70",
    "surface": "#ffffff",
    "surface-alt": "#eaeae3",
    "border": "#d6d6cd",
    "primary": "#3a6ea5",
    "primary-hover": "#2e5783",
    "primary-light": "#6a96c5",
    "secondary": "#a53a6e",
    "secondary-hover": "#833057",
    "secondary-light": "#c56a96",
    "success": "#3a9a5a",
    "warning": "#d98e04",
    "error": "#c62828",
}

DARK_THEME = {
    "bg": "#1e1e1e",
    "text-primary": "#e0e0e0",
    "text-secondary": "#a0a0a0",
    "text-muted": "#707070",
    "surface": "#2a2a2a",
    "surface-alt": "#3c3c3c",
    "border": "#4a4a4a",
    "primary": "#5a8ed5",
    "primary-hover": "#7aa8e5",
    "primary-light": "#3a6ea5",
    "secondary": "#c55a8e",
    "secondary-hover": "#e57ab8",
    "secondary-light": "#a53a6e",
    "success": "#5a9a5a",
    "warning": "#d9a844",
    "error": "#c64848",
}

THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}

def generate_stylesheet(theme_name="light"):
    """Generate the full application stylesheet for the given theme."""
    theme = THEMES.get(theme_name, LIGHT_THEME)
    
    qss = f"""
    /* ==================== GLOBAL ==================== */
    QMainWindow, QWidget {{
        background-color: {theme['bg']};
        color: {theme['text-primary']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 9pt;
    }}

    QFrame {{
        border-radius: 8px;
    }}

    /* ==================== TYPOGRAPHY ==================== */
    QLabel#mutedText {{
        color: {theme['text-muted']};
    }}

    /* ==================== WIDGETS ==================== */
    QPushButton {{
        background-color: {theme['surface']};
        color: {theme['text-primary']};
        border: 1px solid {theme['border']};
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {theme['surface-alt']};
    }}
    QPushButton:pressed {{
        background-color: {theme['border']};
    }}
    QPushButton:disabled {{
        background-color: {theme['surface-alt']};
        color: {theme['text-muted']};
        border-color: {theme['border']};
    }}

    QLineEdit, QSpinBox, QTimeEdit, QComboBox {{
        padding: 6px 10px;
        border: 1px solid {theme['border']};
        border-radius: 4px;
        background-color: {theme['surface']};
        color: {theme['text-primary']};
    }}
    QLineEdit:focus, QSpinBox:focus, QTimeEdit:focus, QComboBox:focus {{
        border-color: {theme['primary']};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: url(./arrow.png); /* A proper icon should be used here */
    }}

    QGroupBox {{
        font-weight: bold;
        border: 1px solid {theme['border']};
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 10px 0 10px;
        background-color: {theme['bg']};
    }}

    QToolTip {{
        background-color: {theme['surface-alt']};
        color: {theme['text-primary']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 8pt;
    }}

    /* ==================== SCROLLBAR ==================== */
    QScrollBar:vertical {{
        background-color: {theme['surface-alt']};
        width: 12px;
        margin: 0px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {theme['border']};
        border-radius: 6px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {theme['text-muted']};
    }}
    QScrollBar:horizontal {{
        background-color: {theme['surface-alt']};
        height: 12px;
        margin: 0px;
        border-radius: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {theme['border']};
        border-radius: 6px;
        min-width: 20px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {theme['text-muted']};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        border: none;
        background: none;
    }}

    /* ==================== MENU & STATUS BAR ==================== */
    QMenuBar {{
        background-color: {theme['surface']};
        border-bottom: 1px solid {theme['border']};
    }}
    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 12px;
    }}
    QMenuBar::item:selected {{
        background-color: {theme['primary']};
        color: {theme['surface']};
    }}
    QMenu {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 4px 0px;
    }}
    QMenu::item {{
        padding: 6px 10px;
    }}
    QMenu::item:selected {{
        background-color: {theme['primary']};
        color: {theme['surface']};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {theme['border']};
        margin: 4px 10px;
    }}
    QStatusBar {{
        background-color: {theme['surface']};
        border-top: 1px solid {theme['border']};
        color: {theme['text-secondary']};
    }}

    /* ==================== DASHBOARD VIEW ==================== */
    CameraCard {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
    }}
    CameraCard:hover {{
        background-color: {theme['surface-alt']};
        border: 1px solid {theme['primary']};
    }}
    QLabel[status="active"] {{
        color: {theme['success']};
    }}
    QLabel[status="inactive"] {{
        color: {theme['text-muted']};
    }}

    /* ==================== CAMERA PLAYER VIEW ==================== */
    QFrame#sidebar {{
        background-color: {theme['surface-alt']};
        border-right: 1px solid {theme['border']};
    }}
    QPushButton#backButton {{
        background-color: {theme['secondary']};
        color: {theme['surface']};
        border: none;
    }}
    QPushButton#backButton:hover {{
        background-color: {theme['secondary-hover']};
    }}
    QPushButton#cameraSwitchButton {{
        text-align: left;
        background-color: {theme['surface']};
    }}
    QPushButton#cameraSwitchButton:hover {{
        background-color: {theme['surface-alt']};
    }}
    QPushButton#cameraSwitchButton:checked {{
        background-color: {theme['primary']};
        color: {theme['surface']};
        border-color: {theme['primary-hover']};
    }}
    QFrame#timelineSection {{
        background-color: {theme['surface']};
        border-top: 1px solid {theme['border']};
    }}

    QLabel#volumeIcon, QSlider {{
        background: transparent;
        border: none;
    }}

    /* ==================== CALENDAR WIDGET ==================== */
    QCalendarWidget {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
    }}
    QCalendarWidget QAbstractItemView {{
        selection-background-color: {theme['primary']};
        selection-color: {theme['surface']};
        border-radius: 4px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {theme['surface-alt']};
        border-bottom: 1px solid {theme['border']};
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    QCalendarWidget QToolButton {{
        background-color: transparent;
        border: none;
        color: {theme['text-primary']};
        padding: 4px;
        border-radius: 4px;
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: {theme['border']};
    }}
    QLabel[legend="complete"] {{ color: {theme['success']}; font-weight: bold; }}
    QLabel[legend="partial"] {{ color: {theme['warning']}; font-weight: bold; }}
    QLabel[legend="none"] {{ color: {theme['text-muted']}; }}

    /* ==================== SETTINGS VIEW ==================== */
    QPushButton#saveButton {{
        background-color: {theme['success']};
        color: {theme['surface']};
        border: none;
    }}
    QPushButton#saveButton:hover {{
        background-color: {theme['success']};
        opacity: 0.8; /* This doesn't work well in QSS, just an example */
    }}
    QPushButton#resetButton {{
        background-color: {theme['warning']};
        color: {theme['text-primary']};
        border: none;
    }}
    QPushButton#resetButton:hover {{
        background-color: {theme['warning']};
        opacity: 0.8;
    }}
    QPushButton#testButton {{
        background-color: {theme['primary-light']};
        color: {theme['text-primary']};
        border: none;
    }}
    QPushButton#testButton:hover {{
        background-color: {theme['primary']};
        color: {theme['surface']};
    }}
    QTextEdit {{
        background-color: {theme['surface-alt']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 8px;
        font-family: monospace;
    }}

    /* ==================== MISC ==================== */
    QProgressBar {{
        border: 1px solid {theme['border']};
        border-radius: 4px;
        text-align: center;
        background-color: {theme['surface-alt']};
        color: {theme['text-primary']};
    }}
    QProgressBar::chunk {{
        background-color: {theme['primary']};
        border-radius: 3px;
    }}
    QSplitter::handle {{
        background: {theme['border']};
    }}
    QSplitter::handle:horizontal {{
        width: 1px;
    }}
    QSplitter::handle:vertical {{
        height: 1px;
    }}
    """
    return qss
