from django.urls import path

from .views import (
    DiagramListView,
    DiagramTypesView,
    GenerateDiagramView,
    ModelStatsView,
)

urlpatterns = [
    path("diagrams/", DiagramListView.as_view(), name="diagram-list"),
    path("diagrams/generate/", GenerateDiagramView.as_view(), name="diagram-generate"),
    path("diagrams/types/", DiagramTypesView.as_view(), name="diagram-types"),
    path("stats/", ModelStatsView.as_view(), name="model-stats"),
]
