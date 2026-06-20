# ui/student_form_page.py
import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox, QGroupBox, 
                             QFormLayout, QScrollArea, QFileDialog)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from models.student import Student
from services.student_service import StudentService
from services.photo_service import PhotoService
from services.import_service import ImportService

class StudentFormPage(QWidget):
    form_submitted = Signal()
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.student_service = StudentService()
        self.photo_service = PhotoService()
        self.import_service = ImportService() # Reuse phone validator
        
        self.is_edit_mode = False
        self.edit_student_id = None
        self.temp_photo_path = "" # Path to newly selected photo (not saved yet)
        self.photo_removed = False # Tracks if existing photo was deleted
        self.existing_photo_path = "" # Path to photo stored in DB before edit
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Header Block
        self.header_title = QLabel("Register Student")
        self.header_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1E2A38;")
        self.header_subtitle = QLabel("Create a new offline record. ID Number must be unique.")
        self.header_subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        
        main_layout.addWidget(self.header_title)
        main_layout.addWidget(self.header_subtitle)

        # Scroll Area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 15, 0)
        form_layout.setSpacing(20)

        # SECTION 1: Basic Details
        basic_group = QGroupBox("Section 1: Basic Details")
        basic_layout = QHBoxLayout(basic_group)
        basic_layout.setContentsMargins(15, 20, 15, 15)
        basic_layout.setSpacing(20)

        # 1.1 Photo column (Left)
        photo_col = QVBoxLayout()
        photo_col.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(140, 160)
        self.photo_preview.setStyleSheet("border: 1px solid #CBD5E1; background-color: #E2E8F0; border-radius: 6px;")
        self.photo_preview.setAlignment(Qt.AlignCenter)
        photo_col.addWidget(self.photo_preview)

        btn_select_photo = QPushButton("Select Photo")
        btn_select_photo.setCursor(Qt.PointingHandCursor)
        btn_select_photo.setStyleSheet("""
            QPushButton {
                background-color: #1E2A38; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2D3E50; }
        """)
        btn_select_photo.clicked.connect(self.select_photo)
        photo_col.addWidget(btn_select_photo)

        self.btn_remove_photo = QPushButton("Remove Photo")
        self.btn_remove_photo.setCursor(Qt.PointingHandCursor)
        self.btn_remove_photo.setStyleSheet("""
            QPushButton {
                background-color: #EF4444; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-size: 11px; font-weight: bold;
            }
            QPushButton:hover { background-color: #DC2626; }
        """)
        self.btn_remove_photo.clicked.connect(self.remove_photo)
        photo_col.addWidget(self.btn_remove_photo)
        
        basic_layout.addLayout(photo_col)

        # 1.2 Input Fields Column (Right)
        fields_form = QFormLayout()
        fields_form.setSpacing(10)
        fields_form.setLabelAlignment(Qt.AlignRight)

        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("e.g. 1998012345V or 199912345678")
        fields_form.addRow("ID Number *:", self.input_id)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Full Name of the Student")
        fields_form.addRow("Student Name *:", self.input_name)

        self.input_year = QLineEdit()
        self.input_year.setPlaceholderText("e.g. 2025")
        fields_form.addRow("Year Registered:", self.input_year)

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Contact Phone Number")
        fields_form.addRow("Phone Number:", self.input_phone)

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText("Permanent Private Address")
        fields_form.addRow("Private Address:", self.input_address)

        basic_layout.addLayout(fields_form, 1)
        form_layout.addWidget(basic_group)

        # SECTION 2: Academic / Training Status
        academic_group = QGroupBox("Section 2: Academic & Training Status")
        academic_layout = QFormLayout(academic_group)
        academic_layout.setContentsMargins(15, 20, 15, 15)
        academic_layout.setSpacing(10)

        status_options = ["No", "Yes", "Pending", "Not Applicable"]

        self.cb_dropout = QComboBox()
        self.cb_dropout.addItems(status_options)
        academic_layout.addRow("Drop Out Status:", self.cb_dropout)

        self.cb_theory = QComboBox()
        self.cb_theory.addItems(status_options)
        academic_layout.addRow("Theory Exam Pass:", self.cb_theory)

        self.cb_l3 = QComboBox()
        self.cb_l3.addItems(status_options)
        academic_layout.addRow("NVQ Level 3 Completed:", self.cb_l3)

        self.cb_l4 = QComboBox()
        self.cb_l4.addItems(status_options)
        academic_layout.addRow("NVQ Level 4 Completed:", self.cb_l4)

        form_layout.addWidget(academic_group)

        # SECTION 3: OJT Details
        ojt_group = QGroupBox("Section 3: On-the-Job Training (OJT) Placement")
        ojt_layout = QFormLayout(ojt_group)
        ojt_layout.setContentsMargins(15, 20, 15, 15)
        ojt_layout.setSpacing(10)

        self.input_ojt_place = QLineEdit()
        self.input_ojt_place.setPlaceholderText("OJT Employer / Company Name")
        ojt_layout.addRow("OJT Place:", self.input_ojt_place)

        self.input_ojt_phone = QLineEdit()
        self.input_ojt_phone.setPlaceholderText("OJT Contact Person Number")
        ojt_layout.addRow("OJT Phone Number:", self.input_ojt_phone)

        self.input_ojt_address = QLineEdit()
        self.input_ojt_address.setPlaceholderText("OJT Works Address")
        ojt_layout.addRow("OJT Address:", self.input_ojt_address)

        form_layout.addWidget(ojt_group)

        # SECTION 4: Job Details
        job_group = QGroupBox("Section 4: Employment Details")
        job_layout = QFormLayout(job_group)
        job_layout.setContentsMargins(15, 20, 15, 15)
        job_layout.setSpacing(10)

        self.input_job_place = QLineEdit()
        self.input_job_place.setPlaceholderText("Current Job Place / Employer Name")
        job_layout.addRow("Job Place:", self.input_job_place)

        self.input_job_address = QLineEdit()
        self.input_job_address.setPlaceholderText("Company Address")
        job_layout.addRow("Job Place Address:", self.input_job_address)

        form_layout.addWidget(job_group)

        # Action Buttons Row
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        actions_layout.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setProperty("class", "SecondaryButton")
        cancel_btn.clicked.connect(self.cancelled.emit)
        
        self.save_btn = QPushButton("Save Student Record")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setProperty("class", "PrimaryButton")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6; color: white; padding: 10px 24px; font-weight: bold; border-radius: 6px;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        self.save_btn.clicked.connect(self.save_student)

        actions_layout.addWidget(cancel_btn)
        actions_layout.addWidget(self.save_btn)
        form_layout.addLayout(actions_layout)

        scroll.setWidget(form_container)
        main_layout.addWidget(scroll)

        # Load empty state
        self.update_photo_preview()

    def select_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Student Photo", "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.temp_photo_path = file_path
            self.photo_removed = False
            self.update_photo_preview()

    def remove_photo(self):
        self.temp_photo_path = ""
        self.photo_removed = True
        self.update_photo_preview()

    def update_photo_preview(self):
        """Redraws the preview frame based on the active state."""
        if self.temp_photo_path:
            pixmap = QPixmap(self.temp_photo_path)
            self.photo_preview.setPixmap(pixmap.scaled(self.photo_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.btn_remove_photo.setEnabled(True)
        elif self.existing_photo_path and not self.photo_removed:
            abs_path = self.photo_service.get_absolute_path(self.existing_photo_path)
            pixmap = QPixmap(abs_path)
            self.photo_preview.setPixmap(pixmap.scaled(self.photo_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.btn_remove_photo.setEnabled(True)
        else:
            # Default empty preview
            abs_path = self.photo_service.get_absolute_path("")
            pixmap = QPixmap(abs_path)
            self.photo_preview.setPixmap(pixmap.scaled(self.photo_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.btn_remove_photo.setEnabled(False)

    def clear_form(self):
        """Clears all text boxes and resets dropdown indexes."""
        self.input_id.clear()
        self.input_name.clear()
        self.input_year.clear()
        self.input_phone.clear()
        self.input_address.clear()
        self.input_ojt_place.clear()
        self.input_ojt_phone.clear()
        self.input_ojt_address.clear()
        self.input_job_place.clear()
        self.input_job_address.clear()
        
        self.cb_dropout.setCurrentIndex(0)
        self.cb_theory.setCurrentIndex(0)
        self.cb_l3.setCurrentIndex(0)
        self.cb_l4.setCurrentIndex(0)

        self.temp_photo_path = ""
        self.existing_photo_path = ""
        self.photo_removed = False
        self.update_photo_preview()

    def set_add_mode(self):
        self.is_edit_mode = False
        self.edit_student_id = None
        self.header_title.setText("Register Student")
        self.header_subtitle.setText("Create a new offline record. ID Number must be unique.")
        self.input_id.setEnabled(True)
        self.clear_form()

    def set_edit_mode(self, student_id: int):
        self.is_edit_mode = True
        self.edit_student_id = student_id
        self.header_title.setText("Edit Student Profile")
        self.header_subtitle.setText("Modify records. Keep ID number unique.")
        
        # Load from DB
        student = self.student_service.get_student_by_id(student_id)
        if not student:
            QMessageBox.warning(self, "Error", "Student record not found.")
            self.cancelled.emit()
            return

        self.input_id.setText(student.id_number)
        self.input_id.setEnabled(True) # Yes, allowed to edit ID but checked for uniqueness
        self.input_name.setText(student.name_of_the_student)
        self.input_year.setText(student.year_of_registered)
        self.input_phone.setText(student.phone_number)
        self.input_address.setText(student.private_address)
        
        self.input_ojt_place.setText(student.ojt_place)
        self.input_ojt_phone.setText(student.ojt_phone_number)
        self.input_ojt_address.setText(student.ojt_address)
        
        self.input_job_place.setText(student.job_place)
        self.input_job_address.setText(student.job_place_address)

        def select_cb_index(cb, val):
            idx = cb.findText(val)
            if idx >= 0:
                cb.setCurrentIndex(idx)
            else:
                cb.setCurrentIndex(0)

        select_cb_index(self.cb_dropout, student.drop_out)
        select_cb_index(self.cb_theory, student.theory_pass)
        select_cb_index(self.cb_l3, student.nvq_l3)
        select_cb_index(self.cb_l4, student.nvq_l4)

        self.existing_photo_path = student.photo_path
        self.temp_photo_path = ""
        self.photo_removed = False
        
        self.update_photo_preview()

    def save_student(self):
        """Performs form validations and executes DB write operations."""
        id_number = self.input_id.text().strip()
        name = self.input_name.text().strip()
        year = self.input_year.text().strip()
        phone = self.input_phone.text().strip()
        address = self.input_address.text().strip()
        
        ojt_place = self.input_ojt_place.text().strip()
        ojt_phone = self.input_ojt_phone.text().strip()
        ojt_address = self.input_ojt_address.text().strip()
        
        job_place = self.input_job_place.text().strip()
        job_place_address = self.input_job_address.text().strip()

        # Validation checks
        if not id_number:
            QMessageBox.warning(self, "Validation Error", "ID Number is required.")
            self.input_id.setFocus()
            return
        if not name:
            QMessageBox.warning(self, "Validation Error", "Student Name is required.")
            self.input_name.setFocus()
            return

        # Phone validations
        if phone and not self.import_service.is_valid_phone(phone):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid phone number for the student.")
            self.input_phone.setFocus()
            return
        if ojt_phone and not self.import_service.is_valid_phone(ojt_phone):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid phone number for the OJT placement contact.")
            self.input_ojt_phone.setFocus()
            return

        # Compile data
        student_data = {
            "id_number": id_number,
            "name_of_the_student": name,
            "year_of_registered": year,
            "phone_number": phone,
            "private_address": address,
            "drop_out": self.cb_dropout.currentText(),
            "theory_pass": self.cb_theory.currentText(),
            "nvq_l3": self.cb_l3.currentText(),
            "nvq_l4": self.cb_l4.currentText(),
            "ojt_place": ojt_place,
            "ojt_phone_number": ojt_phone,
            "ojt_address": ojt_address,
            "job_place": job_place,
            "job_place_address": job_place_address,
            "photo_path": self.existing_photo_path
        }

        if self.is_edit_mode:
            student_data["id"] = self.edit_student_id

        # Photo logic
        photo_path_to_save = self.existing_photo_path

        try:
            if self.photo_removed:
                # User deleted photo
                if self.existing_photo_path:
                    self.photo_service.delete_photo(self.existing_photo_path)
                photo_path_to_save = ""
            elif self.temp_photo_path:
                # User selected a new photo. Save it.
                # If there was an old photo, clean it up first
                if self.existing_photo_path:
                    self.photo_service.delete_photo(self.existing_photo_path)
                
                saved_rel_path = self.photo_service.save_photo(self.temp_photo_path, id_number)
                photo_path_to_save = saved_rel_path

            student_data["photo_path"] = photo_path_to_save

            student_obj = Student.from_dict(student_data)

            # DB Write
            if self.is_edit_mode:
                success = self.student_service.update_student(student_obj)
                if success:
                    QMessageBox.information(self, "Success", "Student record updated successfully.")
                    self.form_submitted.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update student record.")
            else:
                last_id = self.student_service.add_student(student_obj)
                if last_id:
                    QMessageBox.information(self, "Success", "Student record registered successfully.")
                    self.form_submitted.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to insert student record.")
                    
        except ValueError as val_ex:
            # Handles duplicate ID errors or photo format issues
            QMessageBox.warning(self, "Validation Constraint", str(val_ex))
        except Exception as ex:
            QMessageBox.critical(self, "Database System Error", f"Unexpected error during save: {str(ex)}")
