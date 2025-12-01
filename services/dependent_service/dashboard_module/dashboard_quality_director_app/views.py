from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.response_handler import error_response, success_response
from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.quality_app.serializers import QualityReportSerializer

from .models import (
    AcademicPerformanceReport,
    ComplianceAudit,
    CourseSatisfactionSurvey,
    ProgramExecutionTracking,
    QualityStandard,
    StudentRetentionAudit,
)
from .serializers import (
    AcademicPerformanceReportSerializer,
    ComplianceAuditSerializer,
    CourseSatisfactionSurveySerializer,
    ProgramExecutionTrackingSerializer,
    QualityStandardSerializer,
    StudentRetentionAuditSerializer,
)


class QualityStandardViewSet(viewsets.ModelViewSet):
    queryset = QualityStandard.objects.all()
    serializer_class = QualityStandardSerializer
    permission_classes = [IsAuthenticated]


class ComplianceAuditViewSet(viewsets.ModelViewSet):
    queryset = ComplianceAudit.objects.all()
    serializer_class = ComplianceAuditSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def by_status(self, request):
        status_filter = request.query_params.get("status")
        if status_filter:
            audits = self.queryset.filter(compliance_status=status_filter)
            serializer = self.get_serializer(audits, many=True)
            return success_response(data=serializer.data)
        return error_response(message="Status parameter required", status_code=status.HTTP_400_BAD_REQUEST)


class AcademicPerformanceReportViewSet(viewsets.ModelViewSet):
    queryset = AcademicPerformanceReport.objects.all()
    serializer_class = AcademicPerformanceReportSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def by_year_semester(self, request):
        year = request.query_params.get("academic_year")
        sem = request.query_params.get("semester")
        if year and sem:
            reports = self.queryset.filter(academic_year=year, semester=sem)
            serializer = self.get_serializer(reports, many=True)
            return success_response(data=serializer.data)
        return error_response(message="academic_year and semester required", status_code=status.HTTP_400_BAD_REQUEST)


class ProgramExecutionTrackingViewSet(viewsets.ModelViewSet):
    queryset = ProgramExecutionTracking.objects.all()
    serializer_class = ProgramExecutionTrackingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def underperforming(self, request):
        threshold = float(request.query_params.get("threshold", 70))
        programs = self.queryset.filter(progress_percentage__lt=threshold)
        serializer = self.get_serializer(programs, many=True)
        return success_response(data=serializer.data)


class StudentRetentionAuditViewSet(viewsets.ModelViewSet):
    queryset = StudentRetentionAudit.objects.all()
    serializer_class = StudentRetentionAuditSerializer
    permission_classes = [IsAuthenticated]


class CourseSatisfactionSurveyViewSet(viewsets.ModelViewSet):
    queryset = CourseSatisfactionSurvey.objects.all()
    serializer_class = CourseSatisfactionSurveySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def by_course(self, request):
        course = request.query_params.get("course_name")
        if course:
            surveys = self.queryset.filter(course_name=course)
            serializer = self.get_serializer(surveys, many=True)
            return success_response(data=serializer.data)
        return error_response(message="course_name required", status_code=status.HTTP_400_BAD_REQUEST)


class QualityReportViewSet(viewsets.ModelViewSet):
    queryset = QualityReport.objects.all()
    serializer_class = QualityReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)
