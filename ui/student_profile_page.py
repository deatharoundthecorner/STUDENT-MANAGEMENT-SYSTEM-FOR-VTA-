# ui/student_profile_page.py
import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QFileDialog, QMessageBox, QGridLayout)
from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtCore import Qt, Signal
from services.student_service import StudentService
from services.photo_service import PhotoService
from services.export_service import ExportService

class StudentProfilePage(QWidget):
    back_requested = Signal()
    edit_requested = Signal(int) # Emits student DB ID

    def __init__(self):
        super().__init__()
        self.student_service = StudentService()
        self.photo_service = PhotoService()
        self.export_service = ExportService()
        
        self.current_student_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # 1. Header with back button
        header_layout = QHBoxLayout()
        back_btn = QPushButton(" Back to Students")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setProperty("class", "SecondaryButton")
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch(1)
        
        self.edit_btn = QPushButton(" Edit Profile")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setProperty("class", "TableActionEdit")
        self.edit_btn.clicked.connect(self.handle_edit)
        header_layout.addWidget(self.edit_btn)
        
        main_layout.addLayout(header_layout)

        # Scroll Area for Profile Body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        body_container = QWidget()
        body_layout = QVBoxLayout(body_container)
        body_layout.setContentsMargins(0, 0, 15, 0)
        body_layout.setSpacing(20)

        # 2. Main Profile Card (Photo + Basic Info side-by-side)
        profile_card = QFrame()
        profile_card.setProperty("class", "DashboardCard")
        card_layout = QHBoxLayout(profile_card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(30)

        # Photo Left
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 180)
        self.photo_label.setObjectName("PhotoPreviewFrame")
        self.photo_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.photo_label)

        # Info Right
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        self.lbl_name = QLabel("Student Name")
        self.lbl_name.setProperty("class", "PageTitle")
        info_layout.addWidget(self.lbl_name)

        # Grid for basic details
        details_grid = QGridLayout()
        details_grid.setSpacing(8)
        details_grid.setVerticalSpacing(6)

        def add_info_row(grid, row, label, val_widget):
            lbl = QLabel(label)
            lbl.setProperty("class", "CardTitle")
            grid.addWidget(lbl, row, 0)
            grid.addWidget(val_widget, row, 1)

        self.lbl_id = QLabel("-")
        self.lbl_id.setProperty("class", "ProfileValueStrong")
        self.lbl_year = QLabel("-")
        self.lbl_phone = QLabel("-")
        self.lbl_address = QLabel("-")
        self.lbl_address.setWordWrap(True)

        add_info_row(details_grid, 0, "ID NUMBER:", self.lbl_id)
        add_info_row(details_grid, 1, "REGISTERED YEAR:", self.lbl_year)
        add_info_row(details_grid, 2, "PHONE NUMBER:", self.lbl_phone)
        add_info_row(details_grid, 3, "PRIVATE ADDRESS:", self.lbl_address)
        
        details_grid.setColumnStretch(1, 1)
        info_layout.addLayout(details_grid)
        info_layout.addStretch(1)

        card_layout.addLayout(info_layout, 1)
        body_layout.addWidget(profile_card)

        # Helper to create styled sections
        def create_section_box(title):
            box = QFrame()
            box.setProperty("class", "DashboardCard")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(20, 20, 20, 20)
            box_layout.setSpacing(12)
            
            sec_title = QLabel(title)
            sec_title.setProperty("class", "SectionHeader")
            box_layout.addWidget(sec_title)
            
            grid = QGridLayout()
            grid.setSpacing(8)
            box_layout.addLayout(grid)
            return box, grid

        # 3. Academic Status Box
        acad_box, acad_grid = create_section_box("Academic & Training Milestones")
        self.lbl_dropout = QLabel("-")
        self.lbl_theory = QLabel("-")
        self.lbl_l3 = QLabel("-")
        self.lbl_l4 = QLabel("-")

        def style_status_lbl(lbl):
            lbl.setProperty("class", "StatusDefault")
        style_status_lbl(self.lbl_dropout)
        style_status_lbl(self.lbl_theory)
        style_status_lbl(self.lbl_l3)
        style_status_lbl(self.lbl_l4)

        add_info_row(acad_grid, 0, "Drop Out Status:", self.lbl_dropout)
        add_info_row(acad_grid, 1, "Theory Exam Pass:", self.lbl_theory)
        add_info_row(acad_grid, 2, "NVQ Level 3 Status:", self.lbl_l3)
        add_info_row(acad_grid, 3, "NVQ Level 4 Status:", self.lbl_l4)
        body_layout.addWidget(acad_box)

        # 4. OJT Box
        ojt_box, ojt_grid = create_section_box("On-the-Job Training (OJT) Placement")
        self.lbl_ojt_place = QLabel("-")
        self.lbl_ojt_phone = QLabel("-")
        self.lbl_ojt_address = QLabel("-")
        self.lbl_ojt_address.setWordWrap(True)

        # Status styling is handled dynamically via PageTheme properties

        add_info_row(ojt_grid, 0, "OJT Workplace:", self.lbl_ojt_place)
        add_info_row(ojt_grid, 1, "OJT Contact Number:", self.lbl_ojt_phone)
        add_info_row(ojt_grid, 2, "OJT Postal Address:", self.lbl_ojt_address)
        body_layout.addWidget(ojt_box)

        # 5. Employment Box
        job_box, job_grid = create_section_box("Employment Status")
        self.lbl_job_place = QLabel("-")
        self.lbl_job_address = QLabel("-")
        self.lbl_job_address.setWordWrap(True)

        # Status styling is handled dynamically via PageTheme properties

        add_info_row(job_grid, 0, "Current Job Place:", self.lbl_job_place)
        add_info_row(job_grid, 1, "Company Address:", self.lbl_job_address)
        body_layout.addWidget(job_box)

        # 6. Bottom Export Actions Row
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        pdf_btn = QPushButton(" Export Profile PDF")
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.setProperty("class", "PrimaryButton")
        pdf_btn.clicked.connect(self.export_pdf)
        
        print_btn = QPushButton(" Print Profile")
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.setProperty("class", "SecondaryButton")
        print_btn.clicked.connect(self.export_pdf) # Print redirects to generating PDF which is standard offline print workflow!
        
        actions_layout.addWidget(pdf_btn)
        actions_layout.addWidget(print_btn)
        actions_layout.addStretch(1)
        body_layout.addLayout(actions_layout)

        scroll.setWidget(body_container)
        main_layout.addWidget(scroll)

    def load_student(self, student_id: int):
        self.current_student_id = student_id
        student = self.student_service.get_student_by_id(student_id)
        if not student:
            QMessageBox.warning(self, "Error", "Failed to retrieve student records.")
            self.back_requested.emit()
            return

        # Load Text Labels
        self.lbl_name.setText(student.name_of_the_student)
        self.lbl_id.setText(student.id_number)
        self.lbl_year.setText(student.year_of_registered or "N/A")
        self.lbl_phone.setText(student.phone_number or "N/A")
        self.lbl_address.setText(student.private_address or "N/A")
        
        # Color coded statuses
        def set_status_label(lbl, val):
            lbl.setText(val)
            if val == "Yes":
                lbl.setProperty("class", "StatusYes")
            elif val == "No":
                lbl.setProperty("class", "StatusNo")
            elif val == "Pending":
                lbl.setProperty("class", "StatusPending")
            else:
                lbl.setProperty("class", "StatusDefault")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)
            lbl.update()

        set_status_label(self.lbl_dropout, student.drop_out)
        set_status_label(self.lbl_theory, student.theory_pass)
        set_status_label(self.lbl_l3, student.nvq_l3)
        set_status_label(self.lbl_l4, student.nvq_l4)

        # OJT
        self.lbl_ojt_place.setText(student.ojt_place or "N/A")
        self.lbl_ojt_phone.setText(student.ojt_phone_number or "N/A")
        self.lbl_ojt_address.setText(student.ojt_address or "N/A")

        # Job
        self.lbl_job_place.setText(student.job_place or "N/A")
        self.lbl_job_address.setText(student.job_place_address or "N/A")

        # Render Student Photo
        abs_photo = self.photo_service.get_absolute_path(student.photo_path)
        pixmap = QPixmap(abs_photo)
        self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def handle_edit(self):
        if self.current_student_id:
            self.edit_requested.emit(self.current_student_id)

    def export_pdf(self):
        """Triggers QFileDialog and generates profile PDF."""
        if not self.current_student_id:
            return
            
        student = self.student_service.get_student_by_id(self.current_student_id)
        if not student:
            return

        # Prepare default save name
        safe_name = "".join(c if c.isalnum() else "_" for c in student.name_of_the_student)
        default_filename = f"Profile_{student.id_number}_{safe_name}.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Profile PDF", default_filename, "PDF Documents (*.pdf)"
        )
        
        if file_path:
            try:
                photo_abs = self.photo_service.get_absolute_path(student.photo_path)
                self.export_service.export_profile_to_pdf(student, photo_abs, file_path)
                QMessageBox.information(self, "Success", "Profile PDF report exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"An error occurred while generating PDF:\n{str(e)}")
