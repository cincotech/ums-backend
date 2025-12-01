from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentDerogationViewSet,
    VisitorCourseAttributionViewSet,
    QualityReportViewSet,
    RectorDashboardAPIView,
)

router = DefaultRouter()
router.register("derogations", PaymentDerogationViewSet, basename="derogations")
router.register("visitor-courses", VisitorCourseAttributionViewSet, basename="visitor-courses")
router.register("quality-reports", QualityReportViewSet, basename="quality-reports")

urlpatterns = [
    path("dashboard/", RectorDashboardAPIView.as_view()),
    path("", include(router.urls)),
]
