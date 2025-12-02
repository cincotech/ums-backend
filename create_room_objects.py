#!/usr/bin/env python
import os

import django

from services.core_service.academic_module.university_app.models import University
from services.dependent_service.infrastructure_module.building_app.models import (
    Building,
)
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.geo_module.country_app.models import Country

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings.development")
django.setup()

# Créer ou récupérer un pays
country, created = Country.objects.get_or_create(
    country_name="Burundi", defaults={"code": "BI"}
)
print(f"Country: {country.country_name} ({'created' if created else 'exists'})")

# Créer ou récupérer une université
university, created = University.objects.get_or_create(
    university_name="Université Test",
    defaults={"university_abrev": "UT", "country": country},
)
print(
    f"University: {university.university_name} ({'created' if created else 'exists'})"
)

# Créer ou récupérer un bâtiment
building, created = Building.objects.get_or_create(
    building_name="Bâtiment Principal",
    university=university,
    defaults={"building_code": "BP001", "location": "Campus Central"},
)
print(f"Building: {building.building_name} ({'created' if created else 'exists'})")

# Créer une salle
room, created = Room.objects.get_or_create(
    room_name="Salle A101",
    building=building,
    defaults={"capacity": 50, "room_type": "classroom", "is_available": True},
)
print(f"Room: {room.room_name} ({'created' if created else 'exists'})")
print(f"Room ID: {room.id}")
print(f"Building ID: {building.id}")
print(f"University ID: {university.id}")


