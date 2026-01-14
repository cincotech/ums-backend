from django.db.models import Count, Q

from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.teacher_app.models import Attribution


class AcademicDashboardService:
    @staticmethod
    def get_attribution_stats():
        """Obtenir les statistiques des attributions."""
        total = Attribution.objects.count()
        # Count attributions with pending status for either teacher
        pending = Attribution.objects.filter(
            Q(status_principal_teacher="Pending") | Q(status_substitute_teacher="Pending")
        ).count()
        # Count attributions with accepted principal teacher
        approved = Attribution.objects.filter(status_principal_teacher="Accepted").count()
        # Count attributions with refused principal teacher
        rejected = Attribution.objects.filter(status_principal_teacher="Refused").count()

        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
        }

    @staticmethod
    def get_quality_reports_summary():
        """Obtenir un résumé des rapports de qualité."""
        reports = QualityReport.objects.values("report_type").annotate(
            count=Count("id")
        )
        return {report["report_type"]: report["count"] for report in reports}
