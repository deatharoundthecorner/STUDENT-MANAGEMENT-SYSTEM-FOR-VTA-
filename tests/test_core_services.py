import csv
import os
import sqlite3
import tempfile
import unittest
import zipfile
import importlib.util
import logging
import bcrypt
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication

from database.db import DatabaseManager
from models.student import Student
from services.auth_service import AuthService
from utils.security_logging import get_security_logger
from services.audit_service import AuditService
from services.session_lock_service import SessionLockController
from services.backup_service import BackupService
from services.export_service import ExportService
from services.import_service import ImportService
from services.photo_service import PhotoService
from services.settings_service import SettingsService
from services.student_service import StudentService
from ui.main_window import MainWindow


class CoreServicesTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.base_dir = Path(self.temp_dir.name)
        DatabaseManager.set_db_path(self.base_dir / "student_records.db")
        DatabaseManager().initialize_database()
        self.students = StudentService()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_crud_search_filter_and_duplicate_id(self):
        student = Student(
            id_number="TEST-001",
            name_of_the_student="Test Student",
            year_of_registered="2026",
            phone_number="+94 77 123 4567",
            ojt_place="Training Company",
            job_place="Employer",
        )
        student.id = self.students.add_student(student)

        self.assertEqual(self.students.get_student_by_id(student.id).id_number, "TEST-001")
        self.assertEqual(len(self.students.search_and_filter_students("Training", {})), 1)
        self.assertEqual(
            len(self.students.search_and_filter_students("", {"has_ojt": "Yes", "has_job": "Yes"})),
            1,
        )
        with self.assertRaises(ValueError):
            self.students.add_student(Student(id_number="TEST-001", name_of_the_student="Duplicate"))

        student.name_of_the_student = "Updated Student"
        self.assertTrue(self.students.update_student(student))
        self.assertEqual(self.students.get_student_by_id(student.id).name_of_the_student, "Updated Student")
        self.assertTrue(self.students.delete_student(student.id))
        self.assertIsNone(self.students.get_student_by_id(student.id))

    def test_authentication_and_password_change(self):
        auth = AuthService()
        self.assertTrue(auth.create_admin_user("admin", "StrongPass!123")[0])
        self.assertTrue(auth.authenticate("admin", "StrongPass!123"))
        self.assertFalse(auth.authenticate("admin", "incorrect"))
        self.assertTrue(auth.change_password("admin", "StrongPass!123", "ChangedPass!456")[0])
        self.assertTrue(auth.authenticate("admin", "ChangedPass!456"))
        self.assertFalse(auth.authenticate("admin", "StrongPass!123"))
        row = DatabaseManager().execute_read("SELECT password_hash FROM users WHERE username = ?", ("admin",))[0]
        self.assertNotEqual(row["password_hash"], "ChangedPass!456")

    def test_settings_table_and_values(self):
        settings = SettingsService()
        settings.set_setting("theme", "night")
        self.assertEqual(settings.get_setting("theme"), "night")
        self.assertEqual(settings.get_setting("missing", "fallback"), "fallback")

    def test_import_validation_and_export_formats(self):
        csv_path = self.base_dir / "students.csv"
        csv_path.write_text(
            "ID_NUMBER,NAME_OF_THE_STUDENT,PHONE_NUMBER,THEORY_PASS\n"
            "IMPORT-001,Imported Student,12345,yes\n"
            "IMPORT-002,Invalid Student,xx,No\n",
            encoding="utf-8",
        )
        stats = ImportService().import_file(str(csv_path))
        self.assertEqual(stats["success"], 1)
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(self.students.get_student_by_id_number("IMPORT-001").theory_pass, "Yes")

        students = self.students.get_all_students()
        exporter = ExportService()
        csv_output = self.base_dir / "students-out.csv"
        xlsx_output = self.base_dir / "students-out.xlsx"
        pdf_output = self.base_dir / "students-out.pdf"
        exporter.export_to_csv(students, str(csv_output))
        exporter.export_to_excel(students, str(xlsx_output))
        exporter.export_all_to_pdf(students, str(pdf_output))
        self.assertIn("ID_NUMBER", csv_output.read_text(encoding="utf-8"))
        self.assertGreater(xlsx_output.stat().st_size, 0)
        self.assertTrue(pdf_output.read_bytes().startswith(b"%PDF"))

    @unittest.skipUnless(importlib.util.find_spec("xlwt"), "xlwt is required to generate the legacy XLS fixture")
    def test_legacy_xls_import(self):
        import xlwt

        xls_path = self.base_dir / "students.xls"
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("Students")
        for column, value in enumerate(("ID_NUMBER", "NAME_OF_THE_STUDENT", "THEORY_PASS")):
            sheet.write(0, column, value)
        for column, value in enumerate(("XLS-001", "Legacy Student", "Yes")):
            sheet.write(1, column, value)
        workbook.save(str(xls_path))

        stats = ImportService().import_file(str(xls_path))
        self.assertEqual(stats["success"], 1)
        self.assertEqual(self.students.get_student_by_id_number("XLS-001").theory_pass, "Yes")

    def test_photo_formats_fallback_and_cleanup(self):
        photo_service = PhotoService()
        photo_service.writable_dir = self.base_dir
        photo_service.base_dir = self.base_dir
        photo_service.photos_dir = self.base_dir / "student_photos"
        photo_service.assets_dir = self.base_dir / "assets"
        photo_service.photos_dir.mkdir()
        photo_service.assets_dir.mkdir()
        photo_service.default_avatar_path = self.base_dir / "assets" / "default_avatar.png"
        Image.new("RGB", (20, 20), "white").save(self.base_dir / "source.png")
        for extension in ("jpg", "jpeg", "png"):
            source = self.base_dir / f"source.{extension}"
            Image.new("RGB", (20, 20), "white").save(source)
            relative = photo_service.save_photo(str(source), "PHOTO-001")
            self.assertTrue((self.base_dir / relative).exists())
            photo_service.delete_photo(relative)
        self.assertTrue(photo_service.get_absolute_path("").endswith("default_avatar.png"))
        self.assertTrue(photo_service.get_absolute_path("student_photos/missing.png").endswith("default_avatar.png"))

    def test_backup_restore_and_malicious_archive_rejection(self):
        self.students.add_student(Student(id_number="BACKUP-001", name_of_the_student="Before Backup"))
        backup = BackupService()
        backup.base_dir = self.base_dir
        backup.backups_dir = self.base_dir / "backups"
        backup.photos_dir = self.base_dir / "student_photos"
        backup.backups_dir.mkdir()
        backup.photos_dir.mkdir()
        nested_photo_dir = backup.photos_dir / "nested"
        nested_photo_dir.mkdir()
        (nested_photo_dir / "photo.txt").write_text("photo", encoding="utf-8")

        success, backup_path = backup.create_backup()
        self.assertTrue(success)
        self.students.add_student(Student(id_number="BACKUP-002", name_of_the_student="After Backup"))
        success, _ = backup.restore_backup(backup_path)
        self.assertTrue(success)
        self.assertIsNone(self.students.get_student_by_id_number("BACKUP-002"))
        self.assertTrue((backup.photos_dir / "nested" / "photo.txt").exists())

        malicious = self.base_dir / "malicious.zip"
        with zipfile.ZipFile(malicious, "w") as archive:
            archive.write(self.base_dir / "student_records.db", arcname="student_records.db")
            archive.writestr("../outside.txt", "must not extract")
        success, message = backup.restore_backup(str(malicious))
        self.assertFalse(success)
        self.assertIn("Unsafe archive path", message)
        self.assertFalse((self.base_dir.parent / "outside.txt").exists())

        invalid = self.base_dir / "invalid.zip"
        invalid.write_bytes(b"not a zip archive")
        success, _ = backup.restore_backup(str(invalid))
        self.assertFalse(success)

        missing_db = self.base_dir / "missing-db.zip"
        with zipfile.ZipFile(missing_db, "w") as archive:
            archive.writestr("student_photos/placeholder.txt", "photo")
        success, _ = backup.restore_backup(str(missing_db))
        self.assertFalse(success)

        corrupt_db = self.base_dir / "corrupt-db.zip"
        with zipfile.ZipFile(corrupt_db, "w") as archive:
            archive.writestr("student_records.db", b"not sqlite")
        success, _ = backup.restore_backup(str(corrupt_db))
        self.assertFalse(success)

    def test_malformed_import_and_unicode_student(self):
        broken_csv = self.base_dir / "broken.csv"
        broken_csv.write_bytes(b"\xff\xfe\x00\x01")
        stats = ImportService().import_file(str(broken_csv))
        self.assertEqual(stats["success"], 0)
        self.assertTrue(stats["errors"])

        student = Student(id_number="UNICODE-001", name_of_the_student="Zoë 山田 — Student")
        student.id = self.students.add_student(student)
        self.assertEqual(self.students.get_student_by_id(student.id).name_of_the_student, student.name_of_the_student)

    def test_programmatic_edit_navigation_preserves_edit_mode(self):
        student = Student(id_number="UI-001", name_of_the_student="Edit Me")
        student.id = self.students.add_student(student)
        app = QApplication.instance() or QApplication([])
        window = MainWindow()
        try:
            window.show_edit_student_form(student.id)
            self.assertTrue(window.page_student_form.is_edit_mode)
            self.assertEqual(window.page_student_form.input_name.text(), "Edit Me")
            self.assertEqual(window.page_student_form.edit_student_id, student.id)
        finally:
            window.close()
            app.processEvents()

    def test_setup_and_password_validation(self):
        auth = AuthService()
        self.assertTrue(auth.is_setup_required())
        self.assertIn("at least 8 characters", auth.validate_password("short")[1])
        self.assertTrue(auth.create_admin_user("opsadmin", "StrongPass!123")[0])
        self.assertFalse(auth.is_setup_required())
        self.assertTrue(auth.authenticate("opsadmin", "StrongPass!123"))
        self.assertFalse(auth.authenticate("opsadmin", "WrongPass!123"))

    def test_clean_first_run_opens_setup_and_creates_one_admin(self):
        from ui.login_window import LoginWindow

        app = QApplication.instance() or QApplication([])
        window = LoginWindow()
        try:
            self.assertTrue(auth_is_setup_required := AuthService().is_setup_required())
            self.assertIs(window.stack.currentWidget(), window.setup_widget)
            window.setup_widget.username_input.setText("firstadmin")
            window.setup_widget.password_input.setText("StrongPass!123")
            window.setup_widget.confirm_input.setText("StrongPass!123")
            window.setup_widget.handle_setup()
            self.assertFalse(auth_is_setup_required and AuthService().is_setup_required())
            self.assertEqual(DatabaseManager().execute_scalar("SELECT COUNT(*) FROM users"), 1)
            self.assertTrue(AuthService().authenticate("firstadmin", "StrongPass!123"))
        finally:
            window.close()
            app.processEvents()

    def test_setup_cancellation_and_validation_leave_no_user(self):
        from ui.login_window import SetupWizard

        wizard = SetupWizard(AuthService())
        wizard.handle_setup()
        self.assertEqual(DatabaseManager().execute_scalar("SELECT COUNT(*) FROM users"), 0)
        wizard.username_input.setText("canceladmin")
        wizard.password_input.setText("short")
        wizard.confirm_input.setText("short")
        wizard.handle_setup()
        self.assertEqual(DatabaseManager().execute_scalar("SELECT COUNT(*) FROM users"), 0)
        wizard.password_input.setText("StrongPass!123")
        wizard.confirm_input.setText("DifferentPass!123")
        wizard.handle_setup()
        self.assertEqual(DatabaseManager().execute_scalar("SELECT COUNT(*) FROM users"), 0)

    def test_restart_login_and_existing_administrator(self):
        auth = AuthService()
        self.assertTrue(auth.create_admin_user("existingadmin", "StrongPass!123")[0])
        restarted_auth = AuthService()
        self.assertFalse(restarted_auth.is_setup_required())
        self.assertTrue(restarted_auth.authenticate("existingadmin", "StrongPass!123"))

    def test_deprecated_default_credential_is_blocked_until_changed(self):
        auth = AuthService()
        password_hash = bcrypt.hashpw(b"LegacyPass!123", bcrypt.gensalt()).decode("utf-8")
        now = "2026-09-11T00:00:00"
        DatabaseManager().execute_query(
            "INSERT INTO users (username, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?)",
            ("admin", password_hash, now, now),
        )
        DatabaseManager().execute_query(
            "UPDATE users SET password_change_required = 1 WHERE username = ?", ("admin",)
        )
        self.assertFalse(auth.authenticate("admin", "LegacyPass!123"))
        self.assertTrue(auth.change_password("admin", "LegacyPass!123", "ReplacementPass!123")[0])
        self.assertTrue(auth.authenticate("admin", "ReplacementPass!123"))

    def test_argon2_creation_and_bcrypt_upgrade(self):
        auth = AuthService()
        self.assertTrue(auth.create_admin_user("argonadmin", "StrongPass!123")[0])
        stored = DatabaseManager().execute_scalar(
            "SELECT password_hash FROM users WHERE username = ?", ("argonadmin",)
        )
        self.assertTrue(stored.startswith("$argon2id$"))
        self.assertTrue(auth.authenticate("argonadmin", "StrongPass!123"))

        legacy_hash = bcrypt.hashpw(b"LegacyPass!123", bcrypt.gensalt()).decode("utf-8")
        DatabaseManager().execute_query(
            "INSERT INTO users (username, password_hash, password_change_required) VALUES (?, ?, 0)",
            ("legacyadmin", legacy_hash),
        )
        self.assertTrue(auth.authenticate("legacyadmin", "LegacyPass!123"))
        upgraded = DatabaseManager().execute_scalar(
            "SELECT password_hash FROM users WHERE username = ?", ("legacyadmin",)
        )
        self.assertTrue(upgraded.startswith("$argon2id$"))
        self.assertTrue(auth.authenticate("legacyadmin", "LegacyPass!123"))
        self.assertFalse(auth.authenticate("legacyadmin", "wrong-password"))

    def test_forced_reset_cannot_reach_main_window(self):
        from ui.login_window import LoginWindow

        auth = AuthService()
        legacy_hash = bcrypt.hashpw(b"LegacyPass!123", bcrypt.gensalt()).decode("utf-8")
        DatabaseManager().execute_query(
            "INSERT INTO users (username, password_hash, password_change_required) VALUES (?, ?, 1)",
            ("forcedadmin", legacy_hash),
        )
        app = QApplication.instance() or QApplication([])
        window = LoginWindow()
        login_signals = []
        window.login_successful.connect(lambda: login_signals.append(True))
        try:
            window.username_input.setText("forcedadmin")
            window.password_input.setText("LegacyPass!123")
            window.handle_login()
            self.assertIs(window.stack.currentWidget(), window.forced_change_widget)
            self.assertEqual(login_signals, [])
            self.assertFalse(auth.authenticate("forcedadmin", "LegacyPass!123"))
            window.forced_change_widget.current_input.setText("LegacyPass!123")
            window.forced_change_widget.new_input.setText("ReplacementPass!123")
            window.forced_change_widget.confirm_input.setText("ReplacementPass!123")
            window.forced_change_widget.handle_change()
            self.assertIs(window.stack.currentWidget(), window.login_card)
            self.assertTrue(auth.authenticate("forcedadmin", "ReplacementPass!123"))
        finally:
            window.close()
            app.processEvents()

    def test_session_lock_state_and_minimize_policy(self):
        controller = SessionLockController(timeout_seconds=15, lock_on_minimize=True)
        self.assertFalse(controller.check_timeout(now=controller.last_activity + 14))
        self.assertTrue(controller.check_timeout(now=controller.last_activity + 15))
        self.assertFalse(controller.unlock(False))
        self.assertTrue(controller.unlock(True))
        controller.handle_minimized()
        self.assertTrue(controller.locked)

    def test_security_log_redacts_credentials(self):
        logger = get_security_logger()
        log_path = next(handler.baseFilename for handler in logger.handlers if hasattr(handler, "baseFilename"))
        logger.info("password=HiddenPass!123 api_key=hidden-token address=private phone=555 image=photo.png")
        for handler in logger.handlers:
            handler.flush()
        log_text = Path(log_path).read_text(encoding="utf-8")
        self.assertNotIn("HiddenPass!123", log_text)
        self.assertNotIn("hidden-token", log_text)
        self.assertNotIn("private", log_text)
        self.assertNotIn("555", log_text)
        self.assertNotIn("photo.png", log_text)
        self.assertIn("[REDACTED]", log_text)

    def test_audit_events_are_append_only_and_redacted(self):
        audit = AuditService()
        audit.set_actor(username="audit-admin")
        audit.log_event(
            "student.update",
            record_id="42",
            summary={"changed": True, "fields_hash": "safe-hash"},
        )
        events = audit.list_events("student.update")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["actor_username"], "audit-admin")
        self.assertEqual(events[0]["record_id"], "42")
        self.assertIn("safe-hash", events[0]["summary_json"])
        self.assertEqual(len(events[0]["event_hash"]), 64)
        self.assertEqual(events[0]["previous_hash"], "GENESIS")
        self.assertNotIn("private address", events[0]["summary_json"].lower())
        self.assertIn("T", events[0]["occurred_at_utc"])
        with self.assertRaises(sqlite3.IntegrityError):
            DatabaseManager().execute_query("DELETE FROM audit_events")

        audit.log_event("student.view", record_id="42", summary={"viewed": True})
        chained = audit.list_events()
        self.assertEqual(chained[0]["previous_hash"], events[0]["event_hash"])

    def test_legacy_schema_upgrade_preserves_data_and_version(self):
        db_path = self.base_dir / "legacy_records.db"
        DatabaseManager.set_db_path(db_path)
        conn = sqlite3.connect(db_path)
        conn.executescript(
            """
            CREATE TABLE students (id INTEGER PRIMARY KEY, id_number TEXT UNIQUE NOT NULL,
                name_of_the_student TEXT NOT NULL, photo_path TEXT);
            CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL, created_at TEXT, updated_at TEXT);
            CREATE TABLE app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO students (id_number, name_of_the_student, photo_path)
                VALUES ('LEGACY-001', 'Legacy Student', 'student_photos/legacy.png');
            INSERT INTO app_settings (key, value) VALUES ('theme', 'night');
            INSERT INTO schema_meta (key, value) VALUES ('schema_version', '1.1');
            """
        )
        conn.commit()
        conn.close()

        DatabaseManager().initialize_database()
        conn = sqlite3.connect(db_path)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
        conn.close()
        self.assertIn("password_change_required", columns)
        self.assertEqual(DatabaseManager().execute_scalar("SELECT value FROM schema_meta WHERE key = 'schema_version'"), "1.3")
        self.assertEqual(DatabaseManager().execute_scalar("SELECT name_of_the_student FROM students"), "Legacy Student")
        self.assertEqual(DatabaseManager().execute_scalar("SELECT value FROM app_settings WHERE key = 'theme'"), "night")

    def test_failed_schema_upgrade_rolls_back(self):
        db_path = self.base_dir / "failed_legacy_records.db"
        DatabaseManager.set_db_path(db_path)
        conn = sqlite3.connect(db_path)
        conn.executescript(
            """
            CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL, created_at TEXT, updated_at TEXT);
            CREATE TABLE schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO schema_meta (key, value) VALUES ('schema_version', '1.1');
            INSERT INTO users (username, password_hash) VALUES ('admin', 'not-a-valid-bcrypt-hash');
            CREATE TRIGGER fail_schema_version_update
            BEFORE UPDATE ON schema_meta
            BEGIN SELECT RAISE(ABORT, 'forced migration failure'); END;
            """
        )
        conn.commit()
        conn.close()

        with self.assertRaises(sqlite3.DatabaseError):
            DatabaseManager().initialize_database()
        conn = sqlite3.connect(db_path)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
        version = conn.execute("SELECT value FROM schema_meta WHERE key = 'schema_version'").fetchone()[0]
        conn.close()
        self.assertNotIn("password_change_required", columns)
        self.assertEqual(version, "1.1")



    def test_argon2_missing_dependency_actionable_error(self):
        import services.auth_service as auth_mod
        original_hasher = auth_mod.PASSWORD_HASHER
        try:
            auth_mod.PASSWORD_HASHER = None
            with self.assertRaises(RuntimeError) as ctx:
                auth_mod.AuthService()
            self.assertIn("argon2-cffi", str(ctx.exception))
            self.assertIn("pip install argon2-cffi", str(ctx.exception))
        finally:
            auth_mod.PASSWORD_HASHER = original_hasher

    def test_connection_closure_and_rollback_on_failure(self):
        db = DatabaseManager()
        # Verify active connections empty before
        self.assertEqual(len(DatabaseManager._active_connections), 0)

        # Successful read
        res = db.execute_read("SELECT count(*) as c FROM students")
        self.assertEqual(len(DatabaseManager._active_connections), 0)
        self.assertEqual(res[0]["c"], 0)

        # Successful scalar
        count = db.execute_scalar("SELECT count(*) FROM students")
        self.assertEqual(len(DatabaseManager._active_connections), 0)
        self.assertEqual(count, 0)

        # Successful query
        rowid = db.execute_query(
            "INSERT INTO app_settings (key, value) VALUES (?, ?)",
            ("test_key", "test_val")
        )
        self.assertEqual(len(DatabaseManager._active_connections), 0)
        self.assertGreater(rowid, 0)

        # Failed query (syntax or constraint violation)
        with self.assertRaises(sqlite3.DatabaseError):
            db.execute_query("INSERT INTO non_existent_table VALUES (1)")
        self.assertEqual(len(DatabaseManager._active_connections), 0)

        # Context manager connection
        with db.connection() as conn:
            self.assertEqual(len(DatabaseManager._active_connections), 1)
            row = conn.execute("SELECT value FROM app_settings WHERE key = 'test_key'").fetchone()
            self.assertEqual(row[0], "test_val")
        self.assertEqual(len(DatabaseManager._active_connections), 0)

        # Context manager transaction success
        with db.transaction() as conn:
            conn.execute("INSERT INTO app_settings (key, value) VALUES ('tx_key', 'tx_val')")
        self.assertEqual(len(DatabaseManager._active_connections), 0)
        self.assertEqual(db.execute_scalar("SELECT value FROM app_settings WHERE key = 'tx_key'"), "tx_val")

        # Context manager transaction rollback on error
        with self.assertRaises(ValueError):
            with db.transaction() as conn:
                conn.execute("INSERT INTO app_settings (key, value) VALUES ('rollback_key', 'rollback_val')")
                raise ValueError("Forced error to test rollback")
        self.assertEqual(len(DatabaseManager._active_connections), 0)
        self.assertIsNone(db.execute_scalar("SELECT value FROM app_settings WHERE key = 'rollback_key'"))

    def test_backup_snapshot_integrity_validation(self):
        backup_service = BackupService()
        backup_service.backups_dir = self.base_dir / "backups"
        backup_service.backups_dir.mkdir(parents=True, exist_ok=True)
        backup_service.photos_dir = self.base_dir / "student_photos"
        backup_service.photos_dir.mkdir(parents=True, exist_ok=True)

        success, backup_path_str = backup_service.create_backup()
        self.assertTrue(success)
        backup_path = Path(backup_path_str)
        self.assertTrue(backup_path.exists())

        # Verify no temp files left behind in backups_dir
        all_files = list(backup_service.backups_dir.iterdir())
        self.assertEqual(len(all_files), 1)
        self.assertEqual(all_files[0], backup_path)

        # Verify integrity of backup by inspecting its database
        with zipfile.ZipFile(backup_path, 'r') as z:
            self.assertIn("student_records.db", z.namelist())
            extracted_db = self.base_dir / "extracted_check.db"
            with z.open("student_records.db") as src, open(extracted_db, "wb") as dst:
                dst.write(src.read())
            c = sqlite3.connect(extracted_db)
            integrity = c.execute("PRAGMA integrity_check").fetchone()[0]
            c.close()
            self.assertEqual(integrity, "ok")

    def test_restore_closes_connections_and_recovers_on_failure(self):
        backup_service = BackupService()
        backup_service.backups_dir = self.base_dir / "backups"
        backup_service.backups_dir.mkdir(parents=True, exist_ok=True)
        backup_service.photos_dir = self.base_dir / "student_photos"
        backup_service.photos_dir.mkdir(parents=True, exist_ok=True)

        # Insert a record before backup
        DatabaseManager().execute_query(
            "INSERT INTO app_settings (key, value) VALUES ('state', 'pre_backup')"
        )
        success, backup_path = backup_service.create_backup()
        self.assertTrue(success)

        # Change state
        DatabaseManager().execute_query(
            "UPDATE app_settings SET value = 'post_backup' WHERE key = 'state'"
        )
        self.assertEqual(DatabaseManager().execute_scalar("SELECT value FROM app_settings WHERE key = 'state'"), "post_backup")

        # Open a connection to simulate a connection lingering
        lingering_conn = DatabaseManager().get_connection()
        self.assertGreater(len(DatabaseManager._active_connections), 0)

        # Restore must close lingering connections and restore pre_backup state
        restore_success, msg = backup_service.restore_backup(backup_path)
        self.assertTrue(restore_success, msg)
        self.assertEqual(DatabaseManager().execute_scalar("SELECT value FROM app_settings WHERE key = 'state'"), "pre_backup")
        self.assertEqual(len(DatabaseManager._active_connections), 0)



    def test_student_form_validation_and_photo_button_state(self):
        from ui.student_form_page import StudentFormPage
        app = QApplication.instance() or QApplication([])

        form = StudentFormPage()
        form.resize(900, 700)
        form.show()

        # 1. Verify Remove Photo button is hidden on initial placeholder avatar
        self.assertFalse(form.btn_remove_photo.isVisible(), "Remove Photo button should be hidden when placeholder avatar is active")

        # 2. Verify Save button is disabled on empty form
        self.assertFalse(form.save_btn.isEnabled(), "Save button should be disabled when required fields are empty")
        self.assertIn("Student ID / NIC", form.lbl_form_hint.text())

        # 3. Enter ID only -> Save still disabled
        form.input_id.setText("200212345678")
        self.assertFalse(form.save_btn.isEnabled())
        self.assertIn("Full Name", form.lbl_form_hint.text())

        # 4. Enter Name -> Save now enabled
        form.input_name.setText("Nimal Siriwardena")
        self.assertTrue(form.save_btn.isEnabled())
        self.assertIn("ready to save", form.lbl_form_hint.text().lower())

        # 5. Enter invalid year -> Save disabled
        form.input_year.setText("1850")
        self.assertFalse(form.save_btn.isEnabled())
        self.assertIn("Year", form.lbl_form_hint.text())

        # Enter valid year -> Save enabled
        form.input_year.setText("2024")
        self.assertTrue(form.save_btn.isEnabled())

        # 6. Test photo selection toggles Remove Photo button visibility
        dummy_photo = self.base_dir / "valid_student_photo.jpg"
        img = Image.new("RGB", (100, 100), color=(100, 150, 200))
        img.save(dummy_photo, format="JPEG")

        form.temp_photo_path = str(dummy_photo)
        form.update_photo_preview()
        self.assertTrue(form.btn_remove_photo.isVisible(), "Remove Photo button should be visible when photo is set")

        # Remove photo resets to avatar and hides button
        form.remove_photo()
        self.assertFalse(form.btn_remove_photo.isVisible(), "Remove Photo button should be hidden after removing photo")
        self.assertFalse(bool(form.temp_photo_path))

        # 7. Test Cancel handler resets form
        form.input_name.setText("Unsaved Draft Name")
        self.assertEqual(form.input_name.text(), "Unsaved Draft Name")
        form.handle_cancel()
        self.assertEqual(form.input_name.text(), "")
        self.assertFalse(form.save_btn.isEnabled())
        form.close()

    def test_user_access_control_and_admin_role_boundary(self):
        auth = AuthService()
        # Verify setup required on clean DB
        self.assertTrue(auth.is_setup_required())

        # Create initial admin
        success, msg = auth.create_admin_user("admin_sec", "SecurePass123!")
        self.assertTrue(success, msg)
        self.assertFalse(auth.is_setup_required(), "Setup must be permanently closed once admin exists")

        # Verify no duplicate user creation
        dup_success, dup_msg = auth.create_admin_user("admin_sec", "AnotherPass123!")
        self.assertFalse(dup_success, "Duplicate usernames must be rejected")

        # Verify schema enforces single-tier administrator without unauthenticated self-registration
        cols = [row["name"] for row in DatabaseManager().execute_read("PRAGMA table_info(users)")]
        self.assertIn("username", cols)
        self.assertIn("password_hash", cols)
        self.assertNotIn("role", cols, "System schema is single-tier administrator model")

        # Verify password verification works securely
        self.assertEqual(auth.get_login_status("admin_sec", "SecurePass123!"), "success")
        self.assertEqual(auth.get_login_status("admin_sec", "WrongPassword!"), "invalid")
        self.assertEqual(auth.get_login_status("nonexistent", "SomePass123!"), "invalid")


if __name__ == "__main__":
    unittest.main()
