# ui/students_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QFrame,
                             QAbstractItemView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor, QColor
from services.student_service import StudentService


class StudentsPage(QWidget):
    view_student_requested = Signal(int)  # Emits student DB ID
    edit_student_requested = Signal(int)  # Emits student DB ID
    add_student_requested = Signal()

    PAGE_SIZE = 50

    def __init__(self):
        super().__init__()
        self.student_service = StudentService()
        self.current_page = 1
        self.total_pages = 1
        self.cached_students = []
        self.selected_student_id = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(14)

        # 1. Top Header & Action Row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title_label = QLabel("Student Records")
        title_label.setProperty("class", "PageTitle")
        
        subtitle_label = QLabel("Search, filter, inspect, and manage student enrollment and training dossiers.")
        subtitle_label.setProperty("class", "PageSubtitle")
        
        title_block.addWidget(title_label)
        title_block.addWidget(subtitle_label)
        header_layout.addLayout(title_block, 1)

        add_btn = QPushButton("+ Register Student")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setProperty("class", "PrimaryButton")
        add_btn.setMinimumWidth(160)
        add_btn.clicked.connect(self.add_student_requested.emit)
        header_layout.addWidget(add_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)
        main_layout.addLayout(header_layout)

        # 2. Search & Filter Card (2-Tier Layout)
        filter_panel = QFrame()
        filter_panel.setObjectName("FilterPanel")
        panel_layout = QVBoxLayout(filter_panel)
        panel_layout.setContentsMargins(16, 14, 16, 14)
        panel_layout.setSpacing(10)

        # Row 1: Search Field
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Student ID, Name, Phone Number, OJT Company, or Employment...")
        self.search_input.setObjectName("SearchInput")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input, 1)
        panel_layout.addLayout(search_layout)

        # Row 2: Two-Tier Filter Grid
        filters_grid = QGridLayout()
        filters_grid.setHorizontalSpacing(10)
        filters_grid.setVerticalSpacing(8)

        # Tier 1: Year & Academic Status
        self.cb_year = QComboBox()
        self.cb_year.addItem("All Years")
        self.cb_year.currentIndexChanged.connect(self.on_filter_changed)

        self.cb_dropout = QComboBox()
        self.cb_dropout.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_dropout.currentIndexChanged.connect(self.on_filter_changed)

        self.cb_theory = QComboBox()
        self.cb_theory.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_theory.currentIndexChanged.connect(self.on_filter_changed)

        self.cb_l3 = QComboBox()
        self.cb_l3.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_l3.currentIndexChanged.connect(self.on_filter_changed)

        self.cb_l4 = QComboBox()
        self.cb_l4.addItems(["All", "Yes", "No", "Pending", "Not Applicable"])
        self.cb_l4.currentIndexChanged.connect(self.on_filter_changed)

        def make_filter_group(label_text, widget):
            box = QVBoxLayout()
            box.setSpacing(2)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #475569;")
            box.addWidget(lbl)
            box.addWidget(widget)
            return box

        filters_grid.addLayout(make_filter_group("Registered Year", self.cb_year), 0, 0)
        filters_grid.addLayout(make_filter_group("Drop Out", self.cb_dropout), 0, 1)
        filters_grid.addLayout(make_filter_group("Theory Exam", self.cb_theory), 0, 2)
        filters_grid.addLayout(make_filter_group("NVQ Level 3", self.cb_l3), 0, 3)
        filters_grid.addLayout(make_filter_group("NVQ Level 4", self.cb_l4), 0, 4)

        # Tier 2: Placement, Employment & Reset Button
        self.cb_has_ojt = QComboBox()
        self.cb_has_ojt.addItems(["All", "Yes", "No"])
        self.cb_has_ojt.currentIndexChanged.connect(self.on_filter_changed)

        self.cb_has_job = QComboBox()
        self.cb_has_job.addItems(["All", "Yes", "No"])
        self.cb_has_job.currentIndexChanged.connect(self.on_filter_changed)

        reset_btn = QPushButton("Reset Filters")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setProperty("class", "SecondaryButton")
        reset_btn.clicked.connect(self.reset_filters)

        filters_grid.addLayout(make_filter_group("OJT Placed", self.cb_has_ojt), 1, 0)
        filters_grid.addLayout(make_filter_group("Employed", self.cb_has_job), 1, 1)

        reset_box = QVBoxLayout()
        reset_box.setSpacing(2)
        reset_box.addWidget(QLabel(" "))
        reset_box.addWidget(reset_btn)
        filters_grid.addLayout(reset_box, 1, 2)

        panel_layout.addLayout(filters_grid)
        main_layout.addWidget(filter_panel)

        # 3. Selection Action Bar & Table Stats Header
        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        self.lbl_selected_info = QLabel("No student selected — Click any record or double-click to view dossier")
        self.lbl_selected_info.setStyleSheet("color: #64748B; font-size: 12px; font-style: italic;")
        action_bar.addWidget(self.lbl_selected_info, 1)

        self.btn_action_view = QPushButton("View Dossier")
        self.btn_action_view.setProperty("class", "PrimaryButton")
        self.btn_action_view.setEnabled(False)
        self.btn_action_view.clicked.connect(self.on_action_bar_view)

        self.btn_action_edit = QPushButton("Edit Record")
        self.btn_action_edit.setProperty("class", "SecondaryButton")
        self.btn_action_edit.setEnabled(False)
        self.btn_action_edit.clicked.connect(self.on_action_bar_edit)

        self.btn_action_delete = QPushButton("Delete")
        self.btn_action_delete.setProperty("class", "DangerButton")
        self.btn_action_delete.setEnabled(False)
        self.btn_action_delete.clicked.connect(self.on_action_bar_delete)

        action_bar.addWidget(self.btn_action_view)
        action_bar.addWidget(self.btn_action_edit)
        action_bar.addWidget(self.btn_action_delete)
        main_layout.addLayout(action_bar)

        # 4. Students Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID Number", "Student Name", "Year", "Phone Number", 
            "Drop Out", "Theory Pass", "NVQ L3", "NVQ L4", 
            "OJT Place", "Job Place", "Actions"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)
        main_layout.addWidget(self.table, 1)

        # 5. Pagination Footer
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(4, 0, 4, 0)
        pagination_layout.setSpacing(10)

        self.lbl_record_count = QLabel("Showing 0 students")
        self.lbl_record_count.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 500;")
        pagination_layout.addWidget(self.lbl_record_count)

        pagination_layout.addStretch(1)

        self.btn_prev_page = QPushButton("◀ Previous")
        self.btn_prev_page.setProperty("class", "SecondaryButton")
        self.btn_prev_page.setFixedHeight(30)
        self.btn_prev_page.clicked.connect(self.go_prev_page)
        pagination_layout.addWidget(self.btn_prev_page)

        self.lbl_page_info = QLabel("Page 1 of 1")
        self.lbl_page_info.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px; padding: 0 6px;")
        pagination_layout.addWidget(self.lbl_page_info)

        self.btn_next_page = QPushButton("Next ▶")
        self.btn_next_page.setProperty("class", "SecondaryButton")
        self.btn_next_page.setFixedHeight(30)
        self.btn_next_page.clicked.connect(self.go_next_page)
        pagination_layout.addWidget(self.btn_next_page)

        main_layout.addLayout(pagination_layout)

        # Initialize Data
        self.populate_years_dropdown()
        self.refresh_data()

    def populate_years_dropdown(self):
        """Fetches unique registered years and updates dropdown options."""
        self.cb_year.blockSignals(True)
        current = self.cb_year.currentText()
        self.cb_year.clear()
        self.cb_year.addItem("All Years")
        years = self.student_service.get_unique_registered_years()
        for yr in years:
            self.cb_year.addItem(yr)
        idx = self.cb_year.findText(current)
        if idx >= 0:
            self.cb_year.setCurrentIndex(idx)
        else:
            self.cb_year.setCurrentIndex(0)
        self.cb_year.blockSignals(False)

    def on_search_changed(self):
        self.current_page = 1
        self.refresh_data()

    def on_filter_changed(self):
        self.current_page = 1
        self.refresh_data()

    def reset_filters(self):
        """Clears all inputs and resets filters."""
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)

        for cb in (self.cb_year, self.cb_dropout, self.cb_theory, self.cb_l3, 
                   self.cb_l4, self.cb_has_ojt, self.cb_has_job):
            cb.blockSignals(True)
            cb.setCurrentIndex(0)
            cb.blockSignals(False)

        self.current_page = 1
        self.refresh_data()

    def refresh_data(self):
        """Retrieves and populates the table based on active search/filters with pagination."""
        search_text = self.search_input.text().strip()
        
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

        # Query database for all matching records
        self.cached_students = self.student_service.search_and_filter_students(search_text, filters)
        total_count = len(self.cached_students)

        # Pagination calculations
        self.total_pages = max(1, (total_count + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

        start_idx = (self.current_page - 1) * self.PAGE_SIZE
        end_idx = min(start_idx + self.PAGE_SIZE, total_count)
        page_students = self.cached_students[start_idx:end_idx]

        # Update table rows
        self.table.setRowCount(0)
        self.selected_student_id = None
        self._update_action_bar_state(None)

        for row_idx, student in enumerate(page_students):
            self.table.insertRow(row_idx)

            # Text items
            self.table.setItem(row_idx, 0, QTableWidgetItem(student.id_number))
            self.table.setItem(row_idx, 1, QTableWidgetItem(student.name_of_the_student))
            self.table.setItem(row_idx, 2, QTableWidgetItem(student.year_of_registered or ""))
            self.table.setItem(row_idx, 3, QTableWidgetItem(student.phone_number or ""))
            
            # Status items
            def create_status_item(val):
                item = QTableWidgetItem(val or "")
                item.setTextAlignment(Qt.AlignCenter)
                if val == "Yes":
                    item.setForeground(QColor("#059669"))
                elif val == "No":
                    item.setForeground(QColor("#DC2626"))
                elif val == "Pending":
                    item.setForeground(QColor("#2563EB"))
                return item
            
            self.table.setItem(row_idx, 4, create_status_item(student.drop_out))
            self.table.setItem(row_idx, 5, create_status_item(student.theory_pass))
            self.table.setItem(row_idx, 6, create_status_item(student.nvq_l3))
            self.table.setItem(row_idx, 7, create_status_item(student.nvq_l4))
            self.table.setItem(row_idx, 8, QTableWidgetItem(student.ojt_place or ""))
            self.table.setItem(row_idx, 9, QTableWidgetItem(student.job_place or ""))

            # Action Buttons Cell
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)

            btn_view = QPushButton("View")
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.setProperty("student_id", student.id)
            btn_view.setProperty("class", "TableActionView")
            btn_view.clicked.connect(self.on_view_clicked)
 
            btn_edit = QPushButton("Edit")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setProperty("student_id", student.id)
            btn_edit.setProperty("class", "TableActionEdit")
            btn_edit.clicked.connect(self.on_edit_clicked)
 
            btn_delete = QPushButton("Delete")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.setProperty("student_id", student.id)
            btn_delete.setProperty("class", "TableActionDelete")
            btn_delete.clicked.connect(self.on_delete_clicked)

            actions_layout.addWidget(btn_view)
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            
            self.table.setCellWidget(row_idx, 10, actions_widget)

        # Update Pagination Controls
        if total_count == 0:
            self.lbl_record_count.setText("No matching students found")
        else:
            self.lbl_record_count.setText(f"Showing {start_idx + 1}–{end_idx} of {total_count} students")
            
        self.lbl_page_info.setText(f"Page {self.current_page} of {self.total_pages}")
        self.btn_prev_page.setEnabled(self.current_page > 1)
        self.btn_next_page.setEnabled(self.current_page < self.total_pages)

        # Column widths
        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(2, 70)
        self.table.setColumnWidth(3, 115)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 90)
        self.table.setColumnWidth(6, 85)
        self.table.setColumnWidth(7, 85)
        self.table.setColumnWidth(10, 160)

    def on_table_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self._update_action_bar_state(None)
            return

        row = selected_rows[0].row()
        start_idx = (self.current_page - 1) * self.PAGE_SIZE
        if start_idx + row < len(self.cached_students):
            student = self.cached_students[start_idx + row]
            self._update_action_bar_state(student)

    def on_table_double_clicked(self, row, col):
        start_idx = (self.current_page - 1) * self.PAGE_SIZE
        if start_idx + row < len(self.cached_students):
            student = self.cached_students[start_idx + row]
            self.view_student_requested.emit(student.id)

    def _update_action_bar_state(self, student):
        if student:
            self.selected_student_id = student.id
            self.lbl_selected_info.setText(
                f"Selected: <b>{student.name_of_the_student}</b> (ID: {student.id_number})"
            )
            self.lbl_selected_info.setStyleSheet("color: #0F172A; font-size: 13px;")
            self.btn_action_view.setEnabled(True)
            self.btn_action_edit.setEnabled(True)
            self.btn_action_delete.setEnabled(True)
        else:
            self.selected_student_id = None
            self.lbl_selected_info.setText("No student selected — Click any record or double-click to view dossier")
            self.lbl_selected_info.setStyleSheet("color: #64748B; font-size: 12px; font-style: italic;")
            self.btn_action_view.setEnabled(False)
            self.btn_action_edit.setEnabled(False)
            self.btn_action_delete.setEnabled(False)

    def on_action_bar_view(self):
        if self.selected_student_id:
            self.view_student_requested.emit(self.selected_student_id)

    def on_action_bar_edit(self):
        if self.selected_student_id:
            self.edit_student_requested.emit(self.selected_student_id)

    def on_action_bar_delete(self):
        if self.selected_student_id:
            self._execute_delete_student(self.selected_student_id)

    def go_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()

    def go_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_data()

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
            self._execute_delete_student(student_id)

    def _execute_delete_student(self, student_id: int):
        student = self.student_service.get_student_by_id(student_id)
        if not student:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete Record", 
            f"Are you sure you want to permanently delete the student records for '{student.name_of_the_student}' (ID: {student.id_number})?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
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
