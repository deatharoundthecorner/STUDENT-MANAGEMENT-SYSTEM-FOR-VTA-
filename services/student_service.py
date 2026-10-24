# services/student_service.py
from datetime import datetime
from database.db import DatabaseManager
from models.student import Student
from services.audit_service import AuditService

class StudentService:
    def __init__(self):
        self.db = DatabaseManager()
        self.audit = AuditService()

    def add_student(self, student: Student) -> int:
        """Inserts a new student record into database. Validates uniqueness of ID number."""
        # Check uniqueness of ID number
        if self.get_student_by_id_number(student.id_number) is not None:
            raise ValueError(f"Student ID Number '{student.id_number}' already exists.")

        query = """
            INSERT INTO students (
                id_number, year_of_registered, name_of_the_student, private_address,
                phone_number, drop_out, theory_pass, nvq_l3, nvq_l4,
                ojt_place, ojt_address, ojt_phone_number, job_place, job_place_address,
                photo_path, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now_str = datetime.now().isoformat()
        params = (
            student.id_number,
            student.year_of_registered,
            student.name_of_the_student,
            student.private_address,
            student.phone_number,
            student.drop_out,
            student.theory_pass,
            student.nvq_l3,
            student.nvq_l4,
            student.ojt_place,
            student.ojt_address,
            student.ojt_phone_number,
            student.job_place,
            student.job_place_address,
            student.photo_path,
            now_str,
            now_str
        )
        last_id = self.db.execute_query(query, params)
        student.id = last_id
        self.audit.log_event("student.create", last_id, {"id_number_hash": hash(student.id_number), "fields": ["student"]})
        return last_id

    def update_student(self, student: Student) -> bool:
        """Updates an existing student record."""
        # Verify unique constraint on ID number (excluding current record)
        existing = self.get_student_by_id_number(student.id_number)
        if existing and existing.id != student.id:
            raise ValueError(f"Student ID Number '{student.id_number}' is already assigned to another student.")

        query = """
            UPDATE students SET
                id_number = ?,
                year_of_registered = ?,
                name_of_the_student = ?,
                private_address = ?,
                phone_number = ?,
                drop_out = ?,
                theory_pass = ?,
                nvq_l3 = ?,
                nvq_l4 = ?,
                ojt_place = ?,
                ojt_address = ?,
                ojt_phone_number = ?,
                job_place = ?,
                job_place_address = ?,
                photo_path = ?,
                updated_at = ?
            WHERE id = ?
        """
        now_str = datetime.now().isoformat()
        params = (
            student.id_number,
            student.year_of_registered,
            student.name_of_the_student,
            student.private_address,
            student.phone_number,
            student.drop_out,
            student.theory_pass,
            student.nvq_l3,
            student.nvq_l4,
            student.ojt_place,
            student.ojt_address,
            student.ojt_phone_number,
            student.job_place,
            student.job_place_address,
            student.photo_path,
            now_str,
            student.id
        )
        rowcount = self.db.execute_query(query, params)
        if rowcount > 0:
            self.audit.log_event("student.update", student.id, {"id_number_hash": hash(student.id_number), "changed": True})
        return rowcount > 0

    def delete_student(self, student_id: int) -> bool:
        """Deletes a student record by ID."""
        query = "DELETE FROM students WHERE id = ?"
        rowcount = self.db.execute_query(query, (student_id,))
        if rowcount > 0:
            self.audit.log_event("student.delete", student_id, {"deleted": True})
        return rowcount > 0

    def get_student_by_id(self, student_id: int) -> Student:
        """Retrieves a single student by DB ID."""
        query = "SELECT * FROM students WHERE id = ?"
        rows = self.db.execute_read(query, (student_id,))
        if rows:
            return Student.from_dict(rows[0])
        return None

    def get_student_by_id_number(self, id_number: str) -> Student:
        """Retrieves a student by their unique national ID number."""
        query = "SELECT * FROM students WHERE id_number = ?"
        rows = self.db.execute_read(query, (id_number,))
        if rows:
            return Student.from_dict(rows[0])
        return None

    def get_all_students(self) -> list:
        """Retrieves all students."""
        query = "SELECT * FROM students ORDER BY name_of_the_student ASC"
        rows = self.db.execute_read(query)
        return [Student.from_dict(row) for row in rows]

    def search_and_filter_students(self, search_text: str = "", filters: dict = None) -> list:
        """Search by text and filter by categories/statuses."""
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        # 1. Search Logic
        if search_text:
            query += """ AND (
                id_number LIKE ? OR 
                name_of_the_student LIKE ? OR 
                phone_number LIKE ? OR 
                ojt_place LIKE ? OR 
                job_place LIKE ?
            )"""
            like_str = f"%{search_text}%"
            params.extend([like_str, like_str, like_str, like_str, like_str])

        # 2. Filters Logic
        if filters:
            if filters.get("year_of_registered"):
                query += " AND year_of_registered = ?"
                params.append(filters["year_of_registered"])
            if filters.get("drop_out"):
                query += " AND drop_out = ?"
                params.append(filters["drop_out"])
            if filters.get("theory_pass"):
                query += " AND theory_pass = ?"
                params.append(filters["theory_pass"])
            if filters.get("nvq_l3"):
                query += " AND nvq_l3 = ?"
                params.append(filters["nvq_l3"])
            if filters.get("nvq_l4"):
                query += " AND nvq_l4 = ?"
                params.append(filters["nvq_l4"])
            if filters.get("has_ojt") is not None:
                # "Yes" means has place
                if filters["has_ojt"] == "Yes":
                    query += " AND ojt_place IS NOT NULL AND ojt_place != ''"
                elif filters["has_ojt"] == "No":
                    query += " AND (ojt_place IS NULL OR ojt_place = '')"
            if filters.get("has_job") is not None:
                if filters["has_job"] == "Yes":
                    query += " AND job_place IS NOT NULL AND job_place != ''"
                elif filters["has_job"] == "No":
                    query += " AND (job_place IS NULL OR job_place = '')"

        query += " ORDER BY name_of_the_student ASC"
        rows = self.db.execute_read(query, tuple(params))
        return [Student.from_dict(row) for row in rows]

    def get_dashboard_statistics(self) -> dict:
        """Retrieves summary metrics for dashboard visualization."""
        stats = {}
        stats["total_students"] = self.db.execute_scalar("SELECT COUNT(*) FROM students")
        stats["drop_out_students"] = self.db.execute_scalar("SELECT COUNT(*) FROM students WHERE drop_out = 'Yes'")
        stats["theory_pass_students"] = self.db.execute_scalar("SELECT COUNT(*) FROM students WHERE theory_pass = 'Yes'")
        stats["nvq_l3_completed"] = self.db.execute_scalar("SELECT COUNT(*) FROM students WHERE nvq_l3 = 'Yes'")
        stats["nvq_l4_completed"] = self.db.execute_scalar("SELECT COUNT(*) FROM students WHERE nvq_l4 = 'Yes'")
        stats["students_with_ojt"] = self.db.execute_scalar(
            "SELECT COUNT(*) FROM students WHERE ojt_place IS NOT NULL AND ojt_place != ''"
        )
        stats["students_with_job"] = self.db.execute_scalar(
            "SELECT COUNT(*) FROM students WHERE job_place IS NOT NULL AND job_place != ''"
        )
        return stats

    def get_unique_registered_years(self) -> list:
        """Retrieves list of all unique registered years for filtering."""
        query = "SELECT DISTINCT year_of_registered FROM students WHERE year_of_registered IS NOT NULL AND year_of_registered != '' ORDER BY year_of_registered DESC"
        rows = self.db.execute_read(query)
        return [row["year_of_registered"] for row in rows]
