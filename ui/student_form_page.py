# ui/student_form_page.py
import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, 
                             QGroupBox, QFormLayout, QScrollArea, QFileDialog, QFrame)
from PySide6.QtGui import QPixmap, QCursor
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
        self.import_service = ImportService()
        
        self.is_edit_mode = False
        self.edit_student_id = None
        self.temp_photo_path = ""       # Path to newly selected photo (not saved yet)
        self.photo_removed = False       # Tracks if existing photo was deleted
        self.existing_photo_path = ""    # Path to photo stored in DB before edit
        
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 24, 28, 20)
        root_layout.setSpacing(14)

        # 1. Header Title & Mode Block
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        self.header_title = QLabel("Register Student")
        self.header_title.setProperty("class", "PageTitle")
        
        self.header_subtitle = QLabel("Create a new student training dossier. Student ID Number must be unique.")
        self.header_subtitle.setProperty("class", "PageSubtitle")
        
        title_block.addWidget(self.header_title)
        title_block.addWidget(self.header_subtitle)
        header_layout.addLayout(title_block, 1)

        self.mode_badge = QLabel("ADD MODE")
        self.mode_badge.setStyleSheet(
            "background-color: #2563EB; color: #FFFFFF; font-weight: 700; "
            "font-size: 11px; padding: 4px 10px; border-radius: 4px;"
        )
        header_layout.addWidget(self.mode_badge, alignment=Qt.AlignRight | Qt.AlignVCenter)
        root_layout.addLayout(header_layout)

        # 2. Scrollable Form Container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("FormScrollArea")
        
        form_container = QWidget()
        form_container_layout = QVBoxLayout(form_container)
        form_container_layout.setContentsMargins(0, 0, 12, 0)
        form_container_layout.setSpacing(16)

        # 2-Column Responsive Layout
        self.columns_layout = QHBoxLayout()
        self.columns_layout.setSpacing(16)

        # ================= LEFT COLUMN =================
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # SECTION 1: Basic Details
        sec1_group = QGroupBox("Section 1: Basic Identification & Contact")
        sec1_layout = QVBoxLayout(sec1_group)
        sec1_layout.setContentsMargins(16, 16, 16, 16)
        sec1_layout.setSpacing(14)

        # Photo Preview + Photo Buttons
        photo_row = QHBoxLayout()
        photo_row.setSpacing(14)
        
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(110, 130)
        self.photo_preview.setObjectName("PhotoPreviewFrame")
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 6px; background-color: #F8FAFC;")
        photo_row.addWidget(self.photo_preview)

        photo_btn_col = QVBoxLayout()
        photo_btn_col.setSpacing(6)
        photo_btn_col.setAlignment(Qt.AlignVCenter)

        btn_select_photo = QPushButton("Select Photo...")
        btn_select_photo.setCursor(Qt.PointingHandCursor)
        btn_select_photo.setProperty("class", "SecondaryButton")
        btn_select_photo.clicked.connect(self.select_photo)
        photo_btn_col.addWidget(btn_select_photo)

        self.btn_remove_photo = QPushButton("Remove Photo")
        self.btn_remove_photo.setCursor(Qt.PointingHandCursor)
        self.btn_remove_photo.setProperty("class", "DangerButton")
        self.btn_remove_photo.clicked.connect(self.remove_photo)
        photo_btn_col.addWidget(self.btn_remove_photo)

        photo_hint = QLabel("Supported: JPG, PNG\nMax size recommended: 5MB")
        photo_hint.setStyleSheet("color: #64748B; font-size: 11px;")
        photo_btn_col.addWidget(photo_hint)

        photo_row.addLayout(photo_btn_col, 1)
        sec1_layout.addLayout(photo_row)

        # Form Inputs for Basic Details
        sec1_form = QFormLayout()
        sec1_form.setSpacing(10)
        sec1_form.setLabelAlignment(Qt.AlignLeft)

        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("e.g. 1998012345V or 200012345678")
        sec1_form.addRow("Student ID / NIC *", self.input_id)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Full Legal Name of the Student")
        sec1_form.addRow("Full Name *", self.input_name)

        self.input_year = QLineEdit()
        self.input_year.setPlaceholderText("e.g. 2026")
        sec1_form.addRow("Registration Year", self.input_year)

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("e.g. 0771234567 or +94771234567")
        sec1_form.addRow("Contact Phone", self.input_phone)

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText("Permanent Residential Address")
        sec1_form.addRow("Private Address", self.input_address)

        sec1_layout.addLayout(sec1_form)
        left_col.addWidget(sec1_group)

        # SECTION 2: Academic / Training Status
        sec2_group = QGroupBox("Section 2: Academic & Institutional Status")
        sec2_layout = QFormLayout(sec2_group)
        sec2_layout.setContentsMargins(16, 16, 16, 16)
        sec2_layout.setSpacing(10)
        sec2_layout.setLabelAlignment(Qt.AlignLeft)

        status_options = ["No", "Yes", "Pending", "Not Applicable"]

        self.cb_dropout = QComboBox()
        self.cb_dropout.addItems(status_options)
        sec2_layout.addRow("Drop Out Status", self.cb_dropout)

        self.cb_theory = QComboBox()
        self.cb_theory.addItems(status_options)
        sec2_layout.addRow("Theory Exam Pass", self.cb_theory)

        self.cb_l3 = QComboBox()
        self.cb_l3.addItems(status_options)
        sec2_layout.addRow("NVQ Level 3 Status", self.cb_l3)

        self.cb_l4 = QComboBox()
        self.cb_l4.addItems(status_options)
        sec2_layout.addRow("NVQ Level 4 Status", self.cb_l4)

        left_col.addWidget(sec2_group)
        self.columns_layout.addLayout(left_col, 1)

        # ================= RIGHT COLUMN =================
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        # SECTION 3: OJT Details
        sec3_group = QGroupBox("Section 3: On-the-Job Training (OJT) Placement")
        sec3_layout = QFormLayout(sec3_group)
        sec3_layout.setContentsMargins(16, 16, 16, 16)
        sec3_layout.setSpacing(10)
        sec3_layout.setLabelAlignment(Qt.AlignLeft)

        self.input_ojt_place = QLineEdit()
        self.input_ojt_place.setPlaceholderText("Training Company / Industrial Facility")
        sec3_layout.addRow("OJT Company", self.input_ojt_place)

        self.input_ojt_phone = QLineEdit()
        self.input_ojt_phone.setPlaceholderText("OJT Supervisor / Coordinator Contact")
        sec3_layout.addRow("OJT Phone", self.input_ojt_phone)

        self.input_ojt_address = QLineEdit()
        self.input_ojt_address.setPlaceholderText("Workplace Location / Address")
        sec3_layout.addRow("OJT Address", self.input_ojt_address)

        right_col.addWidget(sec3_group)

        # SECTION 4: Job Details
        sec4_group = QGroupBox("Section 4: Post-Graduation Employment")
        sec4_layout = QFormLayout(sec4_group)
        sec4_layout.setContentsMargins(16, 16, 16, 16)
        sec4_layout.setSpacing(10)
        sec4_layout.setLabelAlignment(Qt.AlignLeft)

        self.input_job_place = QLineEdit()
        self.input_job_place.setPlaceholderText("Hiring Organization / Employer Name")
        sec4_layout.addRow("Employer Name", self.input_job_place)

        self.input_job_address = QLineEdit()
        self.input_job_address.setPlaceholderText("Workplace / Branch Address")
        sec4_layout.addRow("Job Address", self.input_job_address)

        right_col.addWidget(sec4_group)
        right_col.addStretch(1)

        self.columns_layout.addLayout(right_col, 1)
        form_container_layout.addLayout(self.columns_layout)

        scroll.setWidget(form_container)
        root_layout.addWidget(scroll, 1)

        # 3. Fixed Bottom Action Toolbar (Always Visible)
        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: transparent; border-top: 1px solid #CBD5E1; padding-top: 12px;")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(12)

        self.lbl_form_hint = QLabel("* Required fields must be completed before saving.")
        self.lbl_form_hint.setStyleSheet("color: #64748B; font-size: 12px;")
        footer_layout.addWidget(self.lbl_form_hint)

        footer_layout.addStretch(1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setProperty("class", "SecondaryButton")
        self.cancel_btn.setMinimumWidth(110)
        self.cancel_btn.clicked.connect(self.handle_cancel)
        footer_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save Student Record")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setProperty("class", "PrimaryButton")
        self.save_btn.setMinimumWidth(160)
        self.save_btn.clicked.connect(self.save_student)
        footer_layout.addWidget(self.save_btn)

        root_layout.addWidget(footer_frame)

        # Live Form Validation Signals
        self.input_id.textChanged.connect(self._validate_form_inputs)
        self.input_name.textChanged.connect(self._validate_form_inputs)
        self.input_year.textChanged.connect(self._validate_form_inputs)
        self.input_phone.textChanged.connect(self._validate_form_inputs)

        # Initial Preview & Validation State
        self.update_photo_preview()
        self._validate_form_inputs()

    def select_photo(self):
        """Opens file dialog for selecting passport photo with integrity and size validation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Student Passport Photograph", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            p = Path(file_path)
            # Check file size (max 5 MB)
            if p.stat().st_size > 5 * 1024 * 1024:
                QMessageBox.warning(
                    self, "Photo Size Limit",
                    f"Selected photo is too large ({p.stat().st_size / (1024*1024):.1f} MB).\n"
                    "Please choose an image under 5 MB."
                )
                return
            # Verify image integrity with Pillow
            try:
                from PIL import Image
                with Image.open(p) as img:
                    img.verify()
            except Exception as e:
                QMessageBox.warning(
                    self, "Invalid Image File",
                    f"The selected file could not be verified as a valid image.\nError: {e}"
                )
                return

            self.temp_photo_path = file_path
            self.photo_removed = False
            self.update_photo_preview()

    def remove_photo(self):
        """Marks current photo as removed and clears preview."""
        self.temp_photo_path = ""
        self.existing_photo_path = ""
        self.photo_removed = True
        self.update_photo_preview()

    def update_photo_preview(self):
        """Renders either newly selected photo, existing photo, or default avatar."""
        if self.temp_photo_path and os.path.exists(self.temp_photo_path):
            pixmap = QPixmap(self.temp_photo_path)
            self.photo_preview.setPixmap(
                pixmap.scaled(self.photo_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.btn_remove_photo.setVisible(True)
            self.btn_remove_photo.setEnabled(True)
        elif self.existing_photo_path and not self.photo_removed:
            abs_path = self.photo_service.get_absolute_path(self.existing_photo_path)
            if os.path.exists(abs_path):
                pixmap = QPixmap(abs_path)
                self.photo_preview.setPixmap(
                    pixmap.scaled(self.photo_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.btn_remove_photo.setVisible(True)
                self.btn_remove_photo.setEnabled(True)
            else:
                self._set_default_avatar()
        else:
            self._set_default_avatar()

    def _set_default_avatar(self):
        abs_path = self.photo_service.get_absolute_path("")
        if os.path.exists(abs_path):
            pixmap = QPixmap(abs_path)
            self.photo_preview.setPixmap(
                pixmap.scaled(self.photo_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.photo_preview.setText("No Photo")
        # Hide and disable Remove Photo button when placeholder avatar is active
        self.btn_remove_photo.setVisible(False)
        self.btn_remove_photo.setEnabled(False)

    def handle_cancel(self):
        """Resets form inputs and exits without saving uncommitted data."""
        self.clear_form()
        self.cancelled.emit()

    def _validate_form_inputs(self):
        """Performs live check of required inputs to update Save button and helper hint."""
        id_text = self.input_id.text().strip()
        name_text = self.input_name.text().strip()
        year_text = self.input_year.text().strip()
        phone_text = self.input_phone.text().strip()

        missing = []
        if not id_text:
            missing.append("Student ID / NIC")
        if not name_text:
            missing.append("Full Name")

        if missing:
            self.save_btn.setEnabled(False)
            self.lbl_form_hint.setText(f"* Please provide: {', '.join(missing)} to enable saving.")
            self.lbl_form_hint.setStyleSheet("color: #E11D48; font-size: 12px; font-weight: 500;")
            self.save_btn.setToolTip(f"Complete required fields ({', '.join(missing)}) to save.")
            return

        # Check year validity if provided
        if year_text and (not year_text.isdigit() or len(year_text) != 4 or int(year_text) < 1990 or int(year_text) > 2100):
            self.save_btn.setEnabled(False)
            self.lbl_form_hint.setText("* Registration Year must be a 4-digit year (e.g., 2026).")
            self.lbl_form_hint.setStyleSheet("color: #E11D48; font-size: 12px; font-weight: 500;")
            self.save_btn.setToolTip("Enter a valid 4-digit registration year.")
            return

        # Check phone validity if provided
        if phone_text and not self.import_service.is_valid_phone(phone_text):
            self.save_btn.setEnabled(False)
            self.lbl_form_hint.setText("* Please enter a valid contact phone number format.")
            self.lbl_form_hint.setStyleSheet("color: #E11D48; font-size: 12px; font-weight: 500;")
            self.save_btn.setToolTip("Enter a valid phone number.")
            return

        self.save_btn.setEnabled(True)
        self.lbl_form_hint.setText("All required fields completed. Ready to save.")
        self.lbl_form_hint.setStyleSheet("color: #059669; font-size: 12px; font-weight: 500;")
        self.save_btn.setToolTip("Click to save record")

    def clear_form(self):
        """Clears all input boxes and resets dropdown states."""
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
        self._validate_form_inputs()

    def set_add_mode(self):
        self.is_edit_mode = False
        self.edit_student_id = None
        self.header_title.setText("Register Student")
        self.header_subtitle.setText("Create a new student training dossier. Student ID Number must be unique.")
        self.mode_badge.setText("ADD MODE")
        self.mode_badge.setStyleSheet(
            "background-color: #2563EB; color: #FFFFFF; font-weight: 700; "
            "font-size: 11px; padding: 4px 10px; border-radius: 4px;"
        )
        self.save_btn.setText("Save Student Record")
        self.input_id.setEnabled(True)
        self.clear_form()

    def set_edit_mode(self, student_id: int):
        self.is_edit_mode = True
        self.edit_student_id = student_id
        self.header_title.setText("Edit Student Dossier")
        self.header_subtitle.setText("Modify existing student information. Student ID Number must remain unique.")
        self.mode_badge.setText("EDIT MODE")
        self.mode_badge.setStyleSheet(
            "background-color: #059669; color: #FFFFFF; font-weight: 700; "
            "font-size: 11px; padding: 4px 10px; border-radius: 4px;"
        )
        self.save_btn.setText("Update Student Record")
        
        student = self.student_service.get_student_by_id(student_id)
        if not student:
            QMessageBox.warning(self, "Record Error", "Student record was not found in the database.")
            self.cancelled.emit()
            return

        self.input_id.setText(student.id_number or "")
        self.input_id.setEnabled(True)
        self.input_name.setText(student.name_of_the_student or "")
        self.input_year.setText(student.year_of_registered or "")
        self.input_phone.setText(student.phone_number or "")
        self.input_address.setText(student.private_address or "")
        
        self.input_ojt_place.setText(student.ojt_place or "")
        self.input_ojt_phone.setText(student.ojt_phone_number or "")
        self.input_ojt_address.setText(student.ojt_address or "")
        
        self.input_job_place.setText(student.job_place or "")
        self.input_job_address.setText(student.job_place_address or "")

        def select_cb(cb, val):
            idx = cb.findText(val or "No")
            cb.setCurrentIndex(idx if idx >= 0 else 0)

        select_cb(self.cb_dropout, student.drop_out)
        select_cb(self.cb_theory, student.theory_pass)
        select_cb(self.cb_l3, student.nvq_l3)
        select_cb(self.cb_l4, student.nvq_l4)

        self.existing_photo_path = student.photo_path or ""
        self.temp_photo_path = ""
        self.photo_removed = False
        
        self.update_photo_preview()
        self._validate_form_inputs()

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
            QMessageBox.warning(self, "Validation Required", "Student ID / NIC number is required.")
            self.input_id.setFocus()
            return
        if not name:
            QMessageBox.warning(self, "Validation Required", "Full Student Name is required.")
            self.input_name.setFocus()
            return

        # Year validation
        if year and (not year.isdigit() or len(year) != 4 or int(year) < 1990 or int(year) > 2100):
            QMessageBox.warning(self, "Validation Required", "Please enter a valid 4-digit registration year (e.g. 2026).")
            self.input_year.setFocus()
            return

        # Phone validations
        if phone and not self.import_service.is_valid_phone(phone):
            QMessageBox.warning(self, "Validation Required", "Please enter a valid phone number for the student.")
            self.input_phone.setFocus()
            return
        if ojt_phone and not self.import_service.is_valid_phone(ojt_phone):
            QMessageBox.warning(self, "Validation Required", "Please enter a valid phone number for the OJT placement contact.")
            self.input_ojt_phone.setFocus()
            return

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

        photo_path_to_save = self.existing_photo_path
        new_photo_path = ""

        try:
            if self.photo_removed:
                photo_path_to_save = ""
            elif self.temp_photo_path:
                new_photo_path = self.photo_service.save_photo(self.temp_photo_path, id_number)
                photo_path_to_save = new_photo_path

            student_data["photo_path"] = photo_path_to_save
            student_obj = Student.from_dict(student_data)

            # DB Write
            if self.is_edit_mode:
                success = self.student_service.update_student(student_obj)
                if success:
                    if self.existing_photo_path and self.existing_photo_path != photo_path_to_save:
                        self.photo_service.delete_photo(self.existing_photo_path)
                    QMessageBox.information(self, "Success", "Student record updated successfully.")
                    self.form_submitted.emit()
                else:
                    if new_photo_path:
                        self.photo_service.delete_photo(new_photo_path)
                    QMessageBox.warning(self, "Error", "Failed to update student record.")
            else:
                last_id = self.student_service.add_student(student_obj)
                if last_id:
                    if self.photo_removed and self.existing_photo_path:
                        self.photo_service.delete_photo(self.existing_photo_path)
                    QMessageBox.information(self, "Success", "Student record registered successfully.")
                    self.form_submitted.emit()
                else:
                    if new_photo_path:
                        self.photo_service.delete_photo(new_photo_path)
                    QMessageBox.warning(self, "Error", "Failed to insert student record.")
                    
        except ValueError as val_ex:
            if new_photo_path:
                self.photo_service.delete_photo(new_photo_path)
            QMessageBox.warning(self, "Validation Constraint", str(val_ex))
        except Exception as ex:
            if new_photo_path:
                self.photo_service.delete_photo(new_photo_path)
            QMessageBox.critical(self, "Database System Error", f"Unexpected error during save: {str(ex)}")
