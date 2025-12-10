# FINAL_IMPORT_EXCEL_WITH_REAL_DEPARTMENTS.py
import os
import django
import pandas as pd
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ums.settings.development")
django.setup()

# ====================== IMPORTS ======================
from services.core_service.academic_module.university_app.models import University
from services.core_service.academic_module.faculty_app.models import Faculty, TypeFormation
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.module_app.models import Module,Semester
from services.core_service.academic_module.course_app.models import Course

# ====================== CONFIG ======================
UNIVERSITY_ID = "02886153-a251-41c2-af8d-08417ffe6677"
university = University.objects.get(id=UNIVERSITY_ID)
print(f"Université liée → {university} | ID: {UNIVERSITY_ID}\n")

# ====================== CRÉATION AUTOMATIQUE DES TypeFormation (PLUS JAMAIS D'ERREUR) ======================
print("Création / vérification des TypeFormation...")
TypeFormation.objects.get_or_create(name="Faculté",   defaults={"code": "F", "description": "Formation de type Faculté"})
TypeFormation.objects.get_or_create(name="Institut",  defaults={"code": "I", "description": "Formation de type Institut"})
TypeFormation.objects.get_or_create(name="Master",    defaults={"code": "M"})
TypeFormation.objects.get_or_create(name="Doctorat",  defaults={"code": "D"})
print("TypeFormation prêts !\n")

# Maintenant on peut les récupérer sans risque
type_faculte  = TypeFormation.objects.get(name="Faculté")
type_institut = TypeFormation.objects.get(name="Institut")

# ====================== SEMESTRES 1 à 8 ======================
for i in range(1, 9):
    Semester.objects.get_or_create(number=i, defaults={"name": f"Semestre {i}"})
semesters = {i: Semester.objects.get(number=i) for i in range(1, 9)}

# ====================== VRAIS NOMS DE DÉPARTEMENTS ======================
DEPARTMENT_NAMES = {
    "AC":   "ANNEE COMMUNE",
    "GC":   "GENIE CIVIL",
    "GE":   "GENIE ELECTRIQUE",
    "PC":   "PHASE COMMUNE",
    "GL":   "GENIE LOGICIEL",
    "RT":   "RESEAUX ET TELECOMMUNICATIONS",
    "SE":   "SOL ET ENVIRONNEMENT",
    "EPA":  "EAU POLLUTION ET ASSENISSEMENT",
    "CB":   "CLIMAT ET BIODIVERSITE",
    "CCA":  "COMPTABILITE CONTROL ET AUDIT",
    "FBA":  "FINANCES BANQUES ET ASSURANCES",
    "MM":   "MARKETING ET MANAGEMENT",
    "DC":   "DEVELOPPEMENT COMMUNAUTRAIRE",
    "BA":   "BANQUE ET ASSURANCE",
    "FC":   "FINANCE ET COMPTABILITE",
    "IG":   "INFORMATIQUE DE GESTION",
    "EMI":  "ELECTRONIQUE ET MAINTENANCE INFORMATIQUE",
}

# ====================== FACULTÉS OFFICIELLES ======================
FACULTIES = [
    {"name": "FACULTÉ DES SCIENCES DE L'INGÉNIEUR",                                 "abbr": "FSI",  "type": type_faculte},
    {"name": "FACULTÉ DES TECHNOLOGIES DE L'INFORMATION ET DE LA COMMUNICATION",   "abbr": "FTIC", "type": type_faculte},
    {"name": "FACULTÉ DES SCIENCES DE L'ENVIRONNEMENT",                             "abbr": "FSE",  "type": type_faculte},
    {"name": "FACULTÉ DES HAUTES ÉTUDES COMMERCIALES",                              "abbr": "FHEC", "type": type_faculte},
    {"name": "INSTITUT SUPÉRIEUR PROFESSIONNEL",                                    "abbr": "ISP",  "type": type_institut},
    {"name": "INSTITUT SUPÉRIEUR D'INFORMATIQUE APPLIQUÉE",                         "abbr": "ISIA", "type": type_institut},
]

