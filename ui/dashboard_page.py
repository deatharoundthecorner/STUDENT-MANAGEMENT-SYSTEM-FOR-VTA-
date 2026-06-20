# ui/dashboard_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from services.student_service import StudentService

class DashboardCard(QFrame):
    def __init__(self, title: str, value: str, icon: str, color_hex: str):
        super().__init__()
        self.setObjectName("DashboardCard")
        self.setStyleSheet(f"""
            QFrame#DashboardCard {{
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Left Accent Bar
        accent_bar = QFrame()
        accent_bar.setFixedWidth(5)
        accent_bar.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
        layout.addWidget(accent_bar)

        # Text Block
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet("color: #1E293B; font-size: 28px; font-weight: 800;")
        
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.value_lbl)
        text_layout.addStretch(1)
        layout.addLayout(text_layout, 1)

        # Icon Block
        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setStyleSheet(f"font-size: 32px; color: {color_hex}; padding: 5px;")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_lbl)

    def update_value(self, new_val):
        self.value_lbl.setText(str(new_val))

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.student_service = StudentService()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Header Title
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Dashboard Overview")
        title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #1E2A38;")
        
        subtitle_label = QLabel("Real-time summary of student milestones, registrations, and employment status.")
        subtitle_label.setStyleSheet("font-size: 13px; color: #64748B;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        # Cards Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # We will create the 7 cards
        self.card_total = DashboardCard("Total Enrolled", "0", "👥", "#3B82F6") # Blue
        self.card_dropout = DashboardCard("Drop Out", "0", "⚠️", "#EF4444") # Red
        self.card_theory = DashboardCard("Theory Exam Pass", "0", "📝", "#10B981") # Emerald Green
        self.card_l3 = DashboardCard("NVQ Level 3 Completed", "0", "🎓", "#8B5CF6") # Purple
        self.card_l4 = DashboardCard("NVQ Level 4 Completed", "0", "🏆", "#EC4899") # Pink
        self.card_ojt = DashboardCard("In OJT Placement", "0", "💼", "#06B6D4") # Cyan
        self.card_job = DashboardCard("Secured Employment", "0", "🚀", "#F59E0B") # Amber Orange

        # Place them in grid: 3 columns layout
        grid_layout.addWidget(self.card_total, 0, 0)
        grid_layout.addWidget(self.card_dropout, 0, 1)
        grid_layout.addWidget(self.card_theory, 0, 2)
        grid_layout.addWidget(self.card_l3, 1, 0)
        grid_layout.addWidget(self.card_l4, 1, 1)
        grid_layout.addWidget(self.card_ojt, 1, 2)
        grid_layout.addWidget(self.card_job, 2, 0) # Span option is not strictly needed, but let's keep it clean
        
        # Empty space holders for layout filling
        spacer_card = QFrame()
        spacer_card.setStyleSheet("border: none; background: transparent;")
        grid_layout.addWidget(spacer_card, 2, 1)
        grid_layout.addWidget(spacer_card, 2, 2)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch(1)

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
