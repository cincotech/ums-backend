#!/usr/bin/env python
import json
import os

import django

from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.scheduling_module.scheduling_app.models import Timetable
from services.foundational_service.auth_module.user_app.models import User
from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.country_app.models import Country
from services.foundational_service.geo_module.province_app.models import Province

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings.development")
django.setup()

print("=== OBJETS DISPONIBLES ===")

# Vérifier les Timetables
timetables = Timetable.objects.all()
print(f"Timetables disponibles: {timetables.count()}")
for tt in timetables:
    print(f"  - Timetable ID: {tt.id}")

# Vérifier les Students
students = Student.objects.all()
print(f"\nStudents disponibles: {students.count()}")
for student in students:
    print(f"  - Student ID: {student.id}")

# Si pas d'étudiant, créer un utilisateur et un étudiant
if students.count() == 0:
    print("\n=== CRÉATION D'UN ÉTUDIANT ===")

    # Créer un utilisateur pour l'étudiant
    user, created = User.objects.get_or_create(
        email="student@test.com",
        defaults={"first_name": "Marie", "last_name": "Dupont"},
    )
    print(f"User créé: {user.email}")

    # Créer une colline d'abord

    country, _ = Country.objects.get_or_create(
        country_name="Burundi", defaults={"code": "BI"}
    )

    province, _ = Province.objects.get_or_create(
        province_name="Bujumbura Mairie", defaults={"country": country}
    )

    commune, _ = Commune.objects.get_or_create(
        commune_name="Mukaza", defaults={"province": province}
    )

    colline, _ = Colline.objects.get_or_create(
        colline_name="Rohero", defaults={"commune": commune}
    )

    # Créer un étudiant
    student = Student.objects.create(user=user, matricule="STU001", colline=colline)
    print(f"Student créé: {student.id}")
    students = Student.objects.all()

# Générer JSON si on a les objets nécessaires
if timetables.exists() and students.exists():
    first_timetable = timetables.first()
    first_student = students.first()

    print("\n=== JSON POUR ATTENDANCE ===")

    json_data = {
        "timetable": str(first_timetable.id),
        "student": str(first_student.id),
        "status": "Present",
        "remarks": "Étudiant présent et attentif",
    }
    print(json.dumps(json_data, indent=2))

    print("\n=== IDs UTILISÉS ===")
    print(f"Timetable ID: {first_timetable.id}")
    print(f"Student ID: {first_student.id}")
else:
    print("\n❌ Objets manquants pour créer une Attendance")
    if not timetables.exists():
        print("- Aucun Timetable disponible")
    if not students.exists():
        print("- Aucun Student disponible")
