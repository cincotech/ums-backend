from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/geo/", include("services.foundational_service.geo_module.urls")),
    path(
        "api/scheduling/", include("services.dependent_service.scheduling_module.urls")
    ),
    path(
        "api/infrastructure/",
        include("services.dependent_service.infrastructure_module.urls"),
    ),
    path("api/", include("services.dependent_service.notification_module.urls")),
    path(
        "api/visualization/",
        include("services.dependent_service.visualization_module.urls"),
    ),
    # Raw OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc UI
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(
        "api/",
        include("services.foundational_service.auth_module.authentication_app.urls"),
    ),
    path(
        "api/academic/infrastructure/",
        include("services.dependent_service.infrastructure_module.urls"),
    ),
    path("api/academic/", include("services.core_service.academic_module.urls")),
    path("api/", include("services.core_service.student_module.urls")),
    # path("api/", include("services.core_service.finance_module.urls")),
    path("api/", include("services.dependent_service.scheduling_module.urls")),
    path("api/", include("services.dependent_service.dashboard_module.urls")),
    path(
        "api/",
        include("services.dependent_service.exam_module.urls"),
    ),
    path("api/", include("services.dependent_service.visualization_module.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
