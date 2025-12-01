from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QualityReportViewSet, AttributionValidationViewSet

router = DefaultRouter()
router.register('quality-reports', QualityReportViewSet, basename='quality-reports')
router.register('attribution-validations', AttributionValidationViewSet, basename='attribution-validations')

urlpatterns = [
    path('', include(router.urls)),
]
