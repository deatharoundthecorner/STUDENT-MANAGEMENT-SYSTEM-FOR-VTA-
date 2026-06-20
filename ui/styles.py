# ui/styles.py

STYLE_SHEET = """
/* Global Styles */
QWidget {
    font-family: "Segoe UI", "Segoe UI Semibold", "Inter", sans-serif;
    font-size: 13px;
    color: #1E293B;
    background-color: transparent;
}

/* Main Window */
QMainWindow {
    background-color: #F8FAFC;
}

/* Sidebar Navigation */
QFrame#SidebarFrame {
    background-color: #1E2A38;
    border: none;
    min-width: 240px;
    max-width: 240px;
}

QLabel#SidebarTitle {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: bold;
    padding: 20px 10px;
    background-color: #151F2A;
}

QPushButton.SidebarButton {
    color: #94A3B8;
    background-color: transparent;
    border: none;
    border-radius: 6px;
    text-align: left;
    padding: 12px 15px;
    font-size: 14px;
    font-weight: 500;
    margin: 4px 10px;
}

QPushButton.SidebarButton:hover {
    color: #FFFFFF;
    background-color: #2D3E50;
}

QPushButton.SidebarButton:checked {
    color: #FFFFFF;
    background-color: #3B82F6;
    font-weight: bold;
}

QPushButton.SidebarLogoutButton {
    color: #F87171;
    background-color: transparent;
    border: none;
    border-radius: 6px;
    text-align: left;
    padding: 12px 15px;
    font-size: 14px;
    font-weight: 500;
    margin: 20px 10px 10px 10px;
}

QPushButton.SidebarLogoutButton:hover {
    color: #FFFFFF;
    background-color: #EF4444;
}

/* Buttons */
QPushButton {
    background-color: #1E293B;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 0px 16px;
    min-height: 44px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #334155;
}

QPushButton:pressed {
    background-color: #0F172A;
}

QPushButton.PrimaryButton {
    color: #FFFFFF;
    background-color: #3B82F6;
    border: none;
    border-radius: 6px;
    padding: 0px 16px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #2563EB;
}

QPushButton.PrimaryButton:pressed {
    background-color: #1D4ED8;
}

QPushButton.SecondaryButton {
    color: #475569;
    background-color: #E2E8F0;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 0px 16px;
    font-weight: 600;
}

QPushButton.SecondaryButton:hover {
    background-color: #CBD5E1;
}

QPushButton.DangerButton {
    color: #FFFFFF;
    background-color: #EF4444;
    border: none;
    border-radius: 6px;
    padding: 0px 16px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: #DC2626;
}

/* Dashboard Cards */
QFrame.DashboardCard {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 15px;
}

QLabel.CardTitle {
    color: #64748B;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel.CardValue {
    color: #1E293B;
    font-size: 26px;
    font-weight: bold;
    margin-top: 5px;
}

/* Input Fields */
QLineEdit {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding-left: 12px;
    padding-right: 12px;
    padding-top: 0px;
    padding-bottom: 0px;
    min-height: 42px;
    font-size: 14px;
    selection-background-color: #3B82F6;
    selection-color: #FFFFFF;
}

QLineEdit:focus {
    border: 2px solid #3B82F6;
    background-color: #FFFFFF;
}

QTextEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    color: #1E293B;
    selection-background-color: #93C5FD;
}

QTextEdit:focus, QComboBox:focus {
    border: 1px solid #3B82F6;
    background-color: #FFFFFF;
}

QComboBox::drop-down {
    border: none;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
}

/* Data Tables */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
    selection-background-color: #EFF6FF;
    selection-color: #1E293B;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #F1F5F9;
}

QHeaderView::section {
    background-color: #1E2A38;
    color: #FFFFFF;
    padding: 10px;
    border: none;
    font-weight: 600;
    font-size: 13px;
}

/* Tab Widgets */
QTabWidget::pane {
    border: 1px solid #E2E8F0;
    background-color: #FFFFFF;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 18px;
    color: #64748B;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #1E2A38;
    border-bottom: 2px solid #3B82F6;
    font-weight: 600;
}

/* Group Boxes / Forms */
QGroupBox {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-top: 15px;
    font-weight: bold;
    color: #1E2A38;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 5px;
    background-color: #F8FAFC;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #F1F5F9;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

/* Dialogs */
QDialog {
    background-color: #F8FAFC;
}
"""
