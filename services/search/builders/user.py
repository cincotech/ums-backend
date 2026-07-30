from typing import Any

from django.db.models import Model

from .base import safe_related


def build_user(user: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a User, aggregating from related profiles.

    Gathers identity info from the User model and denormalizes data from
    related Teacher, Student, and UniversityAdmin profiles.
    """
    # Get related profiles
    teacher = safe_related(user, "teacher")
    student = safe_related(user, "students_users")  # related_name is students_users
    university_admin = safe_related(user, "university_admin")

    # Basic identity
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or None

    # Gather student data
    student_class_group = None
    student_class = None
    student_department = None
    student_faculty = None
    matricule = None
    cni = None
    birthplace = None
    if student:
        # Get the first active matricule
        active_mat = student.get_active_matricule()
        if active_mat:
            matricule = active_mat.matricule
        # Get latest inscription for academic context
        latest_inscription = student.inscriptions.order_by("-date_inscription").first()
        if latest_inscription:
            if latest_inscription.class_group:
                student_class_group = latest_inscription.class_group.name
            if latest_inscription.class_fk:
                student_class = latest_inscription.class_fk.class_name
                # department and faculty from class
                dept = safe_related(latest_inscription.class_fk, "department")
                if dept:
                    student_department = dept.department_name
                    faculty = safe_related(dept, "faculty")
                    if faculty:
                        student_faculty = faculty.faculty_name
        # birthplace from student's colline
        if student.colline:
            birthplace = student.colline.name

    # Gather teacher data
    grade = None
    speciality = None
    if teacher:
        grade = teacher.teacher_grade
        speciality = teacher.speciality

    # Gather university admin data
    admin_faculty_id = None
    admin_faculty_name = None
    if university_admin:
        # university_admin is associated with a university; no FacultyAdmin model exists yet.
        pass

    # University from user itself
    university = safe_related(user, "university")
    university_id = str(university.id) if university else None
    university_name = university.university_name if university else None

    # Booleans
    is_teacher = teacher is not None
    is_student = student is not None
    is_university_admin = university_admin is not None
    is_faculty_admin = False  # No FacultyAdmin model found

    return {
        "username": user.username or None,
        "first_name": user.first_name or None,
        "last_name": user.last_name or None,
        "full_name": full_name,
        "email": user.email or None,
        "phone_number": user.phone_number or None,
        "matricule": matricule,
        "cni": cni,
        "birthdate": str(user.birth_date) if user.birth_date else None,
        "birthplace": birthplace,
        "gender": user.gender or None,
        "grade": grade,
        "speciality": speciality,
        "is_teacher": is_teacher,
        "is_student": is_student,
        "is_faculty_admin": is_faculty_admin,
        "is_university_admin": is_university_admin,
        "university_id": university_id,
        "university_name": university_name,
        "student_class_group": student_class_group,
        "student_class": student_class,
        "student_department": student_department,
        "student_faculty": student_faculty,
        "admin_faculty_id": admin_faculty_id,
        "admin_faculty_name": admin_faculty_name,
        "is_active": user.is_active,
    }
