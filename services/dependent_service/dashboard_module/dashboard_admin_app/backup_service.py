import os
from io import StringIO

from cryptography.fernet import Fernet
from django.core.management import call_command
from django.utils import timezone

from services.core_service.academic_module.university_app.models import University
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
    BackupRecord,
    EmergencyRecovery,
)


class SecureBackupService:
    """Secure backup and restore service using django-dbbackup"""

    BACKUP_DIR = "backups"
    ENCRYPTION_KEY_ENV = "BACKUP_ENCRYPTION_KEY"

    @staticmethod
    def get_encryption_key():
        """Get or generate encryption key"""
        key = os.getenv(SecureBackupService.ENCRYPTION_KEY_ENV)
        if not key:
            key = Fernet.generate_key().decode()
            os.environ[SecureBackupService.ENCRYPTION_KEY_ENV] = key
        return key.encode() if isinstance(key, str) else key

    @staticmethod
    def encrypt_backup(data, key):
        """Encrypt backup data"""
        cipher = Fernet(key)
        return cipher.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_backup(encrypted_data, key):
        """Decrypt backup data"""
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def create_backup(university, initiated_by):
        """Create encrypted backup for university"""
        backup = BackupRecord.objects.create(
            backup_type="full",
            status="running",
            initiated_by=initiated_by,
            metadata={
                "university_id": str(university.id),
                "university_name": university.university_name,
                "encrypted": True,
            },
        )

        try:
            os.makedirs(SecureBackupService.BACKUP_DIR, exist_ok=True)

            # Create backup using django-dbbackup
            output = StringIO()
            call_command("dbbackup", stdout=output, verbosity=0)

            # Get latest backup file
            backup_files = sorted(
                [
                    f
                    for f in os.listdir(SecureBackupService.BACKUP_DIR)
                    if f.endswith(".dump")
                ],
                key=lambda x: os.path.getctime(
                    os.path.join(SecureBackupService.BACKUP_DIR, x)
                ),
                reverse=True,
            )

            if backup_files:
                backup_file = os.path.join(
                    SecureBackupService.BACKUP_DIR, backup_files[0]
                )

                # Read and encrypt backup
                with open(backup_file, "rb") as f:
                    backup_data = f.read()

                key = SecureBackupService.get_encryption_key()
                encrypted_data = SecureBackupService.encrypt_backup(
                    backup_data.decode("latin-1"), key
                )

                # Save encrypted backup
                encrypted_file = backup_file.replace(".dump", ".enc")
                with open(encrypted_file, "w") as f:
                    f.write(encrypted_data)

                file_size = os.path.getsize(encrypted_file)

                backup.mark_completed(file_path=encrypted_file, file_size=file_size)

                # Log success
                AuditLog.objects.create(
                    user=initiated_by,
                    university=university,
                    action="backup_initiated",
                    severity="info",
                    description=f"Encrypted backup created for {university.university_name}",
                    success=True,
                )

                return backup
            else:
                raise Exception("No backup file generated")

        except Exception as e:
            backup.mark_failed(str(e))
            AuditLog.objects.create(
                user=initiated_by,
                university=university,
                action="backup_initiated",
                severity="error",
                description=f"Backup failed for {university.university_name}",
                error_message=str(e),
                success=False,
            )
            raise

    @staticmethod
    def restore_backup(backup_record, performed_by):
        """Restore from encrypted backup"""
        recovery = EmergencyRecovery.objects.create(
            recovery_type="data_recovery",
            performed_by=performed_by,
            status="in_progress",
            reason=f"Restoring from backup {backup_record.id}",
            details={"backup_id": str(backup_record.id)},
        )

        try:
            if not backup_record.file_path or not os.path.exists(
                backup_record.file_path
            ):
                raise Exception("Backup file not found")

            # Decrypt backup
            with open(backup_record.file_path, "r") as f:
                encrypted_data = f.read()

            key = SecureBackupService.get_encryption_key()
            decrypted_data = SecureBackupService.decrypt_backup(encrypted_data, key)

            # Write decrypted data to temp file
            temp_file = backup_record.file_path.replace(".enc", ".tmp")
            with open(temp_file, "w") as f:
                f.write(decrypted_data)

            # Restore using django-dbbackup
            output = StringIO()
            call_command(
                "dbrestore",
                input_filename=temp_file,
                stdout=output,
                verbosity=0,
                interactive=False,
            )

            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)

            university_id = backup_record.metadata.get("university_id")
            university = University.objects.get(id=university_id)

            recovery.status = "completed"
            recovery.result = (
                f"Successfully restored data for {university.university_name}"
            )
            recovery.completed_at = timezone.now()
            recovery.save()

            AuditLog.objects.create(
                user=performed_by,
                university=university,
                action="restore_initiated",
                severity="info",
                description=f"Data restored from encrypted backup {backup_record.id}",
                success=True,
            )

            return recovery

        except Exception as e:
            recovery.status = "failed"
            recovery.result = str(e)
            recovery.completed_at = timezone.now()
            recovery.save()

            try:
                university_id = backup_record.metadata.get("university_id")
                university = University.objects.get(id=university_id)
                AuditLog.objects.create(
                    user=performed_by,
                    university=university,
                    action="restore_initiated",
                    severity="error",
                    description=f"Restore failed from backup {backup_record.id}",
                    error_message=str(e),
                    success=False,
                )
            except Exception as e:  # Catch all exceptions safely
                print(f"Error setting success: {e}")

            raise

    @staticmethod
    def get_university_backups(university):
        """Get all backups for university"""
        return BackupRecord.objects.filter(
            metadata__university_id=str(university.id)
        ).order_by("-started_at")

    @staticmethod
    def delete_backup(backup_record):
        """Delete backup file securely"""
        if backup_record.file_path and os.path.exists(backup_record.file_path):
            # Overwrite file before deletion for security
            with open(backup_record.file_path, "wb") as f:
                f.write(os.urandom(os.path.getsize(backup_record.file_path)))
            os.remove(backup_record.file_path)

        backup_record.delete()
