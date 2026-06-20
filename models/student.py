# models/student.py
from datetime import datetime

class Student:
    def __init__(
        self,
        id_number: str,
        name_of_the_student: str,
        id: int = None,
        year_of_registered: str = "",
        private_address: str = "",
        phone_number: str = "",
        drop_out: str = "No",
        theory_pass: str = "No",
        nvq_l3: str = "No",
        nvq_l4: str = "No",
        ojt_place: str = "",
        ojt_address: str = "",
        ojt_phone_number: str = "",
        job_place: str = "",
        job_place_address: str = "",
        photo_path: str = "",
        created_at: str = None,
        updated_at: str = None
    ):
        self.id = id
        self.id_number = id_number
        self.year_of_registered = year_of_registered
        self.name_of_the_student = name_of_the_student
        self.private_address = private_address
        self.phone_number = phone_number
        self.drop_out = drop_out
        self.theory_pass = theory_pass
        self.nvq_l3 = nvq_l3
        self.nvq_l4 = nvq_l4
        self.ojt_place = ojt_place
        self.ojt_address = ojt_address
        self.ojt_phone_number = ojt_phone_number
        self.job_place = job_place
        self.job_place_address = job_place_address
        self.photo_path = photo_path
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        return cls(
            id=data.get("id"),
            id_number=data.get("id_number", ""),
            year_of_registered=data.get("year_of_registered", ""),
            name_of_the_student=data.get("name_of_the_student", ""),
            private_address=data.get("private_address", ""),
            phone_number=data.get("phone_number", ""),
            drop_out=data.get("drop_out", "No"),
            theory_pass=data.get("theory_pass", "No"),
            nvq_l3=data.get("nvq_l3", "No"),
            nvq_l4=data.get("nvq_l4", "No"),
            ojt_place=data.get("ojt_place", ""),
            ojt_address=data.get("ojt_address", ""),
            ojt_phone_number=data.get("ojt_phone_number", ""),
            job_place=data.get("job_place", ""),
            job_place_address=data.get("job_place_address", ""),
            photo_path=data.get("photo_path", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "id_number": self.id_number,
            "year_of_registered": self.year_of_registered,
            "name_of_the_student": self.name_of_the_student,
            "private_address": self.private_address,
            "phone_number": self.phone_number,
            "drop_out": self.drop_out,
            "theory_pass": self.theory_pass,
            "nvq_l3": self.nvq_l3,
            "nvq_l4": self.nvq_l4,
            "ojt_place": self.ojt_place,
            "ojt_address": self.ojt_address,
            "ojt_phone_number": self.ojt_phone_number,
            "job_place": self.job_place,
            "job_place_address": self.job_place_address,
            "photo_path": self.photo_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
