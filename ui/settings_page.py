# ui/settings_page.py
import sys
from PySide6.QtWidgets import (QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QGroupBox,
                             QFormLayout, QFrame, QComboBox, QScrollArea,
                             QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSizePolicy, QProgressBar)
from PySide6.QtCore import Qt, QSize
from ui.icons import get_icon, get_pixmap
from ui.widgets import PasswordLineEdit, FormLabel, StatusBanner
from services.audit_service import AuditService
from services.auth_service import AuthService
from database.db import DatabaseManager
from services.photo_service import PhotoService
from services.settings_service import SettingsService
from ui.styles import polish_widget


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.db_manager = DatabaseManager()
        self.photo_service = PhotoService()
        self.settings_service = SettingsService()
        self.audit_service = AuditService()
        self.authenticated_user = None
        self.init_ui()
        self.set_authenticated_user(None)

    def set_authenticated_user(self, username: str):
        """Injects authenticated administrator identity into the settings page."""
        self.authenticated_user = username or None
        if self.authenticated_user:
            self.lbl_auth_status.setText(f"Active Account: <b>{self.authenticated_user}</b> (Administrator)")
            self.lbl_auth_status.setStyleSheet("color: #059669; font-size: 12px; font-weight: 600;")
            self.input_curr_pass.setEnabled(True)
            self.input_new_pass.setEnabled(True)
            self.input_conf_pass.setEnabled(True)
            self.btn_change_pass.setEnabled(True)
        else:
            self.lbl_auth_status.setText("No authenticated administrator session active.")
            self.lbl_auth_status.setStyleSheet("color: #DC2626; font-size: 12px; font-weight: 500;")
            self.input_curr_pass.setEnabled(False)
            self.input_new_pass.setEnabled(False)
            self.input_conf_pass.setEnabled(False)
            self.btn_change_pass.setEnabled(False)
            self.input_curr_pass.clear()
            self.input_new_pass.clear()
            self.input_conf_pass.clear()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(14)

        # Header Title
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        title_label = QLabel("Settings & Access Control")
        title_label.setProperty("class", "PageTitle")
        subtitle_label = QLabel("Manage administrator credentials, customize appearance, configure session lock, and review audit events.")
        subtitle_label.setProperty("class", "PageSubtitle")
        title_block.addWidget(title_label)
        title_block.addWidget(subtitle_label)
        main_layout.addLayout(title_block)

        # Scroll area to handle smaller screens cleanly
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 16, 0)
        content_layout.setSpacing(18)

        # 1. Account & Security Section
        pass_group = QGroupBox("Account & Security — Administrator Password")
        pass_layout = QVBoxLayout(pass_group)
        pass_layout.setContentsMargins(20, 20, 20, 20)
        pass_layout.setSpacing(14)

        self.lbl_auth_status = QLabel("Active Account: Checking session...")
        self.lbl_auth_status.setStyleSheet("color: #64748B; font-size: 12px;")
        pass_layout.addWidget(self.lbl_auth_status)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        # Current password
        form_layout.addWidget(FormLabel("Current Password", required=True))
        self.input_curr_pass = PasswordLineEdit("Enter current administrator password")
        self.input_curr_pass.setFixedHeight(38)
        form_layout.addWidget(self.input_curr_pass)

        # New password
        form_layout.addWidget(FormLabel("New Password", required=True))
        self.input_new_pass = PasswordLineEdit("Enter new password (minimum 8 characters)")
        self.input_new_pass.setFixedHeight(38)
        form_layout.addWidget(self.input_new_pass)

        # Password Strength Bar
        strength_container = QWidget()
        strength_layout = QVBoxLayout(strength_container)
        strength_layout.setContentsMargins(0, 0, 0, 0)
        strength_layout.setSpacing(4)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setProperty("class", "PasswordStrengthBar")

        self.lbl_strength_text = QLabel("Password strength: Minimum 8 characters with letters and numbers/symbols.")
        self.lbl_strength_text.setStyleSheet("color: #64748B; font-size: 11px;")

        strength_layout.addWidget(self.strength_bar)
        strength_layout.addWidget(self.lbl_strength_text)
        form_layout.addWidget(strength_container)

        # Confirm password
        form_layout.addWidget(FormLabel("Confirm New Password", required=True))
        self.input_conf_pass = PasswordLineEdit("Re-type new password to confirm")
        self.input_conf_pass.setFixedHeight(38)
        form_layout.addWidget(self.input_conf_pass)

        pass_layout.addLayout(form_layout)

        # Password Policy Explanation Note
        policy_note = QLabel(
            "<b>Policy:</b> Minimum 8 characters. Must contain both letters and numbers or symbols "
            "(passphrases of 15+ characters do not require numbers/symbols). "
            "Passwords cannot start or end with spaces. Common guessable passwords are prohibited."
        )
        policy_note.setWordWrap(True)
        policy_note.setStyleSheet("color: #64748B; font-size: 11px; line-height: 1.4;")
        pass_layout.addWidget(policy_note)

        self.btn_change_pass = QPushButton("Update Administrator Password")
        self.btn_change_pass.setFixedHeight(40)
        self.btn_change_pass.setCursor(Qt.PointingHandCursor)
        self.btn_change_pass.setProperty("class", "PrimaryButton")
        self.btn_change_pass.clicked.connect(self.handle_change_password)
        pass_layout.addWidget(self.btn_change_pass)

        self.input_new_pass.textChanged.connect(self.on_new_password_changed)

        content_layout.addWidget(pass_group)

        # 2. Appearance Settings Section
        appearance_group = QGroupBox("Appearance & Display Theme")
        appearance_layout = QFormLayout(appearance_group)
        appearance_layout.setContentsMargins(20, 20, 20, 20)
        appearance_layout.setSpacing(12)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Day Mode (Clean Institutional Light)", "Night Mode (Deep Slate Institutional Dark)"])
        self.theme_combo.setFixedHeight(38)

        saved_theme = self.settings_service.get_setting("theme", "day")
        if saved_theme.lower() == "night":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)

        self.theme_combo.currentIndexChanged.connect(self.handle_theme_change)
        appearance_layout.addRow("Color Theme:", self.theme_combo)

        content_layout.addWidget(appearance_group)

        # 3. Session Security Section
        security_group = QGroupBox("Session Inactivity Lock")
        security_layout = QFormLayout(security_group)
        security_layout.setContentsMargins(20, 20, 20, 20)
        security_layout.setSpacing(12)

        self.lock_timeout_spin = QSpinBox()
        self.lock_timeout_spin.setRange(1, 120)
        self.lock_timeout_spin.setFixedHeight(38)
        self.lock_timeout_spin.setSuffix(" minutes")
        timeout_minutes = int(self.settings_service.get_setting("lock_timeout_seconds", "900")) // 60
        self.lock_timeout_spin.setValue(max(1, timeout_minutes))
        self.lock_timeout_spin.valueChanged.connect(
            lambda value: self.settings_service.set_setting("lock_timeout_seconds", str(value * 60))
        )
        self.lock_on_minimize_check = QCheckBox("Lock application immediately upon window minimization")
        self.lock_on_minimize_check.setChecked(
            self.settings_service.get_setting("lock_on_minimize", "0") == "1"
        )
        self.lock_on_minimize_check.toggled.connect(
            lambda checked: self.settings_service.set_setting("lock_on_minimize", "1" if checked else "0")
        )
        security_layout.addRow("Inactivity Timeout:", self.lock_timeout_spin)
        security_layout.addRow("Window Minimize Policy:", self.lock_on_minimize_check)
        content_layout.addWidget(security_group)

        # 4. System Storage Locations Info Section
        storage_group = QGroupBox("Database & Local Storage Directory")
        storage_layout = QFormLayout(storage_group)
        storage_layout.setContentsMargins(20, 20, 20, 20)
        storage_layout.setSpacing(12)

        db_path_lbl = QLineEdit(str(self.db_manager.get_db_path()))
        db_path_lbl.setReadOnly(True)
        db_path_lbl.setFixedHeight(38)
        db_path_lbl.setProperty("class", "ReadOnlyPath")
        storage_layout.addRow("SQLite Database Location:", db_path_lbl)

        photos_path_lbl = QLineEdit(self.photo_service.get_photos_dir_path())
        photos_path_lbl.setReadOnly(True)
        photos_path_lbl.setFixedHeight(38)
        photos_path_lbl.setProperty("class", "ReadOnlyPath")
        storage_layout.addRow("Student Photos Repository:", photos_path_lbl)

        content_layout.addWidget(storage_group)

        # 5. Application Metadata Section
        meta_group = QGroupBox("System Information")
        meta_layout = QFormLayout(meta_group)
        meta_layout.setContentsMargins(20, 20, 20, 20)
        meta_layout.setSpacing(8)

        def add_info_row(label, val):
            lbl = QLabel(val)
            lbl.setProperty("class", "BodyText")
            meta_layout.addRow(label, lbl)

        add_info_row("Application Name:", "Student Management System (SMS)")
        add_info_row("Runtime Engine:", f"Python {sys.version.split()[0]}")
        add_info_row("User Interface Framework:", "PySide6 (Qt 6 for Python)")
        add_info_row("Database Engine:", "SQLite 3 (Local Encrypted/Sanitized Offline Database)")
        self.lbl_release_version = QLabel("1.1.1 (Windows Desktop Native Edition)")
        self.lbl_release_version.setProperty("class", "BodyText")
        meta_layout.addRow("Release Version:", self.lbl_release_version)

        content_layout.addWidget(meta_group)

        # 6. Security & Activity Audit Section
        audit_group = QGroupBox("Security and Activity Audit Log")
        audit_layout = QVBoxLayout(audit_group)
        audit_layout.setContentsMargins(20, 20, 20, 20)
        audit_layout.setSpacing(12)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.audit_filter = QLineEdit()
        self.audit_filter.setFixedHeight(38)
        self.audit_filter.setPlaceholderText("Filter audit events by action type (e.g. login, create, export, password)...")
        self.audit_filter.returnPressed.connect(self.refresh_audit_events)

        refresh_audit = QPushButton("Refresh Events")
        refresh_audit.setFixedHeight(38)
        refresh_audit.setCursor(Qt.PointingHandCursor)
        refresh_audit.setProperty("class", "SecondaryButton")
        refresh_audit.clicked.connect(self.refresh_audit_events)

        filter_row.addWidget(self.audit_filter, 1)
        filter_row.addWidget(refresh_audit)
        audit_layout.addLayout(filter_row)

        self.audit_table = QTableWidget(0, 5)
        self.audit_table.setHorizontalHeaderLabels(["UTC Time", "User", "Action", "Record ID", "Summary Details"])
        self.audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.audit_table.setAlternatingRowColors(True)
        self.audit_table.verticalHeader().setVisible(False)
        self.audit_table.setMinimumHeight(240)

        aud_header = self.audit_table.horizontalHeader()
        aud_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        aud_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        aud_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        aud_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        aud_header.setSectionResizeMode(4, QHeaderView.Stretch)

        audit_layout.addWidget(self.audit_table)
        content_layout.addWidget(audit_group)

        self.refresh_audit_events()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def on_new_password_changed(self, text: str):
        """Calculates and renders live password strength feedback."""
        if not text:
            self.strength_bar.setValue(0)
            self.strength_bar.setStyleSheet("")
            self.lbl_strength_text.setText("Password strength: Enter password")
            self.lbl_strength_text.setStyleSheet("color: #64748B; font-size: 11px;")
            return

        if text.strip() != text:
            self.strength_bar.setValue(20)
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #DC2626; }")
            self.lbl_strength_text.setText("Password strength: Cannot begin or end with spaces")
            self.lbl_strength_text.setStyleSheet("color: #DC2626; font-size: 11px; font-weight: 600;")
        elif len(text) < 8:
            self.strength_bar.setValue(20)
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #DC2626; }")
            self.lbl_strength_text.setText("Password strength: Too short (minimum 8 characters)")
            self.lbl_strength_text.setStyleSheet("color: #DC2626; font-size: 11px; font-weight: 600;")
        elif text.lower() in AuthService.COMMON_PASSWORDS:
            self.strength_bar.setValue(25)
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #DC2626; }")
            self.lbl_strength_text.setText("Password strength: Common guessable password (rejected)")
            self.lbl_strength_text.setStyleSheet("color: #DC2626; font-size: 11px; font-weight: 600;")
        elif len(text) >= 15:
            self.strength_bar.setValue(100)
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #059669; }")
            self.lbl_strength_text.setText("Password strength: Excellent passphrase (15+ characters)")
            self.lbl_strength_text.setStyleSheet("color: #059669; font-size: 11px; font-weight: 600;")
        elif any(c.isalpha() for c in text) and any(not c.isalpha() for c in text):
            if len(text) >= 12:
                self.strength_bar.setValue(75)
                self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #2563EB; }")
                self.lbl_strength_text.setText("Password strength: Strong")
                self.lbl_strength_text.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: 600;")
            else:
                self.strength_bar.setValue(50)
                self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #D97706; }")
                self.lbl_strength_text.setText("Password strength: Medium (meets minimum requirements)")
                self.lbl_strength_text.setStyleSheet("color: #D97706; font-size: 11px; font-weight: 600;")
        else:
            self.strength_bar.setValue(35)
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #D97706; }")
            self.lbl_strength_text.setText("Password strength: Needs letters and numbers or symbols")
            self.lbl_strength_text.setStyleSheet("color: #D97706; font-size: 11px; font-weight: 600;")

    def handle_change_password(self):
        if not self.authenticated_user:
            self.btn_change_pass.setEnabled(False)
            self.input_curr_pass.setEnabled(False)
            self.input_new_pass.setEnabled(False)
            self.input_conf_pass.setEnabled(False)
            QMessageBox.warning(self, "Session Error", "No active authenticated administrator session.\nPlease log in again.")
            return

        self.btn_change_pass.setEnabled(False)
        self.btn_change_pass.setText("Updating Password...")
        QApplication.processEvents()
        try:
            self._execute_change_password()
        finally:
            self.btn_change_pass.setEnabled(True)
            self.btn_change_pass.setText("Update Administrator Password")

    def _execute_change_password(self):

        curr_pass = self.input_curr_pass.text()
        new_pass = self.input_new_pass.text()
        conf_pass = self.input_conf_pass.text()

        if not curr_pass or not new_pass or not conf_pass:
            QMessageBox.warning(self, "Validation Error", "All password fields are required.")
            return

        if curr_pass == new_pass:
            QMessageBox.warning(self, "Validation Error", "New password cannot be the same as the current password.")
            self.input_new_pass.clear()
            self.input_conf_pass.clear()
            self.input_new_pass.setFocus()
            return

        if new_pass != conf_pass:
            QMessageBox.warning(self, "Validation Error", "New password and confirmation password do not match.")
            self.input_conf_pass.clear()
            self.input_conf_pass.setFocus()
            return

        success, msg = self.auth_service.change_password(self.authenticated_user, curr_pass, new_pass)
        if success:
            QMessageBox.information(
                self, "Success",
                "Administrator password updated successfully!\nPlease use your new password the next time you sign in."
            )
            self.input_curr_pass.clear()
            self.input_new_pass.clear()
            self.input_conf_pass.clear()
            self.strength_bar.setValue(0)
            self.lbl_strength_text.setText("Password strength: Enter password")
            self.refresh_audit_events()
        else:
            QMessageBox.warning(self, "Failed", f"Failed to update password:\n{msg}")
            self.input_curr_pass.clear()
            self.input_curr_pass.setFocus()

    def handle_theme_change(self, index):
        theme_name = "night" if index == 1 else "day"
        self.settings_service.set_setting("theme", theme_name)

        # Apply theme instantly
        from ui.styles import apply_theme
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            apply_theme(app, theme_name)

        main_win = self.window()
        if main_win:
            main_win.style().unpolish(main_win)
            main_win.style().polish(main_win)
            if hasattr(main_win, "sync_theme_toggle_button"):
                main_win.sync_theme_toggle_button(theme_name)

    def refresh_audit_events(self):
        events = self.audit_service.list_events(self.audit_filter.text().strip())
        self.audit_table.setRowCount(len(events))
        for row, ev in enumerate(events):
            time_item = QTableWidgetItem(ev.get("occurred_at_utc", ""))
            user_item = QTableWidgetItem(ev.get("actor_username", "") or "System")
            action_item = QTableWidgetItem(ev.get("action_type", ""))
            rec_item = QTableWidgetItem(str(ev.get("record_id", "") or "-"))
            summary_item = QTableWidgetItem(ev.get("summary_json", ""))

            self.audit_table.setItem(row, 0, time_item)
            self.audit_table.setItem(row, 1, user_item)
            self.audit_table.setItem(row, 2, action_item)
            self.audit_table.setItem(row, 3, rec_item)
            self.audit_table.setItem(row, 4, summary_item)
