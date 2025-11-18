from django.db.models import Count
from django.utils import timezone

from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.exam_module.result_app.models import CompiledResult

from .models import AttributionValidation, QualityReport


class DashboardService:

    @staticmethod
    def get_attribution_stats():
        """Get course attribution statistics for visiting professors"""
        return {
            "pending_attributions": Attribution.objects.filter(
                status_principal_teacher="Pending"
            ).count(),
            "approved_attributions": Attribution.objects.filter(
                status_principal_teacher="Accepted"
            ).count(),
            "rejected_attributions": Attribution.objects.filter(
                status_principal_teacher="Refused"
            ).count(),
            "total_attributions": Attribution.objects.count(),
        }

    @staticmethod
    def get_academic_performance_stats():
        """Get academic performance statistics"""
        total_students = Student.objects.count()

        # Calculate success rate from compiled results
        passed_students = CompiledResult.objects.filter(status="passed").count()

        success_rate = (
            (passed_students / total_students * 100) if total_students > 0 else 0
        )

        # Calculate retention rate (students who continue vs those who left)
        current_inscriptions = Inscription.objects.filter(
            academic_year__is_current=True
        ).count()

        retention_rate = (
            (current_inscriptions / total_students * 100) if total_students > 0 else 0
        )

        return {
            "total_students": total_students,
            "success_rate": round(success_rate, 2),
            "retention_rate": round(retention_rate, 2),
            "passed_students": passed_students,
            "current_inscriptions": current_inscriptions,
        }

    @staticmethod
    def get_visiting_professors_attributions():
        """Get attributions for visiting professors that need validation"""
        return (
            Attribution.objects.filter(status_principal_teacher="Pending")
            .select_related("course", "principal_teacher__user", "academic_year")
            .order_by("-date_attribution")
        )

    @staticmethod
    def validate_attribution(attribution_id, user, status, comments=None):
        """Validate course attribution for visiting professor"""
        attribution = Attribution.objects.get(id=attribution_id)

        validation, created = AttributionValidation.objects.get_or_create(
            attribution=attribution,
            defaults={
                "validated_by": user,
                "validation_status": status,
                "validation_date": timezone.now(),
                "comments": comments,
            },
        )

        if not created:
            validation.validated_by = user
            validation.validation_status = status
            validation.validation_date = timezone.now()
            validation.comments = comments
            validation.save()

        # Update attribution status
        if status == "approved":
            attribution.status_principal_teacher = "Accepted"
        elif status == "rejected":
            attribution.status_principal_teacher = "Refused"

        attribution.authorized_by = user
        attribution.save()

        return validation

    @staticmethod
    def generate_quality_report(report_type, user):
        """Generate quality assurance reports"""
        data = {}

        if report_type == "academic_performance":
            data = DashboardService.get_academic_performance_stats()
            title = "Academic Performance Report"

        elif report_type == "retention_rate":
            stats = DashboardService.get_academic_performance_stats()
            data = {
                "retention_rate": stats["retention_rate"],
                "total_students": stats["total_students"],
                "current_inscriptions": stats["current_inscriptions"],
            }
            title = "Student Retention Rate Report"

        elif report_type == "success_rate":
            stats = DashboardService.get_academic_performance_stats()
            data = {
                "success_rate": stats["success_rate"],
                "passed_students": stats["passed_students"],
                "total_students": stats["total_students"],
            }
            title = "Student Success Rate Report"

        elif report_type == "program_advancement":
            # Get program advancement statistics
            advancement_data = CompiledResult.objects.values("status").annotate(
                count=Count("id")
            )
            data = {
                "advancement_breakdown": list(advancement_data),
                "total_evaluations": CompiledResult.objects.count(),
            }
            title = "Program Advancement Report"

        report = QualityReport.objects.create(
            report_type=report_type, title=title, data=data, generated_by=user
        )

        return report
