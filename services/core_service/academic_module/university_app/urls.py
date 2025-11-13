from rest_framework.routers import DefaultRouter

from .views import AcademicYearViewSet, UniversityDegreeViewSet, UniversityViewSet

router = DefaultRouter()
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("universities", UniversityViewSet, basename="university")
router.register("degrees", UniversityDegreeViewSet, basename="university-degree")

urlpatterns = router.urls
