# ui/main_window.py
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QStackedWidget, QLabel, 
                             QFrame, QMessageBox, QButtonGroup, QDialog, 
                             QLineEdit, QFormLayout)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, Signal, QEvent, QTimer

from ui.styles import STYLE_SHEET
from ui.dashboard_page import DashboardPage
from ui.students_page import StudentsPage
from ui.student_form_page import StudentFormPage
from ui.student_profile_page import StudentProfilePage
from ui.import_page import ImportPage
from ui.export_backup_page import ExportBackupPage
from ui.settings_page import SettingsPage
from services.auth_service import AuthService
from services.session_lock_service import SessionLockController
from utils.paths import get_asset_path


class SessionLockDialog(QDialog):
    def __init__(self, username, auth_service, parent=None):
        super().__init__(parent)
        self.username = username
        self.auth_service = auth_service
        self.setWindowTitle("Session locked")
        self.setModal(True)
        layout = QFormLayout(self)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Administrator password")
        self.message = QLabel("Enter your password to resume the session.")
        self.message.setWordWrap(True)
        unlock_button = QPushButton("Unlock session")
        unlock_button.clicked.connect(self.try_unlock)
        self.password_input.returnPressed.connect(self.try_unlock)
        layout.addRow(self.message)
        layout.addRow("Password:", self.password_input)
        layout.addRow(unlock_button)

    def try_unlock(self):
        if self.auth_service.get_login_status(self.username, self.password_input.text()) == "success":
            self.accept()
            return
        self.message.setText("The password is incorrect. The session remains locked.")
        self.password_input.clear()
        self.password_input.setFocus()

class MainWindow(QMainWindow):
    logout_requested = Signal()
 
    def __init__(self):
        super().__init__()
        from services.settings_service import SettingsService
        self.settings_service = SettingsService()
        self.auth_service = AuthService()
        self.session_controller = None
        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self.check_session_lock)
        self.init_ui()

    def start_session(self, username):
        timeout = int(self.settings_service.get_setting("lock_timeout_seconds", "900"))
        lock_on_minimize = self.settings_service.get_setting("lock_on_minimize", "0") == "1"
        self.session_controller = SessionLockController(timeout, lock_on_minimize)
        QApplication.instance().installEventFilter(self)
        self.session_timer.start()
        self.session_username = username

    def stop_session(self):
        self.session_timer.stop()
        if QApplication.instance():
            QApplication.instance().removeEventFilter(self)
        self.session_controller = None

    def check_session_lock(self):
        if self.session_controller and self.session_controller.check_timeout():
            self.show_session_lock()

    def show_session_lock(self):
        if not self.session_controller or not self.session_controller.locked:
            return
        dialog = SessionLockDialog(self.session_username, self.auth_service, self)
        if dialog.exec() == QDialog.Accepted:
            self.session_controller.unlock(True)

    def eventFilter(self, watched, event):
        if self.session_controller:
            if event.type() == QEvent.WindowStateChange and self.isMinimized():
                self.session_controller.handle_minimized()
                if self.session_controller.locked:
                    QTimer.singleShot(0, self.show_session_lock)
            elif event.type() in (QEvent.MouseMove, QEvent.MouseButtonPress, QEvent.KeyPress, QEvent.TouchBegin):
                self.session_controller.record_activity()
        return super().eventFilter(watched, event)

    def init_ui(self):
        self.setWindowTitle("Student Management System - Administrator Panel")
        self.resize(1100, 700)
        self.setMinimumSize(1000, 650)
        
        # Set Window Icon explicitly
        icon_path = get_asset_path("assets/branding/app_icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

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

        # Branding Header in Sidebar
        brand_container = QWidget()
        brand_layout = QHBoxLayout(brand_container)
        brand_layout.setContentsMargins(18, 16, 18, 16)
        brand_layout.setSpacing(12)

        logo_label = QLabel()
        logo_path = get_asset_path("assets/branding/app_logo.png")
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
            logo_label.setFixedSize(36, 36)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        brand_title = QLabel("SMS ADMIN")
        brand_title.setObjectName("SidebarTitle")
        brand_sub = QLabel("Student Management")
        brand_sub.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 500;")
        title_box.addWidget(brand_title)
        title_box.addWidget(brand_sub)

        brand_layout.addWidget(logo_label)
        brand_layout.addLayout(title_box)
        brand_layout.addStretch(1)

        sidebar_layout.addWidget(brand_container)
        sidebar_layout.addSpacing(10)

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
 
        # Theme Toggle Button
        self.btn_theme_toggle = QPushButton()
        self.btn_theme_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_theme_toggle.setProperty("class", "SidebarButton")
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme_toggle)
        
        current_theme = self.settings_service.get_setting("theme", "day")
        self.sync_theme_toggle_button(current_theme)
 
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
        self.page_students.add_student_requested.connect(lambda: self.switch_to_page_index(2, prepare_add=True)) # Add student page
        
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
            self.switch_to_page_index(page_index, prepare_add=(page_index == 2))

    def switch_to_page_index(self, index, prepare_add=False):
        # Refresh target pages if needed when switching
        if index == 0:
            self.page_dashboard.refresh_data()
        elif index == 1:
            self.page_students.refresh_data()
        elif index == 2 and prepare_add:
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

    def toggle_theme(self):
        current_theme = self.settings_service.get_setting("theme", "day")
        new_theme = "night" if current_theme == "day" else "day"
        
        # Save settings
        self.settings_service.set_setting("theme", new_theme)
        
        # Apply theme globally to the QApplication
        from ui.styles import apply_theme
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            apply_theme(app, new_theme)
            
        # Re-polish main window
        self.style().unpolish(self)
        self.style().polish(self)
        
        # Sync the toggle button icon/text
        self.sync_theme_toggle_button(new_theme)
        
        # Also sync dropdown inside settings page if it is loaded
        if hasattr(self, "page_settings") and hasattr(self.page_settings, "theme_combo"):
            self.page_settings.theme_combo.blockSignals(True)
            self.page_settings.theme_combo.setCurrentIndex(1 if new_theme == "night" else 0)
            self.page_settings.theme_combo.blockSignals(False)

    def sync_theme_toggle_button(self, theme_name):
        if theme_name == "night":
            self.btn_theme_toggle.setText("☀️ Day Mode")
            self.btn_theme_toggle.setToolTip("Switch to Day Mode")
        else:
            self.btn_theme_toggle.setText("🌙 Night Mode")
            self.btn_theme_toggle.setToolTip("Switch to Night Mode")
