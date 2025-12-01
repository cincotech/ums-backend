from django.db.models import Count
from services.core_service.academic_module.quality_app.models import QualityReport
from .models import AttributionValidation


class AcademicDashboardService:
    @staticmethod
    def get_attribution_stats():
        """Obtenir les statistiques des attributions."""
        total = AttributionValidation.objects.count()
        pending = AttributionValidation.objects.filter(validation_status='pending').count()
        approved = AttributionValidation.objects.filter(validation_status='approved').count()
        rejected = AttributionValidation.objects.filter(validation_status='rejected').count()
        
        return {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
        }

    @staticmethod
    def get_quality_reports_summary():
        """Obtenir un résumé des rapports de qualité."""
        reports = QualityReport.objects.values('report_type').annotate(count=Count('id'))
        return {report['report_type']: report['count'] for report in reports}
