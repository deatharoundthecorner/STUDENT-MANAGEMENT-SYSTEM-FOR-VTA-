# ui/styles.py
# Comprehensive Design System for Student Management System (SMS) - Windows Desktop Edition

# Design Tokens: Spacing, Radius, Typography Scale
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

RADIUS = {
    "sm": 4,
    "md": 6,
    "lg": 8,
    "xl": 12,
}

CONTROL_HEIGHT = {
    "sm": 32,
    "md": 38,
    "lg": 44,
}

# Day Mode Palette (Light Institutional Theme)
DAY_COLORS = {
    "main_bg": "#F8FAFC",          # Slate-50: Crisp institutional canvas
    "card_bg": "#FFFFFF",          # Pure white card surface
    "sidebar_bg": "#0F172A",       # Slate-900: Deep professional navy
    "sidebar_hover": "#1E293B",    # Slate-800: Lighter navy on hover
    "sidebar_active": "#2563EB",   # Royal blue accent indicator
    "sidebar_text": "#94A3B8",     # Slate-400: Neutral navigation text
    "sidebar_text_hover": "#FFFFFF",
    "sidebar_title_bg": "#020617", # Slate-950: Brand header
    "topbar_bg": "#FFFFFF",        # Crisp white top navigation bar
    "topbar_border": "#E2E8F0",    # Slate-200 top divider
    "text_color": "#0F172A",       # Slate-900: High-contrast primary text
    "muted_text": "#64748B",       # Slate-500: Secondary descriptive text
    "border_color": "#CBD5E1",     # Slate-300: Clean container border
    "border_light": "#E2E8F0",     # Slate-200: Subtle card divider
    "accent_blue": "#2563EB",      # Blue-600: Institutional primary blue
    "accent_blue_hover": "#1D4ED8",# Blue-700: Hover state
    "accent_blue_pressed": "#1E40AF",# Blue-800: Pressed state
    "input_bg": "#FFFFFF",
    "input_border": "#CBD5E1",
    "input_focus_border": "#2563EB",
    "button_dark": "#0F172A",
    "table_grid": "#F1F5F9",       # Slate-100: Soft row separators
    "table_selection_bg": "#EFF6FF", # Soft blue row selection
    "table_selection_text": "#1E3A8A",# Deep navy selected text
    "tab_inactive_bg": "#F1F5F9",  # Slate-100
    "success": "#059669",          # Emerald-600
    "success_bg": "#ECFDF5",       # Emerald-50
    "warning": "#D97706",          # Amber-600
    "warning_bg": "#FFFBEB",       # Amber-50
    "danger": "#DC2626",           # Red-600
    "danger_hover": "#B91C1C",     # Red-700
    "danger_bg": "#FEF2F2",        # Red-50
    "danger_text": "#991B1B",      # Red-800
    "selected_bg": "#EFF6FF",      # Blue-50
    # Table Row Action Button Tokens
    "action_view_bg": "#EFF6FF",     # Blue-50
    "action_view_text": "#1D4ED8",   # Blue-700
    "action_view_border": "#BFDBFE", # Blue-200
    "action_view_hover": "#2563EB",  # Blue-600
    "action_edit_bg": "#ECFDF5",     # Emerald-50
    "action_edit_text": "#047857",   # Emerald-700
    "action_edit_border": "#A7F3D0", # Emerald-200
    "action_edit_hover": "#059669",  # Emerald-600
    "action_del_bg": "#FEF2F2",      # Red-50
    "action_del_text": "#B91C1C",    # Red-700
    "action_del_border": "#FECACA",  # Red-200
    "action_del_hover": "#DC2626",   # Red-600
}

