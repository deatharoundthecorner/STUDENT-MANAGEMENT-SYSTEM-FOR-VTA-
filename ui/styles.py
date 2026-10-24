# ui/styles.py
# Comprehensive Design System for Student Management System (SMS) - Windows Desktop Edition

DAY_COLORS = {
    "main_bg": "#F8FAFC",          # Light neutral canvas
    "card_bg": "#FFFFFF",          # Crisp white card surface
    "sidebar_bg": "#0F172A",       # Deep professional navy (slate-900)
    "sidebar_hover": "#1E293B",    # Slightly lighter navy (slate-800)
    "sidebar_active": "#2563EB",   # Royal blue active indicator
    "sidebar_text": "#94A3B8",     # Slate-400
    "sidebar_text_hover": "#FFFFFF",
    "sidebar_title_bg": "#020617",  # Ultra deep navy
    "text_color": "#0F172A",       # Primary text (high contrast slate-900)
    "muted_text": "#475569",       # Secondary text (slate-600)
    "border_color": "#CBD5E1",     # Clean subtle border (slate-300)
    "border_light": "#E2E8F0",     # Card divider (slate-200)
    "accent_blue": "#2563EB",      # Accessible primary blue (blue-600)
    "accent_blue_hover": "#1D4ED8",# Hover blue (blue-700)
    "accent_blue_pressed": "#1E40AF",# Pressed blue (blue-800)
    "input_bg": "#FFFFFF",
    "input_border": "#CBD5E1",
    "input_focus_border": "#2563EB",
    "button_dark": "#0F172A",
    "table_grid": "#F1F5F9",
    "table_selection_bg": "#EFF6FF", # Soft blue row selection
    "table_selection_text": "#1E3A8A",
    "tab_inactive_bg": "#F1F5F9",
    "success": "#059669",          # Emerald green
    "success_bg": "#ECFDF5",
    "warning": "#D97706",          # Amber
    "warning_bg": "#FFFBEB",
    "danger": "#DC2626",           # Red
    "danger_hover": "#B91C1C",
    "danger_bg": "#FEF2F2",
    "danger_text": "#991B1B",
    "selected_bg": "#EFF6FF",
}

NIGHT_COLORS = {
    "main_bg": "#0F172A",          # Slate-900
    "card_bg": "#1E293B",          # Slate-800
    "sidebar_bg": "#020617",       # Slate-950
    "sidebar_hover": "#0F172A",
    "sidebar_active": "#3B82F6",
    "sidebar_text": "#94A3B8",
    "sidebar_text_hover": "#F8FAFC",
    "sidebar_title_bg": "#000000",
    "text_color": "#F8FAFC",       # Crisp light text
    "muted_text": "#94A3B8",
    "border_color": "#334155",     # Slate-700
    "border_light": "#1E293B",
    "accent_blue": "#3B82F6",
    "accent_blue_hover": "#60A5FA",
    "accent_blue_pressed": "#1D4ED8",
    "input_bg": "#111827",
    "input_border": "#374151",
    "input_focus_border": "#60A5FA",
    "button_dark": "#2563EB",
    "table_grid": "#334155",
    "table_selection_bg": "#1E3A8A",
    "table_selection_text": "#FFFFFF",
    "tab_inactive_bg": "#111827",
    "success": "#10B981",
    "success_bg": "#064E3B",
    "warning": "#F59E0B",
    "warning_bg": "#78350F",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "danger_bg": "#7F1D1D",
    "danger_text": "#FCA5A5",
    "selected_bg": "#1E3A8A",
}

