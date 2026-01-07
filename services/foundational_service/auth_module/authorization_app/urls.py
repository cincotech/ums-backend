from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet, SupervisorViewSet

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("supervisors", SupervisorViewSet, basename="supervisors")

urlpatterns = router.urls