# Night Mode Palette (Dark Institutional Theme)
NIGHT_COLORS = {
    "main_bg": "#0B1120",          # Deep navy/slate canvas
    "card_bg": "#1E293B",          # Slate-800 card surface
    "sidebar_bg": "#020617",       # Slate-950 deep navy sidebar
    "sidebar_hover": "#0F172A",    # Slate-900 on hover
    "sidebar_active": "#3B82F6",   # Bright blue accent indicator
    "sidebar_text": "#94A3B8",     # Slate-400
    "sidebar_text_hover": "#F8FAFC",
    "sidebar_title_bg": "#000000",
    "topbar_bg": "#0F172A",        # Slate-900 top navigation bar
    "topbar_border": "#1E293B",    # Slate-800 divider
    "text_color": "#F8FAFC",       # Slate-50: Crisp light text
    "muted_text": "#94A3B8",       # Slate-400: Secondary text
    "border_color": "#334155",     # Slate-700: Sleek dark border
    "border_light": "#1E293B",     # Slate-800
    "accent_blue": "#3B82F6",      # Blue-500: Vibrant accent
    "accent_blue_hover": "#60A5FA",# Blue-400: Hover state
    "accent_blue_pressed": "#1D4ED8",# Blue-700: Pressed state
    "input_bg": "#0F172A",         # Slate-900 input field
    "input_border": "#334155",     # Slate-700
    "input_focus_border": "#60A5FA",
    "button_dark": "#2563EB",
    "table_grid": "#334155",       # Slate-700
    "table_selection_bg": "#1E3A8A", # Deep navy selection
    "table_selection_text": "#FFFFFF",
    "tab_inactive_bg": "#0F172A",
    "success": "#10B981",          # Emerald-500
    "success_bg": "#064E3B",       # Emerald-900
    "warning": "#F59E0B",          # Amber-500
    "warning_bg": "#78350F",       # Amber-900
    "danger": "#EF4444",           # Red-500
    "danger_hover": "#DC2626",     # Red-600
    "danger_bg": "#7F1D1D",        # Red-900
    "danger_text": "#FCA5A5",      # Red-200
    "selected_bg": "#1E3A8A",
    # Table Row Action Button Tokens
    "action_view_bg": "#172554",     # Blue-950
    "action_view_text": "#93C5FD",   # Blue-300
    "action_view_border": "#1E40AF", # Blue-800
    "action_view_hover": "#2563EB",  # Blue-600
    "action_edit_bg": "#064E3B",     # Emerald-950
    "action_edit_text": "#6EE7B7",   # Emerald-300
    "action_edit_border": "#065F46", # Emerald-800
    "action_edit_hover": "#059669",  # Emerald-600
    "action_del_bg": "#450A0A",      # Red-950
    "action_del_text": "#FCA5A5",    # Red-300
    "action_del_border": "#991B1B",  # Red-800
    "action_del_hover": "#DC2626",   # Red-600
}

