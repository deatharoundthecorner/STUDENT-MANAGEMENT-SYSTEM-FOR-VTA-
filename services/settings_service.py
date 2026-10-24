# services/settings_service.py
from database.db import DatabaseManager
from services.audit_service import AuditService

class SettingsService:
    def __init__(self):
        self.db = DatabaseManager()
        self.audit = AuditService()
        self.ensure_table()

    def ensure_table(self):
        """Creates the app_settings table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
        self.db.execute_query(query)

    def get_setting(self, key: str, default: str = None) -> str:
        """Retrieves a setting by key. Returns default if not found."""
        query = "SELECT value FROM app_settings WHERE key = ?"
        val = self.db.execute_scalar(query, (key,))
        return val if val is not None else default

    def set_setting(self, key: str, value: str):
        """Saves a setting, overwriting if it exists."""
        query = "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)"
        self.db.execute_query(query, (key, value))
        self.audit.log_event("settings.change", summary={"key": key, "value_changed": True})
