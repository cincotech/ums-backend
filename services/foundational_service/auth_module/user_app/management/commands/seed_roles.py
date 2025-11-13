from django.core.management.base import BaseCommand

from services.foundational_service.auth_module.user_app.models import Role

ROLES = [
    (
        "super_admin",
        "Full system access. Manages all users, configurations, roles, and global security. Handles system backup, audit, and restoration. | Accès complet au système. Gère tous les utilisateurs, configurations, rôles et sécurité globale. Gère la sauvegarde, l'audit et la restauration du système.",
    ),
    (
        "rector",
        "Highest authority of the university, overseeing institutional leadership, academic and administrative supervision, and exceptional authorizations. | Autorité suprême de l'université, supervisant la direction institutionnelle, la supervision académique et administrative, et les autorisations exceptionnelles.",
    ),
    (
        "director_academic",
        "Supervises academic programs, validates course assignments, and monitors performance under the Rector's direction. | Supervise les programmes académiques, valide les affectations de cours et surveille la performance sous la direction du Recteur.",
    ),
    (
        "director_quality_assurance",
        "Analyzes performance, ensures compliance with accreditation standards, manages academic quality evaluations, and oversees institutional quality improvement. | Analyse la performance, assure la conformité aux normes d'accréditation, gère les évaluations de qualité académique et supervise l'amélioration continue de la qualité institutionnelle.",
    ),
    (
        "dean",
        "Faculty-level academic administrator managing programs, teaching schedules, and student academic progress. | Administrateur académique au niveau de la faculté, gère les programmes, les emplois du temps des cours et le progrès académique des étudiants.",
    ),
    (
        "student_service",
        "Handles student registration, re-enrollment, absences, documents, orientation, and administrative records. | Gère l'inscription des étudiants, la réinscription, les absences, les documents, l'orientation et les dossiers administratifs.",
    ),
    (
        "finance_service",
        "Manages payments, tuition collection, and student financial records, ensuring accurate accounting and reporting. | Gère les paiements, la collecte des frais de scolarité et les dossiers financiers des étudiants, assurant une comptabilité et un reporting précis.",
    ),
    (
        "general_service",
        "Provides administrative and logistical support, ensuring smooth daily operations and coordination between departments. | Fournit un support administratif et logistique, assurant le bon déroulement des opérations quotidiennes et la coordination entre les départements.",
    ),
    (
        "rector_office",
        "Assists the Rector with administrative coordination, communication, and governance-related activities. | Assiste le Recteur dans la coordination administrative, la communication et les activités liées à la gouvernance.",
    ),
    (
        "academic_affairs",
        "Coordinates academic content, examinations, faculty activities, and ensures regulation compliance. | Coordonne le contenu académique, les examens, les activités du corps professoral et assure le respect des règlements.",
    ),
    (
        "teacher",
        "Delivers courses, evaluates students, participates in academic research, and contributes to curriculum development. | Dispense les cours, évalue les étudiants, participe à la recherche académique et contribue au développement du programme.",
    ),
    (
        "supervisor",
        "Guides students in academic and research activities, monitors progress, and provides mentorship. | Guide les étudiants dans les activités académiques et de recherche, surveille le progrès et fournit un mentorat.",
    ),
    (
        "student",
        "Manages own academic profile, enrollments, payments, course participation, and document requests. | Gère son propre profil académique, ses inscriptions, paiements, participation aux cours et demandes de documents.",
    ),
    (
        "alumni",
        "Former student maintaining engagement, mentoring, offering career support, and requesting academic documents post-graduation. | Ancien étudiant maintenant engagé, mentor, offrant un soutien de carrière et demandant des documents académiques après l'obtention du diplôme.",
    ),
    (
        "'delegate'",
        "Represents the students of a class or group, communicates with teachers and administration, and organizes class activities. | Représente les étudiants d'une classe ou d'un groupe, communique avec les enseignants et l'administration, et organise les activités de la classe.",
    ),
]


class Command(BaseCommand):
    help = "Seed initial roles into the database."

    def handle(self, *args, **options):
        for name, description in ROLES:
            Role.objects.get_or_create(name=name, defaults={"description": description})
        self.stdout.write(self.style.SUCCESS("✅ Roles seeded successfully!"))
