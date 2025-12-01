import json

from django.core import serializers as django_serializers
from django.utils import timezone

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.teacher_app.models import Teacher
from services.core_service.academic_module.university_app.models import University
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.dashboard_module.dashboard_super_admin_app.models import (
    AuditLog,
    BackupRecord,
    EmergencyRecovery,
)
from services.dependent_service.document_module.request_app.models import Request
from services.dependent_service.exam_module.exam_app.models import Exam

from .models import (
    UniversityConfiguration,
    UniversityNotification,
    UniversityStatistics,
)


class UniversityAdminService:
    """Service for university admin dashboard operations - single university focus"""

    @staticmethod
    def get_dashboard_stats(university):
        """Get comprehensive statistics for a single university"""
        return {
            "total_students": Student.objects.filter(
                user__university=university
            ).count(),
            "total_teachers": Teacher.objects.filter(
                user__university=university
            ).count(),
            "total_faculties": Faculty.objects.filter(university=university).count(),
            "total_departments": Department.objects.filter(
                faculty__university=university
            ).count(),
            "total_courses": Course.objects.all().count(),
            "active_enrollments": Inscription.objects.filter(
                academic_year__university=university, is_year_close=False
            ).count(),
            "completed_exams": Exam.objects.all().count(),
            "pending_requests": Request.objects.all().count(),
        }

    @staticmethod
    def update_university_statistics(university):
        """Update or create statistics for university"""
        stats, _ = UniversityStatistics.objects.get_or_create(university=university)
        stats_data = UniversityAdminService.get_dashboard_stats(university)

        for key, value in stats_data.items():
            setattr(stats, key, value)

        stats.save()
        return stats

    @staticmethod
    def create_notification(
        university,
        recipient,
        title,
        message,
        notification_type="info",
        priority="low",
        action_url=None,
    ):
        """Create notification for admin"""
        return UniversityNotification.objects.create(
            university=university,
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
        )


class ConfigurationService:
    """Service for university configuration management"""

    @staticmethod
    def get_or_create_config(university, category, key, default_value=None):
        """Get or create a configuration"""
        config, created = UniversityConfiguration.objects.get_or_create(
            university=university,
            category=category,
            key=key,
            defaults={"value": default_value or {}},
        )
        return config

    @staticmethod
    def update_config(university, category, key, value, modified_by):
        """Update configuration value"""
        config = UniversityConfiguration.objects.get(
            university=university, category=category, key=key
        )
        config.value = value
        config.modified_by = modified_by
        config.save()
        return config

    @staticmethod
    def get_category_configs(university, category):
        """Get all configs for a category"""
        return UniversityConfiguration.objects.filter(
            university=university, category=category, is_active=True
        )

    @staticmethod
    def get_all_configs(university):
        """Get all active configurations for university"""
        return UniversityConfiguration.objects.filter(
            university=university, is_active=True
        ).order_by("category", "key")


class BackupRestoreService:
    """Service for university data backup and restore using super admin models"""

    UNIVERSITY_MODELS = [
        Faculty,
        Department,
        Course,
        Teacher,
        Student,
        Inscription,
        Exam,
        Request,
    ]

    @staticmethod
    def create_backup(university, initiated_by):
        """Create backup record for university data"""
        backup = BackupRecord.objects.create(
            backup_type="full",
            status="running",
            initiated_by=initiated_by,
            metadata={
                "university_id": str(university.id),
                "university_name": university.university_name,
            },
        )

        try:
            # Serialize university data
            backup_data = {}
            for model in BackupRestoreService.UNIVERSITY_MODELS:
                queryset = model.objects.filter(university=university)
                if queryset.exists():
                    backup_data[model.__name__] = json.loads(
                        django_serializers.serialize("json", queryset)
                    )

            # Store backup data in metadata
            backup.metadata["data"] = backup_data
            backup.mark_completed(
                file_path=f"backup_university_{university.id}",
                file_size=len(json.dumps(backup_data)),
            )

            # Log backup action
            AuditLog.objects.create(
                user=initiated_by,
                university=university,
                action="backup_initiated",
                severity="info",
                description=f"Backup created for {university.university_name}",
                success=True,
            )

            return backup
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
        """Restore university data from backup"""
        recovery = EmergencyRecovery.objects.create(
            recovery_type="data_recovery",
            performed_by=performed_by,
            status="in_progress",
            reason=f"Restoring from backup {backup_record.id}",
            details={"backup_id": str(backup_record.id)},
        )

        try:
            university_id = backup_record.metadata.get("university_id")
            backup_data = backup_record.metadata.get("data", {})

            # Restore data for each model
            for model_name, data in backup_data.items():
                model = next(
                    (
                        m
                        for m in BackupRestoreService.UNIVERSITY_MODELS
                        if m.__name__ == model_name
                    ),
                    None,
                )
                if model and data:
                    django_serializers.deserialize(
                        "json", json.dumps(data), ignorenonexistent=True
                    )

            recovery.status = "completed"
            recovery.result = (
                f"Successfully restored data for university {university_id}"
            )
            recovery.completed_at = timezone.now()
            recovery.save()

            # Log restore action
            university = University.objects.get(id=university_id)
            AuditLog.objects.create(
                user=performed_by,
                university=university,
                action="restore_initiated",
                severity="info",
                description=f"Data restored from backup {backup_record.id}",
                success=True,
            )

            return recovery
        except Exception as e:
            recovery.status = "failed"
            recovery.result = str(e)
            recovery.completed_at = timezone.now()
            recovery.save()

            AuditLog.objects.create(
                user=performed_by,
                university=backup_record.metadata.get("university_id"),
                action="restore_initiated",
                severity="error",
                description=f"Restore failed from backup {backup_record.id}",
                error_message=str(e),
                success=False,
            )
            raise

    @staticmethod
    def get_university_backups(university):
        """Get all backups for a university"""
        return BackupRecord.objects.filter(
            metadata__university_id=str(university.id)
        ).order_by("-started_at")
