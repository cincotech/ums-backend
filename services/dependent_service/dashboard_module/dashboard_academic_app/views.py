from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.response_handler import success_response

from .serializers import (
    AttributionValidationSerializer,
    DashboardStatsSerializer,
    QualityReportSerializer,
)
from .services import DashboardService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Get dashboard overview with key statistics"""
    try:
        attribution_stats = DashboardService.get_attribution_stats()
        performance_stats = DashboardService.get_academic_performance_stats()

        dashboard_data = {**attribution_stats, **performance_stats}

        serializer = DashboardStatsSerializer(dashboard_data)
        return success_response(
            data=serializer.data, message="Dashboard overview retrieved successfully"
        )
    except Exception as e:
        return success_response(
            message=f"Error retrieving dashboard data: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def visiting_professors_attributions(request):
    """Get course attributions for visiting professors that need validation"""
    try:
        attributions = DashboardService.get_visiting_professors_attributions()

        attribution_data = []
        for attribution in attributions:
            attribution_data.append(
                {
                    "id": str(attribution.id),
                    "course_name": attribution.course.course_name,
                    "teacher_name": f"{attribution.principal_teacher.user.first_name} {attribution.principal_teacher.user.last_name}",
                    "academic_year": str(attribution.academic_year),
                    "date_attribution": attribution.date_attribution,
                    "status": attribution.status_principal_teacher,
                    "comments": attribution.commentaire,
                }
            )

        return success_response(
            data=attribution_data,
            message="Visiting professors attributions retrieved successfully",
        )
    except Exception as e:
        return success_response(
            message=f"Error retrieving attributions: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_attribution(request, attribution_id):
    """Validate course attribution for visiting professor"""
    try:
        validation_status = request.data.get("status")
        comments = request.data.get("comments", "")
        if validation_status not in ["approved", "rejected"]:
            return success_response(
                message="Invalid validation status. Must be 'approved' or 'rejected'",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        validation = DashboardService.validate_attribution(
            attribution_id, request.user, validation_status, comments
        )
        serializer = AttributionValidationSerializer(validation)
        return success_response(
            data=serializer.data,
            message=f"Attribution {validation_status} successfully",
        )
    except Exception as e:
        return success_response(
            message=f"Error validating attribution: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def academic_performance_report(request):
    """Get academic performance supervision data"""
    try:
        performance_stats = DashboardService.get_academic_performance_stats()

        return success_response(
            data=performance_stats,
            message="Academic performance report retrieved successfully",
        )
    except Exception as e:
        return success_response(
            message=f"Error retrieving performance report: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_quality_report(request):
    """Generate quality assurance reports"""
    try:
        report_type = request.data.get("report_type")

        if report_type not in [
            "academic_performance",
            "retention_rate",
            "success_rate",
            "program_advancement",
        ]:
            return success_response(
                message="Invalid report type", status_code=status.HTTP_400_BAD_REQUEST
            )

        report = DashboardService.generate_quality_report(report_type, request.user)
        serializer = QualityReportSerializer(report)

        return success_response(
            data=serializer.data, message="Quality report generated successfully"
        )
    except Exception as e:
        return success_response(
            message=f"Error generating report: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quality_reports_list(request):
    """Get list of quality reports"""
    try:
        from .models import QualityReport

        reports = QualityReport.objects.all().order_by("-generated_date")
        serializer = QualityReportSerializer(reports, many=True)

        return success_response(
            data=serializer.data, message="Quality reports retrieved successfully"
        )
    except Exception as e:
        return success_response(
            message=f"Error retrieving reports: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
