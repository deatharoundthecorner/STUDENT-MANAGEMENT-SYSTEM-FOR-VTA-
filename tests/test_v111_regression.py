import os
import sys
import unittest
import tempfile
import sqlite3
import logging
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

import utils.paths
from utils.security_logging import get_security_logger, log_security_event
from database.db import DatabaseManager
from services.auth_service import AuthService
from services.student_service import StudentService
from services.photo_service import PhotoService
from models.student import Student
from ui.student_form_page import StudentFormPage
from ui.login_window import LoginWindow


class V111RegressionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.orig_sms_data_dir = os.environ.get("SMS_DATA_DIR")
        self.temp_dir = tempfile.TemporaryDirectory(prefix="sms_v111_test_", ignore_cleanup_errors=True)
        self.qa_dir = Path(self.temp_dir.name).resolve()
        os.environ["SMS_DATA_DIR"] = str(self.qa_dir)

        # Reset DatabaseManager to point to isolated temp database
        DatabaseManager._instance = None
        DatabaseManager._db_path = None
        DatabaseManager.close_all_connections()
        DatabaseManager().initialize_database()

    def tearDown(self):
        # Close handlers and connections to release locks on Windows
        for logger_name in ["student_management_system.security", "root"]:
            l = logging.getLogger(logger_name)
            for h in list(l.handlers):
                h.close()
                l.removeHandler(h)
        DatabaseManager.close_all_connections()

        if self.orig_sms_data_dir is not None:
            os.environ["SMS_DATA_DIR"] = self.orig_sms_data_dir
        else:
            os.environ.pop("SMS_DATA_DIR", None)

        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    # 1. Development storage location
    def test_01_development_storage_location(self):
        if "SMS_DATA_DIR" in os.environ:
            del os.environ["SMS_DATA_DIR"]
        try:
            _, dev_dir = utils.paths.get_paths()
            expected_dev = utils.paths.get_user_data_dir() / "StudentManagementSystem-Dev"
            self.assertEqual(dev_dir, expected_dev)
        finally:
            os.environ["SMS_DATA_DIR"] = str(self.qa_dir)

    # 2. Installed storage location
    def test_02_installed_storage_location(self):
        if "SMS_DATA_DIR" in os.environ:
            del os.environ["SMS_DATA_DIR"]
        setattr(sys, "frozen", True)
        setattr(sys, "executable", r"C:\Program Files\Student Management System\StudentManagementSystem.exe")
        try:
            _, frozen_dir = utils.paths.get_paths()
            expected_prod = utils.paths.get_user_data_dir() / "StudentManagementSystem"
            self.assertEqual(frozen_dir, expected_prod)
        finally:
            if hasattr(sys, "frozen"):
                delattr(sys, "frozen")
            os.environ["SMS_DATA_DIR"] = str(self.qa_dir)

    # 3. SMS_DATA_DIR override priority
    def test_03_sms_data_dir_override_priority(self):
        # Even if frozen is simulated, SMS_DATA_DIR must take top priority
        setattr(sys, "frozen", True)
        try:
            _, resolved_dir = utils.paths.get_paths()
            self.assertEqual(resolved_dir, self.qa_dir)
        finally:
            if hasattr(sys, "frozen"):
                delattr(sys, "frozen")

    # 4. Security logging isolation & redaction
    def test_04_security_logging_isolation(self):
        logger = get_security_logger()
        for h in list(logger.handlers):
            h.close()
            logger.removeHandler(h)
        logger = get_security_logger()
        log_security_event("Test security log with password=SuperSecretPassword123!")

        log_file = self.qa_dir / "logs" / "security.log"
        self.assertTrue(log_file.exists())
        content = log_file.read_text(encoding="utf-8")
        self.assertNotIn("SuperSecretPassword123!", content)
        self.assertIn("password=[REDACTED]", content)

    # 5. Fresh administrator setup
    def test_05_fresh_administrator_setup(self):
        auth = AuthService()
        self.assertTrue(auth.is_setup_required())

        success, msg = auth.create_admin_user("RegAdminQA", "ValidP@ssw0rd2026#")
        self.assertTrue(success, f"Failed to create admin: {msg}")
        self.assertFalse(auth.is_setup_required())

    # 6. Password hashing without plaintext persistence
    def test_06_password_hashing_without_plaintext_persistence(self):
        auth = AuthService()
        pwd = "ComplexP@ssphrase2026!"
        auth.create_admin_user("HashAuditUser", pwd)

        row = DatabaseManager().execute_read(
            "SELECT username, password_hash FROM users WHERE username = ?",
            ("HashAuditUser",)
        )
        self.assertEqual(len(row), 1)
        stored_hash = row[0]["password_hash"]

        # Must be Argon2id format
        self.assertTrue(stored_hash.startswith("$argon2id$"))
        # Plaintext password must never appear anywhere in stored hash
        self.assertNotIn(pwd, stored_hash)

        # Ensure authentication succeeds
        self.assertTrue(auth.authenticate("HashAuditUser", pwd))
        self.assertFalse(auth.authenticate("HashAuditUser", "WrongPassword!"))

    # 7. ADD MODE button interaction
    def test_07_add_mode_button_interaction(self):
        form = StudentFormPage()
        form.set_add_mode()
        self.assertFalse(form.is_edit_mode)
        self.assertEqual(form.btn_add_mode.text(), "ADD MODE")
        self.assertEqual(form.header_title.text(), "Register Student")

        # In ADD mode, clicking button without changes clears form and keeps add mode
        form.input_id.setText("")
        form.handle_add_mode_clicked()
        self.assertFalse(form.is_edit_mode)

    # 8. EDIT MODE to ADD MODE transition
    def test_08_edit_mode_to_add_mode_transition(self):
        student_svc = StudentService()
        synth = Student(
            id_number="TEST-EDIT-001",
            name_of_the_student="Edit Transition Student",
            year_of_registered="2025"
        )
        sid = student_svc.add_student(synth)

        form = StudentFormPage()
        form.show()
        form.set_edit_mode(sid)
        self.assertTrue(form.is_edit_mode)
        self.assertEqual(form.edit_student_id, sid)
        self.assertEqual(form.btn_add_mode.text(), "+ Switch to Add Mode")
        self.assertEqual(form.mode_indicator.text(), "EDIT MODE")
        self.assertFalse(form.mode_indicator.isHidden())

        # Transition to ADD mode via button click
        form.handle_add_mode_clicked()
        self.assertFalse(form.is_edit_mode)
        self.assertIsNone(form.edit_student_id)
        self.assertEqual(form.btn_add_mode.text(), "ADD MODE")
        self.assertTrue(form.mode_indicator.isHidden())
        self.assertEqual(form.header_title.text(), "Register Student")

    # 9. Clearing previous student fields and photo state
    def test_09_clearing_previous_student_fields_and_photo(self):
        student_svc = StudentService()
        synth = Student(
            id_number="TEST-CLEAR-001",
            name_of_the_student="Clear Fields Student",
            year_of_registered="2024",
            phone_number="0779998877",
            private_address="789 Clear Lane",
            ojt_place="Clear OJT",
            job_place="Clear Job"
        )
        sid = student_svc.add_student(synth)

        form = StudentFormPage()
        form.set_edit_mode(sid)
        self.assertEqual(form.input_id.text(), "TEST-CLEAR-001")
        self.assertEqual(form.input_name.text(), "Clear Fields Student")

        # Switch to ADD MODE
        form.handle_add_mode_clicked()
        self.assertEqual(form.input_id.text(), "")
        self.assertEqual(form.input_name.text(), "")
        self.assertEqual(form.input_year.text(), "")
        self.assertEqual(form.input_phone.text(), "")
        self.assertEqual(form.input_address.text(), "")
        self.assertEqual(form.input_ojt_place.text(), "")
        self.assertEqual(form.input_job_place.text(), "")
        self.assertEqual(form.temp_photo_path, "")
        self.assertEqual(form.existing_photo_path, "")
        self.assertFalse(form.photo_removed)

    # 10. Unsaved-change confirmation (accept and cancel)
    def test_10_unsaved_change_confirmation(self):
        orig_question = QMessageBox.question
        try:
            form = StudentFormPage()
            form.set_add_mode()
            form.input_id.setText("UNSAVED-123")
            form.input_name.setText("Unsaved Name")
            self.assertTrue(form.has_unsaved_changes())

            # Case A: User clicks Cancel (No) -> Keep unsaved data
            QMessageBox.question = lambda *args, **kwargs: QMessageBox.No
            form.handle_add_mode_clicked()
            self.assertEqual(form.input_id.text(), "UNSAVED-123")
            self.assertEqual(form.input_name.text(), "Unsaved Name")

            # Case B: User clicks OK (Yes) -> Discard and reset
            QMessageBox.question = lambda *args, **kwargs: QMessageBox.Yes
            form.handle_add_mode_clicked()
            self.assertEqual(form.input_id.text(), "")
            self.assertEqual(form.input_name.text(), "")
            self.assertFalse(form.has_unsaved_changes())
        finally:
            QMessageBox.question = orig_question

    # 11. Preventing duplicate student IDs
    def test_11_preventing_duplicate_student_ids(self):
        student_svc = StudentService()
        synth1 = Student(
            id_number="UNIQUE-001",
            name_of_the_student="First Student",
            year_of_registered="2026"
        )
        student_svc.add_student(synth1)

        synth2 = Student(
            id_number="UNIQUE-001",  # Same ID!
            name_of_the_student="Duplicate Student",
            year_of_registered="2026"
        )
        with self.assertRaises(ValueError):
            student_svc.add_student(synth2)

    # 12. Inserting a new student without modifying the previous record
    def test_12_insert_new_student_without_modifying_previous(self):
        student_svc = StudentService()
        synth1 = Student(
            id_number="RECORD-001",
            name_of_the_student="Original Unchanged Record",
            year_of_registered="2025",
            phone_number="0771234567"
        )
        sid1 = student_svc.add_student(synth1)

        synth2 = Student(
            id_number="RECORD-002",
            name_of_the_student="Second New Record",
            year_of_registered="2026",
            phone_number="0777654321"
        )
        sid2 = student_svc.add_student(synth2)

        # Verify sid1 is completely intact
        rec1 = student_svc.get_student_by_id(sid1)
        self.assertEqual(rec1.id_number, "RECORD-001")
        self.assertEqual(rec1.name_of_the_student, "Original Unchanged Record")
        self.assertEqual(rec1.year_of_registered, "2025")
        self.assertEqual(rec1.phone_number, "0771234567")

        # Verify sid2 was correctly created
        rec2 = student_svc.get_student_by_id(sid2)
        self.assertEqual(rec2.id_number, "RECORD-002")
        self.assertEqual(rec2.name_of_the_student, "Second New Record")
        self.assertEqual(rec2.year_of_registered, "2026")
        self.assertEqual(rec2.phone_number, "0777654321")


if __name__ == "__main__":
    unittest.main()
