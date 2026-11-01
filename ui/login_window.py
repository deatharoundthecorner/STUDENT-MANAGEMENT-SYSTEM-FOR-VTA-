# ui/login_window.py
# Redesigned Authentication and Administrator Setup Windows
# Adhering to the clean, neutral, modern ChatGPT-inspired design system

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QStackedWidget, QProgressBar,
                             QApplication)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, Signal, QSize
from ui.icons import get_icon
from ui.widgets import PasswordLineEdit, make_password_input, FormLabel, StatusBanner
from services.auth_service import AuthService
from utils.paths import get_asset_path


class SetupWizard(QWidget):
    setup_completed = Signal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.init_ui()

    def init_ui(self):
        self.setObjectName("SetupWizard")
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(0)

        # Setup Card Container (ensures crisp, solid card background in both light & dark modes)
        self.setup_card = QFrame()
        self.setup_card.setObjectName("SetupCard")
        layout = QVBoxLayout(self.setup_card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        # 1. Header with Application Identity
        header_row = QHBoxLayout()
        header_row.setSpacing(14)

        logo_label = QLabel()
        logo_path = get_asset_path("assets/branding/app_logo.png")
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
            logo_label.setFixedSize(44, 44)
        header_row.addWidget(logo_label)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Administrator Setup")
        title.setProperty("class", "PageTitle")
        subtitle = QLabel("Create the master administrator account for this workstation.")
        subtitle.setProperty("class", "PageSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_row.addLayout(title_col)
        layout.addLayout(header_row)

        # 2. Local Storage Notice Banner (styled via theme tokens)
        notice_card = QFrame()
        notice_card.setObjectName("NoticeCard")
        notice_layout = QHBoxLayout(notice_card)
        notice_layout.setContentsMargins(8, 6, 8, 6)
        notice_layout.setSpacing(8)

        notice_icon = QLabel()
        notice_icon.setPixmap(get_icon("info", color="#2563EB", size=16).pixmap(16, 16))
        notice_icon.setFixedSize(16, 16)
        notice_text = QLabel("Account credentials and student databases are stored strictly on this workstation.")
        notice_text.setObjectName("NoticeText")
        notice_text.setWordWrap(True)
        notice_layout.addWidget(notice_icon)
        notice_layout.addWidget(notice_text, 1)
        layout.addWidget(notice_card)

        # 3. Form Container
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(0, 2, 0, 0)
        form_layout.setSpacing(8)

        # Field 1: Username
        lbl_user = FormLabel("Administrator Username", required=True)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g. admin or director")
        self.username_input.setFixedHeight(38)
        self.username_input.setProperty("class", "FormInput")
        form_layout.addWidget(lbl_user)
        form_layout.addWidget(self.username_input)

        # Field 2: Password
        lbl_pass = FormLabel("Master Password", required=True)
        self.password_input = PasswordLineEdit("At least 8 characters with letters & numbers/symbols")
        self.password_input.setFixedHeight(38)
        self.password_input.textChanged.connect(self.on_password_changed)
        form_layout.addWidget(lbl_pass)
        form_layout.addWidget(self.password_input)

        # Password Strength Indicator Bar & Label
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setProperty("class", "PasswordStrengthBar")

        self.lbl_strength = QLabel("Password policy: Minimum 8 characters with letters and numbers/symbols.")
        self.lbl_strength.setStyleSheet("color: #64748B; font-size: 11px;")
        self.lbl_strength.setWordWrap(True)

        form_layout.addWidget(self.strength_bar)
        form_layout.addWidget(self.lbl_strength)

        # Field 3: Confirm Password
        lbl_confirm = FormLabel("Confirm Master Password", required=True)
        self.confirm_input = PasswordLineEdit("Re-enter password to verify")
        self.confirm_input.setFixedHeight(38)
        form_layout.addWidget(lbl_confirm)
        form_layout.addWidget(self.confirm_input)

        # Stable Status / Error Banner (reserved space prevents layout jumping)
        self.status_banner = StatusBanner()
        self.status_label = self.status_banner  # Backward-compatible attribute reference
        form_layout.addWidget(self.status_banner)

        # Primary Action Button
        self.create_btn = QPushButton("Create Administrator Account")
        self.create_btn.setProperty("class", "PrimaryButton")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.setFixedHeight(42)
        self.create_btn.clicked.connect(self.handle_setup)
        form_layout.addWidget(self.create_btn)

        layout.addWidget(form_frame)
        root_layout.addWidget(self.setup_card)

        # Keyboard Navigation
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.confirm_input)
        self.setTabOrder(self.confirm_input, self.create_btn)

        self.username_input.returnPressed.connect(self.handle_setup)
        self.password_input.returnPressed.connect(self.handle_setup)
        self.confirm_input.returnPressed.connect(self.handle_setup)

    def on_password_changed(self, text: str):
        if not text:
            self.strength_bar.setValue(0)
            self.strength_bar.setStyleSheet("")
            self.lbl_strength.setText("Password policy: Minimum 8 characters with letters and numbers/symbols.")
            self.lbl_strength.setStyleSheet("color: #64748B; font-size: 11px;")
            return
        if text.strip() != text:
            self.strength_bar.setValue(20)
            self.strength_bar.setStyleSheet("QProgressBar[class*='PasswordStrengthBar']::chunk { background-color: #DC2626; border-radius: 2px; }")
            self.lbl_strength.setText("Password cannot begin or end with spaces")
            self.lbl_strength.setStyleSheet("color: #DC2626; font-size: 11px; font-weight: 600;")
            return
        if len(text) < 8:
            self.strength_bar.setValue(20)
            self.strength_bar.setStyleSheet("QProgressBar[class*='PasswordStrengthBar']::chunk { background-color: #DC2626; border-radius: 2px; }")
            self.lbl_strength.setText("Password too short (minimum 8 characters)")
            self.lbl_strength.setStyleSheet("color: #DC2626; font-size: 11px; font-weight: 600;")
        elif text.lower() in AuthService.COMMON_PASSWORDS:
            self.strength_bar.setValue(25)
            self.strength_bar.setStyleSheet("QProgressBar[class*='PasswordStrengthBar']::chunk { background-color: #DC2626; border-radius: 2px; }")
            self.lbl_strength.setText("Common guessable password (rejected)")
            self.lbl_strength.setStyleSheet("color: #DC2626; font-size: 11px; font-weight: 600;")
        elif len(text) >= 15:
            self.strength_bar.setValue(100)
            self.strength_bar.setStyleSheet("QProgressBar[class*='PasswordStrengthBar']::chunk { background-color: #059669; border-radius: 2px; }")
            self.lbl_strength.setText("Excellent passphrase (15+ characters)")
            self.lbl_strength.setStyleSheet("color: #059669; font-size: 11px; font-weight: 600;")
        elif any(c.isalpha() for c in text) and any(not c.isalpha() for c in text):
            self.strength_bar.setValue(65)
            self.strength_bar.setStyleSheet("QProgressBar[class*='PasswordStrengthBar']::chunk { background-color: #2563EB; border-radius: 2px; }")
            self.lbl_strength.setText("Strong password (letters and numbers/symbols)")
            self.lbl_strength.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: 600;")
        else:
            self.strength_bar.setValue(35)
            self.strength_bar.setStyleSheet("QProgressBar[class*='PasswordStrengthBar']::chunk { background-color: #D97706; border-radius: 2px; }")
            self.lbl_strength.setText("Include both letters and numbers or symbols")
            self.lbl_strength.setStyleSheet("color: #D97706; font-size: 11px; font-weight: 600;")

    def handle_setup(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password or not confirm:
            self.status_banner.show_error("Please complete all required fields before continuing.")
            return
        if password != confirm:
            self.status_banner.show_error("Passwords do not match. Please verify and re-enter.")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        valid, msg = self.auth_service.validate_password(password)
        if not valid:
            self.status_banner.show_error(msg)
            self.password_input.clear()
            self.confirm_input.clear()
            self.password_input.setFocus()
            return

        # Double-submission protection
        self.create_btn.setEnabled(False)
        self.create_btn.setText("Creating Account...")
        QApplication.processEvents()

        try:
            success, msg = self.auth_service.create_admin_user(username, password)
            if success:
                self.status_banner.show_success("Administrator account created successfully.")
                self.setup_completed.emit()
            else:
                self.status_banner.show_error(msg)
        finally:
            self.create_btn.setEnabled(True)
            self.create_btn.setText("Create Administrator Account")


class ForcedPasswordChangeDialog(QWidget):
    change_completed = Signal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.username = ""
        self.init_ui()

    def init_ui(self):
        self.setObjectName("ForcedPasswordChange")
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("ForcedChangeCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        # Header
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        logo_label = QLabel()
        logo_path = get_asset_path("assets/branding/app_logo.png")
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
            logo_label.setFixedSize(44, 44)
        header_row.addWidget(logo_label)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Password Update Required")
        title.setProperty("class", "PageTitle")
        subtitle = QLabel("Please set a new secure password before accessing the system.")
        subtitle.setProperty("class", "PageSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_row.addLayout(title_col)
        layout.addLayout(header_row)

        form = QFrame()
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(0, 4, 0, 0)
        form_layout.setSpacing(10)

        form_layout.addWidget(FormLabel("Current Temporary Password", required=True))
        self.current_input = PasswordLineEdit("Enter temporary password")
        form_layout.addWidget(self.current_input)

        form_layout.addWidget(FormLabel("New Password", required=True))
        self.new_input = PasswordLineEdit("Minimum 8 characters with letters & symbols")
        form_layout.addWidget(self.new_input)

        form_layout.addWidget(FormLabel("Confirm New Password", required=True))
        self.confirm_input = PasswordLineEdit("Re-enter new password to verify")
        form_layout.addWidget(self.confirm_input)

        self.status_banner = StatusBanner()
        self.status_label = self.status_banner
        form_layout.addWidget(self.status_banner)

        self.change_button = QPushButton("Update Password & Continue")
        self.change_button.setProperty("class", "PrimaryButton")
        self.change_button.setCursor(Qt.PointingHandCursor)
        self.change_button.setFixedHeight(42)
        self.change_button.clicked.connect(self.handle_change)
        form_layout.addWidget(self.change_button)

        layout.addWidget(form)

        # Tab order
        self.setTabOrder(self.current_input, self.new_input)
        self.setTabOrder(self.new_input, self.confirm_input)
        self.setTabOrder(self.confirm_input, self.change_button)

        self.confirm_input.returnPressed.connect(self.handle_change)
        root_layout.addWidget(card)

    def set_username(self, username: str):
        self.username = username
        self.current_input.clear()
        self.new_input.clear()
        self.confirm_input.clear()
        self.status_banner.clear_message()
        self.current_input.setFocus()

    def handle_change(self):
        current = self.current_input.text()
        new_password = self.new_input.text()
        confirmation = self.confirm_input.text()

        if not current or not new_password or not confirmation:
            self.status_banner.show_error("Please complete all password fields before continuing.")
            return
        if not self.auth_service.verify_current_password(self.username, current):
            self.status_banner.show_error("The current password entered is incorrect.")
            self.current_input.clear()
            self.current_input.setFocus()
            return
        if current == new_password:
            self.status_banner.show_error("New password cannot be the same as the current password.")
            self.new_input.clear()
            self.confirm_input.clear()
            self.new_input.setFocus()
            return
        if new_password != confirmation:
            self.status_banner.show_error("The new passwords do not match. Please verify and re-type.")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return

        self.change_button.setEnabled(False)
        self.change_button.setText("Updating Credentials...")
        QApplication.processEvents()

        try:
            success, message = self.auth_service.change_password(self.username, current, new_password)
            if success:
                self.change_completed.emit()
            else:
                self.status_banner.show_error(message)
                self.new_input.clear()
                self.confirm_input.clear()
                self.new_input.setFocus()
        finally:
            self.change_button.setEnabled(True)
            self.change_button.setText("Update Password & Continue")


class LoginWindow(QWidget):
    login_successful = Signal()
    setup_completed = Signal()

    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.authenticated_username = ""
        self.init_ui()
        if self.auth_service.is_setup_required():
            self.show_setup_view()
        else:
            self.show_login_view()

    def init_ui(self):
        self.setWindowTitle("Student Management System - Sign In")
        self.resize(480, 640)
        self.setMinimumSize(460, 600)
        self.setMaximumSize(560, 720)
        self.setObjectName("LoginWindow")

        # Set Window Icon
        icon_path = get_asset_path("assets/branding/app_icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.stack = QStackedWidget(self)
        self.stack.setObjectName("AuthStack")

        # -------------------------------------------------------------
        # 1. Login Card
        # -------------------------------------------------------------
        self.login_card = QFrame()
        self.login_card.setObjectName("LoginCard")
        self.login_layout = QVBoxLayout(self.login_card)
        self.login_layout.setContentsMargins(32, 28, 32, 28)
        self.login_layout.setSpacing(12)

        # Brand Emblem & Title
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = get_asset_path("assets/branding/app_logo.png")
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(68, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
            logo_label.setFixedHeight(72)
        else:
            logo_label.setText("SMS")
            logo_label.setObjectName("LoginLogo")

        subtitle_label = QLabel("Student Management System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("LoginSubtitle")

        edition_label = QLabel("Windows Desktop Edition  •  Administrator Sign In")
        edition_label.setAlignment(Qt.AlignCenter)
        edition_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500; margin-bottom: 4px;")

        # Inputs
        user_label = FormLabel("Administrator Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter administrator username")
        self.username_input.setFixedHeight(38)
        self.username_input.setProperty("class", "FormInput")

        pass_label = FormLabel("Password")
        self.password_input = PasswordLineEdit("Enter password")
        self.password_input.setFixedHeight(38)

        # Status / Error banner with reserved height
        self.error_banner = StatusBanner()
        self.error_label = self.error_banner  # Backward-compatible attribute reference

        self.login_btn = QPushButton("Sign In")
        self.login_btn.setProperty("class", "PrimaryButton")
        self.login_btn.setFixedHeight(42)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)

        self.login_layout.addWidget(logo_label)
        self.login_layout.addWidget(subtitle_label)
        self.login_layout.addWidget(edition_label)
        self.login_layout.addSpacing(6)
        self.login_layout.addWidget(user_label)
        self.login_layout.addWidget(self.username_input)
        self.login_layout.addWidget(pass_label)
        self.login_layout.addWidget(self.password_input)
        self.login_layout.addWidget(self.error_banner)
        self.login_layout.addWidget(self.login_btn)
        self.login_layout.addStretch(1)

        # Keyboard Navigation
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.login_btn)

        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)

        # -------------------------------------------------------------
        # 2. Setup Widget & Forced Change Widget
        # -------------------------------------------------------------
        self.setup_widget = SetupWizard(self.auth_service)
        self.setup_widget.setup_completed.connect(self.on_setup_completed)
        self.forced_change_widget = ForcedPasswordChangeDialog(self.auth_service)
        self.forced_change_widget.change_completed.connect(self.on_forced_change_completed)

        self.stack.addWidget(self.login_card)
        self.stack.addWidget(self.setup_widget)
        self.stack.addWidget(self.forced_change_widget)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 16, 16, 16)
        outer_layout.addWidget(self.stack)

    def show_login_view(self):
        self.stack.setCurrentWidget(self.login_card)
        self.username_input.setFocus()

    def show_setup_view(self):
        self.stack.setCurrentWidget(self.setup_widget)
        self.setup_widget.username_input.setFocus()

    def show_forced_change_view(self, username):
        self.forced_change_widget.set_username(username)
        self.stack.setCurrentWidget(self.forced_change_widget)

    def on_forced_change_completed(self):
        self.error_banner.show_success("Password updated. Sign in with your new password.")
        self.show_login_view()

    def on_setup_completed(self):
        self.setup_completed.emit()
        self.username_input.clear()
        self.password_input.clear()
        self.error_banner.show_success("Account initialized. Please sign in.")
        self.show_login_view()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_banner.show_error("Please enter both username and password.")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Verifying Credentials...")
        QApplication.processEvents()

        try:
            login_status = self.auth_service.get_login_status(username, password)
            if login_status == "password_change_required":
                self.show_forced_change_view(username)
            elif login_status == "success":
                self.error_banner.clear_message()
                self.authenticated_username = username
                self.login_successful.emit()
            else:
                self.error_banner.show_error("Invalid username or password credentials.")
                self.password_input.clear()
                self.password_input.setFocus()
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Sign In")
