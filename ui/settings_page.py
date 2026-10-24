# ui/settings_page.py
import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QGroupBox, 
                             QFormLayout, QFrame, QComboBox, QScrollArea,
                             QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSizePolicy)
from PySide6.QtCore import Qt
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
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Header Title
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title_label = QLabel("Settings")
        title_label.setProperty("class", "PageTitle")
        subtitle_label = QLabel("Configure access controls, view storage paths, and check application metadata.")
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
        content_layout.setContentsMargins(0, 0, 15, 0)
        content_layout.setSpacing(20)

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
        btn_change_pass.setFixedHeight(42)
        btn_change_pass.setCursor(Qt.PointingHandCursor)
        btn_change_pass.setProperty("class", "PrimaryButton")
        btn_change_pass.clicked.connect(self.handle_change_password)
        pass_layout.addRow("", btn_change_pass)

        content_layout.addWidget(pass_group)

        # 1.5 Appearance Settings Section
        appearance_group = QGroupBox("Appearance Settings")
        appearance_layout = QFormLayout(appearance_group)
        appearance_layout.setContentsMargins(15, 20, 15, 15)
        appearance_layout.setSpacing(12)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Day Mode", "Night Mode"])
        self.theme_combo.setFixedHeight(38)
        
        # Load currently saved theme
        saved_theme = self.settings_service.get_setting("theme", "day")
        if saved_theme == "night":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)
            
        self.theme_combo.currentIndexChanged.connect(self.handle_theme_change)
        appearance_layout.addRow("Application Theme:", self.theme_combo)

        content_layout.addWidget(appearance_group)

        # 1.6 Session Security Section
        security_group = QGroupBox("Session Security")
        security_layout = QFormLayout(security_group)
        security_layout.setContentsMargins(15, 20, 15, 15)
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
        self.lock_on_minimize_check = QCheckBox("Lock immediately when the application is minimized")
        self.lock_on_minimize_check.setChecked(
            self.settings_service.get_setting("lock_on_minimize", "0") == "1"
        )
        self.lock_on_minimize_check.toggled.connect(
            lambda checked: self.settings_service.set_setting("lock_on_minimize", "1" if checked else "0")
        )
        security_layout.addRow("Inactivity timeout:", self.lock_timeout_spin)
        security_layout.addRow("Minimize policy:", self.lock_on_minimize_check)
        content_layout.addWidget(security_group)

        # 2. System Storage Locations Info Section
        storage_group = QGroupBox("Database & Storage Paths")
        storage_layout = QFormLayout(storage_group)
        storage_layout.setContentsMargins(15, 20, 15, 15)
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
        storage_layout.addRow("Student Photos Location:", photos_path_lbl)

        content_layout.addWidget(storage_group)

        # 3. Application Metadata Section
        meta_group = QGroupBox("Application Information")
        meta_layout = QFormLayout(meta_group)
        meta_layout.setContentsMargins(15, 20, 15, 15)
        meta_layout.setSpacing(8)

        def add_info_row(label, val):
            lbl = QLabel(val)
            lbl.setProperty("class", "BodyText")
            meta_layout.addRow(label, lbl)
 
        add_info_row("Application Name:", "Student Management System (SMS)")
        add_info_row("Runtime Engine:", f"Python {sys.version.split()[0]}")
        add_info_row("User Interface Framework:", "PySide6 (Qt 6 for Python)")
        add_info_row("Database Engine:", "SQLite 3 (Local Offline Database)")
        add_info_row("Release Version:", "1.0.0 (Windows Desktop Native Edition)")
 
        content_layout.addWidget(meta_group)

        # 4. Security & Activity Audit Section
        audit_group = QGroupBox("Security and Activity Audit")
        audit_layout = QVBoxLayout(audit_group)
        audit_layout.setContentsMargins(15, 20, 15, 15)
        audit_layout.setSpacing(12)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        self.audit_filter = QLineEdit()
        self.audit_filter.setFixedHeight(38)
        self.audit_filter.setPlaceholderText("Filter by action type (e.g. login, create, export)...")
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
        self.audit_table.setMinimumHeight(220)
        
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
        for row_index, event in enumerate(events):
            values = [event["occurred_at_utc"], event.get("actor_username") or "system", event["action_type"], event.get("record_id") or "", event["summary_json"]]
            for column, value in enumerate(values):
                self.audit_table.setItem(row_index, column, QTableWidgetItem(str(value)))
