"""
Synonym Configuration for Typesense Search.

This module provides domain-specific synonyms to improve search recall.
Synonyms allow users to find results even when using different terminology.

Synonyms are organized by domain and can be easily extended.

Typesense v30+ : les synonymes sont globaux via l'API synonym_sets.
Chaque set contient des items [{id, synonyms}].
Pour les appliquer à une collection, il faut référencer le nom du set
dans le champ `synonym_sets` du schéma de la collection.
"""

# ---------------------------------------------------------------------------
# Nom du synonym set global utilisé par toutes les collections
# ---------------------------------------------------------------------------
UMS_SYNONYM_SET_NAME = "ums-synonyms"

# ---------------------------------------------------------------------------
# Academic domain synonyms - French/English and abbreviations
# ---------------------------------------------------------------------------
ACADEMIC_SYNONYMS: dict[str, list[str]] = {
    # Informatique / Computer Science
    "informatique": ["computer", "computing", "it", "ict", "si"],
    "ordinateur": ["computer", "pc"],
    "programmation": ["programming", "coding", "dev", "development"],
    "algorithme": ["algorithm", "algo", "algorithms"],
    "base de données": ["database", "bd", "db", "bdd", "base de donnees"],
    "réseau": ["network", "reseaux", "networks", "reseau"],
    "système": ["system", "systeme", "systems", "systemes"],
    # Programming languages (abbreviations and full names)
    "java": ["java programming"],
    "python": ["python programming"],
    "javascript": ["js", "ecmascript"],
    "sql": ["structured query language", "base de données sql"],
    # Electronics and Automation
    "automate": ["automates", "automation", "automatisé", "automatise"],
    "instrumentation": ["instruments", "mesure", "mesures", "measurements"],
    "électronique": ["electronique", "electronic", "electronics", "electroniques"],
    "télécommunication": ["telecommunication", "telecom", "telecoms"],
    # Mathematics and Science
    "mathématiques": ["mathematiques", "mathematics", "math", "maths"],
    "physique": ["physics", "physique"],
    "chimie": ["chemistry", "chimie"],
    # Business and Management
    "gestion": ["management", "business", "admin"],
    "finance": ["financial", "financier"],
    "comptabilité": ["accounting", "comptabilite", "compta"],
    # Network and Systems
    "réseaux informatiques": ["computer networks", "reseaux", "networking"],
    "sécurité": ["security", "securite", "cybersecurity", "cybersécurité"],
    "administration": ["admin", "administration", "administrateur"],
    # Education terms
    "cours": ["course", "module", "lesson"],
    "module": ["cours", "course", "unit"],
    "semestre": ["semester", "term"],
    "licence": ["bachelor", "bac", "undergraduate"],
    "master": ["masters", "graduate", "postgraduate"],
    "doctorat": ["phd", "doctorate", "doctoral"],
    # Common French/English pairs
    "introduction": ["intro", "introduction", "initiation"],
    "avancé": ["avance", "advanced", "avancées", "avances"],
    "débutant": ["debutant", "beginner", "basic", "basique", "initiation"],
    "appliqué": ["applique", "applied", "appliquée", "appliquee"],
    # Navigation / UI terms
    "accueil": ["home", "dashboard", "tableau de bord", "tableau_de_bord"],
    "home": ["accueil", "dashboard", "tableau de bord", "main"],
    "dashboard": [
        "tableau de bord",
        "tableau_de_bord",
        "accueil",
        "home",
        "overview",
        "vue d'ensemble",
    ],
    "profil": ["profile", "compte", "account", "my account", "mon compte"],
    "paramètres": ["settings", "configuration", "config", "parametres", "preferences"],
    "déconnexion": ["logout", "sign out", "deconnexion", "quitter", "se deconnecter"],
    "connexion": ["login", "sign in", "se connecter", "authentification", "auth"],
    "mot de passe": ["password", "mdp", "passwd", "mot_de_passe"],
    # User / People
    "utilisateur": ["user", "users", "utilisateurs", "usager", "compte"],
    "étudiant": [
        "student",
        "etudiant",
        "students",
        "etudiants",
        "élève",
        "eleve",
        "apprenant",
    ],
    "enseignant": [
        "teacher",
        "professeur",
        "prof",
        "enseignant",
        "teachers",
        "formateur",
        "instructeur",
    ],
    "administrateur": ["admin", "administrator", "gestionnaire", "super admin"],
    "personnel": [
        "staff",
        "personnel",
        "employé",
        "employe",
        "employee",
        "employees",
        "ressources humaines",
        "rh",
        "hr",
    ],
    "directeur": ["director", "head", "chef", "responsable", "doyen", "dean"],
    # Academic roles and structures
    "département": ["department", "dept", "departement", "section", "service"],
    "faculté": ["faculty", "faculte", "fac", "college", "école", "ecole"],
    "université": ["university", "universite", "uni", "campus", "institution"],
    "classe": ["class", "promotion", "group", "groupe", "niveau"],
    "inscription": [
        "enrollment",
        "registration",
        "inscription",
        "enregistrement",
        "admission",
    ],
    # Common actions
    "rechercher": ["search", "recherche", "chercher", "find", "trouver", "query"],
    "créer": ["create", "new", "ajouter", "add", "nouveau", "creer"],
    "modifier": ["edit", "update", "change", "modify", "éditer", "editer"],
    "supprimer": ["delete", "remove", "effacer", "détruire", "detruire"],
    "afficher": ["show", "display", "view", "voir", "consulter", "lister", "list"],
    "exporter": ["export", "download", "télécharger", "telecharger", "csv", "pdf"],
    "importer": ["import", "upload", "charger", "bulk", "batch"],
    # Status / States
    "actif": ["active", "enabled", "activé", "enable"],
    "inactif": ["inactive", "disabled", "désactivé", "desactive", "disable"],
    "archivé": ["archived", "archive", "archivee"],
    "en attente": ["pending", "waiting", "en_attente", "en cours", "processing"],
    "validé": [
        "validated",
        "approved",
        "valide",
        "accepté",
        "accepte",
        "confirmed",
        "confirmé",
    ],
    "rejeté": ["rejected", "refusé", "refuse", "denied", "rejete"],
}

