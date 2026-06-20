# database/db.py
import sqlite3
import os
from pathlib import Path
from database.schema import CREATE_STUDENTS_TABLE, CREATE_USERS_TABLE, CREATE_INDEX_STUDENTS_ID

class DatabaseManager:
    _instance = None
    _db_path = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def set_db_path(cls, path: Path):
        cls._db_path = Path(path).resolve()

    @classmethod
    def get_db_path(cls) -> Path:
        if cls._db_path is None:
            # Default to the application folder
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).resolve().parent.parent
            cls._db_path = base_dir / "student_records.db"
        return cls._db_path

    def get_connection(self):
        db_path = self.get_db_path()
        # Ensure parent directories exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_database(self):
        """Creates tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_STUDENTS_TABLE)
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(CREATE_INDEX_STUDENTS_ID)
            conn.commit()

    def execute_query(self, query: str, params: tuple = ()) -> int:
        """Executes INSERT, UPDATE, DELETE queries. Returns the last row ID or rowcount."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if query.strip().upper().startswith("INSERT"):
                return cursor.lastrowid
            return cursor.rowcount

    def execute_read(self, query: str, params: tuple = ()) -> list:
        """Executes SELECT queries and returns rows as list of dicts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    def execute_scalar(self, query: str, params: tuple = ()):
        """Executes SELECT and returns first value of the first row."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
