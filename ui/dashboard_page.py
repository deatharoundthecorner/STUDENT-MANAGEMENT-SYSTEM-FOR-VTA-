# ui/dashboard_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QFrame, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt
from services.student_service import StudentService


class DashboardCard(QFrame):
    def __init__(self, title: str, value: str, icon_symbol: str, color_hex: str, subtitle: str = ""):
        super().__init__()
        self.setObjectName("DashboardCard")
        self.setProperty("class", "DashboardCard")
        self.setMinimumHeight(105)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)
 
        # Left Accent Bar
        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
        layout.addWidget(accent_bar)
 
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
            self.sub_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            text_layout.addWidget(self.sub_lbl)
        else:
            self.sub_lbl = None

        text_layout.addStretch(1)
        layout.addLayout(text_layout, 1)
 
        # Icon / Badge Container
        badge = QFrame()
        badge.setFixedSize(48, 48)
        badge.setStyleSheet(
            f"background-color: {color_hex}1A; border: 1px solid {color_hex}33; border-radius: 24px;"
        )
        badge_layout = QVBoxLayout(badge)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel(icon_symbol)
        self.icon_lbl.setStyleSheet(f"font-size: 20px; color: {color_hex}; font-weight: bold;")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        badge_layout.addWidget(self.icon_lbl)

        layout.addWidget(badge, alignment=Qt.AlignRight | Qt.AlignVCenter)

    def update_value(self, new_val):
        self.value_lbl.setText(str(new_val))


class DashboardPage(QWidget):
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

        # Responsive Cards Grid
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)

        # 7 Database-Derived Milestone Cards
        self.card_total = DashboardCard("Total Enrolled", "0", "👥", "#2563EB", "Active + past registered")
        self.card_dropout = DashboardCard("Drop Out", "0", "⚠️", "#DC2626", "Discontinued training")
        self.card_theory = DashboardCard("Theory Exam Pass", "0", "✓", "#059669", "Written assessment passed")
        self.card_l3 = DashboardCard("NVQ Level 3", "0", "★", "#7C3AED", "NVQ-3 certification complete")
        self.card_l4 = DashboardCard("NVQ Level 4", "0", "🏆", "#DB2777", "NVQ-4 supervisory level")
        self.card_ojt = DashboardCard("In OJT Placement", "0", "💼", "#0891B2", "On-the-job industrial training")
        self.card_job = DashboardCard("Secured Employment", "0", "🚀", "#D97706", "Graduates in permanent jobs")

        self.cards = [
            self.card_total, self.card_dropout, self.card_theory, self.card_l3,
            self.card_l4, self.card_ojt, self.card_job
        ]

        self._relayout_grid(1200)

        main_layout.addLayout(self.grid_layout)
        main_layout.addStretch(1)

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

    def _relayout_grid(self, width: int):
        """Rearranges cards into 4 columns (wide) or 2 columns (medium/narrow) without empty holes."""
        # Clear existing items from grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if width >= 1050:
            # 4 Columns x 2 Rows Layout
            # Row 0: 4 Cards
            self.grid_layout.addWidget(self.card_total, 0, 0)
            self.grid_layout.addWidget(self.card_dropout, 0, 1)
            self.grid_layout.addWidget(self.card_theory, 0, 2)
            self.grid_layout.addWidget(self.card_l3, 0, 3)

            # Row 1: 3 Cards (Card 7 spans remaining 2 columns to balance grid)
            self.grid_layout.addWidget(self.card_l4, 1, 0)
            self.grid_layout.addWidget(self.card_ojt, 1, 1)
            self.grid_layout.addWidget(self.card_job, 1, 2, 1, 2)
        else:
            # 2 Columns x 4 Rows Layout
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
        self.card_total.update_value(stats.get("total_students", 0))
        self.card_dropout.update_value(stats.get("drop_out_students", 0))
        self.card_theory.update_value(stats.get("theory_pass_students", 0))
        self.card_l3.update_value(stats.get("nvq_l3_completed", 0))
        self.card_l4.update_value(stats.get("nvq_l4_completed", 0))
        self.card_ojt.update_value(stats.get("students_with_ojt", 0))
        self.card_job.update_value(stats.get("students_with_job", 0))

class_name = "DashboardPage"
