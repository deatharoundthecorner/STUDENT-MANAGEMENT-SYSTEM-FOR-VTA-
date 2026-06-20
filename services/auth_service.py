# services/auth_service.py
import bcrypt
from datetime import datetime
from database.db import DatabaseManager

class AuthService:
    def __init__(self):
        self.db = DatabaseManager()

    def hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies a password against its bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    def authenticate(self, username, password) -> bool:
        """Authenticates a user against SQLite users table."""
        query = "SELECT password_hash FROM users WHERE username = ?"
        rows = self.db.execute_read(query, (username,))
        if not rows:
            return False
        hashed_password = rows[0]["password_hash"]
        return self.verify_password(password, hashed_password)

    def change_password(self, username, old_password, new_password) -> tuple:
        """Changes the admin password after verifying the old one."""
        if not new_password or len(new_password) < 4:
            return False, "New password must be at least 4 characters long."

        if not self.authenticate(username, old_password):
            return False, "Incorrect current password."

        new_hash = self.hash_password(new_password)
        updated_at = datetime.now().isoformat()
        query = "UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?"
        rowcount = self.db.execute_query(query, (new_hash, updated_at, username))
        if rowcount > 0:
            return True, "Password changed successfully."
        return False, "Failed to update password in database."

    def seed_default_admin(self):
        """Seeds the default admin credentials if the users table is empty."""
        query_check = "SELECT COUNT(*) FROM users WHERE username = 'admin'"
        count = self.db.execute_scalar(query_check)
        if count == 0:
            hashed_pass = self.hash_password("admin123")
            created_at = datetime.now().isoformat()
            query_insert = "INSERT INTO users (username, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?)"
            self.db.execute_query(query_insert, ("admin", hashed_pass, created_at, created_at))
            print("Default admin user seeded: admin / admin123")
