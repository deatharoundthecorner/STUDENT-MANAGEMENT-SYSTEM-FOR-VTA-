# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame, QMessageBox, QButtonGroup
from PySide6.QtCore import Qt, Signal

from ui.styles import STYLE_SHEET
from ui.dashboard_page import DashboardPage
from ui.students_page import StudentsPage
from ui.student_form_page import StudentFormPage
from ui.student_profile_page import StudentProfilePage
from ui.import_page import ImportPage
from ui.export_backup_page import ExportBackupPage
from ui.settings_page import SettingsPage

class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Student Management System - Administrator Panel")
        self.resize(1100, 700)
        self.setMinimumSize(1000, 650)
        self.setStyleSheet(STYLE_SHEET)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Base horizontal layout: [Sidebar] [Content Stack]
        base_layout = QHBoxLayout(central_widget)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)

        # 1. Sidebar Setup
        sidebar = QFrame()
        sidebar.setObjectName("SidebarFrame")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Branding
        brand_label = QLabel("  SMS ADMIN")
        brand_label.setObjectName("SidebarTitle")
        brand_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        sidebar_layout.addWidget(brand_label)
        sidebar_layout.addSpacing(15)

        # Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_dashboard = QPushButton(" Dashboard")
        self.btn_students = QPushButton(" Student Records")
        self.btn_add_student = QPushButton(" Add Student")
        self.btn_import = QPushButton(" Import Data")
        self.btn_export = QPushButton(" Export / Backup")
        self.btn_settings = QPushButton(" Settings")

        buttons = [
            (self.btn_dashboard, 0),
            (self.btn_students, 1),
            (self.btn_add_student, 2),
            (self.btn_import, 3),
            (self.btn_export, 4),
            (self.btn_settings, 5)
        ]

        for btn, index in buttons:
            btn.setCheckable(True)
            btn.setObjectName(f"nav_btn_{index}")
            btn.setProperty("page_index", index)
            btn.setCursor(Qt.PointingHandCursor)
            # Add custom class to match styles
            btn.setClassName("SidebarButton") if hasattr(btn, "setClassName") else btn.setProperty("class", "SidebarButton")
            self.nav_group.addButton(btn)
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(self.navigate_to_page)

        # Default check
        self.btn_dashboard.setChecked(True)

        # Push elements to top, and place logout at bottom
        sidebar_layout.addStretch(1)

        # Logout Button
        btn_logout = QPushButton(" Logout")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setProperty("class", "SidebarLogoutButton")
        btn_logout.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(btn_logout)

        base_layout.addWidget(sidebar)

        # 2. Content Stack Setup
        self.content_stack = QStackedWidget()
        
        # Instantiate pages
        self.page_dashboard = DashboardPage()
        self.page_students = StudentsPage()
        self.page_student_form = StudentFormPage()
        self.page_import = ImportPage()
        self.page_export_backup = ExportBackupPage()
        self.page_settings = SettingsPage()
        self.page_profile = StudentProfilePage()

        # Connect navigation triggers
        self.page_students.view_student_requested.connect(self.show_student_profile)
        self.page_students.edit_student_requested.connect(self.show_edit_student_form)
        self.page_students.add_student_requested.connect(lambda: self.switch_to_page_index(2)) # Add student page
        
        self.page_student_form.form_submitted.connect(self.on_student_form_submitted)
        self.page_student_form.cancelled.connect(self.on_student_form_cancelled)
        
        self.page_profile.back_requested.connect(self.show_students_list_page)
        self.page_profile.edit_requested.connect(self.show_edit_student_form)

        # Add to stack
        self.content_stack.addWidget(self.page_dashboard)       # Index 0
        self.content_stack.addWidget(self.page_students)        # Index 1
        self.content_stack.addWidget(self.page_student_form)    # Index 2
        self.content_stack.addWidget(self.page_import)          # Index 3
        self.content_stack.addWidget(self.page_export_backup)   # Index 4
        self.content_stack.addWidget(self.page_settings)        # Index 5
        self.content_stack.addWidget(self.page_profile)         # Index 6

        base_layout.addWidget(self.content_stack)

        # Initial loading
        self.page_dashboard.refresh_data()

    def navigate_to_page(self):
        btn = self.sender()
        if btn:
            page_index = btn.property("page_index")
            self.switch_to_page_index(page_index)

    def switch_to_page_index(self, index):
        # Refresh target pages if needed when switching
        if index == 0:
            self.page_dashboard.refresh_data()
        elif index == 1:
            self.page_students.refresh_data()
        elif index == 2:
            self.page_student_form.clear_form() # Reset for add mode
            self.page_student_form.set_add_mode()
        elif index == 4:
            self.page_export_backup.refresh_backups()
        
        # Check matching button in sidebar
        for btn in self.nav_group.buttons():
            if btn.property("page_index") == index:
                btn.setChecked(True)
                break
            else:
                # If page is not in sidebar (e.g. profile view page 6), clear button selection
                if index == 6:
                    self.nav_group.setExclusive(False)
                    btn.setChecked(False)
                    self.nav_group.setExclusive(True)

        self.content_stack.setCurrentIndex(index)

    def show_student_profile(self, student_id):
        self.page_profile.load_student(student_id)
        self.switch_to_page_index(6) # Switch to profile view

    def show_edit_student_form(self, student_id):
        self.page_student_form.clear_form()
        self.page_student_form.set_edit_mode(student_id)
        self.switch_to_page_index(2) # Form index

    def show_students_list_page(self):
        self.switch_to_page_index(1)

    def on_student_form_submitted(self):
        # Go back to students table and refresh
        self.switch_to_page_index(1)

    def on_student_form_cancelled(self):
        # Cancel edit/add and return
        self.switch_to_page_index(1)

    def handle_logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout", "Are you sure you want to log out of the system?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
            
    def refresh_all_data(self):
        """Called upon restore or app init to refresh counts."""
        self.page_dashboard.refresh_data()
        self.page_students.refresh_data()
        self.page_export_backup.refresh_backups()
