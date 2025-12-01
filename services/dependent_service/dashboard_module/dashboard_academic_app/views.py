from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.quality_app.serializers import QualityReportSerializer
from .models import AttributionValidation
from .serializers import (
    AttributionValidationSerializer,
    AttributionValidationDecisionSerializer,
)
from .permissions import IsDean, IsAcademicSecretary


class QualityReportViewSet(viewsets.ModelViewSet):
    queryset = QualityReport.objects.all()
    serializer_class = QualityReportSerializer
    permission_classes = [IsAuthenticated, IsDean]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


class AttributionValidationViewSet(viewsets.ModelViewSet):
    queryset = AttributionValidation.objects.all()
    serializer_class = AttributionValidationSerializer
    permission_classes = [IsAuthenticated, IsDean]

    @action(detail=True, methods=['POST'])
    def validate(self, request, pk=None):
        validation = self.get_object()
        serializer = AttributionValidationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validation.validation_status = serializer.validated_data['validation_status']
        validation.comments = serializer.validated_data.get('comments', '')
        validation.validated_by = request.user
        validation.validation_date = timezone.now()
        validation.save()

        return Response(AttributionValidationSerializer(validation).data)
