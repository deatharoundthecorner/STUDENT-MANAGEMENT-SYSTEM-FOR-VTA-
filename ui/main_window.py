# ui/main_window.py
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton, QStackedWidget, QLabel,
                             QFrame, QMessageBox, QButtonGroup, QDialog,
                             QLineEdit, QFormLayout, QSizePolicy)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, Signal, QEvent, QTimer, QSize

from ui.styles import STYLE_SHEET
from ui.icons import get_icon, get_pixmap
from ui.widgets import PasswordLineEdit
from ui.dashboard_page import DashboardPage
from ui.students_page import StudentsPage
from ui.student_form_page import StudentFormPage
from ui.student_profile_page import StudentProfilePage
from ui.import_page import ImportPage
from ui.export_backup_page import ExportBackupPage
from ui.settings_page import SettingsPage
from services.auth_service import AuthService
from services.session_lock_service import SessionLockController
from services.settings_service import SettingsService
from utils.paths import get_asset_path


class SessionLockDialog(QDialog):
    def __init__(self, username, auth_service, parent=None):
        super().__init__(parent)
        self.username = username
        self.auth_service = auth_service
        self.setWindowTitle("Session Locked")
        self.setModal(True)
        self.setFixedWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QLabel("Workstation Session Locked")
        header.setProperty("class", "PageTitle")
        layout.addWidget(header)

        self.message = QLabel("Enter your administrator password to resume active session.")
        self.message.setWordWrap(True)
        self.message.setProperty("class", "BodyText")
        layout.addWidget(self.message)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.password_input = PasswordLineEdit("Administrator password")
        self.password_input.setFixedHeight(38)
        self.password_input.returnPressed.connect(self.try_unlock)
        form_layout.addRow("Password:", self.password_input)
        layout.addLayout(form_layout)

        unlock_button = QPushButton("Unlock Session")
        unlock_button.setProperty("class", "PrimaryButton")
        unlock_button.setFixedHeight(40)
        unlock_button.setCursor(Qt.PointingHandCursor)
        unlock_button.clicked.connect(self.try_unlock)
        layout.addWidget(unlock_button)

    def try_unlock(self):
        if self.auth_service.get_login_status(self.username, self.password_input.text()) == "success":
            self.accept()
            return
        self.message.setText("The password is incorrect. The session remains locked.")
        self.message.setStyleSheet("color: #DC2626; font-weight: 600;")
        self.password_input.clear()
        self.password_input.setFocus()


