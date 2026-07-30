from typing import Any

from django.db.models import Model

from .base import safe_related


def build_class(class_obj: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Class."""
    department = safe_related(class_obj, "department")
    faculty = safe_related(department, "faculty") if department else None
    university = safe_related(faculty, "university") if faculty else None

    return {
        "class_name": class_obj.class_name or None,
        "department_name": (
            getattr(department, "department_name", None) if department else None
        ),
        "faculty_name": getattr(faculty, "faculty_name", None) if faculty else None,
        "university_id": str(university.id) if university else None,
    }
