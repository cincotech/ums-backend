from typing import Any

from django.db.models import Model

from .base import safe_related


def build_class_group(class_group: Model) -> dict[str, Any]:
    class_fk = safe_related(class_group, "class_fk")
    class_name = class_fk.class_name if class_fk else None

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

    try:
        student_count = class_group.students.count()
    except Exception:
        student_count = 0

    return {
        "group_name": class_group.group_name or None,
        "class_name": class_name,
        "academic_year": (
            str(class_group.academic_year_id) if class_group.academic_year_id else None
        ),
        "department_name": department_name,
        "faculty_name": faculty_name,
        "university_id": university_id,
        "student_count": student_count,
        "is_default": class_group.is_default,
    }
