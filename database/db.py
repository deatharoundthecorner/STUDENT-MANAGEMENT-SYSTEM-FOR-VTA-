# database/db.py
import sqlite3
import os
import logging
from contextlib import contextmanager
from pathlib import Path
from database.schema import (
    CREATE_STUDENTS_TABLE,
    CREATE_USERS_TABLE,
    CREATE_INDEX_STUDENTS_ID,
    CREATE_SETTINGS_TABLE,
    CREATE_SCHEMA_VERSION_TABLE,
    CREATE_AUDIT_EVENTS_TABLE,
    CREATE_AUDIT_EVENTS_INDEXES,
    CREATE_AUDIT_EVENTS_TRIGGERS,
    SCHEMA_VERSION,
)
from utils.security_logging import log_security_event


class DatabaseManager:
    _instance = None
    _db_path = None
    _active_connections = set()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def set_db_path(cls, path: Path):
        cls.close_all_connections()
        cls._db_path = Path(path).resolve()

    @classmethod
    def get_db_path(cls) -> Path:
        if cls._db_path is None:
            from utils.paths import get_paths
            _, writable_dir = get_paths()
            cls._db_path = writable_dir / "student_records.db"
        return cls._db_path

    @classmethod
    def close_all_connections(cls):
        """Closes all active SQLite connections tracked by the manager.
        Crucial on Windows before backup restoration or database file replacement.
        """
        for conn in list(cls._active_connections):
            try:
                conn.close()
            except Exception:
                pass
        cls._active_connections.clear()

    def get_connection(self):
        db_path = self.get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        self._active_connections.add(conn)
        return conn

    @contextmanager
    def connection(self):
        """Context manager yielding an open connection and guaranteeing closure upon exit."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self._active_connections.discard(conn)
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def transaction(self):
        """Context manager providing an atomic transaction: commits on success,
        rolls back on exception, and guarantees connection closure.
        """
        conn = self.get_connection()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            self._active_connections.discard(conn)
            try:
                conn.close()
            except Exception:
                pass

    def initialize_database(self):
        """Creates tables and upgrades legacy schemas in one transaction."""
        conn = self.get_connection()
        try:
            conn.execute("BEGIN")
            cursor = conn.cursor()
            cursor.execute(CREATE_STUDENTS_TABLE)
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(CREATE_INDEX_STUDENTS_ID)
            cursor.execute(CREATE_SETTINGS_TABLE)
            cursor.execute(CREATE_SCHEMA_VERSION_TABLE)
            cursor.execute(CREATE_AUDIT_EVENTS_TABLE)
            for statement in CREATE_AUDIT_EVENTS_INDEXES + CREATE_AUDIT_EVENTS_TRIGGERS:
                cursor.execute(statement)
            user_columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
            if "password_change_required" not in user_columns:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN password_change_required INTEGER NOT NULL DEFAULT 0"
                )
                cursor.execute("UPDATE users SET password_change_required = 1")
            audit_columns = {row[1] for row in cursor.execute("PRAGMA table_info(audit_events)").fetchall()}
            if "previous_hash" not in audit_columns:
                cursor.execute("ALTER TABLE audit_events ADD COLUMN previous_hash TEXT")
            if "event_hash" not in audit_columns:
                cursor.execute("ALTER TABLE audit_events ADD COLUMN event_hash TEXT")
                cursor.execute("UPDATE audit_events SET event_hash = 'legacy-unverified-' || id WHERE event_hash IS NULL")
            cursor.execute(
                "INSERT INTO schema_meta (key, value) VALUES ('schema_version', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (SCHEMA_VERSION,),
            )
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            log_security_event("Database initialization or migration failed", logging.ERROR, exc_info=True)
            raise
        finally:
            self._active_connections.discard(conn)
            try:
                conn.close()
            except Exception:
                pass

    def execute_query(self, query: str, params: tuple = ()) -> int:
        """Executes INSERT, UPDATE, DELETE queries. Returns the last row ID or rowcount."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if query.strip().upper().startswith("INSERT"):
                return cursor.lastrowid
            return cursor.rowcount
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            self._active_connections.discard(conn)
            try:
                conn.close()
            except Exception:
                pass

    def execute_read(self, query: str, params: tuple = ()) -> list:
        """Executes SELECT queries and returns rows as list of dicts."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self._active_connections.discard(conn)
            try:
                conn.close()
            except Exception:
                pass

    def execute_scalar(self, query: str, params: tuple = ()):
        """Executes SELECT and returns first value of the first row."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        finally:
            self._active_connections.discard(conn)
            try:
                conn.close()
            except Exception:
                pass
