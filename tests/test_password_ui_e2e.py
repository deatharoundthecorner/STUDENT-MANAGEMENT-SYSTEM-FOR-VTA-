import sys
import unittest
import tempfile
import sqlite3
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

import utils.paths
from database.db import DatabaseManager
from services.auth_service import AuthService
from ui.main_window import MainWindow
from ui.settings_page import SettingsPage

class MockMessageBox:
    def __init__(self):
        self.last_warning = None
        self.last_info = None

    def warning(self, parent, title, text):
        self.last_warning = (title, text)
        return QMessageBox.Ok

    def information(self, parent, title, text):
        self.last_info = (title, text)
        return QMessageBox.Ok

class TestPasswordUIEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_full_settings_password_ui_lifecycle(self):
        mock_msg = MockMessageBox()
        orig_warning = QMessageBox.warning
        orig_info = QMessageBox.information
        QMessageBox.warning = mock_msg.warning
        QMessageBox.information = mock_msg.information

        try:
            with tempfile.TemporaryDirectory(prefix='sms_test_pwd_ui_', ignore_cleanup_errors=True) as tmp_dir:
                tmp_path = Path(tmp_dir)
                db_path = tmp_path / 'test_pwd_ui.db'

                utils.paths.get_paths = lambda: (Path('.').resolve(), tmp_path)
                DatabaseManager.set_db_path(db_path)
                DatabaseManager().initialize_database()

                auth_service = AuthService()

                # 1. Unauthenticated Settings Page Safety
                isolated_settings = SettingsPage()
                isolated_settings.handle_change_password()
                self.assertFalse(isolated_settings.btn_change_pass.isEnabled())
                self.assertFalse(isolated_settings.input_curr_pass.isEnabled())
                self.assertEqual(mock_msg.last_warning[0], 'Session Error')

                # 2. Setup synthetic admin account
                admin_user = 'institution_admin'
                initial_pass = 'InitialAdminPass2026!'
                auth_service.create_admin_user(admin_user, initial_pass)

                # 3. Main Window session initiation
                main_win = MainWindow()
                main_win.start_session(admin_user)

                main_win.switch_to_page_index(5) # Settings page
                settings_page = main_win.page_settings
                self.assertEqual(settings_page.authenticated_user, admin_user)
                self.assertTrue(settings_page.btn_change_pass.isEnabled())

                # 4. Password reuse rejection
                settings_page.input_curr_pass.setText(initial_pass)
                settings_page.input_new_pass.setText(initial_pass)
                settings_page.input_conf_pass.setText(initial_pass)
                settings_page.btn_change_pass.click()
                self.assertIn('cannot be the same', mock_msg.last_warning[1].lower())
                self.assertEqual(settings_page.input_new_pass.text(), '')

                # 5. Confirmation mismatch rejection
                settings_page.input_curr_pass.setText(initial_pass)
                settings_page.input_new_pass.setText('NewPassphrase2026!#')
                settings_page.input_conf_pass.setText('DifferentPassphrase2026!#')
                settings_page.btn_change_pass.click()
                self.assertIn('do not match', mock_msg.last_warning[1].lower())
                self.assertEqual(settings_page.input_conf_pass.text(), '')

                # 6. Common password rejection
                settings_page.input_curr_pass.setText(initial_pass)
                settings_page.input_new_pass.setText('password123')
                settings_page.input_conf_pass.setText('password123')
                settings_page.btn_change_pass.click()
                self.assertIn('failed', mock_msg.last_warning[0].lower())

                # 7. Short password rejection (< 8 chars)
                settings_page.input_curr_pass.setText(initial_pass)
                settings_page.input_new_pass.setText('short1')
                settings_page.input_conf_pass.setText('short1')
                settings_page.btn_change_pass.click()
                self.assertIn('failed', mock_msg.last_warning[0].lower())

                # 7b. Whitespace at start/end rejection & live strength feedback
                settings_page.input_new_pass.setText(' LeadingSpacePass1!')
                self.assertIn('spaces', settings_page.lbl_strength_text.text().lower())
                settings_page.input_curr_pass.setText(initial_pass)
                settings_page.input_conf_pass.setText(' LeadingSpacePass1!')
                settings_page.btn_change_pass.click()
                self.assertIn('failed', mock_msg.last_warning[0].lower())

                # 8. Incorrect current password attempt
                settings_page.input_curr_pass.setText('WrongCurrentPassword999!')
                settings_page.input_new_pass.setText('NewPassphrase2026!#')
                settings_page.input_conf_pass.setText('NewPassphrase2026!#')
                settings_page.btn_change_pass.click()
                self.assertIn('incorrect', mock_msg.last_warning[1].lower())
                self.assertEqual(settings_page.input_curr_pass.text(), '')

                # 9. Successful Password Update via UI
                new_passphrase = 'Correct Horse Battery Staple 2026!'
                settings_page.input_curr_pass.setText(initial_pass)
                settings_page.input_new_pass.setText(new_passphrase)
                settings_page.input_conf_pass.setText(new_passphrase)
                settings_page.btn_change_pass.click()
                self.assertIn('updated successfully', mock_msg.last_info[1].lower())

                # 10. Inputs cleared and no leaks in audit log
                self.assertEqual(settings_page.input_curr_pass.text(), '')
                self.assertEqual(settings_page.input_new_pass.text(), '')
                self.assertEqual(settings_page.input_conf_pass.text(), '')
                self.assertEqual(settings_page.strength_bar.value(), 0)

                conn = sqlite3.connect(str(db_path))
                cur = conn.cursor()
                cur.execute('SELECT action_type, actor_username, summary_json FROM audit_events')
                for _, _, summary in cur.fetchall():
                    self.assertNotIn(initial_pass, summary)
                    self.assertNotIn(new_passphrase, summary)

                # 11. Session Logout / Stop
                main_win.stop_session()
                self.assertIsNone(main_win.page_settings.authenticated_user)
                self.assertFalse(main_win.page_settings.btn_change_pass.isEnabled())

                # 12. Re-login Verification: Old rejected, new accepted
                self.assertFalse(auth_service.authenticate(admin_user, initial_pass))
                self.assertTrue(auth_service.authenticate(admin_user, new_passphrase))

                # 13. Hash verified as Argon2id
                cur.execute('SELECT password_hash FROM users WHERE username = ?', (admin_user,))
                stored_hash = cur.fetchone()[0]
                self.assertTrue(stored_hash.startswith('$'))
                conn.close()
        finally:
            QMessageBox.warning = orig_warning
            QMessageBox.information = orig_info

if __name__ == '__main__':
    unittest.main()
