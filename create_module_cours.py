# create_departments_and_classes.py
import os
import django
from uuid import UUID

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings.development")
django.setup()

from django.db import transaction

# Imports exacts selon ta structure
from services.core_service.academic_module.university_app.models import University
from services.core_service.academic_module.faculty_app.models import Faculty, TypeFormation
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.class_app.models import Class  # ou le bon app

UNIVERSITY_ID = UUID("02886153-a251-41c2-af8d-08417ffe6677")

# ===================================================================
# DONNÉES À CRÉER (tout corrigé orthographiquement)
# ===================================================================

DEPARTMENTS_DATA = [
    # FSI - Faculté des Sciences de l'Ingénieur
    {"faculty": "FACULTÉ DES SCIENCES DE L'INGÉNIEUR", "dept": "Génie Informatique",              "abbr": "GI"},
    {"faculty": "FACULTÉ DES SCIENCES DE L'INGÉNIEUR", "dept": "Génie Électrique",               "abbr": "GE"},
    {"faculty": "FACULTÉ DES SCIENCES DE L'INGÉNIEUR", "dept": "Génie Mécanique",                "abbr": "GM"},
    {"faculty": "FACULTÉ DES SCIENCES DE L'INGÉNIEUR", "dept": "Génie Civil",                    "abbr": "GC"},

    # FTIC - Faculté des Technologies de l'Information et de la Communication
    {"faculty": "FACULTÉ DES TECHNOLOGIES DE L'INFORMATION ET DE LA COMMUNICATION", "dept": "Informatique",                "abbr": "INFO"},
    {"faculty": "FACULTÉ DES TECHNOLOGIES DE L'INFORMATION ET DE LA COMMUNICATION", "dept": "Télécommunications",         "abbr": "TELECOM"},
    {"faculty": "FACULTÉ DES TECHNOLOGIES DE L'INFORMATION ET DE LA COMMUNICATION", "dept": "Réseaux et Sécurité",         "abbr": "RS"},

    # FSE - Faculté des Sciences de l'Environnement
    {"faculty": "FACULTÉ DES SCIENCES DE L'ENVIRONNEMENT", "dept": "Sciences de l'Environnement",     "abbr": "SE"},
    {"faculty": "FACULTÉ DES SCIENCES DE L'ENVIRONNEMENT", "dept": "Gestion des Ressources Naturelles", "abbr": "GRN"},

    # FHEC - Faculté des Hautes Études Commerciales
    {"faculty": "FACULTÉ DES HAUTES ÉTUDES COMMERCIALES", "dept": "Management",                       "abbr": "MGT"},
    {"faculty": "FACULTÉ DES HAUTES ÉTUDES COMMERCIALES", "dept": "Finance et Comptabilité",          "abbr": "FC"},
    {"faculty": "FACULTÉ DES HAUTES ÉTUDES COMMERCIALES", "dept": "Marketing et Commerce",            "abbr": "MC"},

    # ISP - Institut Supérieur Professionnel
    {"faculty": "INSTITUT SUPÉRIEUR PROFESSIONNEL", "dept": "Techniques Commerciales",                "abbr": "TC"},
    {"faculty": "INSTITUT SUPÉRIEUR PROFESSIONNEL", "dept": "Informatique de Gestion",               "abbr": "IG"},

    # ISIA - Institut Supérieur d'Informatique Appliquée
    {"faculty": "INSTITUT SUPÉRIEUR D'INFORMATIQUE APPLIQUÉE", "dept": "Développement Logiciel",      "abbr": "DL"},
    {"faculty": "INSTITUT SUPÉRIEUR D'INFORMATIQUE APPLIQUÉE", "dept": "Cybersécurité",               "abbr": "CYBER"},
    {"faculty": "INSTITUT SUPÉRIEUR D'INFORMATIQUE APPLIQUÉE", "dept": "Intelligence Artificielle",    "abbr": "IA"},
]

# Classes standard par département (L1 à L3 + M1/M2 si applicable)
CLASSES_PAR_DEPT = [
    "L1", "L2", "L3", "M1", "M2"
]

def create_departments_and_classes():
    print("Démarrage de la création des départements et classes...\n")

    with transaction.atomic():
        for item in DEPARTMENTS_DATA:
            faculty = Faculty.objects.get(faculty_name=item["faculty"])

            # Création du département (idempotent)
            dept, dept_created = Department.objects.get_or_create(
                department_name=item["dept"],
                faculty=faculty,
                defaults={"abreviation": item["abbr"]}
            )
            status_dept = "Créé" if dept_created else "Existant"
            print(f"{status_dept} Département → {dept} ({dept.abreviation}) - {faculty.faculty_abreviation}")

            # Création des classes L1/L2/L3/M1/M2
            for level in CLASSES_PAR_DEPT:
                class_name = f"{level} {item['dept']}" if level.startswith("M") else f"{level} {item['dept']}"

                obj, created = Class.objects.get_or_create(
                    class_name=class_name,
                    department=dept,
                )
                status_class = "Créé" if created else "Existant"
                print(f"   ├─ {status_class} Classe → {obj}")

    print("\nTout est terminé ! Départements + Classes créés avec succès !")

if __name__ == "__main__":
    create_departments_and_classes()