class MainWindow(QMainWindow):
    logout_requested = Signal()

    PAGE_TITLES = {
        0: "Dashboard Overview",
        1: "Student Records Directory",
        2: "Student Registration & Dossier Form",
        3: "Batch Data Import",
        4: "Export Reports & Database Backup",
        5: "System & Security Settings",
        6: "Student Profile Dossier",
    }

    def __init__(self):
        super().__init__()
        self.settings_service = SettingsService()
        self.auth_service = AuthService()
        self.session_controller = None
        self.session_username = None
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
        if hasattr(self, "lbl_topbar_user"):
            self.lbl_topbar_user.setText(f"Admin: {username}")
        if hasattr(self, "page_settings"):
            self.page_settings.set_authenticated_user(username)

    def stop_session(self):
        self.session_timer.stop()
        if QApplication.instance():
            QApplication.instance().removeEventFilter(self)
        self.session_controller = None
        self.session_username = None
        if hasattr(self, "lbl_topbar_user"):
            self.lbl_topbar_user.setText("")
        if hasattr(self, "page_settings"):
            self.page_settings.set_authenticated_user(None)

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
        self.setWindowTitle("Student Management System - Windows Desktop Native Edition")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 650)

        # Center window on primary screen if available
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - 1280) // 2
            y = (geo.height() - 800) // 2
            self.move(max(0, x), max(0, y))

        # Set Window Icon explicitly
        icon_path = get_asset_path("assets/branding/app_icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Base horizontal layout: [Sidebar Frame] [Right Container (TopBar + Content Stack)]
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
            pix = QPixmap(str(logo_path)).scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
            logo_label.setFixedSize(38, 38)

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

        # Navigation Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.setIcon(get_icon("dashboard", color="#94A3B8", active_color="#14B8A6", size=18))
        self.btn_dashboard.setIconSize(QSize(18, 18))

        self.btn_students = QPushButton("Student Records")
        self.btn_students.setIcon(get_icon("students", color="#94A3B8", active_color="#14B8A6", size=18))
        self.btn_students.setIconSize(QSize(18, 18))

        self.btn_add_student = QPushButton("Add Student")
        self.btn_add_student.setIcon(get_icon("add_student", color="#94A3B8", active_color="#14B8A6", size=18))
        self.btn_add_student.setIconSize(QSize(18, 18))

        self.btn_import = QPushButton("Import Data")
        self.btn_import.setIcon(get_icon("import", color="#94A3B8", active_color="#14B8A6", size=18))
        self.btn_import.setIconSize(QSize(18, 18))

        self.btn_export = QPushButton("Export / Backup")
        self.btn_export.setIcon(get_icon("export", color="#94A3B8", active_color="#14B8A6", size=18))
        self.btn_export.setIconSize(QSize(18, 18))

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setIcon(get_icon("settings", color="#94A3B8", active_color="#14B8A6", size=18))
        self.btn_settings.setIconSize(QSize(18, 18))

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
            btn.setProperty("class", "SidebarButton")
            self.nav_group.addButton(btn)
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(self.navigate_to_page)

        # Default check
        self.btn_dashboard.setChecked(True)

        # Push elements to top, and place logout at bottom
        sidebar_layout.addStretch(1)

        # Theme Toggle Button inside sidebar
        self.btn_theme_toggle = QPushButton()
        self.btn_theme_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_theme_toggle.setProperty("class", "SidebarButton")
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme_toggle)

        current_theme = self.settings_service.get_setting("theme", "day")

        # Logout Button
        btn_logout = QPushButton("Logout")
        btn_logout.setIcon(get_icon("logout", color="#EF4444", active_color="#DC2626", size=18))
        btn_logout.setIconSize(QSize(18, 18))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setProperty("class", "SidebarLogoutButton")
        btn_logout.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(btn_logout)

        base_layout.addWidget(sidebar)

        # 2. Right Container: TopBar + Content Stack
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # TopBar Frame
        topbar_frame = QFrame()
        topbar_frame.setObjectName("TopBarFrame")
        topbar_layout = QHBoxLayout(topbar_frame)
        topbar_layout.setContentsMargins(28, 0, 28, 0)
        topbar_layout.setSpacing(16)

        self.lbl_topbar_title = QLabel(self.PAGE_TITLES[0])
        self.lbl_topbar_title.setObjectName("TopBarTitle")
        topbar_layout.addWidget(self.lbl_topbar_title)

        topbar_layout.addStretch(1)

        # Quick Theme Toggle in TopBar
        self.btn_topbar_theme = QPushButton()
        self.btn_topbar_theme.setCursor(Qt.PointingHandCursor)
        self.btn_topbar_theme.setProperty("class", "SecondaryButton")
        self.btn_topbar_theme.setFixedHeight(34)
        self.btn_topbar_theme.clicked.connect(self.toggle_theme)
        topbar_layout.addWidget(self.btn_topbar_theme)

        # Synchronize both sidebar and topbar theme toggles now that both exist
        self.sync_theme_toggle_button(current_theme)

        # Authenticated User Badge
        self.lbl_topbar_user = QLabel("Administrator")
        self.lbl_topbar_user.setObjectName("TopBarUserBadge")
        topbar_layout.addWidget(self.lbl_topbar_user)

        right_layout.addWidget(topbar_frame)

        # 3. Content Stack Setup
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
        self.page_students.add_student_requested.connect(lambda: self.switch_to_page_index(2, prepare_add=True))

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

        right_layout.addWidget(self.content_stack)
        base_layout.addWidget(right_container, 1)

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
                if index == 6:
                    self.nav_group.setExclusive(False)
                    btn.setChecked(False)
                    self.nav_group.setExclusive(True)

        if hasattr(self, "lbl_topbar_title"):
            self.lbl_topbar_title.setText(self.PAGE_TITLES.get(index, "Student Management System"))

        self.content_stack.setCurrentIndex(index)

    def show_student_profile(self, student_id):
        self.page_profile.load_student(student_id)
        self.switch_to_page_index(6)

    def show_edit_student_form(self, student_id):
        self.page_student_form.clear_form()
        self.page_student_form.set_edit_mode(student_id)
        self.switch_to_page_index(2)

    def show_students_list_page(self):
        self.switch_to_page_index(1)

    def on_student_form_submitted(self):
        self.switch_to_page_index(1)

    def on_student_form_cancelled(self):
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

        # Refresh pages that render theme-dependent icons or colors
        if hasattr(self, "page_students"):
            self.page_students.refresh_data()
        if hasattr(self, "page_dashboard"):
            self.page_dashboard.refresh_data()

    def sync_theme_toggle_button(self, theme_name):
        is_night = str(theme_name).lower() == "night"
        text = "Day Mode" if is_night else "Night Mode"
        icon_name = "sun" if is_night else "moon"
        tip = "Switch to Day Mode" if is_night else "Switch to Night Mode"
        icon_color = "#F59E0B" if is_night else "#64748B"

        if hasattr(self, "btn_theme_toggle"):
            self.btn_theme_toggle.setText(text)
            self.btn_theme_toggle.setIcon(get_icon(icon_name, color=icon_color, size=18))
            self.btn_theme_toggle.setIconSize(QSize(18, 18))
            self.btn_theme_toggle.setToolTip(tip)
        if hasattr(self, "btn_topbar_theme"):
            self.btn_topbar_theme.setText(text)
            self.btn_topbar_theme.setIcon(get_icon(icon_name, color=icon_color, size=16))
            self.btn_topbar_theme.setIconSize(QSize(16, 16))
            self.btn_topbar_theme.setToolTip(tip)
