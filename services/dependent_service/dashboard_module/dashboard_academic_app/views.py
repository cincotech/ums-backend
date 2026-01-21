from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.quality_app.serializers import (
    QualityReportSerializer,
)

# from .models import AttributionValidation
from .permissions import IsDean

# from .serializers import (
#     AttributionValidationDecisionSerializer,
#     AttributionValidationSerializer,
# )


class QualityReportViewSet(viewsets.ModelViewSet):
    queryset = QualityReport.objects.all()
    serializer_class = QualityReportSerializer
    permission_classes = [IsAuthenticated, IsDean]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


# class AttributionValidationViewSet(viewsets.ModelViewSet):
#     queryset = AttributionValidation.objects.all()
#     serializer_class = AttributionValidationSerializer
#     permission_classes = [IsAuthenticated, IsDean]

#     @action(detail=True, methods=["POST"])
#     def validate(self, request, pk=None):
#         validation = self.get_object()
#         serializer = AttributionValidationDecisionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         validation.validation_status = serializer.validated_data["validation_status"]
#         validation.comments = serializer.validated_data.get("comments", "")
#         validation.validated_by = request.user
#         validation.validation_date = timezone.now()
#         validation.save()

#         return Response(AttributionValidationSerializer(validation).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDean])
def dashboard_overview(request):
    return Response({"message": "Dashboard overview"})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDean])
def visiting_professors_attributions(request):
    return Response({"message": "Visiting professors attributions"})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDean])
def validate_attribution(request, attribution_id):
    return Response({"message": "Attribution validated"})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDean])
def academic_performance_report(request):
    return Response({"message": "Academic performance report"})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDean])
def generate_quality_report(request):
    return Response({"message": "Quality report generated"})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDean])
def quality_reports_list(request):
    return Response({"message": "Quality reports list"})
