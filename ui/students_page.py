# ui/students_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from services.student_service import StudentService

class StudentsPage(QWidget):
    view_student_requested = Signal(int) # Emits student DB ID
    edit_student_requested = Signal(int) # Emits student DB ID
    add_student_requested = Signal()

    def __init__(self):
        super().__init__()
        self.student_service = StudentService()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # 1. Page Header Block
        header_layout = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        
        title_label = QLabel("Student Records")
        title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #1E2A38;")
        
        subtitle_label = QLabel("Search, filter, and manage individual student profiles.")
        subtitle_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        title_block.addWidget(title_label)
        title_block.addWidget(subtitle_label)
        header_layout.addLayout(title_block)

        add_btn = QPushButton("+ Register Student")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        add_btn.clicked.connect(self.add_student_requested.emit)
        header_layout.addWidget(add_btn, alignment=Qt.AlignVCenter)
        main_layout.addLayout(header_layout)

        # 2. Search and Filter Panel (Rounded Gray Card)
        filter_panel = QFrame()
        filter_panel.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
            QLabel {
                font-weight: 600;
                color: #475569;
                font-size: 11px;
                text-transform: uppercase;
            }
        """)
        
        panel_layout = QVBoxLayout(filter_panel)
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(12)

        # Search Bar Row
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Student ID, Name, Phone Number, OJT or Job organization...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 13px;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background-color: #F8FAFC;
            }
            QLineEdit:focus {
                border: 1.5px solid #3B82F6;
                background-color: #FFFFFF;
            }
        """)
        self.search_input.textChanged.connect(self.refresh_data)
        search_layout.addWidget(self.search_input)
        panel_layout.addLayout(search_layout)

        # Dropdowns Filters Row
        filters_grid = QHBoxLayout()
        filters_grid.setSpacing(10)

        # 2.1 Registered Year
        yr_layout = QVBoxLayout()
        yr_layout.addWidget(QLabel("Registered Year"))
        self.cb_year = QComboBox()
        self.cb_year.addItem("All Years")
        self.cb_year.currentIndexChanged.connect(self.refresh_data)
        yr_layout.addWidget(self.cb_year)
        filters_grid.addLayout(yr_layout, 1)

        # 2.2 Drop Out
        do_layout = QVBoxLayout()
        do_layout.addWidget(QLabel("Drop Out"))
        self.cb_dropout = QComboBox()
        self.cb_dropout.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_dropout.currentIndexChanged.connect(self.refresh_data)
        do_layout.addWidget(self.cb_dropout)
        filters_grid.addLayout(do_layout, 1)

        # 2.3 Theory Pass
        tp_layout = QVBoxLayout()
        tp_layout.addWidget(QLabel("Theory Pass"))
        self.cb_theory = QComboBox()
        self.cb_theory.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_theory.currentIndexChanged.connect(self.refresh_data)
        tp_layout.addWidget(self.cb_theory)
        filters_grid.addLayout(tp_layout, 1)

        # 2.4 NVQ L3
        l3_layout = QVBoxLayout()
        l3_layout.addWidget(QLabel("NVQ L3"))
        self.cb_l3 = QComboBox()
        self.cb_l3.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_l3.currentIndexChanged.connect(self.refresh_data)
        l3_layout.addWidget(self.cb_l3)
        filters_grid.addLayout(l3_layout, 1)

        # 2.5 NVQ L4
        l4_layout = QVBoxLayout()
        l4_layout.addWidget(QLabel("NVQ L4"))
        self.cb_l4 = QComboBox()
        self.cb_l4.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_l4.currentIndexChanged.connect(self.refresh_data)
        l4_layout.addWidget(self.cb_l4)
        filters_grid.addLayout(l4_layout, 1)

        # 2.6 Has OJT
        ojt_layout = QVBoxLayout()
        ojt_layout.addWidget(QLabel("OJT Placed"))
        self.cb_has_ojt = QComboBox()
        self.cb_has_ojt.addItems(["All", "Yes", "No"])
        self.cb_has_ojt.currentIndexChanged.connect(self.refresh_data)
        ojt_layout.addWidget(self.cb_has_ojt)
        filters_grid.addLayout(ojt_layout, 1)

        # 2.7 Has Job
        job_layout = QVBoxLayout()
        job_layout.addWidget(QLabel("Employed"))
        self.cb_has_job = QComboBox()
        self.cb_has_job.addItems(["All", "Yes", "No"])
        self.cb_has_job.currentIndexChanged.connect(self.refresh_data)
        job_layout.addWidget(self.cb_has_job)
        filters_grid.addLayout(job_layout, 1)

        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)
        reset_btn.clicked.connect(self.reset_filters)
        
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(QLabel(" "))
        btn_layout.addWidget(reset_btn)
        filters_grid.addLayout(btn_layout, 0)

        panel_layout.addLayout(filters_grid)
        main_layout.addWidget(filter_panel)

        # 3. Students Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID Number", "Name", "Year Registered", "Phone Number", 
            "Drop Out", "Theory Pass", "NVQ L3", "NVQ L4", 
            "OJT Place", "Job Place", "Actions"
        ])
        
        # Styles for table headers and columns sizing
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(self.table)

        # Initial populate
        self.populate_years_dropdown()
        self.refresh_data()

    def populate_years_dropdown(self):
        """Fetches unique registered years and updates dropdown options."""
        self.cb_year.blockSignals(True)
        self.cb_year.clear()
        self.cb_year.addItem("All Years")
        years = self.student_service.get_unique_registered_years()
        for yr in years:
            self.cb_year.addItem(yr)
        self.cb_year.blockSignals(False)

    def reset_filters(self):
        """Clears all inputs and resets filters."""
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)

        self.cb_year.blockSignals(True)
        self.cb_year.setCurrentIndex(0)
        self.cb_year.blockSignals(False)

        self.cb_dropout.blockSignals(True)
        self.cb_dropout.setCurrentIndex(0)
        self.cb_dropout.blockSignals(False)

        self.cb_theory.blockSignals(True)
        self.cb_theory.setCurrentIndex(0)
        self.cb_theory.blockSignals(False)

        self.cb_l3.blockSignals(True)
        self.cb_l3.setCurrentIndex(0)
        self.cb_l3.blockSignals(False)

        self.cb_l4.blockSignals(True)
        self.cb_l4.setCurrentIndex(0)
        self.cb_l4.blockSignals(False)

        self.cb_has_ojt.blockSignals(True)
        self.cb_has_ojt.setCurrentIndex(0)
        self.cb_has_ojt.blockSignals(False)

        self.cb_has_job.blockSignals(True)
        self.cb_has_job.setCurrentIndex(0)
        self.cb_has_job.blockSignals(False)

        self.refresh_data()

    def refresh_data(self):
        """Retrieves and populates the table based on active search/filters."""
        search_text = self.search_input.text().strip()
        
        # Compile filters
        filters = {}
        
        if self.cb_year.currentIndex() > 0:
            filters["year_of_registered"] = self.cb_year.currentText()
            
        def get_status_val(cb):
            return None if cb.currentText() == "All" else cb.currentText()
            
        filters["drop_out"] = get_status_val(self.cb_dropout)
        filters["theory_pass"] = get_status_val(self.cb_theory)
        filters["nvq_l3"] = get_status_val(self.cb_l3)
        filters["nvq_l4"] = get_status_val(self.cb_l4)
        
        if self.cb_has_ojt.currentText() != "All":
            filters["has_ojt"] = self.cb_has_ojt.currentText()
            
        if self.cb_has_job.currentText() != "All":
            filters["has_job"] = self.cb_has_job.currentText()

        # Query database
        students = self.student_service.search_and_filter_students(search_text, filters)

        # Clear table
        self.table.setRowCount(0)
        
        for student in students:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # Create items
            self.table.setItem(row_idx, 0, QTableWidgetItem(student.id_number))
            self.table.setItem(row_idx, 1, QTableWidgetItem(student.name_of_the_student))
            self.table.setItem(row_idx, 2, QTableWidgetItem(student.year_of_registered or ""))
            self.table.setItem(row_idx, 3, QTableWidgetItem(student.phone_number or ""))
            
            # Status items (color coded values)
            def create_status_item(val):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if val == "Yes":
                    item.setForeground(Qt.darkGreen)
                elif val == "No":
                    item.setForeground(Qt.darkRed)
                elif val == "Pending":
                    item.setForeground(Qt.blue)
                return item
            
            self.table.setItem(row_idx, 4, create_status_item(student.drop_out))
            self.table.setItem(row_idx, 5, create_status_item(student.theory_pass))
            self.table.setItem(row_idx, 6, create_status_item(student.nvq_l3))
            self.table.setItem(row_idx, 7, create_status_item(student.nvq_l4))
            self.table.setItem(row_idx, 8, QTableWidgetItem(student.ojt_place or ""))
            self.table.setItem(row_idx, 9, QTableWidgetItem(student.job_place or ""))

            # Actions cell widget
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(6)

            btn_view = QPushButton("View")
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.setProperty("student_id", student.id)
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #2563EB; }
            """)
            btn_view.clicked.connect(self.on_view_clicked)

            btn_edit = QPushButton("Edit")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setProperty("student_id", student.id)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #059669; }
            """)
            btn_edit.clicked.connect(self.on_edit_clicked)

            btn_delete = QPushButton("Delete")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.setProperty("student_id", student.id)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #DC2626; }
            """)
            btn_delete.clicked.connect(self.on_delete_clicked)

            actions_layout.addWidget(btn_view)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            
            self.table.setCellWidget(row_idx, 10, actions_widget)
            
        # Adjust section sizes slightly
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(3)
        self.table.resizeColumnToContents(4)
        self.table.resizeColumnToContents(5)
        self.table.resizeColumnToContents(6)
        self.table.resizeColumnToContents(7)

    def on_view_clicked(self):
        btn = self.sender()
        if btn:
            student_id = btn.property("student_id")
            self.view_student_requested.emit(student_id)

    def on_edit_clicked(self):
        btn = self.sender()
        if btn:
            student_id = btn.property("student_id")
            self.edit_student_requested.emit(student_id)

    def on_delete_clicked(self):
        btn = self.sender()
        if btn:
            student_id = btn.property("student_id")
            
            # Fetch name
            student = self.student_service.get_student_by_id(student_id)
            if not student:
                return
                
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                f"Are you sure you want to permanently delete the student records for '{student.name_of_the_student}' (ID: {student.id_number})?\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # If student had photo, delete photo file
                if student.photo_path:
                    from services.photo_service import PhotoService
                    PhotoService().delete_photo(student.photo_path)
                    
                success = self.student_service.delete_student(student_id)
                if success:
                    QMessageBox.information(self, "Success", "Student record successfully deleted.")
                    self.refresh_data()
                    self.populate_years_dropdown()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete student record.")
