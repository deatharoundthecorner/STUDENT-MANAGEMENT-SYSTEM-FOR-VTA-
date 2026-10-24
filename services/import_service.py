# services/import_service.py
import re
import pandas as pd
from pathlib import Path
from database.db import DatabaseManager
from models.student import Student
from services.student_service import StudentService
from services.audit_service import AuditService

class ImportService:
    def __init__(self):
        self.student_service = StudentService()
        self.audit = AuditService()

    def is_valid_phone(self, phone: str) -> bool:
        """Validates phone-like numbers (digits, spaces, dashes, parentheses, plus)."""
        if not phone:
            return True # Optional field
        # Allow numbers, spaces, dashes, plus sign, brackets, minimum 5 characters
        cleaned = str(phone).strip()
        if len(cleaned) < 5:
            return False
        pattern = r'^[+\d\s\(\)-]+$'
        return bool(re.match(pattern, cleaned))

    def get_column_mapping(self, columns: list) -> dict:
        """Maps file column headers to standard schema fields (case-insensitive)."""
        schema_fields = [
            "id_number", "year_of_registered", "name_of_the_student", "private_address",
            "phone_number", "drop_out", "theory_pass", "nvq_l3", "nvq_l4",
            "ojt_place", "ojt_address", "ojt_phone_number", "job_place", "job_place_address"
        ]
        
        mapping = {}
        for col in columns:
            normalized_col = str(col).strip().lower().replace(" ", "_")
            for field in schema_fields:
                if normalized_col == field:
                    mapping[col] = field
                    break
        return mapping

    def preview_file(self, file_path_str: str) -> tuple:
        """
        Reads first 10 rows of a file for UI preview.
        Returns a tuple of (headers: list, rows: list of lists, error: str)
        """
        try:
            file_path = Path(file_path_str)
            if not file_path.exists():
                return [], [], "File does not exist."

            # Determine file type
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, nrows=10, dtype=str)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=10, dtype=str)
            else:
                return [], [], "Unsupported file format. Please select CSV or Excel."

            df = df.fillna("")
            headers = df.columns.tolist()
            rows = df.values.tolist()
            return headers, rows, ""
        except Exception as e:
            return [], [], f"Error reading preview: {str(e)}"

    def import_file(self, file_path_str: str) -> dict:
        """
        Imports student records from CSV or Excel file.
        Returns statistics: {'success': int, 'skipped': int, 'failed': int, 'errors': list}
        """
        stats = {"success": 0, "skipped": 0, "failed": 0, "errors": []}
        
        try:
            file_path = Path(file_path_str)
            if not file_path.exists():
                stats["errors"].append("File does not exist.")
                return stats

            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, dtype=str)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, dtype=str)
            else:
                stats["errors"].append("Unsupported file format.")
                return stats

            df = df.fillna("")
            mapping = self.get_column_mapping(df.columns)
            
            # Check if required columns are present
            # Match columns case insensitively
            col_by_field = {v: k for k, v in mapping.items()}
            
            if "id_number" not in col_by_field:
                stats["errors"].append("Missing required column: 'id_number' or 'ID_NUMBER'.")
                return stats
            if "name_of_the_student" not in col_by_field:
                stats["errors"].append("Missing required column: 'name_of_the_student' or 'NAME_OF_THE_STUDENT'.")
                return stats

            valid_statuses = ["Yes", "No", "Pending", "Not Applicable"]

            for index, row in df.iterrows():
                row_num = index + 2  # 1-indexed header + 1
                try:
                    # Extract fields using mapping
                    id_number = str(row[col_by_field["id_number"]]).strip()
                    name = str(row[col_by_field["name_of_the_student"]]).strip()
                    
                    # Basic Validation
                    if not id_number:
                        stats["failed"] += 1
                        stats["errors"].append(f"Row {row_num}: ID Number is blank.")
                        continue
                    if not name:
                        stats["failed"] += 1
                        stats["errors"].append(f"Row {row_num}: Student Name is blank.")
                        continue

                    # Phone Validations
                    phone = str(row.get(col_by_field.get("phone_number"), "")).strip()
                    if phone and not self.is_valid_phone(phone):
                        stats["failed"] += 1
                        stats["errors"].append(f"Row {row_num}: Invalid Student Phone '{phone}'.")
                        continue
                    
                    ojt_phone = str(row.get(col_by_field.get("ojt_phone_number"), "")).strip()
                    if ojt_phone and not self.is_valid_phone(ojt_phone):
                        stats["failed"] += 1
                        stats["errors"].append(f"Row {row_num}: Invalid OJT Phone '{ojt_phone}'.")
                        continue

                    # Duplicate check
                    existing = self.student_service.get_student_by_id_number(id_number)
                    if existing:
                        stats["skipped"] += 1
                        # Do not report duplicate as error, just count it
                        continue

                    # Status parsing & defaults
                    def parse_status(val):
                        val_str = str(val).strip().title()
                        if val_str in valid_statuses:
                            return val_str
                        return "No" # Default status

                    drop_out = parse_status(row.get(col_by_field.get("drop_out"), "No"))
                    theory_pass = parse_status(row.get(col_by_field.get("theory_pass"), "No"))
                    nvq_l3 = parse_status(row.get(col_by_field.get("nvq_l3"), "No"))
                    nvq_l4 = parse_status(row.get(col_by_field.get("nvq_l4"), "No"))

                    # Create Student object
                    student = Student(
                        id_number=id_number,
                        name_of_the_student=name,
                        year_of_registered=str(row.get(col_by_field.get("year_of_registered"), "")).strip(),
                        private_address=str(row.get(col_by_field.get("private_address"), "")).strip(),
                        phone_number=phone,
                        drop_out=drop_out,
                        theory_pass=theory_pass,
                        nvq_l3=nvq_l3,
                        nvq_l4=nvq_l4,
                        ojt_place=str(row.get(col_by_field.get("ojt_place"), "")).strip(),
                        ojt_address=str(row.get(col_by_field.get("ojt_address"), "")).strip(),
                        ojt_phone_number=ojt_phone,
                        job_place=str(row.get(col_by_field.get("job_place"), "")).strip(),
                        job_place_address=str(row.get(col_by_field.get("job_place_address"), "")).strip(),
                        photo_path=""
                    )
                    
                    self.student_service.add_student(student)
                    stats["success"] += 1
                except Exception as ex:
                    stats["failed"] += 1
                    stats["errors"].append(f"Row {row_num}: Unexpected error: {str(ex)}")
            
        except Exception as e:
            stats["errors"].append(f"Fatal import error: {str(e)}")
            
        self.audit.log_event("import", summary={"success": stats["success"], "skipped": stats["skipped"], "failed": stats["failed"]})
        return stats

    def generate_template(self, target_path_str: str, file_format: str = "csv"):
        """Generates a sample CSV or Excel import template."""
        columns = [
            "ID_NUMBER", "YEAR_OF_REGISTERED", "NAME_OF_THE_STUDENT", "PRIVATE_ADDRESS",
            "PHONE_NUMBER", "DROP_OUT", "THEORY_PASS", "NVQ_L3", "NVQ_L4",
            "OJT_PLACE", "OJT_ADDRESS", "OJT_PHONE_NUMBER", "JOB_PLACE", "JOB_PLACE_ADDRESS"
        ]
        
        sample_data = [
            {
                "ID_NUMBER": "1998012345V",
                "YEAR_OF_REGISTERED": "2025",
                "NAME_OF_THE_STUDENT": "Ranasinghe Banda",
                "PRIVATE_ADDRESS": "123, Galle Road, Colombo 03",
                "PHONE_NUMBER": "+94 77 123 4567",
                "DROP_OUT": "No",
                "THEORY_PASS": "Yes",
                "NVQ_L3": "Yes",
                "NVQ_L4": "Pending",
                "OJT_PLACE": "Abans PLC",
                "OJT_ADDRESS": "498, Galle Road, Colombo 03",
                "OJT_PHONE_NUMBER": "0112565656",
                "JOB_PLACE": "",
                "JOB_PLACE_ADDRESS": ""
            },
            {
                "ID_NUMBER": "1999567891V",
                "YEAR_OF_REGISTERED": "2024",
                "NAME_OF_THE_STUDENT": "Fathima Asma",
                "PRIVATE_ADDRESS": "45, Main Street, Kandy",
                "PHONE_NUMBER": "+94 81 987 6543",
                "DROP_OUT": "No",
                "THEORY_PASS": "Yes",
                "NVQ_L3": "Yes",
                "NVQ_L4": "Yes",
                "OJT_PLACE": "Dialog Axiata",
                "OJT_ADDRESS": "Union Place, Colombo 02",
                "OJT_PHONE_NUMBER": "0117100100",
                "JOB_PLACE": "WSO2 Lanka",
                "JOB_PLACE_ADDRESS": "Flower Road, Colombo 07"
            }
        ]
        
        df = pd.DataFrame(sample_data, columns=columns)
        target_path = Path(target_path_str)
        
        # Ensure parent exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_format.lower() == "csv":
            df.to_csv(target_path, index=False)
        else:
            df.to_excel(target_path, index=False)
        
        return str(target_path.resolve())
