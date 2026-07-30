from typing import Any

from django.db.models import Model

from .base import safe_related


def build_faculty(faculty: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Faculty."""
    university = safe_related(faculty, "university")

    return {
        "faculty_name": faculty.faculty_name or None,
        "faculty_abreviation": faculty.faculty_abreviation or None,
        "university_id": str(university.id) if university else None,
        "university_name": (
            getattr(university, "university_name", None) if university else None
        ),
    }
