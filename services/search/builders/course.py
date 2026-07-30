from typing import Any

from django.db.models import Model

from .base import safe_related


def build_course(course: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Course."""
    module = safe_related(course, "module")
    class_obj = safe_related(module, "class_fk") if module else None
    department = safe_related(class_obj, "department") if class_obj else None
    faculty = safe_related(department, "faculty") if department else None
    university = safe_related(faculty, "university") if faculty else None

    return {
        "course_name": course.course_name or None,
        "course_code": course.course_code or None,
        "module_name": getattr(module, "module_name", None) if module else None,
        "module_id": str(module.id) if module else None,
        "department_name": (
            getattr(department, "department_name", None) if department else None
        ),
        "faculty_name": getattr(faculty, "faculty_name", None) if faculty else None,
        "university_id": str(university.id) if university else None,
        "credits": int(course.credits) if course.credits is not None else None,
        "cm": int(course.cm) if course.cm is not None else None,
        "td": int(course.td) if course.td is not None else None,
        "tp": int(course.tp) if course.tp is not None else None,
    }
