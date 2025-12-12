# Données de configuration pour l'import
from services.core_service.academic_module.faculty_app.models import TypeFormation

# Types de formation (seront créés automatiquement)
TYPE_FORMATIONS = [
    {"name": "Faculté", "code": "F", "description": "Formation de type Faculté"},
    {"name": "Institut", "code": "I", "description": "Formation de type Institut"},
    {"name": "Master", "code": "M"},
    {"name": "Doctorat", "code": "D"},
]

# Noms complets des départements
DEPARTMENT_NAMES = {
    "AC": "ANNEE COMMUNE",
    "GC": "GENIE CIVIL",
    "GE": "GENIE ELECTRIQUE",
    "PC": "PHASE COMMUNE",
    "GL": "GENIE LOGICIEL",
    "RT": "RESEAUX ET TELECOMMUNICATIONS",
    "SE": "SOL ET ENVIRONNEMENT",
    "EPA": "EAU POLLUTION ET ASSENISSEMENT",
    "CB": "CLIMAT ET BIODIVERSITE",
    "CCA": "COMPTABILITE CONTROL ET AUDIT",
    "FBA": "FINANCES BANQUES ET ASSURANCES",
    "MM": "MARKETING ET MANAGEMENT",
    "DC": "DEVELOPPEMENT COMMUNAUTRAIRE",
    "BA": "BANQUE ET ASSURANCE",
    "FC": "FINANCE ET COMPTABILITE",
    "IG": "INFORMATIQUE DE GESTION",
    "EMI": "ELECTRONIQUE ET MAINTENANCE INFORMATIQUE",
}


# Facultés officielles (fonction pour éviter les erreurs d'import)
def get_faculties():
    type_faculte = TypeFormation.objects.get(name="Faculté")
    type_institut = TypeFormation.objects.get(name="Institut")

    return [
        {
            "name": "FACULTÉ DES SCIENCES DE L'INGÉNIEUR",
            "abbr": "FSI",
            "type": type_faculte,
        },
        {
            "name": "FACULTÉ DES TECHNOLOGIES DE L'INFORMATION ET DE LA COMMUNICATION",
            "abbr": "FTIC",
            "type": type_faculte,
        },
        {
            "name": "FACULTÉ DES SCIENCES DE L'ENVIRONNEMENT",
            "abbr": "FSE",
            "type": type_faculte,
        },
        {
            "name": "FACULTÉ DES HAUTES ÉTUDES COMMERCIALES",
            "abbr": "FHEC",
            "type": type_faculte,
        },
        {
            "name": "INSTITUT SUPÉRIEUR PROFESSIONNEL",
            "abbr": "ISP",
            "type": type_institut,
        },
        {
            "name": "INSTITUT SUPÉRIEUR D'INFORMATIQUE APPLIQUÉE",
            "abbr": "ISIA",
            "type": type_institut,
        },
    ]


# Mapping des classes vers les semestres
CLASS_SEMESTER_MAPPING = {
    # Première année (Semestres 1 et 2)
    "BAC I": [1, 2],
    "IG I": 1,
    "EMI I": 1,
    "IDC I": 1,
    "IBA I": 1,
    "IFC I": 1,
    # Deuxième année (Semestres 3 et 4)
    "BAC II": [3, 4],
    "IG II": 3,
    "EMI II": 3,
    "IDC II": 3,
    "IBA II": 3,
    "IFC II": 3,
    # Troisième année (Semestres 5 et 6)
    "BAC III": [5, 6],
    "IDC III": 5,
    "IBA III": 5,
    "IFC III": 5,
    # Quatrième année (Semestres 7 et 8)
    "BAC IV": [7, 8],
}
