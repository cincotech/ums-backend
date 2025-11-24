# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated

# from core.response_handler import error_response, success_response

# from .serializers import (
#     AttributionValidationSerializer,
#     PaymentDerogationSerializer,
#     PaymentOverviewSerializer,
#     RecteurDashboardStatsSerializer,
# )
# from .services import RecteurDashboardService


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def recteur_dashboard_overview(request):
#     """Get recteur dashboard overview with key statistics"""
#     try:
#         stats = RecteurDashboardService.get_dashboard_stats()
#         serializer = RecteurDashboardStatsSerializer(stats)
#         return success_response(
#             data=serializer.data, message="Dashboard overview retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def payment_derogations(request):
#     """Get payment derogation requests"""
#     try:
#         status_filter = request.GET.get("status", "pending")
#         derogations = RecteurDashboardService.get_payment_derogations(status_filter)
#         serializer = PaymentDerogationSerializer(derogations, many=True)
#         return success_response(
#             data=serializer.data, message="Payment derogations retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def process_payment_derogation(request, derogation_id):
#     """Process payment derogation decision (approve/reject)"""
#     try:
#         decision = request.data.get("decision")  # 'approved' or 'rejected'
#         notes = request.data.get("notes", "")

#         if decision not in ["approved", "rejected"]:
#             return error_response(
#                 message="Invalid decision. Must be 'approved' or 'rejected'",
#                 status_code=status.HTTP_400_BAD_REQUEST,
#             )

#         derogation = RecteurDashboardService.process_derogation(
#             derogation_id, decision, notes, request.user
#         )

#         serializer = PaymentDerogationSerializer(derogation)
#         return success_response(data=serializer.data, message=f"Derogation {decision}")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def visiting_professor_attributions(request):
#     """Get course attributions for visiting professors pending validation"""
#     try:
#         attributions = RecteurDashboardService.get_visiting_professor_attributions()
#         serializer = AttributionValidationSerializer(attributions, many=True)
#         return success_response(data=serializer.data, message="Attributions retrieved")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def validate_course_attribution(request, attribution_id):
#     """Validate course attribution for visiting professor"""
#     try:
#         decision = request.data.get("decision")  # 'approved' or 'rejected'
#         notes = request.data.get("notes", "")

#         if decision not in ["approved", "rejected"]:
#             return error_response(
#                 message="Invalid decision. Must be 'approved' or 'rejected'",
#                 status_code=status.HTTP_400_BAD_REQUEST,
#             )

#         attribution = RecteurDashboardService.validate_course_attribution(
#             attribution_id, decision, notes, request.user
#         )

#         serializer = AttributionValidationSerializer(attribution)
#         return success_response(data=serializer.data, message=f"Attribution {decision}")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def payment_tracking_overview(request):
#     """Get global payment tracking and collection rates"""
#     try:
#         overview = RecteurDashboardService.get_payment_overview()
#         serializer = PaymentOverviewSerializer(overview)
#         return success_response(
#             data=serializer.data, message="Payment overview retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def academic_performance_supervision(request):
#     """Get academic performance supervision data"""
#     try:
#         performance = RecteurDashboardService.get_academic_performance_overview()
#         return success_response(
#             data=performance, message="Academic performance data retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def quality_reports_consultation(request):
#     """Get quality assurance reports for recteur consultation"""
#     try:
#         from services.dependent_service.dashboard_module.dashboard_app.serializers import (
#             QualityReportSerializer,
#         )

#         reports = RecteurDashboardService.get_quality_reports_summary()
#         serializer = QualityReportSerializer(reports, many=True)
#         return success_response(
#             data=serializer.data, message="Quality reports retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
