# ui/dashboard_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QFrame, QScrollArea, QSizePolicy, QProgressBar, QPushButton)
from PySide6.QtCore import Qt, Signal, QSize
from ui.icons import get_icon, get_pixmap
from services.student_service import StudentService


class DashboardCard(QFrame):
    def __init__(self, title: str, value: str, icon_symbol: str, color_hex: str, subtitle: str = ""):
        super().__init__()
        self.setObjectName("DashboardCard")
        self.setProperty("class", "DashboardCard")
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
 
        # Metric Info Block
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setProperty("class", "CardTitle")
        self.title_lbl.setWordWrap(True)
        
        self.value_lbl = QLabel(str(value))
        self.value_lbl.setProperty("class", "CardValue")
        
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.value_lbl)

        if subtitle:
            self.sub_lbl = QLabel(subtitle)
            self.sub_lbl.setProperty("class", "CardSubtitle")
            text_layout.addWidget(self.sub_lbl)
        else:
            self.sub_lbl = None

        text_layout.addStretch(1)
        layout.addLayout(text_layout, 1)
 
        # Clean Neutral Badge Container (eliminates saturated rainbow alpha rings)
        badge = QFrame()
        badge.setProperty("class", "CardBadge")
        badge.setFixedSize(44, 44)
        badge_layout = QVBoxLayout(badge)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel()
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        if icon_symbol in ["academic", "user_x", "check_circle", "award", "certificate", "briefcase", "trending_up"]:
            self.icon_lbl.setPixmap(get_pixmap(icon_symbol, color=color_hex, stroke_width=1.75, size=22))
        else:
            self.icon_lbl.setText(icon_symbol)
            self.icon_lbl.setStyleSheet(f"font-size: 18px; color: {color_hex}; font-weight: bold;")
        badge_layout.addWidget(self.icon_lbl)

        layout.addWidget(badge, alignment=Qt.AlignRight | Qt.AlignVCenter)

    def update_value(self, new_val, subtitle: str = ""):
        self.value_lbl.setText(str(new_val))
        if subtitle and self.sub_lbl:
            self.sub_lbl.setText(subtitle)


