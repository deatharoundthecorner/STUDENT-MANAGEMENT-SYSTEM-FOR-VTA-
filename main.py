# main.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from database.db import DatabaseManager
from services.auth_service import AuthService
from services.photo_service import PhotoService
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def setup_directories():
    """Ensures necessary application folders exist before run."""
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent
    
    # Required directories
    directories = [
        base_dir / "student_photos",
        base_dir / "backups",
        base_dir / "assets"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def main():
    # 1. Setup local storage folders
    setup_directories()

    # 2. Database initialization
    db = DatabaseManager()
    db.initialize_database()

    # 3. Seed default admin credentials (admin / admin123)
    auth = AuthService()
    auth.seed_default_admin()
    
    # 4. Initialize photo service to make sure default avatar is present
    photo_service = PhotoService()

    # 5. Start PySide6 Application
    app = QApplication(sys.argv)
    app.setApplicationName("Student Management System")

    # Instantiate windows
    login_win = LoginWindow()
    main_win = MainWindow()

    # Connect signals
    def on_login_success():
        login_win.hide()
        main_win.refresh_all_data()
        main_win.show()

    def on_logout():
        main_win.hide()
        login_win.username_input.clear()
        login_win.password_input.clear()
        login_win.error_label.setText("")
        login_win.show()

    login_win.login_successful.connect(on_login_success)
    main_win.logout_requested.connect(on_logout)

    login_win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
