from django.core.management.base import BaseCommand

from services.core_service.academic_module.faculty_app.models import (
    Faculty,
    TypeFormation,
)
from services.core_service.academic_module.university_app.models import University
from services.foundational_service.geo_module.country_app.models import Country


class Command(BaseCommand):
    help = "Create Burundi, UPG University, TypeFormations and Faculties"

    def handle(self, *args, **kwargs):
        # 1️⃣ Create country
        burundi, created = Country.objects.get_or_create(
            country_name="Burundi", defaults={"code": "BI"}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created country: {burundi}"))
        else:
            self.stdout.write(self.style.WARNING(f"Country already exists: {burundi}"))

        # 2️⃣ Create UPG University
        upg, created = University.objects.get_or_create(
            university_name="Gitega Polytechnic University",
            defaults={"university_abrev": "UPG", "country": burundi},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created university: {upg}"))
        else:
            self.stdout.write(self.style.WARNING(f"University already exists: {upg}"))

        # 3️⃣ Create TypeFormations
        types_data = [
            {"name": "Faculté", "code": "F", "description": "Undergraduate faculty"},
            {"name": "Institut", "code": "I", "description": "Professional institute"},
            {"name": "Master", "code": "M", "description": "Master programs"},
            {"name": "Doctorat", "code": "D", "description": "Doctorate programs"},
        ]

        type_map = {}
        for t in types_data:
            tf, created = TypeFormation.objects.get_or_create(
                code=t["code"],
                defaults={"name": t["name"], "description": t["description"]},
            )
            type_map[t["code"]] = tf
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created TypeFormation: {tf}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"TypeFormation already exists: {tf}")
                )

        # 4️⃣ Create Faculties for UPG
        faculties_data = [
            {"name": "Faculty of Engineering", "abreviation": "ENG", "type_code": "I"},
            {"name": "Faculty of Science", "abreviation": "SCI", "type_code": "F"},
            {"name": "Faculty of Economics", "abreviation": "ECO", "type_code": "M"},
            {"name": "Faculty of Medicine", "abreviation": "MED", "type_code": "D"},
        ]

        for f in faculties_data:
            tf = type_map.get(f["type_code"])
            faculty, created = Faculty.objects.get_or_create(
                faculty_name=f["name"],
                university=upg,
                defaults={"faculty_abreviation": f["abreviation"], "types": tf},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Faculty: {faculty}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Faculty already exists: {faculty}")
                )

        self.stdout.write(self.style.SUCCESS("✅ All data created successfully!"))
