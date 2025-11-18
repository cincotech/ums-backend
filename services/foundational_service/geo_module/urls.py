# services/foundational_service/geo_module/urls.py
from django.urls import path

from services.foundational_service.geo_module.colline_app.views import (
    CollineDetailAPIView,
    CollineListCreateAPIView,
)
from services.foundational_service.geo_module.commune_app.views import (
    CommuneDetailAPIView,
    CommuneListCreateAPIView,
)
from services.foundational_service.geo_module.country_app.views import (
    CountryDetailAPIView,
    CountryListCreateAPIView,
)
from services.foundational_service.geo_module.province_app.views import (
    ProvinceDetailAPIView,
    ProvinceListCreateAPIView,
)
from services.foundational_service.geo_module.zone_app.views import (
    ZoneDetailAPIView,
    ZoneListCreateAPIView,
)

urlpatterns = [
    # Country
    path("countries/", CountryListCreateAPIView.as_view(), name="country-list"),
    path("countries/<uuid:pk>/", CountryDetailAPIView.as_view(), name="country-detail"),
    # Province
    path("provinces/", ProvinceListCreateAPIView.as_view(), name="province-list"),
    path(
        "provinces/<uuid:pk>/", ProvinceDetailAPIView.as_view(), name="province-detail"
    ),
    # Commune
    path("communes/", CommuneListCreateAPIView.as_view(), name="commune-list"),
    path("communes/<uuid:pk>/", CommuneDetailAPIView.as_view(), name="commune-detail"),
    # Zone
    path("zones/", ZoneListCreateAPIView.as_view(), name="zone-list"),
    path("zones/<uuid:pk>/", ZoneDetailAPIView.as_view(), name="zone-detail"),
    # Colline
    path("collines/", CollineListCreateAPIView.as_view(), name="colline-list"),
    path("collines/<uuid:pk>/", CollineDetailAPIView.as_view(), name="colline-detail"),
]