STYLE_SHEET_TEMPLATE = """
/* Global Defaults */
QWidget {
    font-family: "Segoe UI", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
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

QWidget#LoginWindow, QWidget#SetupWizard, QWidget#ForcedPasswordChange, QStackedWidget#AuthStack {
    background-color: {main_bg};
}

/* TopBar Header Frame */
QFrame#TopBarFrame {
    background-color: {topbar_bg};
    border-bottom: 1px solid {topbar_border};
    min-height: 52px;
    max-height: 52px;
}

QLabel#TopBarTitle {
    color: {text_color};
    font-size: 15px;
    font-weight: 700;
}

QLabel#TopBarUserBadge {
    background-color: {tab_inactive_bg};
    color: {text_color};
    border: 1px solid {border_color};
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
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
    padding: 18px 16px 4px 16px;
    background-color: {sidebar_title_bg};
}

QLabel#SidebarSubtitle {
    color: {sidebar_text};
    font-size: 11px;
    font-weight: 500;
    padding: 0 16px 16px 16px;
    background-color: {sidebar_title_bg};
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

/* Sidebar Navigation Buttons */
QPushButton[class*="SidebarButton"] {
    color: {sidebar_text};
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0 6px 6px 0;
    text-align: left;
    padding: 11px 16px;
    font-size: 13px;
    font-weight: 500;
    margin: 2px 10px 2px 0px;
}

QPushButton[class*="SidebarButton"]:hover {
    color: {sidebar_text_hover};
    background-color: {sidebar_hover};
    border-left: 3px solid rgba(255, 255, 255, 0.3);
}

QPushButton[class*="SidebarButton"]:checked {
    color: #FFFFFF;
    background-color: {sidebar_hover};
    border-left: 3px solid {accent_blue};
    font-weight: 600;
}

QPushButton[class*="SidebarButton"]:focus {
    outline: none;
}

/* Sidebar Logout Button */
QPushButton[class*="SidebarLogoutButton"] {
    color: #F87171;
    background-color: transparent;
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 6px;
    text-align: left;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
    margin: 10px 14px 16px 14px;
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
    padding: 0 18px;
    min-height: 38px;
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
    border: 2px solid {accent_blue_hover};
}

/* Secondary / Neutral Buttons */
QPushButton[class*="SecondaryButton"] {
    background-color: {card_bg};
    color: {text_color};
    border: 1px solid {border_color};
    border-radius: 6px;
    padding: 0 16px;
    min-height: 38px;
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
    min-height: 38px;
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
    padding: 0 16px;
    min-height: 38px;
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
    color: {muted_text};
    border-color: {border_color};
}

/* Table Row Action Buttons - Refined Semantic Pill Style */
QPushButton[class*="TableActionView"] {
    background-color: {action_view_bg};
    color: {action_view_text};
    border: 1px solid {action_view_border};
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    min-height: 24px;
    max-height: 28px;
}

QPushButton[class*="TableActionView"]:hover {
    background-color: {action_view_hover};
    color: #FFFFFF;
    border-color: {action_view_hover};
}

QPushButton[class*="TableActionView"]:focus {
    outline: none;
    border: 2px solid {accent_blue};
}

QPushButton[class*="TableActionEdit"] {
    background-color: {action_edit_bg};
    color: {action_edit_text};
    border: 1px solid {action_edit_border};
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    min-height: 24px;
    max-height: 28px;
}

QPushButton[class*="TableActionEdit"]:hover {
    background-color: {action_edit_hover};
    color: #FFFFFF;
    border-color: {action_edit_hover};
}

QPushButton[class*="TableActionEdit"]:focus {
    outline: none;
    border: 2px solid {success};
}

QPushButton[class*="TableActionDelete"] {
    background-color: {action_del_bg};
    color: {action_del_text};
    border: 1px solid {action_del_border};
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    min-height: 24px;
    max-height: 28px;
}

QPushButton[class*="TableActionDelete"]:hover {
    background-color: {action_del_hover};
    color: #FFFFFF;
    border-color: {action_del_hover};
}

QPushButton[class*="TableActionDelete"]:focus {
    outline: none;
    border: 2px solid {danger};
}

/* Auxiliary Table & Label Classes */
QLabel[class*="FilterLabel"] {
    color: {muted_text};
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 2px;
}

QLabel[class*="PaginationLabel"], QLabel[class*="PageInfoLabel"] {
    color: {muted_text};
    font-size: 12px;
    font-weight: 600;
    padding: 0 6px;
}

QLabel[class*="MutedText"] {
    color: {muted_text};
    font-size: 12px;
    font-weight: 500;
}

QLabel[class*="SelectedStudentActive"] {
    color: {text_color};
    font-size: 13px;
    font-weight: 600;
}

QLabel[class*="SelectedStudentInactive"] {
    color: {muted_text};
    font-size: 12px;
    font-style: italic;
}

/* Tertiary / Ghost Buttons */
QPushButton[class*="GhostButton"] {
    background-color: transparent;
    color: {text_color};
    border: none;
    border-radius: 6px;
    padding: 0 12px;
    min-height: 34px;
    font-weight: 500;
    font-size: 13px;
}

QPushButton[class*="GhostButton"]:hover {
    background-color: {tab_inactive_bg};
}

QPushButton[class*="GhostButton"]:pressed {
    background-color: {border_color};
}

/* Form Inputs & Controls */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: {input_bg};
    border: 1px solid {input_border};
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 36px;
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
    min-height: 36px;
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
    selection-color: {table_selection_text};
    padding: 4px;
}

QSpinBox {
    background-color: {input_bg};
    border: 1px solid {input_border};
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 36px;
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
    padding: 10px 12px;
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

QLabel[class*="LoginFormLabel"], QLabel[class*="FormLabel"] {
    color: {text_color};
    font-weight: 600;
    font-size: 12px;
    margin-bottom: 2px;
}

QLabel[class*="StatusBanner"] {
    min-height: 22px;
    font-size: 12px;
    font-weight: 500;
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

/* Progress Bars */
QProgressBar {
    background-color: {tab_inactive_bg};
    border: 1px solid {border_color};
    border-radius: 4px;
    text-align: center;
    font-size: 10px;
    font-weight: 600;
    color: {text_color};
    min-height: 10px;
    max-height: 12px;
}

QProgressBar::chunk {
    background-color: {accent_blue};
    border-radius: 3px;
}

/* Empty State Styling */
QFrame#EmptyStateFrame {
    background-color: {card_bg};
    border: 1px dashed {border_color};
    border-radius: 8px;
    padding: 30px;
}

QLabel#EmptyStateIcon {
    font-size: 36px;
}

QLabel#EmptyStateTitle {
    font-size: 16px;
    font-weight: 700;
    color: {text_color};
}

QLabel#EmptyStateDescription {
    font-size: 13px;
    color: {muted_text};
    line-height: 1.4;
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

QFrame#LoginCard, QFrame#SetupCard, QFrame#ForcedChangeCard {
    background-color: {card_bg};
    border: 1px solid {border_color};
    border-radius: 12px;
}

QFrame#NoticeCard {
    background-color: {selected_bg};
    border: 1px solid {accent_blue};
    border-radius: 6px;
    padding: 8px 12px;
}

QLabel#NoticeText {
    color: {text_color};
    font-size: 11px;
    font-weight: 500;
}

QProgressBar[class*="PasswordStrengthBar"] {
    background-color: {tab_inactive_bg};
    border: 1px solid {border_color};
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
}

QProgressBar[class*="PasswordStrengthBar"]::chunk {
    border-radius: 2px;
}

QFrame#FormFooterFrame {
    background-color: {card_bg};
    border-top: 1px solid {border_color};
    min-height: 54px;
    max-height: 54px;
}

QFrame[class*="CardBadge"] {
    background-color: {tab_inactive_bg};
    border: 1px solid {border_color};
    border-radius: 8px;
}

QLabel[class*="CardSubtitle"] {
    color: {muted_text};
    font-size: 11px;
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
    # Case-insensitive robust comparison
    if str(theme_name).strip().lower() == "night":
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
