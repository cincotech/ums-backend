from rest_framework.routers import DefaultRouter

from .views import ModuleViewSet, SemesterViewSet

router = DefaultRouter()
router.register(r"modules", ModuleViewSet, basename="module")
router.register(r"semesters", SemesterViewSet, basename="semester")

urlpatterns = router.urls
