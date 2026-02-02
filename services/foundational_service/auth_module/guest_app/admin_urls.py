from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import admin_views

router = DefaultRouter()
router.register(
    r"account-requests", admin_views.AccountRequestViewSet, basename="account-request"
)

urlpatterns = [
    path("", include(router.urls)),
]
