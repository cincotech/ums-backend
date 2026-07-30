from typing import Any

from django.db.models import Model

from .base import safe_related


def build_module(module: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Module."""
    class_obj = safe_related(module, "class_fk")
    department = safe_related(class_obj, "department") if class_obj else None
    faculty = safe_related(department, "faculty") if department else None
    university = safe_related(faculty, "university") if faculty else None

    return {
        "module_name": module.module_name or None,
        "module_code": module.code or None,
        "class_name": getattr(class_obj, "class_name", None) if class_obj else None,
        "department_name": (
            getattr(department, "department_name", None) if department else None
        ),
        "faculty_name": getattr(faculty, "faculty_name", None) if faculty else None,
        "university_id": str(university.id) if university else None,
    }
