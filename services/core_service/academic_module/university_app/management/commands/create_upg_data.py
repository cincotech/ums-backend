from django.core.management.base import BaseCommand

from services.core_service.academic_module.faculty_app.models import (
    Faculty,
    TypeFormation,
)
from services.core_service.academic_module.university_app.models import University
from services.foundational_service.geo_module.country_app.models import Country


class Command(BaseCommand):
    help = "Créer le pays Burundi, l'université UPG, les TypeFormations et les Facultés"

    def handle(self, *args, **kwargs):

        # 1️⃣ Créer le pays Burundi
        burundi, created = Country.objects.get_or_create(
            country_name="Burundi", defaults={"code": "BI"}
        )
        self.stdout.write(
            self.style.SUCCESS(f"Création du pays : {burundi}")
            if created
            else self.style.WARNING(f"Le pays existe déjà : {burundi}")
        )

        # 2️⃣ Créer l’Université Polytechnique de Gitega (UPG)
        upg, created = University.objects.get_or_create(
            university_name="Université Polytechnique de Gitega",
            defaults={"university_abrev": "UPG", "country": burundi},
        )
        self.stdout.write(
            self.style.SUCCESS(f"Université créée : {upg}")
            if created
            else self.style.WARNING(f"L'université existe déjà : {upg}")
        )

        # 3️⃣ Créer les types de formation
        types_data = [
            {
                "name": "Faculté",
                "code": "F",
                "description": "Formation de niveau licence",
            },
            {
                "name": "Institut",
                "code": "I",
                "description": "Formation professionnelle et technique",
            },
            {
                "name": "Master",
                "code": "M",
                "description": "Formation de niveau master",
            },
            {
                "name": "Doctorat",
                "code": "D",
                "description": "Formation de recherche doctorale",
            },
        ]

        type_map = {}
        for t in types_data:
            tf, created = TypeFormation.objects.get_or_create(
                code=t["code"],
                defaults={"name": t["name"], "description": t["description"]},
            )
            type_map[t["code"]] = tf
            self.stdout.write(
                self.style.SUCCESS(f"TypeFormation créé : {tf}")
                if created
                else self.style.WARNING(f"TypeFormation déjà existant : {tf}")
            )

        # 4️⃣ Créer les Facultés de l’UPG (en français et réalistes)
        faculties_data = [
            {
                "name": "Faculté des Sciences et Technologies de l’Information",
                "abbreviation": "FSTI",
                "type_code": "F",
            },
            {
                "name": "Faculté des Sciences de l’Environnement",
                "abbreviation": "FSE",
                "type_code": "F",
            },
            {
                "name": "Faculté des Sciences de l’Ingénieur",
                "abbreviation": "FSI",
                "type_code": "F",
            },
            {
                "name": "Faculté des Hautes Études Commerciales",
                "abbreviation": "FHEC",
                "type_code": "M",
            },
        ]

        for f in faculties_data:
            tf = type_map[f["type_code"]]
            faculty, created = Faculty.objects.get_or_create(
                faculty_name=f["name"],
                university=upg,
                types=tf,  # ForeignKey
                defaults={"faculty_abreviation": f["abbreviation"]},
            )
            self.stdout.write(
                self.style.SUCCESS(f"Faculté créée : {faculty}")
                if created
                else self.style.WARNING(f"Faculté déjà existante : {faculty}")
            )

        self.stdout.write(
            self.style.SUCCESS("✅ Toutes les données ont été créées avec succès !")
        )
