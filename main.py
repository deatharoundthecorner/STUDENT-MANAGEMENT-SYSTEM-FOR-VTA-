# main.py
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication, QMessageBox
from database.db import DatabaseManager
from services.auth_service import AuthService
from services.photo_service import PhotoService
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from services.audit_service import AuditService
from utils.paths import get_paths, get_asset_path

def setup_directories():
    """Ensures necessary application folders exist before run."""
    _, writable_dir = get_paths()
    
    # Required directories
    directories = [
        writable_dir / "student_photos",
        writable_dir / "backups",
        writable_dir / "assets"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def main():
    # 1. Setup local storage folders
    setup_directories()

    # 2. Configure Windows taskbar grouping AppUserModelID
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "SMS.StudentManagementSystem.Admin.1.0"
            )
        except Exception:
            pass

    # 3. Configure High-DPI scaling before constructing QApplication
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # 4. Start Qt before database initialization so migration failures are user-facing.
    app = QApplication(sys.argv)
    app.setApplicationName("Student Management System")
    app.setApplicationDisplayName("Student Management System")

    # Set custom Windows application icon for all application windows & taskbar
    icon_path = get_asset_path("assets/branding/app_icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    try:
        DatabaseManager().initialize_database()
    except Exception:
        QMessageBox.critical(
            None,
            "Database initialization failed",
            "The application could not prepare its local database. "
            "Your existing data was not changed. Contact support before retrying.",
        )
        return 1

    # 5. Settings & Theme initialization
    from services.settings_service import SettingsService
    settings_service = SettingsService()
    current_theme = settings_service.get_setting("theme", "day")

    # 6. Initialize photo service to make sure default avatar is present
    photo_service = PhotoService()

    # 7. Apply initial theme
    from ui.styles import apply_theme
    apply_theme(app, current_theme)

    # Instantiate windows
    login_win = LoginWindow()
    main_win = MainWindow()

    # Connect signals
    def on_login_success():
        login_win.hide()
        main_win.refresh_all_data()
        main_win.start_session(login_win.authenticated_username)
        AuditService.set_actor(username=login_win.authenticated_username)
        main_win.show()

    def on_setup_success():
        login_win.show_login_view()

    def on_logout():
        AuditService().log_event("logout", summary={"result": "user_requested"})
        AuditService.clear_actor()
        main_win.stop_session()
        main_win.hide()
        login_win.username_input.clear()
        login_win.password_input.clear()
        login_win.error_label.setText("")
        login_win.show_login_view()

    login_win.login_successful.connect(on_login_success)
    login_win.setup_completed.connect(on_setup_success)
    main_win.logout_requested.connect(on_logout)

    login_win.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
