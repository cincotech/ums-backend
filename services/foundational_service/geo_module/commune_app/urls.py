from django.urls import path
from .views import CommuneListCreateAPIView, CommuneDetailAPIView

urlpatterns = [
    path("communes/", CommuneListCreateAPIView.as_view(), name="commune-list-create"),
    path("communes/<uuid:pk>/", CommuneDetailAPIView.as_view(), name="commune-detail"),
]
