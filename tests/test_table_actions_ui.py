import sys
import unittest
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor

import utils.paths
from database.db import DatabaseManager
from services.student_service import StudentService
from models.student import Student
from ui.students_page import StudentsPage
from ui.styles import apply_theme

class TestTableActionsUIRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.tmp_dir = tempfile.TemporaryDirectory(prefix="sms_test_table_actions_")
        cls.tmp_path = Path(cls.tmp_dir.name)
        cls.db_path = cls.tmp_path / "test_table_actions.db"
        utils.paths.get_paths = lambda: (Path(".").resolve(), cls.tmp_path)
        DatabaseManager.set_db_path(cls.db_path)
        DatabaseManager().initialize_database()

        student_svc = StudentService()
        dummy = Student(
            id=1,
            id_number="200012345678",
            name_of_the_student="Test Regression Student",
            year_of_registered="2024",
            phone_number="0771122334"
        )
        student_svc.add_student(dummy)

    @classmethod
    def tearDownClass(cls):
        DatabaseManager.close_all_connections()
        try:
            cls.tmp_dir.cleanup()
        except Exception:
            pass

    def test_row_action_buttons_visibility_and_dimensions(self):
        """Verifies that table row action buttons have visible labels and are not clipped."""
        for theme in ["day", "night"]:
            with self.subTest(theme=theme):
                apply_theme(self.app, theme)

                page = StudentsPage()
                page.resize(1280, 800)
                page.show()

                page.refresh_data()

                for _ in range(5):
                    self.app.processEvents()

                self.assertGreaterEqual(page.table.rowCount(), 1, "Table has no rows.")
                row_height = page.table.rowHeight(0)
                self.assertGreaterEqual(row_height, 40, f"Table row height {row_height}px is too cramped for buttons.")

                actions_cell = page.table.cellWidget(0, 10)
                self.assertIsNotNone(actions_cell, "Actions cellWidget missing at (0, 10)")

                cell_geom = actions_cell.geometry()
                self.assertGreaterEqual(cell_geom.height(), 26, f"Actions cell height {cell_geom.height()}px causes vertical clipping.")
                self.assertGreaterEqual(cell_geom.width(), 190, f"Actions cell width {cell_geom.width()}px too narrow for 3 action buttons.")

                buttons = actions_cell.findChildren(QPushButton)
                self.assertEqual(len(buttons), 3, "Expected exactly 3 action buttons (View, Edit, Delete).")

                btn_texts = [b.text() for b in buttons]
                self.assertEqual(btn_texts, ["View", "Edit", "Delete"], "Button text missing or incorrect.")

                for b in buttons:
                    self.assertTrue(b.isVisible(), f"Button '{b.text()}' is not visible.")
                    self.assertFalse(b.icon().isNull(), f"Button '{b.text()}' is missing its SVG icon.")
                    b_geom = b.geometry()
                    self.assertGreaterEqual(b_geom.width(), 45, f"Button '{b.text()}' width {b_geom.width()}px is truncated.")
                    self.assertGreaterEqual(b_geom.height(), 24, f"Button '{b.text()}' height {b_geom.height()}px is truncated.")
                    self.assertLessEqual(b_geom.height(), cell_geom.height() + 4, f"Button '{b.text()}' height exceeds cell container.")

                    # Pixel-level render validation: Button must visibly draw non-background text/icon pixels
                    pix = b.grab()
                    qimg = pix.toImage()
                    w, h = qimg.width(), qimg.height()
                    bg_col = qimg.pixelColor(w // 2, 4)
                    diff_count = 0
                    for y in range(4, h - 4):
                        for x in range(4, w - 4):
                            c = qimg.pixelColor(x, y)
                            if abs(c.red() - bg_col.red()) + abs(c.green() - bg_col.green()) + abs(c.blue() - bg_col.blue()) > 30:
                                diff_count += 1
                    self.assertGreater(diff_count, 40, f"Button '{b.text()}' ({theme}) has no visible text or icon pixels (empty outline defect).")

                page.close()

if __name__ == "__main__":
    unittest.main()
