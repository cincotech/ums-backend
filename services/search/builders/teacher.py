from typing import Any

from django.db.models import Model

from .base import safe_related


def build_teacher(teacher: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Teacher."""
    user = safe_related(teacher, "user")
    university = safe_related(teacher, "university")

    full_name = None
    email = None
    phone = None
    if user:
        first = getattr(user, "first_name", "") or ""
        last = getattr(user, "last_name", "") or ""
        full_name = f"{first} {last}".strip() or None
        email = getattr(user, "email", None) or None
        phone = getattr(user, "phone_number", None) or None

    return {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "teacher_grade": teacher.teacher_grade or None,
        "speciality": teacher.speciality or None,
        "university_id": str(university.id) if university else None,
        "academic_year": (
            str(teacher.academic_year_id) if teacher.academic_year_id else None
        ),
    }
