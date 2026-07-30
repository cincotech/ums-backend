from typing import Any

from django.db.models import Model

from .base import safe_related


def build_result(result: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Result."""
    course = safe_related(result, "course")
    inscription = safe_related(result, "inscription")
    session = safe_related(result, "session")

    student = None
    student_first_name = None
    student_last_name = None
    student_email = None
    if inscription:
        student = safe_related(inscription, "student")

    if student:
        user = safe_related(student, "user")
        if user:
            first = getattr(user, "first_name", "") or ""
            last = getattr(user, "last_name", "") or ""
            student_first_name = first.strip() or None
            student_last_name = last.strip() or None
            student_email = getattr(user, "email", None) or None

    return {
        "mark": result.mark,
        "status": result.status or None,
        "comment": result.comment or None,
        "course_name": course.course_name if course else None,
        "student_first_name": student_first_name,
        "student_last_name": student_last_name,
        "student_email": student_email,
        "session_name": session.session_name if session else None,
    }
