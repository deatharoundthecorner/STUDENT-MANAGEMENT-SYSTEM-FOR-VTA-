# ui/settings_page.py
import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QGroupBox, 
                             QFormLayout, QFrame)
from PySide6.QtCore import Qt
from services.auth_service import AuthService
from database.db import DatabaseManager
from services.photo_service import PhotoService

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.db_manager = DatabaseManager()
        self.photo_service = PhotoService()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header Title
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title_label = QLabel("Settings")
        title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #1E2A38;")
        subtitle_label = QLabel("Configure access controls, view storage paths, and check application metadata.")
        subtitle_label.setStyleSheet("font-size: 13px; color: #64748B;")
        title_block.addWidget(title_label)
        title_block.addWidget(subtitle_label)
        main_layout.addLayout(title_block)

        # 1. Change Password Section
        pass_group = QGroupBox("Change Administrator Password")
        pass_layout = QFormLayout(pass_group)
        pass_layout.setContentsMargins(15, 20, 15, 15)
        pass_layout.setSpacing(10)

        self.input_curr_pass = QLineEdit()
        self.input_curr_pass.setEchoMode(QLineEdit.Password)
        self.input_curr_pass.setPlaceholderText("Enter current administrator password")
        self.input_curr_pass.setFixedHeight(42)
        
        self.input_new_pass = QLineEdit()
        self.input_new_pass.setEchoMode(QLineEdit.Password)
        self.input_new_pass.setPlaceholderText("Enter new password (min. 4 characters)")
        self.input_new_pass.setFixedHeight(42)

        self.input_conf_pass = QLineEdit()
        self.input_conf_pass.setEchoMode(QLineEdit.Password)
        self.input_conf_pass.setPlaceholderText("Re-type new password to verify")
        self.input_conf_pass.setFixedHeight(42)

        pass_layout.addRow("Current Password:", self.input_curr_pass)
        pass_layout.addRow("New Password:", self.input_new_pass)
        pass_layout.addRow("Confirm Password:", self.input_conf_pass)

        btn_change_pass = QPushButton("Update Password")
        btn_change_pass.setFixedHeight(46)
        btn_change_pass.setCursor(Qt.PointingHandCursor)
        btn_change_pass.setStyleSheet("""
            QPushButton {
                background-color: #1E2A38; color: white; border: none; border-radius: 6px; padding: 0px 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2D3E50; }
        """)
        btn_change_pass.clicked.connect(self.handle_change_password)
        pass_layout.addRow("", btn_change_pass)

        main_layout.addWidget(pass_group)

        # 2. System Storage Locations Info Section
        storage_group = QGroupBox("Database & Storage Paths")
        storage_layout = QFormLayout(storage_group)
        storage_layout.setContentsMargins(15, 20, 15, 15)
        storage_layout.setSpacing(12)

        db_path_lbl = QLineEdit(str(self.db_manager.get_db_path()))
        db_path_lbl.setReadOnly(True)
        db_path_lbl.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; color: #475569;")
        storage_layout.addRow("SQLite Database Location:", db_path_lbl)

        photos_path_lbl = QLineEdit(self.photo_service.get_photos_dir_path())
        photos_path_lbl.setReadOnly(True)
        photos_path_lbl.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; color: #475569;")
        storage_layout.addRow("Student Photos Location:", photos_path_lbl)

        main_layout.addWidget(storage_group)

        # 3. Application Metadata Section
        meta_group = QGroupBox("Application Information")
        meta_layout = QFormLayout(meta_group)
        meta_layout.setContentsMargins(15, 20, 15, 15)
        meta_layout.setSpacing(8)

        def add_info_row(label, val):
            lbl = QLabel(val)
            lbl.setStyleSheet("color: #1E293B; font-weight: 500;")
            meta_layout.addRow(label, lbl)

        add_info_row("Application Name:", "Student Management System (SMS)")
        add_info_row("Runtime Engine:", f"Python {sys.version.split()[0]}")
        add_info_row("User Interface Framework:", "PySide6 (Qt 6 for Python)")
        add_info_row("Database Engine:", "SQLite 3 (Local Offline Database)")
        add_info_row("Release Version:", "1.0.0 (Windows Desktop Native Edition)")

        main_layout.addWidget(meta_group)
        main_layout.addStretch(1)

    def handle_change_password(self):
        curr_pass = self.input_curr_pass.text()
        new_pass = self.input_new_pass.text()
        conf_pass = self.input_conf_pass.text()

        if not curr_pass or not new_pass or not conf_pass:
            QMessageBox.warning(self, "Validation Error", "All password fields are required.")
            return

        if new_pass != conf_pass:
            QMessageBox.warning(self, "Validation Error", "New password and confirmation password do not match.")
            self.input_conf_pass.clear()
            self.input_conf_pass.setFocus()
            return

        success, msg = self.auth_service.change_password("admin", curr_pass, new_pass)
        if success:
            QMessageBox.information(self, "Success", "Administrator password updated successfully!")
            self.input_curr_pass.clear()
            self.input_new_pass.clear()
            self.input_conf_pass.clear()
        else:
            QMessageBox.warning(self, "Failed", f"Failed to update password:\n{msg}")
            self.input_curr_pass.clear()
            self.input_curr_pass.setFocus()
