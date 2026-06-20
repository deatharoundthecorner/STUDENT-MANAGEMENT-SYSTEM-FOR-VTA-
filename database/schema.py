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
    created_at TEXT,
    updated_at TEXT
);
"""

CREATE_INDEX_STUDENTS_ID = """
CREATE INDEX IF NOT EXISTS idx_students_id_number ON students(id_number);
"""
