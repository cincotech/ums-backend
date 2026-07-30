from datetime import date
from typing import Any

from django.db.models import Model

from .base import safe_related


def build_inscription(inscription: Model) -> dict[str, Any]:
    student = safe_related(inscription, "student")

    student_full_name = None
    student_matricule = None
    if student:
        user = safe_related(student, "user")
        if user:
            first = getattr(user, "first_name", "") or ""
            last = getattr(user, "last_name", "") or ""
            student_full_name = f"{first} {last}".strip() or None
        active_mat = student.get_active_matricule()
        student_matricule = active_mat.matricule if active_mat else None

    class_fk = safe_related(inscription, "class_fk")
    class_name = class_fk.class_name if class_fk else None

    class_group = safe_related(inscription, "class_group")
    class_group_name = class_group.group_name if class_group else None

    department_name = None
    faculty_name = None
    university_id = None
    if class_fk:
        dept = safe_related(class_fk, "department")
        if dept:
            department_name = dept.department_name
            faculty = safe_related(dept, "faculty")
            if faculty:
                faculty_name = faculty.faculty_name
                university_id = (
                    str(faculty.university_id) if faculty.university_id else None
                )

    date_inscription = None
    if inscription.date_inscription:
        if isinstance(inscription.date_inscription, date):
            date_inscription = inscription.date_inscription.toordinal()

    return {
        "student_id": str(inscription.student_id) if inscription.student_id else None,
        "student_full_name": student_full_name,
        "student_matricule": student_matricule,
        "academic_year": (
            str(inscription.academic_year_id) if inscription.academic_year_id else None
        ),
        "class_name": class_name,
        "class_group_name": class_group_name,
        "department_name": department_name,
        "faculty_name": faculty_name,
        "university_id": university_id,
        "regist_status": inscription.regist_status or None,
        "date_inscription": date_inscription,
    }
