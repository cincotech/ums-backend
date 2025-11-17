#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ums.settings.development')
django.setup()

from services.dependent_service.scheduling_module.scheduling_app.models import Timetable
from services.core_service.student_module.student_profile_app.models import Student

print("=== OBJETS DISPONIBLES ===")

# Vérifier les Timetables
timetables = Timetable.objects.all()
print(f"Timetables disponibles: {timetables.count()}")
if timetables.exists():
    first_timetable = timetables.first()
    print(f"Premier Timetable ID: {first_timetable.id}")

# Vérifier les Students
students = Student.objects.all()
print(f"Students disponibles: {students.count()}")
if students.exists():
    first_student = students.first()
    print(f"Premier Student ID: {first_student.id}")

# Générer JSON avec des IDs factices si pas d'objets
print("\n=== JSON POUR ATTENDANCE ===")
import json

if timetables.exists() and students.exists():
    json_data = {
        "timetable": str(first_timetable.id),
        "student": str(first_student.id),
        "status": "Present",
        "remarks": "Étudiant présent et attentif"
    }
else:
    # JSON avec des UUIDs factices pour test
    json_data = {
        "timetable": "92de6f3e-91d1-41cc-b750-53ae550fc6de",  # Un des timetables existants
        "student": "11111111-1111-1111-1111-111111111111",     # UUID factice
        "status": "Present",
        "remarks": "Test attendance"
    }
    print("⚠️  Utilisation d'IDs factices - créez d'abord un Student valide")

print(json.dumps(json_data, indent=2))

print("\n=== URL POUR TEST ===")
print("POST http://127.0.0.1:8000/scheduling/attendances/")
print("GET  http://127.0.0.1:8000/scheduling/attendances/")