#!/usr/bin/env python
import json
import os
from datetime import time

from datetime import time

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings.development")
django.setup()

from services.core_service.academic_module.teacher_app.models import Attribution
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.dependent_service.scheduling_module.scheduling_app.models import (
    ScheduleSlot,
)

# Vérifier les objets existants
print("=== OBJETS EXISTANTS ===")

# Rooms existantes
rooms = Room.objects.all()
print(f"Rooms disponibles: {rooms.count()}")
for room in rooms:
    print(f"  - Room ID: {room.id}, Name: {room.room_name}")

# Attributions existantes
attributions = Attribution.objects.all()
print(f"\nAttributions disponibles: {attributions.count()}")
for attr in attributions:
    print(f"  - Attribution ID: {attr.id}, Course: {attr.course}")

# ScheduleSlots existants
slots = ScheduleSlot.objects.all()
print(f"\nScheduleSlots disponibles: {slots.count()}")
for slot in slots:
    print(
        f"  - Slot ID: {slot.id}, Day: {slot.day_of_week}, Time: {slot.start_time}-{slot.end_time}"
    )
    print(
        f"  - Slot ID: {slot.id}, Day: {slot.day_of_week}, Time: {slot.start_time}-{slot.end_time}"
    )

# Si pas d'objets, créer un ScheduleSlot simple
if slots.count() == 0:
    slot = ScheduleSlot.objects.create(
        day_of_week="Monday",
        start_time=time(8, 0),
        end_time=time(10, 0),
        schedule_name="Cours du matin",
        schedule_name="Cours du matin",
    )
    print(f"\nScheduleSlot créé: {slot.id}")

# Générer JSON avec les premiers objets disponibles
if rooms.exists() and attributions.exists():
    first_room = rooms.first()
    first_attribution = attributions.first()


    print("\n=== JSON POUR TIMETABLE ===")
    import json

    json_data = {
        "attribution": str(first_attribution.id),
        "room": first_room.id,
        "start_date": "2025-11-15",
        "end_date": "2026-03-15",
        "status": "Planned",
        "status": "Planned",
    }
    print(json.dumps(json_data, indent=2))
else:
    print("\n❌ Pas assez d'objets pour créer un Timetable")
    print("Vous devez d'abord créer des objets Attribution et Room")

