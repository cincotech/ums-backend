from django.core.management.base import BaseCommand

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.public_app.models import Program


class Command(BaseCommand):
    help = "Ajoute les programmes académiques complets"

    def handle(self, *args, **options):
        faculties = Faculty.objects.all()

        if not faculties.exists():
            self.stdout.write(self.style.ERROR("Aucune faculté trouvée!"))
            return

        programs_data = [
            {
                "presentation": "Programme de master en informatique avancée",
                "content": [
                    "Algorithmes avancés",
                    "Intelligence artificielle",
                    "Cloud computing",
                ],
                "admission_conditions": ["Licence en informatique", "Moyenne >= 12/20"],
                "prerequisites": [
                    "Programmation orientée objet",
                    "Structures de données",
                ],
                "internship": "Stage de 6 mois en entreprise",
                "duration": "2 ans",
                "career_opportunities": [
                    "Architecte logiciel",
                    "Lead developer",
                    "Consultant IT",
                ],
            },
            {
                "presentation": "Programme de licence en gestion d'entreprise",
                "content": [
                    "Comptabilité",
                    "Marketing",
                    "Ressources humaines",
                    "Finance",
                ],
                "admission_conditions": ["Bac général", "Moyenne >= 10/20"],
                "prerequisites": ["Mathématiques", "Économie"],
                "internship": "Stage de 3 mois",
                "duration": "3 ans",
                "career_opportunities": ["Manager", "Consultant", "Entrepreneur"],
            },
            {
                "presentation": "Bases de données; Programmation web et logiciels\nNotion de comptabilité et entrepreneuriat",
                "content": [
                    "Outils de communication et de recherche",
                    "Animation des affaires",
                    "Conduite des affaires",
                    "Sécurisation des opérations d'affaires",
                    "Droit des marchés",
                    "Gestion juridique des entreprises",
                    "Droit de règlement des différends commerciaux",
                    "Droit et environnement international de l'entreprise",
                    "Entrepreneuriat",
                ],
                "admission_conditions": [
                    "Diplôme conférant le grade de Bachelier dans un domaine en rapport avec le Master",
                    "Diplôme conférant le grade de Licencié (ancien système) ou équivalent",
                    "Diplôme burundais ou étranger admis en équivalence",
                ],
                "prerequisites": [
                    "Connaissances de base en droit",
                    "Capacité d'analyse juridique",
                    "Bonne maîtrise du français",
                ],
                "internship": "Des stages sont organisés chaque année depuis la deuxième : un mois pour la deuxième et la troisième années et quatre mois pour la quatrième année avec redaction d'un rapport de stage.",
                "duration": "4 ans",
                "career_opportunities": [
                    "Juriste d'entreprise",
                    "Juriste d'assurance",
                    "Cadre juridique",
                    "Avocat d'affaires",
                    "Mandataire judiciaire",
                    "Conseiller juridique",
                ],
            },
            {
                "presentation": "Programme de licence en sciences de l'ingénieur",
                "content": [
                    "Mécanique",
                    "Électronique",
                    "Thermodynamique",
                    "Matériaux",
                ],
                "admission_conditions": ["Bac scientifique", "Moyenne >= 11/20"],
                "prerequisites": ["Mathématiques avancées", "Physique", "Chimie"],
                "internship": "Stage de 2 mois en industrie",
                "duration": "3 ans",
                "career_opportunities": [
                    "Ingénieur",
                    "Technicien supérieur",
                    "Chef de projet",
                ],
            },
            {
                "presentation": "Programme de master en économie et finance",
                "content": [
                    "Macroéconomie",
                    "Microéconomie",
                    "Finance d'entreprise",
                    "Marchés financiers",
                ],
                "admission_conditions": [
                    "Licence en économie ou gestion",
                    "Moyenne >= 12/20",
                ],
                "prerequisites": ["Économétrie", "Statistiques"],
                "internship": "Stage de 5 mois en institution financière",
                "duration": "2 ans",
                "career_opportunities": [
                    "Analyste financier",
                    "Économiste",
                    "Gestionnaire de portefeuille",
                ],
            },
        ]

        created_count = 0
        for idx, program_data in enumerate(programs_data):
            faculty = faculties[idx % faculties.count()]
            program, created = Program.objects.get_or_create(
                faculty=faculty,
                presentation=program_data["presentation"],
                defaults={**program_data, "is_active": True},
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Programme créé pour {faculty.faculty_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ Programme existant pour {faculty.faculty_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"✓ {created_count} programme(s) créé(s) avec succès!")
        )
