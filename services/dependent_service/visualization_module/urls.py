from django.urls import include, path

urlpatterns = [
    path(
        "", include("services.dependent_service.visualization_module.diagram_app.urls")
    ),
]
