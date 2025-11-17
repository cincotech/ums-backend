#!/usr/bin/env python
import os
import sys
import django
from datetime import date, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ums.settings.development')
django.setup()

from services.foundational_service.geo_module.country_app.models import Country
from services.core_service.academic_module.university_app.models import University, AcademicYear, UniversityDegree
from services.dependent_service.infrastructure_module.building_app.models import Building
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.user_app.models import User
from services.core_service.academic_module.teacher_app.models import Teacher, Attribution
from services.core_service.academic_module.course_app.models import Course
from services.dependent_service.scheduling_module.scheduling_app.models import ScheduleSlot

# 1. Créer Country
country, _ = Country.objects.get_or_create(
    country_name="Burundi",
    defaults={'code': 'BI'}
)

# 2. Créer University
university, _ = University.objects.get_or_create(
    university_name="Université Test",
    defaults={'university_abrev': 'UT', 'country': country}
)

# 3. Créer Building
building, _ = Building.objects.get_or_create(
    building_name="Bâtiment Principal",
    university=university,
    defaults={'building_code': 'BP001', 'location': 'Campus Central'}
)

# 4. Créer Room
room, _ = Room.objects.get_or_create(
    room_name="Salle A101",
    building=building,
    defaults={'capacity': 50, 'room_type': 'classroom', 'is_available': True}
)

# 5. Créer AcademicYear
academic_year, _ = AcademicYear.objects.get_or_create(
    academic_year="2024-2025",
    defaults={
        'description': 'Année académique 2024-2025',
        'civil_year': '2024',
        'start_date': date(2024, 9, 1),
        'end_date': date(2025, 6, 30)
    }
)

# 6. Créer UniversityDegree
degree, _ = UniversityDegree.objects.get_or_create(
    degree_name="Master en Informatique",
    defaults={'description': 'Master en Sciences Informatiques'}
)

# 7. Créer User
user, _ = User.objects.get_or_create(
    email="teacher@test.com",
    defaults={
        'first_name': 'Jean',
        'last_name': 'Dupont'
    }
)

# 8. Créer Teacher
teacher, _ = Teacher.objects.get_or_create(
    user=user,
    defaults={
        'teacher_grade': 'Professeur',
        'degree': degree,
        'university': university,
        'speciality': 'Informatique'
    }
)

# 9. Créer Course
course, _ = Course.objects.get_or_create(
    course_name="Programmation Python",
    defaults={
        'course_code': 'PY101',
        'credits': 3,
        'description': 'Introduction à la programmation Python'
    }
)

# 10. Créer Attribution
attribution, _ = Attribution.objects.get_or_create(
    course=course,
    principal_teacher=teacher,
    academic_year=academic_year,
    defaults={
        'date_attribution': date.today(),
        'status_principal_teacher': 'Accepted',
        'submitted_by': user
    }
)

# 11. Créer ScheduleSlot
schedule_slot, _ = ScheduleSlot.objects.get_or_create(
    day_of_week="Monday",
    start_time=time(8, 0),
    end_time=time(10, 0),
    defaults={'schedule_name': 'Cours du matin'}
)

print("=== OBJETS CRÉÉS ===")
print(f"Room ID: {room.id}")
print(f"Attribution ID: {attribution.id}")
print(f"ScheduleSlot ID: {schedule_slot.id}")

print("\n=== JSON POUR TIMETABLE ===")
json_data = {
    "attribution": str(attribution.id),
    "room": room.id,
    "start_date": "2025-11-15",
    "end_date": "2026-03-15",
    "status": "Planned"
}

import json
print(json.dumps(json_data, indent=2))

print(f"\n=== SLOT ID SÉPARÉ (pour ManyToMany) ===")
print(f"Slot ID: {schedule_slot.id}")