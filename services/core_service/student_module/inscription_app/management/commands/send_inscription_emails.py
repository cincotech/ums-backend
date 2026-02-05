from django.core.management.base import BaseCommand

from services.core_service.student_module.inscription_app.email_utils import (
    send_bulk_inscription_emails,
    send_inscription_confirmation_email,
)
from services.core_service.student_module.inscription_app.models import Inscription


class Command(BaseCommand):
    help = "Envoie des emails de confirmation d'inscription aux étudiants"

    def add_arguments(self, parser):
        parser.add_argument(
            "--inscription-id",
            type=str,
            help="ID de l'inscription spécifique",
        )
        parser.add_argument(
            "--status",
            type=str,
            default="Active",
            help="Statut des inscriptions (Active, Pending, etc.)",
        )
        parser.add_argument(
            "--academic-year",
            type=str,
            help="ID de l'année académique",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Envoyer à toutes les inscriptions actives",
        )

    def handle(self, *args, **options):
        inscription_id = options.get("inscription_id")
        status = options.get("status")
        academic_year = options.get("academic_year")
        send_all = options.get("all")

        if inscription_id:
            try:
                inscription = Inscription.objects.get(id=inscription_id)
                self.stdout.write(
                    self.style.WARNING(
                        f"Envoi de l'email pour {inscription.student.user.get_full_name()}..."
                    )
                )

                if send_inscription_confirmation_email(inscription):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Email envoyé avec succès à {inscription.student.user.email}"
                        )
                    )
                else:
                    self.stdout.write(self.style.ERROR("✗ Échec de l'envoi de l'email"))
            except Inscription.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Inscription {inscription_id} introuvable")
                )
            return

        inscriptions = Inscription.objects.all()

        if not send_all:
            inscriptions = inscriptions.filter(regist_status=status)

        if academic_year:
            inscriptions = inscriptions.filter(academic_year_id=academic_year)

        count = inscriptions.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING("Aucune inscription trouvée avec ces critères")
            )
            return

        self.stdout.write(
            self.style.WARNING(f"Envoi d'emails pour {count} inscription(s)...")
        )

        confirm = input(f"Voulez-vous vraiment envoyer {count} email(s) ? (oui/non): ")
        if confirm.lower() not in ["oui", "yes", "y", "o"]:
            self.stdout.write(self.style.WARNING("Opération annulée"))
            return

        stats = send_bulk_inscription_emails(inscriptions)

        self.stdout.write(self.style.SUCCESS("\n✓ Envoi terminé :"))
        self.stdout.write(f'  Total      : {stats["total"]}')
        self.stdout.write(self.style.SUCCESS(f'  Succès     : {stats["success"]}'))
        if stats["failed"] > 0:
            self.stdout.write(self.style.ERROR(f'  Échecs     : {stats["failed"]}'))
