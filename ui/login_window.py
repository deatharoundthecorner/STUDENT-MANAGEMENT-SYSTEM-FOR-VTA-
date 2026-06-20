# ui/login_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from services.auth_service import AuthService

class LoginWindow(QWidget):
    login_successful = Signal()

    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SMS - System Login")
        self.resize(400, 500)
        self.setMinimumSize(400, 500)
        self.setMaximumSize(450, 550)
        self.setStyleSheet("""
            QWidget#LoginWindow {
                background-color: #F1F5F9;
            }
        """)
        self.setObjectName("LoginWindow")

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Login Card (White Frame)
        card = QFrame()
        card.setStyleSheet("""
            QFrame#LoginCard {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        card.setObjectName("LoginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)

        # Title / Brand Logo Area
        logo_label = QLabel("SMS")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 32px;
            font-weight: 900;
            color: #1E2A38;
            margin-bottom: 2px;
        """)
        
        subtitle_label = QLabel("Student Management System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #64748B;
            margin-bottom: 20px;
        """)

        # Inputs Area
        user_label = QLabel("Administrator Username")
        user_label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username...")
        self.username_input.setText("admin") # Default text for convenience
        self.username_input.setFixedHeight(44)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 12px;
                padding-top: 0px;
                padding-bottom: 0px;
                font-size: 14px;
                selection-background-color: #3B82F6;
                selection-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #64748B;
            }
        """)

        pass_label = QLabel("Password")
        pass_label.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password...")
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding-left: 12px;
                padding-right: 12px;
                padding-top: 0px;
                padding-bottom: 0px;
                font-size: 14px;
                selection-background-color: #3B82F6;
                selection-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #64748B;
            }
        """)

        # Error text holder
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 500;")
        self.error_label.setAlignment(Qt.AlignCenter)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(50)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E2A38;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 0px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2D3E50;
            }
            QPushButton:pressed {
                background-color: #151F2A;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)

        # Helper text for default credentials
        helper_label = QLabel("Default login: admin / admin123")
        helper_label.setAlignment(Qt.AlignCenter)
        helper_label.setStyleSheet("""
            font-size: 11px;
            color: #64748B;
            margin-top: 10px;
        """)

        # Build card
        card_layout.addWidget(logo_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addWidget(user_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(pass_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(helper_label)

        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("Please fill in all security fields.")
            return

        # Authenticate
        is_auth = self.auth_service.authenticate(username, password)
        if is_auth:
            self.error_label.setText("")
            self.login_successful.emit()
        else:
            self.error_label.setText("Invalid username or password credentials.")
            self.password_input.clear()
            self.password_input.setFocus()