# ---------------------------------------------------------------------------
# Abbreviations that should be expanded
# ---------------------------------------------------------------------------
ABBREVIATIONS: dict[str, list[str]] = {
    "ai": ["artificial intelligence", "intelligence artificielle", "ia"],
    "ml": ["machine learning", "apprentissage automatique"],
    "dl": ["deep learning", "apprentissage profond"],
    "iot": ["internet of things", "internet des objets"],
    "api": ["application programming interface", "interface de programmation"],
    "ui": ["user interface", "interface utilisateur"],
    "ux": ["user experience", "experience utilisateur"],
    "sql": ["structured query language"],
    "nosql": ["not only sql"],
    "oop": ["object oriented programming", "programmation orientee objet", "poo"],
    "http": ["hypertext transfer protocol"],
    "tcp": ["transmission control protocol"],
    "ip": ["internet protocol", "protocole internet"],
    "lan": ["local area network", "reseau local"],
    "wan": ["wide area network", "reseau etendu"],
    "vpn": ["virtual private network", "reseau prive virtuel"],
    "db": ["database", "base de donnees", "bdd"],
    "os": ["operating system", "systeme d exploitation", "systeme exploitation"],
    "cpu": ["central processing unit", "processeur", "processor"],
    "ram": ["random access memory", "memoire vive", "memoire"],
    "gpu": ["graphics processing unit", "carte graphique"],
    "ict": [
        "information and communication technology",
        "tic",
        "technologies de l information",
    ],
    "cs": ["computer science", "informatique"],
    "it": ["information technology", "technologies de l information"],
    # User / identity abbreviations
    "id": ["identifier", "identifiant", "identité", "identity"],
    "nom": ["name", "lastname", "last_name", "family name", "surname"],
    "prenom": ["firstname", "first_name", "given name", "prénom"],
    "email": ["mail", "courriel", "e-mail", "adresse mail", "email address"],
    "tel": ["phone", "telephone", "téléphone", "mobile", "gsm", "contact", "cell"],
    "cni": [
        "carte d'identité",
        "national id",
        "identity card",
        "id card",
        "piece identite",
        "passeport",
    ],
    "matricule": [
        "student id",
        "numéro étudiant",
        "registration number",
        "numero etudiant",
        "immatriculation",
    ],
    "naissance": [
        "birth",
        "né",
        "nee",
        "born",
        "date de naissance",
        "date_naissance",
        "anniversaire",
    ],
    "genre": ["gender", "sexe", "sex", "civilite"],
    "adresse": ["address", "localisation", "location", "domicile", "residence"],
    "ville": ["city", "town", "commune", "localité", "localite"],
    "pays": ["country", "nation", "état", "etat"],
    "code postal": ["zip", "postal code", "zip code", "code_postal"],
}

# ---------------------------------------------------------------------------
# ALL_SYNONYMS — merged dict used by build_typesense_synonym_items()
# ---------------------------------------------------------------------------
ALL_SYNONYMS: dict[str, list[str]] = {**ACADEMIC_SYNONYMS, **ABBREVIATIONS}


def build_typesense_synonym_items() -> list[dict]:
    """
    Build synonym items in Typesense v30+ format.

    Each item is:
        {"id": "unique_id", "synonyms": ["term1", "term2", ...]}

    These items go inside a synonym set:
        {"items": [...]}
    """
    items = []
    for idx, (root, synonym_list) in enumerate(ALL_SYNONYMS.items()):
        # Create a safe ID — replace spaces and special chars
        safe_id = root.replace(" ", "_").replace("'", "").replace("é", "e")[:30]
        item_id = f"syn_{idx:03d}_{safe_id}"

        # Include the root word in the synonym list, deduplicate
        all_forms = list(dict.fromkeys([root] + synonym_list))

        items.append(
            {
                "id": item_id,
                "synonyms": all_forms,
            }
        )

    return items


def get_synonyms_for_collection(collection_name: str) -> dict[str, list[str]]:
    """
    Get synonyms appropriate for a specific collection.

    Args:
        collection_name: Name of the Typesense collection

    Returns:
        Dict mapping terms to their synonyms
    """
    synonyms = dict(ACADEMIC_SYNONYMS)
    synonyms.update(ABBREVIATIONS)
    return synonyms
