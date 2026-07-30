from typing import Any

from django.db.models import Model

from .base import safe_related


def build_department(department: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Department."""
    faculty = safe_related(department, "faculty")
    university = safe_related(faculty, "university") if faculty else None

    return {
        "department_name": department.department_name or None,
        "department_code": department.abreviation or None,
        "faculty_name": getattr(faculty, "faculty_name", None) if faculty else None,
        "faculty_id": str(faculty.id) if faculty else None,
        "university_id": str(university.id) if university else None,
    }