STYLE_SHEET_TEMPLATE = """
/* Global Defaults */
QWidget {
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    color: {text_color};
    background-color: transparent;
}

QMainWindow {
    background-color: {main_bg};
}

QDialog {
    background-color: {main_bg};
}

/* Sidebar Navigation Frame */
QFrame#SidebarFrame {
    background-color: {sidebar_bg};
    border: none;
    min-width: 240px;
    max-width: 240px;
}

QLabel#SidebarTitle {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
    padding: 20px 14px;
    background-color: {sidebar_title_bg};
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

QLabel#SidebarSubtitle {
    color: {sidebar_text};
    font-size: 11px;
    font-weight: 500;
    padding: 0 14px 14px 14px;
}

/* Sidebar Navigation Buttons */
QPushButton[class*="SidebarButton"] {
    color: {sidebar_text};
    background-color: transparent;
    border: none;
    border-radius: 6px;
    text-align: left;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    margin: 2px 10px;
}

QPushButton[class*="SidebarButton"]:hover {
    color: {sidebar_text_hover};
    background-color: {sidebar_hover};
}

QPushButton[class*="SidebarButton"]:checked {
    color: #FFFFFF;
    background-color: {sidebar_active};
    font-weight: 600;
}

QPushButton[class*="SidebarButton"]:focus {
    outline: none;
    border: 1px solid {accent_blue};
}

/* Sidebar Logout Button */
QPushButton[class*="SidebarLogoutButton"] {
    color: #F87171;
    background-color: transparent;
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 6px;
    text-align: left;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    margin: 10px 10px 14px 10px;
}

QPushButton[class*="SidebarLogoutButton"]:hover {
    color: #FFFFFF;
    background-color: #DC2626;
    border-color: #DC2626;
}

/* Primary Action Buttons */
QPushButton[class*="PrimaryButton"] {
    background-color: {accent_blue};
    color: #FFFFFF;
    border: 1px solid {accent_blue};
    border-radius: 6px;
    padding: 0 16px;
    min-height: 36px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton[class*="PrimaryButton"]:hover {
    background-color: {accent_blue_hover};
    border-color: {accent_blue_hover};
}

QPushButton[class*="PrimaryButton"]:pressed {
    background-color: {accent_blue_pressed};
}

QPushButton[class*="PrimaryButton"]:disabled {
    background-color: {border_color};
    border-color: {border_color};
    color: {muted_text};
}

QPushButton[class*="PrimaryButton"]:focus {
    outline: none;
    border: 2px solid #93C5FD;
}

/* Secondary / Neutral Buttons */
QPushButton[class*="SecondaryButton"] {
    background-color: {card_bg};
    color: {text_color};
    border: 1px solid {border_color};
    border-radius: 6px;
    padding: 0 14px;
    min-height: 36px;
    font-weight: 500;
    font-size: 13px;
}

QPushButton[class*="SecondaryButton"]:hover {
    background-color: {tab_inactive_bg};
    border-color: {text_color};
}

QPushButton[class*="SecondaryButton"]:pressed {
    background-color: {border_color};
}

QPushButton[class*="SecondaryButton"]:focus {
    outline: none;
    border: 2px solid {accent_blue};
}

/* Success Buttons */
QPushButton[class*="SuccessButton"] {
    background-color: {success};
    color: #FFFFFF;
    border: 1px solid {success};
    border-radius: 6px;
    padding: 0 16px;
    min-height: 36px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton[class*="SuccessButton"]:hover {
    background-color: #047857;
    border-color: #047857;
}

QPushButton[class*="SuccessButton"]:focus {
    outline: none;
    border: 2px solid #6EE7B7;
}

/* Destructive / Danger Buttons */
QPushButton[class*="DangerButton"] {
    background-color: {danger};
    color: #FFFFFF;
    border: 1px solid {danger};
    border-radius: 6px;
    padding: 0 14px;
    min-height: 36px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton[class*="DangerButton"]:hover {
    background-color: {danger_hover};
    border-color: {danger_hover};
}

QPushButton[class*="DangerButton"]:focus {
    outline: none;
    border: 2px solid #FCA5A5;
}

QPushButton[class*="DangerButton"]:disabled {
    background-color: {border_color};
    color: {text_muted};
    border-color: {border_color};
}

/* Table Row Action Buttons */
QPushButton[class*="TableActionView"] {
    background-color: {accent_blue};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    min-height: 26px;
}

QPushButton[class*="TableActionView"]:hover {
    background-color: {accent_blue_hover};
}

QPushButton[class*="TableActionEdit"] {
    background-color: {success};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    min-height: 26px;
}

QPushButton[class*="TableActionEdit"]:hover {
    background-color: #047857;
}

QPushButton[class*="TableActionDelete"] {
    background-color: {danger};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    min-height: 26px;
}

QPushButton[class*="TableActionDelete"]:hover {
    background-color: {danger_hover};
}

/* Form Inputs & Controls */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: {input_bg};
    border: 1px solid {input_border};
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 34px;
    color: {text_color};
    selection-background-color: {accent_blue};
    selection-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid {input_focus_border};
    background-color: {input_bg};
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: {tab_inactive_bg};
    color: {muted_text};
}

QComboBox {
    background-color: {input_bg};
    border: 1px solid {input_border};
    border-radius: 6px;
    padding: 4px 12px;
    min-height: 34px;
    color: {text_color};
}

QComboBox:focus {
    border: 2px solid {input_focus_border};
}

QComboBox::drop-down {
    border: none;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: {card_bg};
    border: 1px solid {border_color};
    color: {text_color};
    selection-background-color: {table_selection_bg};
    selection-color: {text_color};
    padding: 4px;
}

QSpinBox {
    background-color: {input_bg};
    border: 1px solid {input_border};
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 34px;
    color: {text_color};
}

QSpinBox:focus {
    border: 2px solid {input_focus_border};
}

QCheckBox {
    spacing: 8px;
    color: {text_color};
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid {border_color};
    border-radius: 4px;
    background-color: {input_bg};
}

QCheckBox::indicator:checked {
    background-color: {accent_blue};
    border-color: {accent_blue};
}

/* Card Surfaces */
QFrame[class*="DashboardCard"], QFrame[class*="ThemedCard"] {
    background-color: {card_bg};
    border: 1px solid {border_color};
    border-radius: 8px;
}

QFrame[class*="DashboardCard"]:hover {
    border-color: {accent_blue};
}

/* Tables */
QTableWidget, QTableView {
    background-color: {card_bg};
    border: 1px solid {border_color};
    border-radius: 8px;
    gridline-color: {table_grid};
    selection-background-color: {table_selection_bg};
    selection-color: {table_selection_text};
    color: {text_color};
    outline: none;
}

QTableWidget::item, QTableView::item {
    padding: 8px 10px;
    border-bottom: 1px solid {table_grid};
    color: {text_color};
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: {table_selection_bg};
    color: {table_selection_text};
    font-weight: 500;
}

QHeaderView::section {
    background-color: {tab_inactive_bg};
    color: {text_color};
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {border_color};
    border-right: 1px solid {border_color};
    font-weight: 600;
    font-size: 12px;
}

/* Typography & Headings */
QLabel[class*="PageTitle"] {
    font-size: 22px;
    font-weight: 800;
    color: {text_color};
}

QLabel[class*="PageSubtitle"] {
    font-size: 13px;
    color: {muted_text};
    margin-top: 2px;
}

QLabel[class*="SectionHeader"] {
    font-size: 14px;
    font-weight: 700;
    color: {text_color};
    border-bottom: 1px solid {border_color};
    padding-bottom: 6px;
    margin-top: 4px;
}

QLabel[class*="BodyText"] {
    color: {muted_text};
    font-size: 13px;
    line-height: 1.4;
}

QLabel[class*="CardTitle"] {
    font-size: 12px;
    font-weight: 600;
    color: {muted_text};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel[class*="CardValue"] {
    font-size: 26px;
    font-weight: 800;
    color: {text_color};
}

QLabel[class*="LoginFormLabel"] {
    color: {text_color};
    font-weight: 600;
    font-size: 12px;
}

/* Status Indicators */
QLabel[class*="StatusYes"] {
    color: {success};
    font-weight: 700;
}

QLabel[class*="StatusNo"] {
    color: {danger};
    font-weight: 700;
}

QLabel[class*="StatusPending"] {
    color: {accent_blue};
    font-weight: 700;
}

QLabel[class*="StatusDefault"] {
    color: {muted_text};
    font-weight: 500;
}

QLabel[class*="CountSuccess"] {
    color: {success};
    font-weight: 700;
    font-size: 14px;
}

QLabel[class*="CountWarning"] {
    color: {warning};
    font-weight: 700;
    font-size: 14px;
}

QLabel[class*="CountDanger"] {
    color: {danger};
    font-weight: 700;
    font-size: 14px;
}

QLabel[class*="ProfileValueStrong"] {
    color: {text_color};
    font-weight: 700;
    font-size: 14px;
}

/* Form Group Boxes */
QGroupBox {
    border: 1px solid {border_color};
    border-radius: 8px;
    margin-top: 18px;
    font-weight: 700;
    font-size: 13px;
    color: {text_color};
    padding-top: 18px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    background-color: {main_bg};
}

/* Filter Panel Container */
QFrame#FilterPanel {
    background-color: {card_bg};
    border: 1px solid {border_color};
    border-radius: 8px;
}

QFrame#FilterPanel QLabel {
    font-weight: 600;
    color: {muted_text};
    font-size: 11px;
}

QLineEdit#SearchInput {
    background-color: {main_bg};
    border: 1px solid {border_color};
    color: {text_color};
    border-radius: 6px;
}

QLineEdit#SearchInput:focus {
    border: 2px solid {accent_blue};
    background-color: {card_bg};
}

/* Scroll Area & Scrollbars */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: {border_color};
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: {muted_text};
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: {border_color};
    min-width: 24px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: {muted_text};
}

/* Special Components */
QLabel[class*="FileStatus"] {
    background-color: {tab_inactive_bg};
    border: 1px dashed {border_color};
    color: {muted_text};
    font-style: italic;
    padding: 10px;
    border-radius: 6px;
}

QLabel[class*="FileSelected"] {
    background-color: {selected_bg};
    border: 1px solid {accent_blue};
    color: {text_color};
    font-weight: 600;
    padding: 10px;
    border-radius: 6px;
}

QTextEdit[class*="ErrorLog"] {
    background-color: {input_bg};
    border: 1px solid {border_color};
    color: {danger_text};
    font-family: Consolas, monospace;
}

QLineEdit[class*="ReadOnlyPath"] {
    background-color: {tab_inactive_bg};
    border: 1px solid {border_color};
    color: {muted_text};
}

QLabel#PhotoPreviewFrame {
    border: 1px solid {border_color};
    background-color: {card_bg};
    border-radius: 8px;
}

QFrame#LoginCard {
    background-color: {card_bg};
    border: 1px solid {border_color};
    border-radius: 12px;
}

QLabel#LoginLogo {
    font-size: 28px;
    font-weight: 800;
    color: {text_color};
}

QLabel#LoginSubtitle {
    font-size: 13px;
    color: {muted_text};
}
"""

def compile_theme(colors):
    style = STYLE_SHEET_TEMPLATE
    for key, value in colors.items():
        style = style.replace(f"{{{key}}}", value)
    return style

def get_day_theme():
    return compile_theme(DAY_COLORS)

def get_night_theme():
    return compile_theme(NIGHT_COLORS)

def apply_theme(app_or_widget, theme_name):
    if theme_name == "night":
        style = get_night_theme()
    else:
        style = get_day_theme()
    app_or_widget.setStyleSheet(style)

def polish_widget(widget):
    """Forces Qt to re-evaluate stylesheet rules for dynamic property changes."""
    if widget and hasattr(widget, "style") and widget.style():
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

STYLE_SHEET = get_day_theme()
