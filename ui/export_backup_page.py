# ui/export_backup_page.py
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QMessageBox, QGroupBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                             QSizePolicy)
from PySide6.QtCore import Qt
from services.student_service import StudentService
from services.export_service import ExportService
from services.backup_service import BackupService
from ui.styles import polish_widget

class ExportBackupPage(QWidget):
    def __init__(self):
        super().__init__()
        self.student_service = StudentService()
        self.export_service = ExportService()
        self.backup_service = BackupService()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header Title
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title_label = QLabel("Export & System Backup")
        title_label.setProperty("class", "PageTitle")
        subtitle_label = QLabel("Export reports to standard formats and maintain system data backups.")
        subtitle_label.setProperty("class", "PageSubtitle")
        title_block.addWidget(title_label)
        title_block.addWidget(subtitle_label)
        main_layout.addLayout(title_block)

        # SECTION 1: Data Exports Box
        export_group = QGroupBox("Data Exports")
        export_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        export_layout = QVBoxLayout(export_group)
        export_layout.setContentsMargins(15, 20, 15, 15)
        export_layout.setSpacing(12)

        exp_desc = QLabel("Export all enrolled student records to spreadsheets or printer-friendly PDF summaries:")
        exp_desc.setProperty("class", "BodyText")
        export_layout.addWidget(exp_desc)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        excel_btn = QPushButton("Export to Excel (.xlsx)")
        excel_btn.setCursor(Qt.PointingHandCursor)
        excel_btn.setProperty("class", "SuccessButton")
        excel_btn.clicked.connect(lambda: self.handle_export("excel"))
        
        csv_btn = QPushButton("Export to CSV (.csv)")
        csv_btn.setCursor(Qt.PointingHandCursor)
        csv_btn.setProperty("class", "SuccessButton")
        csv_btn.clicked.connect(lambda: self.handle_export("csv"))

        pdf_btn = QPushButton("Export Summary PDF (.pdf)")
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.setProperty("class", "PrimaryButton")
        pdf_btn.clicked.connect(lambda: self.handle_export("pdf"))

        buttons_layout.addWidget(excel_btn)
        buttons_layout.addWidget(csv_btn)
        buttons_layout.addWidget(pdf_btn)
        buttons_layout.addStretch(1)
        export_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(export_group)

        # SECTION 2: System Backups Box
        backup_group = QGroupBox("System Backup & Restore")
        backup_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setContentsMargins(15, 20, 15, 15)
        backup_layout.setSpacing(12)

        backup_header = QHBoxLayout()
        back_desc = QLabel("Creates a single compressed ZIP archive containing the database records and student photos directory.")
        back_desc.setProperty("class", "BodyText")
        backup_header.addWidget(back_desc, 1)

        create_backup_btn = QPushButton("Create Full Backup")
        create_backup_btn.setCursor(Qt.PointingHandCursor)
        create_backup_btn.setProperty("class", "PrimaryButton")
        create_backup_btn.clicked.connect(self.create_backup)
        backup_header.addWidget(create_backup_btn)
        backup_layout.addLayout(backup_header)

        # Backup History Table
        history_title = QLabel("Available Restoration Snapshots:")
        history_title.setProperty("class", "SectionHeader")
        backup_layout.addWidget(history_title)

        self.table_backups = QTableWidget()
        self.table_backups.setColumnCount(4)
        self.table_backups.setHorizontalHeaderLabels(["Filename", "Creation Date", "File Size", "Actions"])
        self.table_backups.verticalHeader().setVisible(False)
        self.table_backups.setAlternatingRowColors(True)
        self.table_backups.setMinimumHeight(240)
        self.table_backups.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        header = self.table_backups.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_backups.setColumnWidth(3, 150)

        backup_layout.addWidget(self.table_backups)

        main_layout.addWidget(backup_group)

        # Load backup history
        self.refresh_backups()

    def handle_export(self, fmt: str):
        students = self.student_service.get_all_students()
        if not students:
            QMessageBox.warning(self, "No Data", "There are no student records in the database to export.")
            return

        if fmt == "excel":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to Excel", "student_records.xlsx", "Excel Spreadsheet (*.xlsx)"
            )
            if file_path:
                try:
                    self.export_service.export_to_excel(students, file_path)
                    QMessageBox.information(self, "Success", "Data exported to Excel successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Export Failed", f"Excel generation failed:\n{str(e)}")
        elif fmt == "csv":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to CSV", "student_records.csv", "CSV Delimited (*.csv)"
            )
            if file_path:
                try:
                    self.export_service.export_to_csv(students, file_path)
                    QMessageBox.information(self, "Success", "Data exported to CSV successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Export Failed", f"CSV generation failed:\n{str(e)}")
        elif fmt == "pdf":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Summary PDF", "student_records_report.pdf", "PDF Document (*.pdf)"
            )
            if file_path:
                try:
                    self.export_service.export_all_to_pdf(students, file_path)
                    QMessageBox.information(self, "Success", "Data summary PDF report exported successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Export Failed", f"PDF generation failed:\n{str(e)}")

    def create_backup(self):
        success, res = self.backup_service.create_backup()
        if success:
            QMessageBox.information(
                self, "Backup Complete", 
                f"Full backup archive generated successfully!\n\nSaved at:\n{res}"
            )
            self.refresh_backups()
        else:
            QMessageBox.warning(self, "Backup Failed", f"Backup failed:\n{res}")

    def refresh_backups(self):
        """Scans backups/ directory and populates UI table list."""
        backups = self.backup_service.list_backups()
        self.table_backups.setRowCount(0)
        
        for bk in backups:
            row_idx = self.table_backups.rowCount()
            self.table_backups.insertRow(row_idx)
            
            self.table_backups.setItem(row_idx, 0, QTableWidgetItem(bk["filename"]))
            self.table_backups.setItem(row_idx, 1, QTableWidgetItem(bk["date"]))
            self.table_backups.setItem(row_idx, 2, QTableWidgetItem(bk["size"]))
            
            # Action Column Widget
            restore_btn = QPushButton("Restore Backup")
            restore_btn.setCursor(Qt.PointingHandCursor)
            restore_btn.setProperty("path", bk["path"])
            restore_btn.setProperty("filename", bk["filename"])
            restore_btn.setProperty("class", "TableActionDelete")
            restore_btn.clicked.connect(self.restore_backup)
            polish_widget(restore_btn)
            
            container = QWidget()
            lay = QHBoxLayout(container)
            lay.setContentsMargins(5, 2, 5, 2)
            lay.addWidget(restore_btn)
            lay.setAlignment(Qt.AlignCenter)
            
            self.table_backups.setCellWidget(row_idx, 3, container)
            
        self.table_backups.resizeColumnToContents(1)
        self.table_backups.resizeColumnToContents(2)

    def restore_backup(self):
        btn = self.sender()
        if btn:
            backup_path = btn.property("path")
            filename = btn.property("filename")
            
            reply = QMessageBox.warning(
                self, "Confirm System Restoration",
                f"WARNING: You are about to restore the system state from snapshot '{filename}'.\n\n"
                "This action will OVERWRITE and REPLACE the active SQLite database and all photo files.\n"
                "Any current unsaved or imported data changes since this backup will be lost.\n\n"
                "Are you sure you want to proceed with the restore?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, msg = self.backup_service.restore_backup(backup_path)
                if success:
                    QMessageBox.information(
                        self, "System Restored",
                        f"Database records and photos have been rolled back successfully!\n\n{msg}"
                    )
                    
                    # Refresh UI components
                    main_win = self.window()
                    if hasattr(main_win, "refresh_all_data"):
                        main_win.refresh_all_data()
                else:
                    QMessageBox.critical(self, "Restoration Failed", f"An error occurred during restore:\n{msg}")
