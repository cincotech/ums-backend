from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AbsenceJustificationViewSet,
    CounselingSessionViewSet,
    DocumentRequestViewSet,
    ScholarshipViewSet,
    StudentActivityViewSet,
    StudentStatusChangeViewSet,
)

router = DefaultRouter()
router.register(r"document-requests", DocumentRequestViewSet)
router.register(r"absence-justifications", AbsenceJustificationViewSet)
router.register(r"student-activities", StudentActivityViewSet)
router.register(r"scholarships", ScholarshipViewSet)
router.register(r"counseling-sessions", CounselingSessionViewSet)
router.register(r"status-changes", StudentStatusChangeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
