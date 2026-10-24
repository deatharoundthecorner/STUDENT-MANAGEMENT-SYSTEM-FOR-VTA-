# database/schema.py

CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_number TEXT UNIQUE NOT NULL,
    year_of_registered TEXT,
    name_of_the_student TEXT NOT NULL,
    private_address TEXT,
    phone_number TEXT,
    drop_out TEXT,
    theory_pass TEXT,
    nvq_l3 TEXT,
    nvq_l4 TEXT,
    ojt_place TEXT,
    ojt_address TEXT,
    ojt_phone_number TEXT,
    job_place TEXT,
    job_place_address TEXT,
    photo_path TEXT,
    created_at TEXT,
    updated_at TEXT
);
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    password_change_required INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
"""

CREATE_INDEX_STUDENTS_ID = """
CREATE INDEX IF NOT EXISTS idx_students_id_number ON students(id_number);
"""

CREATE_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

CREATE_AUDIT_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at_utc TEXT NOT NULL,
    actor_user_id INTEGER,
    actor_username TEXT,
    action_type TEXT NOT NULL,
    record_id TEXT,
    summary_json TEXT NOT NULL,
    previous_hash TEXT,
    event_hash TEXT NOT NULL
);
"""

CREATE_AUDIT_EVENTS_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_audit_events_occurred_at ON audit_events(occurred_at_utc)",
    "CREATE INDEX IF NOT EXISTS idx_audit_events_action ON audit_events(action_type)",
)

CREATE_AUDIT_EVENTS_TRIGGERS = (
    "CREATE TRIGGER IF NOT EXISTS prevent_audit_event_update BEFORE UPDATE ON audit_events "
    "BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END",
    "CREATE TRIGGER IF NOT EXISTS prevent_audit_event_delete BEFORE DELETE ON audit_events "
    "BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END",
)

SCHEMA_VERSION = "1.3"
