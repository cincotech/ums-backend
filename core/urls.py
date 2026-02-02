from django.urls import path

from core.views import health_check, liveness_check, readiness_check

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("ready/", readiness_check, name="readiness_check"),
    path("live/", liveness_check, name="liveness_check"),
]