class DashboardPage(QWidget):
    add_student_requested = Signal()
    import_requested = Signal()

    def __init__(self):
        super().__init__()
        self.student_service = StudentService()
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Scroll Area for responsive dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("DashboardScrollArea")
        
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(20)

        # Header Title Block
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Dashboard Overview")
        title_label.setProperty("class", "PageTitle")
        
        subtitle_label = QLabel("Real-time aggregate student milestones, institutional qualifications, and employment metrics.")
        subtitle_label.setProperty("class", "PageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        # 1. Deliberate Empty State Frame (shown when total_students == 0)
        self.empty_state_frame = QFrame()
        self.empty_state_frame.setObjectName("EmptyStateFrame")
        empty_layout = QVBoxLayout(self.empty_state_frame)
        empty_layout.setContentsMargins(36, 40, 36, 40)
        empty_layout.setSpacing(16)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_icon = QLabel()
        empty_icon.setPixmap(get_pixmap("academic", color="#94A3B8", stroke_width=1.6, size=48))
        empty_icon.setObjectName("EmptyStateIcon")
        empty_icon.setAlignment(Qt.AlignCenter)

        empty_title = QLabel("No Student Records Yet")
        empty_title.setObjectName("EmptyStateTitle")
        empty_title.setAlignment(Qt.AlignCenter)

        empty_desc = QLabel(
            "This workstation database is ready for use but contains no enrolled students.\n"
            "Begin by registering your first student profile or importing an existing roster from Excel/CSV."
        )
        empty_desc.setObjectName("EmptyStateDescription")
        empty_desc.setAlignment(Qt.AlignCenter)

        empty_actions = QHBoxLayout()
        empty_actions.setSpacing(14)
        empty_actions.setAlignment(Qt.AlignCenter)

        btn_add = QPushButton("Register First Student")
        btn_add.setIcon(get_icon("add_student", color="#FFFFFF", size=18))
        btn_add.setIconSize(QSize(18, 18))
        btn_add.setProperty("class", "PrimaryButton")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedHeight(40)
        btn_add.clicked.connect(self._on_add_clicked)

        btn_imp = QPushButton("Batch Import Records")
        btn_imp.setIcon(get_icon("import", color="#475569", size=18))
        btn_imp.setIconSize(QSize(18, 18))
        btn_imp.setProperty("class", "SecondaryButton")
        btn_imp.setCursor(Qt.PointingHandCursor)
        btn_imp.setFixedHeight(40)
        btn_imp.clicked.connect(self._on_import_clicked)

        empty_actions.addWidget(btn_add)
        empty_actions.addWidget(btn_imp)

        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_desc)
        empty_layout.addSpacing(8)
        empty_layout.addLayout(empty_actions)

        main_layout.addWidget(self.empty_state_frame)

        # 2. Responsive Cards Grid Container (shown when total_students > 0)
        self.cards_container = QWidget()
        cards_vbox = QVBoxLayout(self.cards_container)
        cards_vbox.setContentsMargins(0, 0, 0, 0)
        cards_vbox.setSpacing(20)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)

        # 7 Database-Derived Milestone Cards with cohesive restrained palette
        self.card_total = DashboardCard("Total Enrolled", "0", "academic", "#2563EB", "Active + past registered")
        self.card_dropout = DashboardCard("Drop Out", "0", "user_x", "#DC2626", "Discontinued training")
        self.card_theory = DashboardCard("Theory Exam Pass", "0", "check_circle", "#059669", "Written assessment passed")
        self.card_l3 = DashboardCard("NVQ Level 3", "0", "award", "#4F46E5", "NVQ-3 certification complete")
        self.card_l4 = DashboardCard("NVQ Level 4", "0", "certificate", "#0D9488", "NVQ-4 supervisory level")
        self.card_ojt = DashboardCard("In OJT Placement", "0", "briefcase", "#0284C7", "On-the-job industrial training")
        self.card_job = DashboardCard("Secured Employment", "0", "trending_up", "#059669", "Graduates in permanent jobs")

        self.cards = [
            self.card_total, self.card_dropout, self.card_theory, self.card_l3,
            self.card_l4, self.card_ojt, self.card_job
        ]

        self._relayout_grid(1200)
        cards_vbox.addLayout(self.grid_layout)

        # 3. Institutional Training Pipeline & Milestone Progress Card
        self.progress_card = QFrame()
        self.progress_card.setProperty("class", "DashboardCard")
        prog_layout = QVBoxLayout(self.progress_card)
        prog_layout.setContentsMargins(24, 20, 24, 20)
        prog_layout.setSpacing(14)

        prog_title = QLabel("Institutional Training Pipeline & Milestone Rates")
        prog_title.setProperty("class", "SectionHeader")
        prog_layout.addWidget(prog_title)

        prog_desc = QLabel("Real-time completion and placement rates calculated from active database records:")
        prog_desc.setProperty("class", "BodyText")
        prog_layout.addWidget(prog_desc)

        prog_grid = QGridLayout()
        prog_grid.setHorizontalSpacing(20)
        prog_grid.setVerticalSpacing(12)

        def make_prog_row(title_text):
            lbl_title = QLabel(title_text)
            lbl_title.setStyleSheet("font-weight: 600; font-size: 12px;")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setFixedHeight(12)
            lbl_val = QLabel("0%")
            lbl_val.setStyleSheet("font-weight: 700; font-size: 12px; min-width: 45px;")
            lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            return lbl_title, bar, lbl_val

        self.lbl_p1_title, self.bar_p1, self.lbl_p1_val = make_prog_row("Theory Assessment Pass Rate")
        self.lbl_p2_title, self.bar_p2, self.lbl_p2_val = make_prog_row("NVQ Certification Rate (L3+)")
        self.lbl_p3_title, self.bar_p3, self.lbl_p3_val = make_prog_row("Industrial OJT Placement Rate")
        self.lbl_p4_title, self.bar_p4, self.lbl_p4_val = make_prog_row("Graduate Employment Rate")

        prog_grid.addWidget(self.lbl_p1_title, 0, 0)
        prog_grid.addWidget(self.bar_p1, 0, 1)
        prog_grid.addWidget(self.lbl_p1_val, 0, 2)

        prog_grid.addWidget(self.lbl_p2_title, 1, 0)
        prog_grid.addWidget(self.bar_p2, 1, 1)
        prog_grid.addWidget(self.lbl_p2_val, 1, 2)

        prog_grid.addWidget(self.lbl_p3_title, 2, 0)
        prog_grid.addWidget(self.bar_p3, 2, 1)
        prog_grid.addWidget(self.lbl_p3_val, 2, 2)

        prog_grid.addWidget(self.lbl_p4_title, 3, 0)
        prog_grid.addWidget(self.bar_p4, 3, 1)
        prog_grid.addWidget(self.lbl_p4_val, 3, 2)

        prog_grid.setColumnStretch(1, 1)
        prog_layout.addLayout(prog_grid)
        cards_vbox.addWidget(self.progress_card)

        main_layout.addWidget(self.cards_container)
        main_layout.addStretch(1)

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    def _on_add_clicked(self):
        main_win = self.window()
        if main_win and hasattr(main_win, "switch_to_page_index"):
            main_win.switch_to_page_index(2, prepare_add=True)
        self.add_student_requested.emit()

    def _on_import_clicked(self):
        main_win = self.window()
        if main_win and hasattr(main_win, "switch_to_page_index"):
            main_win.switch_to_page_index(3)
        self.import_requested.emit()

    def _relayout_grid(self, width: int):
        """Rearranges cards into 4 columns (wide) or 2 columns (medium/narrow) without empty holes."""
        mode = "wide" if width >= 1050 else "narrow"
        if getattr(self, "_current_layout_mode", None) == mode:
            return
        self._current_layout_mode = mode

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if mode == "wide":
            self.grid_layout.addWidget(self.card_total, 0, 0)
            self.grid_layout.addWidget(self.card_dropout, 0, 1)
            self.grid_layout.addWidget(self.card_theory, 0, 2)
            self.grid_layout.addWidget(self.card_l3, 0, 3)

            self.grid_layout.addWidget(self.card_l4, 1, 0)
            self.grid_layout.addWidget(self.card_ojt, 1, 1)
            self.grid_layout.addWidget(self.card_job, 1, 2, 1, 2)
        else:
            self.grid_layout.addWidget(self.card_total, 0, 0)
            self.grid_layout.addWidget(self.card_dropout, 0, 1)
            self.grid_layout.addWidget(self.card_theory, 1, 0)
            self.grid_layout.addWidget(self.card_l3, 1, 1)
            self.grid_layout.addWidget(self.card_l4, 2, 0)
            self.grid_layout.addWidget(self.card_ojt, 2, 1)
            self.grid_layout.addWidget(self.card_job, 3, 0, 1, 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout_grid(event.size().width())

    def refresh_data(self):
        """Fetches latest numbers from SQLite and updates card UI."""
        stats = self.student_service.get_dashboard_statistics()
        total = stats.get("total_students", 0)

        if total == 0:
            self.empty_state_frame.setVisible(True)
            self.cards_container.setVisible(False)
        else:
            self.empty_state_frame.setVisible(False)
            self.cards_container.setVisible(True)

            drop_out = stats.get("drop_out_students", 0)
            theory = stats.get("theory_pass_students", 0)
            l3 = stats.get("nvq_l3_completed", 0)
            l4 = stats.get("nvq_l4_completed", 0)
            ojt = stats.get("students_with_ojt", 0)
            job = stats.get("students_with_job", 0)

            active = max(0, total - drop_out)
            self.card_total.update_value(total, f"{active} active students")
            self.card_dropout.update_value(drop_out)
            self.card_theory.update_value(theory)
            self.card_l3.update_value(l3)
            self.card_l4.update_value(l4)
            self.card_ojt.update_value(ojt)
            self.card_job.update_value(job)

            # Update real percentage progress bars
            p1 = int(round((theory / total) * 100)) if total > 0 else 0
            p2 = int(round((l3 / total) * 100)) if total > 0 else 0
            p3 = int(round((ojt / total) * 100)) if total > 0 else 0
            p4 = int(round((job / total) * 100)) if total > 0 else 0

            self.bar_p1.setValue(p1)
            self.lbl_p1_val.setText(f"{p1}%")

            self.bar_p2.setValue(p2)
            self.lbl_p2_val.setText(f"{p2}%")

            self.bar_p3.setValue(p3)
            self.lbl_p3_val.setText(f"{p3}%")

            self.bar_p4.setValue(p4)
            self.lbl_p4_val.setText(f"{p4}%")

class_name = "DashboardPage"
