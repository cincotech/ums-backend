from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from core.views import HelloView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HelloView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path(
        "", include("services.foundational_service.auth_module.authentication_app.urls")
    ),
    path("", include("services.core_service.academic_module.urls")),
    path("", include("services.core_service.student_module.urls")),
    path("", include("services.core_service.finance_module.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
