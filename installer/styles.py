"""
Vanish-OS Installer — Modern Minimalist Dark Theme Stylesheet
Cyberpunk / Obsidian aesthetic with neon accents, custom cards, and smooth interactions.
"""

DARK_THEME = """
QWidget {
    background-color: #09090b;
    color: #f4f4f5;
    font-family: 'Segoe UI', 'Inter', 'Ubuntu', sans-serif;
    font-size: 14px;
}

/* Main Window & Containers */
QMainWindow {
    background-color: #09090b;
}

QFrame#sidebar {
    background-color: #0f0f13;
    border-right: 1px solid #27272a;
}

QFrame#card {
    background-color: #121217;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 16px;
}

QFrame#card_selected {
    background-color: #181822;
    border: 1px solid #8b5cf6;
    border-radius: 8px;
    padding: 16px;
}

/* Badges & Pills */
QLabel#badge_success {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid #059669;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#badge_warning {
    background-color: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid #d97706;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#badge_info {
    background-color: rgba(139, 92, 246, 0.15);
    color: #c084fc;
    border: 1px solid #7c3aed;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: bold;
}

/* Headings & Text */
QLabel#title {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.5px;
}

QLabel#subtitle {
    font-size: 13px;
    color: #a1a1aa;
}

QLabel#section_title {
    font-size: 16px;
    font-weight: 700;
    color: #e4e4e7;
}

/* Buttons */
QPushButton {
    background-color: #1e1e24;
    color: #f4f4f5;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #272730;
    border-color: #71717a;
}

QPushButton:pressed {
    background-color: #18181f;
}

QPushButton#btn_primary {
    background-color: #7c3aed;
    color: #ffffff;
    border: 1px solid #8b5cf6;
}

QPushButton#btn_primary:hover {
    background-color: #6d28d9;
    border-color: #a78bfa;
}

QPushButton#btn_primary:pressed {
    background-color: #5b21b6;
}

QPushButton#btn_accent {
    background-color: #0891b2;
    color: #ffffff;
    border: 1px solid #06b6d4;
}

QPushButton#btn_accent:hover {
    background-color: #0e7490;
    border-color: #22d3ee;
}

QPushButton:disabled {
    background-color: #18181b;
    color: #52525b;
    border-color: #27272a;
}

/* Radio Buttons & Checkboxes */
QRadioButton {
    spacing: 10px;
    color: #e4e4e7;
    font-size: 14px;
    font-weight: 500;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #52525b;
    background-color: #18181b;
}

QRadioButton::indicator:checked {
    border: 2px solid #8b5cf6;
    background-color: #8b5cf6;
}

QCheckBox {
    spacing: 10px;
    color: #e4e4e7;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #52525b;
    background-color: #18181b;
}

QCheckBox::indicator:checked {
    border: 2px solid #06b6d4;
    background-color: #06b6d4;
}

/* LineEdits and ComboBoxes */
QLineEdit {
    background-color: #121217;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 10px 12px;
    color: #f4f4f5;
    selection-background-color: #7c3aed;
}

QLineEdit:focus {
    border: 1px solid #8b5cf6;
    background-color: #16161d;
}

QComboBox {
    background-color: #121217;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 10px 12px;
    color: #f4f4f5;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #121217;
    border: 1px solid #3f3f46;
    selection-background-color: #7c3aed;
    color: #f4f4f5;
}

/* Progress Bar */
QProgressBar {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    font-size: 11px;
    font-weight: bold;
    color: #f4f4f5;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #06b6d4);
    border-radius: 5px;
}

/* Log View / Terminal */
QPlainTextEdit#log_view {
    background-color: #050507;
    border: 1px solid #27272a;
    border-radius: 6px;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    color: #a1a1aa;
    padding: 10px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #09090b;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #27272a;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #3f3f46;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
