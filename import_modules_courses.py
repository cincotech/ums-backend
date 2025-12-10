import os
import random

import django
import pandas as pd
from django.db import transaction
from dotenv import load_dotenv

# Configuration Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings.development")
django.setup()

# Chargement des variables d'environnement
load_dotenv("import_config.env")

# Import des données de configuration
from import_data import (
    CLASS_SEMESTER_MAPPING,
    DEPARTMENT_NAMES,
    TYPE_FORMATIONS,
    get_faculties,
)
from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import (
    Faculty,
    TypeFormation,
)
from services.core_service.academic_module.module_app.models import Module, Semester
from services.core_service.academic_module.university_app.models import University

# Imports Django
from services.foundational_service.geo_module.country_app.models import Country


def get_semester(class_name: str) -> Semester:
    """Détermine le semestre basé sur le nom de la classe (aléatoire pour BAC)"""
    c = class_name.upper()
    for class_key, semester_data in CLASS_SEMESTER_MAPPING.items():
        if class_key in c:
            # Si c'est une liste (BAC), choisir aléatoirement
            if isinstance(semester_data, list):
                return Semester.objects.get(number=random.choice(semester_data))
            return Semester.objects.get(number=semester_data)
    return Semester.objects.get(number=1)  # Par défaut semestre 1


def setup_initial_data():
    """Création des données de base"""
    print("Création / vérification des TypeFormation...")
    for tf in TYPE_FORMATIONS:
        TypeFormation.objects.get_or_create(
            name=tf["name"], defaults={k: v for k, v in tf.items() if k != "name"}
        )
    print("TypeFormation prêts !\n")

    # Création des semestres 1 à 8
    for i in range(1, 9):
        Semester.objects.get_or_create(number=i, defaults={"name": f"Semestre {i}"})


def main():
    # Variables d'environnement
    EXCEL_FOLDER = os.getenv("EXCEL_FOLDER")
    EXCEL_FILE = os.getenv("EXCEL_FILE")
    EXCEL_SHEET = os.getenv("EXCEL_SHEET")

    # Création du pays Burundi
    country, created = Country.objects.get_or_create(
        country_name="Burundi", defaults={"code": "BI"}
    )
    print(f"Pays → {country.country_name} {'(créé)' if created else '(existant)'}")

    # Création de l'université
    university, created = University.objects.get_or_create(
        university_name="UNIVERSITE POLYTECHNIQUE DE GITEGA",
        defaults={"university_abrev": "UPG", "country": country},
    )
    print(
        f"Université → {university.university_name} {'(créée)' if created else '(existante)'} | ID: {university.id}\n"
    )

    # Configuration initiale
    setup_initial_data()

    # Chargement du fichier Excel
    EXCEL_PATH = os.path.join(EXCEL_FOLDER, EXCEL_FILE)
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Fichier non trouvé → {EXCEL_PATH}")

    df = pd.read_excel(EXCEL_PATH, sheet_name=EXCEL_SHEET)
    df[["FACU/INST", "DEP", "CLASSE"]] = df[["FACU/INST", "DEP", "CLASSE"]].ffill()
    df = df.dropna(subset=["COURSE_NAME"])

    print(f"{len(df)} lignes chargées depuis l'Excel\n")
    print("DÉBUT DE L'IMPORT COMPLET...\n")

    with transaction.atomic():
        # 1. Création des facultés
        faculties = get_faculties()
        for fac in faculties:
            f, created = Faculty.objects.update_or_create(
                faculty_abreviation=fac["abbr"],
                defaults={
                    "faculty_name": fac["name"],
                    "types": fac["type"],
                    "university": university,
                },
            )
            status = "Créée" if created else "Mise à jour"
            print(f"{status} → {f.faculty_abreviation} : {f.faculty_name}")

        print("\n" + "—" * 80 + "\n")

        modules_created = courses_created = 0

        # 2. Import des modules et cours
        for idx, row in df.iterrows():
            try:
                fac_abbr = str(row["FACU/INST"]).strip().upper()
                dept_abbr = str(row["DEP"]).strip().upper()
                class_name = str(row["CLASSE"]).strip()
                module_name = str(row["MODULE_NAME"]).strip()
                course_name = str(row["COURSE_NAME"]).strip()
                course_code = (
                    str(row["COURSE_CODE"])
                    if pd.notna(row["COURSE_CODE"]) and str(row["COURSE_CODE"]) != "nan"
                    else ""
                )
                cm = int(row["CM"] or 0)
                td = int(row["TD"] or 0)
                tp = int(row["TP"] or 0)

                faculty = Faculty.objects.get(faculty_abreviation=fac_abbr)

                # Département avec le vrai nom
                dept_name = DEPARTMENT_NAMES.get(dept_abbr, f"Département {dept_abbr}")
                department, _ = Department.objects.update_or_create(
                    abreviation=dept_abbr,
                    faculty=faculty,
                    defaults={"department_name": dept_name},
                )

                class_obj, _ = Class.objects.get_or_create(
                    class_name=class_name, department=department
                )
                semester = get_semester(class_name)

                module, mod_created = Module.objects.get_or_create(
                    class_fk=class_obj,
                    module_name=module_name,
                    defaults={"code": course_code[:10], "semester": semester},
                )
                if mod_created:
                    modules_created += 1

                course, crs_created = Course.objects.get_or_create(
                    module=module,
                    course_name=course_name,
                    defaults={
                        "cm": cm,
                        "td": td,
                        "tp": tp,
                        "credits": max(1, (cm + td + tp) // 30),
                    },
                )
                if crs_created:
                    courses_created += 1
                    print(
                        f"{fac_abbr} → {dept_abbr} → {class_name} → S{semester.number} → {course_name}"
                    )

            except Exception as e:
                print(f"ERREUR ligne {idx+2} → {e}")

    print("\n" + "=" * 80)
    print("IMPORT TERMINÉ – TOUT EST PARFAIT")
    print(f"Université : {university} (ID: {university.id})")
    print(f"{modules_created} modules créés")
    print(f"{courses_created} cours créés")


if __name__ == "__main__":
    main()
