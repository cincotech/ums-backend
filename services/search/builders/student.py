from typing import Any

from django.db.models import Model

from .base import safe_related


def build_student(student: Model) -> dict[str, Any]:
    user = safe_related(student, "user")

    full_name = None
    email = None
    phone_number = None
    birthdate = None
    birthplace = None
    gender = None
    if user:
        first = getattr(user, "first_name", "") or ""
        last = getattr(user, "last_name", "") or ""
        full_name = f"{first} {last}".strip() or None
        email = getattr(user, "email", None) or None
        phone_number = getattr(user, "phone_number", None) or None
        birthdate = str(user.birth_date) if getattr(user, "birth_date", None) else None
        gender = getattr(user, "gender", None) or None

    colline = safe_related(student, "colline")
    colline_name = colline.colline_name if colline else None

    active_mat = student.get_active_matricule()
    matricule = active_mat.matricule if active_mat else None

    latest_inscription = student.inscriptions.order_by("-date_inscription").first()
    academic_year = None
    if latest_inscription and latest_inscription.academic_year_id:
        academic_year = str(latest_inscription.academic_year_id)

    is_active = (
        latest_inscription.regist_status == "Active" if latest_inscription else False
    )

    return {
        "full_name": full_name,
        "email": email,
        "phone_number": phone_number,
        "matricule": matricule,
        "birthdate": birthdate,
        "birthplace": birthplace,
        "gender": gender,
        "colline_name": colline_name,
        "academic_year": academic_year,
        "is_active": is_active,
    }
