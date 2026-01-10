from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.quality_app.serializers import (
    QualityReportSerializer,
)

from services.core_service.academic_module.teacher_app.models import Attribution
from .permissions import IsDean
from .serializers import (
    AttributionValidationDecisionSerializer,
    AttributionValidationSerializer,
    TeacherValidationSerializer,
)


class QualityReportViewSet(viewsets.ModelViewSet):
    queryset = QualityReport.objects.all()
    serializer_class = QualityReportSerializer
    permission_classes = [IsAuthenticated, IsDean]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


class AttributionValidationViewSet(viewsets.ModelViewSet):
    queryset = Attribution.objects.all()
    serializer_class = AttributionValidationSerializer
    permission_classes = [IsAuthenticated, IsDean]

    @action(detail=True, methods=["POST"])
    def validate(self, request, pk=None):
        validation = self.get_object()
        serializer = AttributionValidationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validation.validation_status = serializer.validated_data["validation_status"]
        validation.comments = serializer.validated_data.get("comments", "")
        validation.validated_by = request.user
        validation.validation_date = timezone.now()
        validation.save()

        return Response(AttributionValidationSerializer(validation).data)

    @action(detail=True, methods=["POST"])
    def validate_teacher(self, request, pk=None):
        """
        Valider le teacher principal d'une attribution.
        
        Si principal_teacher_status = "approved":
            - status_principal_teacher = "Accepted"
            - status_substitute_teacher = "Refused" (automatiquement)
        
        Si principal_teacher_status = "rejected":
            - status_principal_teacher = "Refused"
        """
        attribution = self.get_object()
        serializer = TeacherValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        principal_status = serializer.validated_data["principal_teacher_status"]
        comments = serializer.validated_data.get("comments", "")

        # Appliquer la logique de validation
        if principal_status == "approved":
            attribution.status_principal_teacher = "Accepted"
            # Le teacher remplaçant est automatiquement refusé
            attribution.status_substitute_teacher = "Refused"
        else:  # rejected
            attribution.status_principal_teacher = "Refused"

        # Sauvegarder les informations de validation
        attribution.validated_by = request.user
        attribution.validation_date = timezone.now()
        attribution.validation_comments = comments
        attribution.save()

        return Response(
            {
                "message": "Validation du teacher effectuée avec succès",
                "attribution_id": str(attribution.id),
                "status_principal_teacher": attribution.status_principal_teacher,
                "status_substitute_teacher": attribution.status_substitute_teacher,
                "validated_by": attribution.validated_by.email if attribution.validated_by else None,
                "validation_date": attribution.validation_date,
            },
            status=status.HTTP_200_OK
        )


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
