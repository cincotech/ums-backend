# services/inscription_template_service.py

from django.contrib.auth import get_user_model

from services.core_service.student_module.student_profile_app.models import (
    Student,
    StudentMatricule,
)

User = get_user_model()


def generate_inscription_template(
    user_id: str, academic_year_id: str, inscription_id: str = None
):
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise Exception("User not found")

    student = Student.objects.filter(user=user).first()

    # -------------------
    # STEP 1
    # -------------------
    step1 = {
        "user_id": str(user.id),
        "user_first_name": user.first_name,
        "user_last_name": user.last_name,
        "user_email": user.email,
        "user_display": f"{user.first_name} {user.last_name} ({user.email})",
        "student_id": str(student.id) if student else None,
    }

    if student and student.colline:
        colline = student.colline
        zone = colline.zone
        commune = zone.commune
        province = commune.province
        country = province.country

        step1.update(
            {
                "colline_id": str(colline.id),
                "colline_name": colline.colline_name,
                "zone_id": str(zone.id),
                "zone_name": zone.zone_name,
                "commune_id": str(commune.id),
                "commune_name": commune.commune_name,
                "province_id": str(province.id),
                "province_name": province.province_name,
                "country_id": str(country.id),
                "country_name": country.country_name,
            }
        )

    # -------------------
    # STEP 2 (Parents)
    # -------------------
    parents_qs = student.parent.all()

    step2 = {
        "student_id": str(student.id) if student else None,
        "parents": [
            {
                "id": str(p.id),
                "parent_name": p.parent_name,
                "parent_phone": p.parent_phone,
                "parent_email": p.parent_email,
                "profession_id": str(p.profession_id),
                "parent_type": p.parent_type,
                "is_alive": p.is_alive,
                "is_contact_person": p.is_contact_person,
            }
            for p in parents_qs
        ],
    }

    # -------------------
    # STEP 3 (High school)
    # -------------------

    hs = student.hs_infos.first()

    step3 = None

    if hs:
        step3 = {
            "highschool_id": str(hs.highschool_id),
            "certificate_id": str(hs.certificate_id),
            "se_mark": hs.se_mark,
            "date_of_obtention": hs.date_of_obtention,  # ✅ fixed
            "formation_ids": [str(f.id) for f in hs.formation.all()],  # ✅ fixed
            "has_university_background": False,
        }

    # -------------------
    # STEP 4 (University)
    # -------------------
    uni = student.graduate_infos.select_related(
        "department__faculty__university__country"
    ).first()

    step4 = None

    if uni:
        step4 = {
            "country_id": str(uni.department.faculty.university.country.id),
            "university_id": str(uni.department.faculty.university.id),
            "faculty_id": str(uni.department.faculty.id),
            "department_id": str(uni.department.id),
            "option": uni.option,
            "mention": uni.mention,
            "degree_id": str(uni.degree_id),
            # ❗ this only works if field exists in model
            "year_obtained": None,
        }

        if step3:
            step3["has_university_background"] = True

    # -------------------
    # STEP 5 (Default)
    # -------------------
    existing_matricules = []
    if student:
        for sm in StudentMatricule.objects.filter(student=student).select_related(
            "type_formation", "academic_year"
        ):
            # Get latest inscription status for this type
            from services.core_service.student_module.inscription_app.models import (
                Inscription,
            )

            latest = (
                Inscription.objects.filter(
                    student=student,
                    class_fk__department__faculty__types=sm.type_formation,
                )
                .order_by("-date_inscription")
                .first()
            )

            existing_matricules.append(
                {
                    "matricule": sm.matricule,
                    "type_formation_code": sm.type_formation.code,
                    "type_formation_name": sm.type_formation.name,
                    "academic_year_label": sm.academic_year.academic_year,
                    "inscription_status": latest.regist_status if latest else None,
                }
            )

    step5 = {
        "academic_year_id": academic_year_id,
        "class_fk_id": None,
        "date_inscription": today_iso(),
        "existing_matricules": existing_matricules,
        "is_multi_formation": len(existing_matricules) > 0,
        "inscription_id": inscription_id,  # Ajouter l'inscription_id dans step5
    }

    # -------------------
    # FINAL OBJECT
    # -------------------
    result = {
        "step1": step1,
        "step2": step2,
        "step3": step3,
    }

    if step4:
        result["step4"] = step4

    result["step5"] = step5

    return result


# helpers
from datetime import date


def today_iso():
    today = date.today()
    print(f"Date générée: {today} -> ISO: {today.isoformat()}")
    return today.isoformat()
