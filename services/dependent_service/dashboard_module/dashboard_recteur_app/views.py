from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone

from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.quality_app.serializers import QualityReportSerializer

from .models import PaymentDerogation, VisitorCourseAttribution
from .serializers import (
    PaymentDerogationSerializer,
    PaymentDerogationDecisionSerializer,
    VisitorCourseAttributionSerializer,
)
from .permissions import IsRector
from .services import RectorAnalyticsService
from .tasks import notify_derogation_decision


class PaymentDerogationViewSet(viewsets.ModelViewSet):
    queryset = PaymentDerogation.objects.all()
    serializer_class = PaymentDerogationSerializer
    permission_classes = [IsAuthenticated, IsRector]

    @action(detail=True, methods=['POST'])
    def decide(self, request, pk=None):
        derog = self.get_object()
        serializer = PaymentDerogationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        derog.status = serializer.validated_data['status']
        derog.rector_decision_by = request.user
        derog.decision_comment = serializer.validated_data.get('comment', '')
        derog.decision_date = timezone.now()
        derog.save()

        notify_derogation_decision.delay(derog.student.email, derog.status)

        return Response(PaymentDerogationSerializer(derog).data)


class VisitorCourseAttributionViewSet(viewsets.ModelViewSet):
    queryset = VisitorCourseAttribution.objects.all()
    serializer_class = VisitorCourseAttributionSerializer
    permission_classes = [IsAuthenticated, IsRector]

    @action(detail=True, methods=['POST'])
    def validate(self, request, pk=None):
        attrib = self.get_object()
        attrib.rector_validation = True
        attrib.validation_date = timezone.now()
        attrib.save()
        return Response(VisitorCourseAttributionSerializer(attrib).data)


class QualityReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QualityReport.objects.all()
    serializer_class = QualityReportSerializer
    permission_classes = [IsAuthenticated, IsRector]


class RectorDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRector]

    def get(self, request):
        return Response({
            'payment': RectorAnalyticsService.payment_overview(),
            'academic': RectorAnalyticsService.academic_performance(),
        })
