# services/auth_service.py
import bcrypt
from datetime import datetime

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
    PASSWORD_HASHER = PasswordHasher(memory_cost=19456, time_cost=2, parallelism=1)
    _argon2_import_error = None
except ImportError as _err:
    PASSWORD_HASHER = None
    _argon2_import_error = _err
    class InvalidHashError(Exception): pass
    class VerificationError(Exception): pass
    class VerifyMismatchError(Exception): pass

from database.db import DatabaseManager
from utils.security_logging import log_security_event
from services.audit_service import AuditService


class AuthService:
    def __init__(self):
        if PASSWORD_HASHER is None:
            raise RuntimeError(
                "Critical authentication dependency 'argon2-cffi' is missing. "
                "The application requires Argon2id password hashing to operate securely. "
                "Please run: pip install argon2-cffi"
            ) from _argon2_import_error
        self.db = DatabaseManager()
        self.audit = AuditService()

    def is_setup_required(self) -> bool:
        """Returns True when the system has no configured admin account."""
        count = self.db.execute_scalar("SELECT COUNT(*) FROM users")
        return count in (None, 0)

    def validate_password(self, password: str) -> tuple:
        """Validates a password and returns (is_valid, message)."""
        if not password:
            return False, "Password is required."
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if password.islower() or password.isupper():
            return False, "Password must include both letters and numbers or symbols."
        if password.strip() != password:
            return False, "Password cannot start or end with spaces."
        return True, "Password is valid."

    def hash_password(self, password: str) -> str:
        """Hashes a new password using Argon2id PHC format."""
        if PASSWORD_HASHER is None:
            raise RuntimeError("Argon2 hasher unavailable. Install argon2-cffi.")
        return PASSWORD_HASHER.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies Argon2id and legacy bcrypt hashes without weakening them."""
        try:
            if hashed_password.startswith("$argon2"):
                if PASSWORD_HASHER is None:
                    raise RuntimeError("Argon2 hasher unavailable. Install argon2-cffi.")
                return PASSWORD_HASHER.verify(hashed_password, password)
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except (InvalidHashError, VerificationError, VerifyMismatchError, ValueError, TypeError):
            return False

    def is_argon2_hash(self, password_hash: str) -> bool:
        return password_hash.startswith("$argon2id$")

    def get_login_status(self, username: str, password: str) -> str:
        """Returns success, password_change_required, or invalid."""
        rows = self.db.execute_read(
            "SELECT id, password_hash, password_change_required FROM users WHERE username = ?",
            (username,),
        )
        if not rows or not self.verify_password(password, rows[0]["password_hash"]):
            self.audit.log_event("login.failure", summary={"username_present": bool(username)})
            return "invalid"
        if rows[0].get("password_change_required", 0):
            self.audit.log_event("login.password_change_required", actor_user_id=rows[0]["id"], actor_username=username, summary={"username_present": True})
            return "password_change_required"
        if not self.is_argon2_hash(rows[0]["password_hash"]):
            self._replace_hash(username, self.hash_password(password), clear_reset=True)
            log_security_event("Legacy password hash upgraded for user login")
        self.audit.log_event("login.success", actor_user_id=rows[0]["id"], actor_username=username, summary={"authenticated": True})
        return "success"

    def verify_current_password(self, username: str, password: str) -> bool:
        rows = self.db.execute_read(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        )
        return bool(rows and self.verify_password(password, rows[0]["password_hash"]))

    def authenticate(self, username, password) -> bool:
        """Authenticates a user against SQLite users table."""
        return self.get_login_status(username, password) == "success"

    def create_admin_user(self, username: str, password: str) -> tuple:
        """Creates the primary admin account when the app is first configured."""
        username = (username or "").strip()
        if not username:
            return False, "Administrator username is required."
        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        valid, message = self.validate_password(password)
        if not valid:
            return False, message
        if self.db.execute_scalar("SELECT COUNT(*) FROM users WHERE username = ?", (username,)):
            return False, "This username is already in use."
        hashed_pass = self.hash_password(password)
        created_at = datetime.now().isoformat()
        query_insert = (
            "INSERT INTO users "
            "(username, password_hash, password_change_required, created_at, updated_at) "
            "VALUES (?, ?, 0, ?, ?)"
        )
        self.db.execute_query(query_insert, (username, hashed_pass, created_at, created_at))
        return True, "Administrator account created successfully."

    def change_password(self, username, old_password, new_password) -> tuple:
        """Changes the admin password after verifying the old one."""
        valid, message = self.validate_password(new_password)
        if not valid:
            return False, message

        rows = self.db.execute_read(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        )
        if not rows or not self.verify_password(old_password, rows[0]["password_hash"]):
            return False, "Incorrect current password."

        new_hash = self.hash_password(new_password)
        updated_at = datetime.now().isoformat()
        rowcount = self._replace_hash(username, new_hash, clear_reset=True, updated_at=updated_at)
        if rowcount > 0:
            self.audit.log_event("password.change", summary={"changed": True})
            return True, "Password changed successfully."
        return False, "Failed to update password in database."

    def seed_default_admin(self):
        """Deprecated compatibility method; it never creates an account."""
        return False

    def _replace_hash(self, username, password_hash, clear_reset, updated_at=None):
        updated_at = updated_at or datetime.now().isoformat()
        query = "UPDATE users SET password_hash = ?, password_change_required = ?, updated_at = ? WHERE username = ?"
        return self.db.execute_query(query, (password_hash, 0 if clear_reset else 1, updated_at, username))
