# ui/import_page.py
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QTextEdit, QFrame, QScrollArea)
from PySide6.QtCore import Qt
from services.import_service import ImportService
from services.student_service import StudentService

class ImportPage(QWidget):
    def __init__(self):
        super().__init__()
        self.import_service = ImportService()
        self.student_service = StudentService()
        self.selected_file_path = ""
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header Title
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title_label = QLabel("Import Student Records")
        title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #1E2A38;")
        subtitle_label = QLabel("Batch upload student data from CSV or Microsoft Excel spreadsheets.")
        subtitle_label.setStyleSheet("font-size: 13px; color: #64748B;")
        title_block.addWidget(title_label)
        title_block.addWidget(subtitle_label)
        main_layout.addLayout(title_block)

        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 15, 0)
        layout.setSpacing(20)

        # 1. Column Explanations & Templates Download Card
        template_card = QFrame()
        template_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(template_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)

        desc_lbl = QLabel(
            "<b>Guidelines:</b><br>"
            "1. Upload files in <b>.csv</b> or <b>.xlsx</b> format.<br>"
            "2. Required columns: <b>ID_NUMBER</b>, <b>NAME_OF_THE_STUDENT</b>.<br>"
            "3. Status dropdowns (Drop Out, Theory Pass, NVQ) accept values: <i>Yes, No, Pending, Not Applicable</i>.<br>"
            "4. Student IDs that already exist in the database will be skipped automatically to prevent duplicates."
        )
        desc_lbl.setStyleSheet("line-height: 1.4; color: #475569; font-size: 13px;")
        card_layout.addWidget(desc_lbl)

        # Download buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        csv_temp_btn = QPushButton("Download CSV Template")
        csv_temp_btn.setCursor(Qt.PointingHandCursor)
        csv_temp_btn.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0; color: #475569; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #CBD5E1; }
        """)
        csv_temp_btn.clicked.connect(lambda: self.download_template("csv"))
        
        excel_temp_btn = QPushButton("Download Excel Template")
        excel_temp_btn.setCursor(Qt.PointingHandCursor)
        excel_temp_btn.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0; color: #475569; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #CBD5E1; }
        """)
        excel_temp_btn.clicked.connect(lambda: self.download_template("xlsx"))

        btn_layout.addWidget(csv_temp_btn)
        btn_layout.addWidget(excel_temp_btn)
        btn_layout.addStretch(1)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(template_card)

        # 2. File Selection Panel
        file_panel = QHBoxLayout()
        self.file_label = QLabel("No file selected. Please select a spreadsheet...")
        self.file_label.setStyleSheet("""
            padding: 10px; background-color: #E2E8F0; border: 1px dashed #CBD5E1; border-radius: 6px; color: #64748B; font-style: italic;
        """)
        file_panel.addWidget(self.file_label, 1)

        select_btn = QPushButton("Select File")
        select_btn.setCursor(Qt.PointingHandCursor)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E2A38; color: white; border: none; border-radius: 6px; padding: 10px 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2D3E50; }
        """)
        select_btn.clicked.connect(self.select_file)
        file_panel.addWidget(select_btn)

        layout.addLayout(file_panel)

        # 3. Data Preview Grid
        self.preview_title = QLabel("Spreadsheet Preview (First 10 rows)")
        self.preview_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E2A38;")
        self.preview_title.setVisible(False)
        layout.addWidget(self.preview_title)

        self.preview_table = QTableWidget()
        self.preview_table.setFixedHeight(200)
        self.preview_table.setVisible(False)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.verticalHeader().setVisible(False)
        layout.addWidget(self.preview_table)

        # 4. Action Row for committing import
        self.commit_btn = QPushButton("Process Data Import")
        self.commit_btn.setEnabled(False)
        self.commit_btn.setCursor(Qt.PointingHandCursor)
        self.commit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6; color: white; border: none; border-radius: 6px; padding: 12px 24px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #2563EB; }
            QPushButton:disabled { background-color: #93C5FD; color: #E0F2FE; }
        """)
        self.commit_btn.clicked.connect(self.process_import)
        layout.addWidget(self.commit_btn, alignment=Qt.AlignLeft)

        # 5. Results Report Frame (Success / Skipped / Failed Counts)
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
            }
        """)
        self.results_frame.setVisible(False)
        res_layout = QVBoxLayout(self.results_frame)
        res_layout.setContentsMargins(15, 15, 15, 15)
        res_layout.setSpacing(10)

        res_title = QLabel("Import Summary Results")
        res_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E2A38;")
        res_layout.addWidget(res_title)

        counts_layout = QHBoxLayout()
        self.lbl_success = QLabel("Success: 0")
        self.lbl_success.setStyleSheet("color: #10B981; font-weight: bold; font-size: 14px;")
        self.lbl_skipped = QLabel("Skipped (Duplicates): 0")
        self.lbl_skipped.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 14px;")
        self.lbl_failed = QLabel("Failed (Errors): 0")
        self.lbl_failed.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 14px;")

        counts_layout.addWidget(self.lbl_success)
        counts_layout.addWidget(self.lbl_skipped)
        counts_layout.addWidget(self.lbl_failed)
        res_layout.addLayout(counts_layout)

        self.error_log = QTextEdit()
        self.error_log.setReadOnly(True)
        self.error_log.setFixedHeight(150)
        self.error_log.setStyleSheet("background-color: #F8FAFC; border: 1px solid #CBD5E1; color: #E11D48; font-family: Consolas, monospace;")
        res_layout.addWidget(self.error_log)
        
        layout.addWidget(self.results_frame)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Spreadsheet File", "",
            "Spreadsheets (*.csv *.xlsx *.xls)"
        )
        if not file_path:
            return

        self.selected_file_path = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.file_label.setStyleSheet("padding: 10px; background-color: #EFF6FF; border: 1.5px solid #3B82F6; border-radius: 6px; color: #1E293B; font-weight: bold;")
        
        # Load Preview
        headers, rows, error = self.import_service.preview_file(file_path)
        if error:
            QMessageBox.warning(self, "Preview Error", error)
            self.commit_btn.setEnabled(False)
            self.preview_table.setVisible(False)
            self.preview_title.setVisible(False)
            return

        # Populating preview table
        self.preview_table.blockSignals(True)
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(len(headers))
        self.preview_table.setHorizontalHeaderLabels(headers)
        
        for r_data in rows:
            row_idx = self.preview_table.rowCount()
            self.preview_table.insertRow(row_idx)
            for c_idx, val in enumerate(r_data):
                self.preview_table.setItem(row_idx, c_idx, QTableWidgetItem(str(val)))
                
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.preview_table.blockSignals(False)

        # Show table
        self.preview_table.setVisible(True)
        self.preview_title.setVisible(True)
        self.commit_btn.setEnabled(True)
        self.results_frame.setVisible(False)

    def process_import(self):
        if not self.selected_file_path:
            return
            
        self.commit_btn.setEnabled(False)
        self.commit_btn.setText("Importing records...")
        
        # Process in service
        stats = self.import_service.import_file(self.selected_file_path)
        
        self.commit_btn.setEnabled(True)
        self.commit_btn.setText("Process Data Import")

        # Update UI results
        self.lbl_success.setText(f"Successfully Imported: {stats['success']}")
        self.lbl_skipped.setText(f"Skipped (Existing IDs): {stats['skipped']}")
        self.lbl_failed.setText(f"Failed (Validation Errors): {stats['failed']}")
        
        if stats["errors"]:
            self.error_log.setText("\n".join(stats["errors"]))
            self.error_log.setVisible(True)
        else:
            self.error_log.setText("All columns parsed without critical formatting issues.")
            
        self.results_frame.setVisible(True)
        
        QMessageBox.information(
            self, "Import Completed", 
            f"Import summary:\n- Success: {stats['success']}\n- Skipped: {stats['skipped']}\n- Failed: {stats['failed']}"
        )
        
        # Refresh parent main window references if they are active
        main_win = self.window()
        if hasattr(main_win, "refresh_all_data"):
            main_win.refresh_all_data()

    def download_template(self, file_format: str):
        default_name = "student_import_template.csv" if file_format == "csv" else "student_import_template.xlsx"
        filter_str = "CSV File (*.csv)" if file_format == "csv" else "Excel File (*.xlsx)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Download Import Template", default_name, filter_str
        )
        
        if file_path:
            try:
                self.import_service.generate_template(file_path, file_format)
                QMessageBox.information(self, "Success", "Import template saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save template:\n{str(e)}")