# ====================== SEMESTRE INTELLIGENT ======================
def get_semester(class_name: str) -> Semester:
    c = class_name.upper()
    if any(x in c for x in ["BAC I", "IG I", "EMI I", "IDC I", "IBA I", "IFC I"]): return semesters[1]
    if any(x in c for x in ["BAC II", "IG II", "EMI II", "IDC II", "IBA II", "IFC II"]): return semesters[3]
    if any(x in c for x in ["BAC III", "IDC III", "IBA III", "IFC III"]): return semesters[5]
    if "BAC IV" in c: return semesters[7]
    return semesters[1]

# ====================== CHARGEMENT EXCEL ======================
EXCEL_PATH = "/home/elvis-brown/Downloads/courses.xlsx"
if not os.path.exists(EXCEL_PATH):
    raise FileNotFoundError(f"Fichier non trouvé → {EXCEL_PATH}")

df = pd.read_excel(EXCEL_PATH, sheet_name="LISTE DES COURS")
df[["FACU/INST", "DEP", "CLASSE"]] = df[["FACU/INST", "DEP", "CLASSE"]].ffill()
df = df.dropna(subset=["COURSE_NAME"])

print(f"{len(df)} lignes chargées depuis l'Excel\n")
print("DÉBUT DE L'IMPORT COMPLET...\n")

# ====================== IMPORT PRINCIPAL ======================
with transaction.atomic():
    # 1. Facultés
    for fac in FACULTIES:
        f, created = Faculty.objects.update_or_create(
            faculty_abreviation=fac["abbr"],
            defaults={
                "faculty_name": fac["name"],
                "types": fac["type"],
                "university": university,
            }
        )
        status = "Créée" if created else "Mise à jour"
        print(f"{status} → {f.faculty_abreviation} : {f.faculty_name}")

    print("\n" + "—" * 80 + "\n")

    modules_created = courses_created = 0

    for idx, row in df.iterrows():
        try:
            fac_abbr   = str(row["FACU/INST"]).strip().upper()
            dept_abbr  = str(row["DEP"]).strip().upper()
            class_name = str(row["CLASSE"]).strip()
            module_name= str(row["MODULE_NAME"]).strip()
            course_name= str(row["COURSE_NAME"]).strip()
            course_code= str(row["COURSE_CODE"]) if pd.notna(row["COURSE_CODE"]) and str(row["COURSE_CODE"]) != "nan" else ""
            cm = int(row["CM"] or 0)
            td = int(row["TD"] or 0)
            tp = int(row["TP"] or 0)

            faculty = Faculty.objects.get(faculty_abreviation=fac_abbr)

            # Département avec le vrai nom
            dept_name = DEPARTMENT_NAMES.get(dept_abbr, f"Département {dept_abbr}")
            department, _ = Department.objects.update_or_create(
                abreviation=dept_abbr,
                faculty=faculty,
                defaults={"department_name": dept_name}
            )

            class_obj, _ = Class.objects.get_or_create(class_name=class_name, department=department)
            semester = get_semester(class_name)

            module, mod_created = Module.objects.get_or_create(
                class_fk=class_obj,
                module_name=module_name,
                defaults={"code": course_code[:10], "semester": semester}
            )
            if mod_created: modules_created += 1

            course, crs_created = Course.objects.get_or_create(
                module=module,
                course_name=course_name,
                defaults={"cm": cm, "td": td, "tp": tp, "credits": max(1, (cm + td + tp) // 30)}
            )
            if crs_created:
                courses_created += 1
                print(f"{fac_abbr} → {dept_abbr} → {class_name} → S{semester.number} → {course_name}")

        except Exception as e:
            print(f"ERREUR ligne {idx+2} → {e}")

print("\n" + "="*80)
print("IMPORT TERMINÉ – TOUT EST PARFAIT")
print(f"Université : {university} (ID: {UNIVERSITY_ID})")
print(f"{modules_created} modules créés")
print(f"{courses_created} cours créés")
print("Tu peux maintenant passer à la suite sans problème")