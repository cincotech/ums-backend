from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"quality-standards", views.QualityStandardViewSet, basename="quality-standards")
router.register(r"compliance-audits", views.ComplianceAuditViewSet, basename="compliance-audits")
router.register(r"academic-performance", views.AcademicPerformanceReportViewSet, basename="academic-performance")
router.register(r"program-execution", views.ProgramExecutionTrackingViewSet, basename="program-execution")
router.register(r"student-retention", views.StudentRetentionAuditViewSet, basename="student-retention")
router.register(r"satisfaction-surveys", views.CourseSatisfactionSurveyViewSet, basename="satisfaction-surveys")
router.register(r"quality-reports", views.QualityReportViewSet, basename="quality-reports")

urlpatterns = [
    path("", include(router.urls)),
]
