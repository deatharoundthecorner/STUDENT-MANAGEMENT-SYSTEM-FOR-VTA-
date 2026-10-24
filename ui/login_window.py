# ui/login_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QStackedWidget
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, Signal
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        # Header with Logo Badge
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
        title = QLabel("First-Run Setup")
        title.setProperty("class", "PageTitle")
        subtitle = QLabel("Create the primary administrator account for this workstation.")
        subtitle.setProperty("class", "PageSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_row.addLayout(title_col)
        layout.addLayout(header_row)

        form = QFrame()
        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(10)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Administrator username")
        self.username_input.setFixedHeight(42)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Strong password (min. 4 characters)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setFixedHeight(42)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 500;")
        self.status_label.setWordWrap(True)

        create_btn = QPushButton("Create Administrator Account")
        create_btn.setProperty("class", "PrimaryButton")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setFixedHeight(46)
        create_btn.clicked.connect(self.handle_setup)
        self.username_input.returnPressed.connect(self.handle_setup)
        self.password_input.returnPressed.connect(self.handle_setup)
        self.confirm_input.returnPressed.connect(self.handle_setup)

        form_layout.addWidget(QLabel("Administrator Username:"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Password:"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(QLabel("Confirm Password:"))
        form_layout.addWidget(self.confirm_input)
        form_layout.addWidget(self.status_label)
        form_layout.addWidget(create_btn)
        layout.addWidget(form)

    def handle_setup(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password or not confirm:
            self.status_label.setText("Please complete all fields before continuing.")
            return
        if password != confirm:
            self.status_label.setText("Passwords do not match. Please try again.")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        valid, msg = self.auth_service.validate_password(password)
        if not valid:
            self.status_label.setText(msg)
            self.password_input.clear()
            self.confirm_input.clear()
            self.password_input.setFocus()
            return

        success, msg = self.auth_service.create_admin_user(username, password)
        if success:
            self.status_label.setText("Administrator account created successfully.")
            self.setup_completed.emit()
        else:
            self.status_label.setText(msg)


class ForcedPasswordChangeDialog(QWidget):
    change_completed = Signal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.username = ""
        self.init_ui()

    def init_ui(self):
        self.setObjectName("ForcedPasswordChange")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        # Header with Logo Badge
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
        subtitle = QLabel("Your account credentials must be updated before continuing.")
        subtitle.setProperty("class", "PageSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_row.addLayout(title_col)
        layout.addLayout(header_row)

        message = QLabel(
            "Enter your current temporary password and select a new secure password."
        )
        message.setWordWrap(True)
        message.setProperty("class", "BodyText")
        layout.addWidget(message)

        self.current_input = QLineEdit()
        self.current_input.setEchoMode(QLineEdit.Password)
        self.current_input.setPlaceholderText("Current password")
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        self.new_input.setPlaceholderText("New password (min. 4 characters)")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirm new password")
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 500;")

        change_button = QPushButton("Update Password & Continue")
        change_button.setProperty("class", "PrimaryButton")
        change_button.setCursor(Qt.PointingHandCursor)
        change_button.setFixedHeight(46)
        change_button.clicked.connect(self.handle_change)
        self.confirm_input.returnPressed.connect(self.handle_change)

        for field in (self.current_input, self.new_input, self.confirm_input):
            field.setFixedHeight(42)
            layout.addWidget(field)
        layout.addWidget(self.status_label)
        layout.addWidget(change_button)

    def set_username(self, username: str):
        self.username = username
        self.current_input.clear()
        self.new_input.clear()
        self.confirm_input.clear()
        self.status_label.clear()
        self.current_input.setFocus()

    def handle_change(self):
        current = self.current_input.text()
        new_password = self.new_input.text()
        confirmation = self.confirm_input.text()
        if not current or not new_password or not confirmation:
            self.status_label.setText("Complete all password fields before continuing.")
            return
        if not self.auth_service.verify_current_password(self.username, current):
            self.status_label.setText("The current password is incorrect.")
            self.current_input.clear()
            self.current_input.setFocus()
            return
        if new_password != confirmation:
            self.status_label.setText("The new passwords do not match.")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        success, message = self.auth_service.change_password(self.username, current, new_password)
        if success:
            self.change_completed.emit()
        else:
            self.status_label.setText(message)
            self.new_input.clear()
            self.confirm_input.clear()
            self.new_input.setFocus()


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
        self.resize(440, 580)
        self.setMinimumSize(440, 580)
        self.setMaximumSize(520, 640)
        self.setObjectName("LoginWindow")

        # Set Window Icon
        icon_path = get_asset_path("assets/branding/app_icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.stack = QStackedWidget(self)
        self.stack.setObjectName("AuthStack")

        self.login_card = QFrame()
        self.login_card.setObjectName("LoginCard")
        self.login_layout = QVBoxLayout(self.login_card)
        self.login_layout.setContentsMargins(35, 35, 35, 35)
        self.login_layout.setSpacing(12)

        # 1. Custom Brand Emblem Header
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = get_asset_path("assets/branding/app_logo.png")
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
            logo_label.setFixedHeight(80)
        else:
            logo_label.setText("SMS")
            logo_label.setObjectName("LoginLogo")

        subtitle_label = QLabel("Student Management System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("LoginSubtitle")

        edition_label = QLabel("Windows Desktop Edition  •  Administrator Sign In")
        edition_label.setAlignment(Qt.AlignCenter)
        edition_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500; margin-bottom: 6px;")

        # 2. Form Inputs
        user_label = QLabel("Administrator Username")
        user_label.setProperty("class", "LoginFormLabel")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter administrator username...")
        self.username_input.setFixedHeight(44)

        pass_label = QLabel("Password")
        pass_label.setProperty("class", "LoginFormLabel")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password...")
        self.password_input.setFixedHeight(44)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 500;")
        self.error_label.setAlignment(Qt.AlignCenter)

        login_btn = QPushButton("Sign In")
        login_btn.setProperty("class", "PrimaryButton")
        login_btn.setFixedHeight(48)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)

        self.login_layout.addWidget(logo_label)
        self.login_layout.addWidget(subtitle_label)
        self.login_layout.addWidget(edition_label)
        self.login_layout.addWidget(user_label)
        self.login_layout.addWidget(self.username_input)
        self.login_layout.addWidget(pass_label)
        self.login_layout.addWidget(self.password_input)
        self.login_layout.addWidget(self.error_label)
        self.login_layout.addWidget(login_btn)

        self.setup_widget = SetupWizard(self.auth_service)
        self.setup_widget.setup_completed.connect(self.on_setup_completed)
        self.forced_change_widget = ForcedPasswordChangeDialog(self.auth_service)
        self.forced_change_widget.change_completed.connect(self.on_forced_change_completed)

        self.stack.addWidget(self.login_card)
        self.stack.addWidget(self.setup_widget)
        self.stack.addWidget(self.forced_change_widget)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
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
        self.error_label.setText("Password updated. Sign in with your new password.")
        self.show_login_view()

    def on_setup_completed(self):
        self.setup_completed.emit()
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setText("")
        self.show_login_view()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("Please fill in all security fields.")
            return

        login_status = self.auth_service.get_login_status(username, password)
        if login_status == "password_change_required":
            self.show_forced_change_view(username)
        elif login_status == "success":
            self.error_label.setText("")
            self.authenticated_username = username
            self.login_successful.emit()
        else:
            self.error_label.setText("Invalid username or password credentials.")
            self.password_input.clear()
            self.password_input.setFocus()
