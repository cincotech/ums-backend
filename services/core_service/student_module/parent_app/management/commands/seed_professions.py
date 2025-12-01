from django.core.management.base import BaseCommand

from services.core_service.student_module.parent_app.models import Profession

PROFESSIONS = [
    "Médecin",
    "Infirmier / Infirmière",
    "Pharmacien / Pharmacienne",
    "Chirurgien",
    "Dentiste",
    "Sage-femme",
    "Technicien de laboratoire médical",
    "Nutritionniste",
    "Psychologue clinicien",
    "Agent de santé communautaire",
    "Enseignant du primaire",
    "Enseignant du secondaire",
    "Professeur d’université",
    "Formateur professionnel",
    "Directeur d’établissement scolaire",
    "Administrateur communal",
    "Fonctionnaire de l’État",
    "Agent de bureau",
    "Chef de service administratif",
    "Secrétaire administratif",
    "Avocat",
    "Juge",
    "Notaire",
    "Greffier",
    "Conseiller juridique",
    "Policier",
    "Militaire",
    "Gardien de sécurité",
    "Agent de renseignement",
    "Agriculteur",
    "Éleveur",
    "Technicien agricole",
    "Ingénieur agronome",
    "Pêcheur",
    "Commerçant",
    "Entrepreneur",
    "Gestionnaire de magasin",
    "Agent de marketing",
    "Caissier",
    "Banquier",
    "Comptable",
    "Auditeur financier",
    "Analyste financier",
    "Agent de microfinance",
    "Ingénieur civil",
    "Technicien en électricité",
    "Mécanicien",
    "Technicien en informatique",
    "Ingénieur en télécommunications",
    "Maçon",
    "Menuisier",
    "Plombier",
    "Architecte",
    "Carreleur",
    "Chauffeur",
    "Conducteur de moto-taxi",
    "Conducteur de camion",
    "Agent de logistique",
    "Réceptionniste",
    "Serveur / Serveuse",
    "Chef cuisinier",
    "Guide touristique",
    "Gestionnaire d’hôtel",
    "Artiste",
    "Musicien",
    "Designer graphique",
    "Photographe",
    "Journaliste",
    "Travailleur social",
    "Conseiller social",
    "Animateur communautaire",
]


class Command(BaseCommand):
    help = "Seed des professions dans la table Profession"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("⏳ Insertion des professions..."))

        count = 0
        for name in PROFESSIONS:
            obj, created = Profession.objects.get_or_create(profession_name=name)
            if created:
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✔ {count} professions insérées avec succès !")
        )
