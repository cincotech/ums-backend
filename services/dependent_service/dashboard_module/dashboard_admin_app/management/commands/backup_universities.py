from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from services.core_service.academic_module.university_app.models import University
from services.dependent_service.dashboard_module.dashboard_admin_app.backup_service import (
    SecureBackupService,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create encrypted backups for all universities"

    def add_arguments(self, parser):
        parser.add_argument(
            "--university-id",
            type=str,
            help="Backup specific university by ID",
        )

    def handle(self, *args, **options):
        university_id = options.get("university_id")

        if university_id:
            universities = University.objects.filter(id=university_id)
        else:
            universities = University.objects.all()

        if not universities.exists():
            self.stdout.write(self.style.ERROR("No universities found"))
            return

        # Get system user for backup
        system_user = User.objects.filter(is_superuser=True).first()
        if not system_user:
            self.stdout.write(self.style.ERROR("No superuser found for backup"))
            return

        for university in universities:
            try:
                backup = SecureBackupService.create_backup(university, system_user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Backup created for {university.university_name}: {backup.id}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Backup failed for {university.university_name}: {str(e)}"
                    )
                )
