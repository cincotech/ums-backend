from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ComplementRequirementViewSet,
    ExamViewSet,
    GradeComplaintViewSet,
    InscriptionViewSet,
    JurySessionViewSet,
    OfficialDocumentViewSet,
    PaymentClaimViewSet,
    compilation_status,
    course_results,
    dashboard_stats,
    grade_entry_status,
)

router = DefaultRouter()

# ==================== VIEWSETS ====================
router.register(r"exams", ExamViewSet, basename="exams")
router.register(r"jury-sessions", JurySessionViewSet, basename="jury-sessions")
router.register(r"grade-complaints", GradeComplaintViewSet, basename="grade-complaints")
router.register(
    r"official-documents", OfficialDocumentViewSet, basename="official-documents"
)
router.register(r"complement-requirements", ComplementRequirementViewSet, basename="complement-requirements")
router.register(r"payment-claims", PaymentClaimViewSet, basename="payment-claims")
router.register(r"inscriptions", InscriptionViewSet, basename="inscriptions")

urlpatterns = [
    # ==================== DASHBOARD ====================
    path("stats/", dashboard_stats, name="dashboard-stats"),
    # ==================== GRADES & RESULTS ====================
    path("grades/status/", grade_entry_status, name="grade-entry-status"),
    path("courses/<uuid:course_id>/results/", course_results, name="course-results"),
    path("results/compilation-status/", compilation_status, name="compilation-status"),
    # ==================== ROUTER URLS ====================
    path("", include(router.urls)),
]
