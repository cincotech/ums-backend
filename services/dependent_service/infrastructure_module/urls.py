# services/dependent_service/infrastructure_module/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import des viewsets de toutes les sous-apps
from services.dependent_service.infrastructure_module.room_app.views import RoomViewSet
from services.dependent_service.infrastructure_module.equipment_app.views import (
    EquipmentTypeViewSet,
    EquipmentViewSet,
    EquipmentAllocationViewSet,
    EquipmentMaintenanceViewSet,
)
from services.dependent_service.infrastructure_module.building_app.views import BuildingAPIView

# --- ROUTERS ---
router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'equipment-types', EquipmentTypeViewSet, basename='equipment-type')
router.register(r'equipments', EquipmentViewSet, basename='equipment')
router.register(r'equipment-allocations', EquipmentAllocationViewSet, basename='equipment-allocation')
router.register(r'equipment-maintenances', EquipmentMaintenanceViewSet, basename='equipment-maintenance')

# --- URLPATTERNS ---
urlpatterns = [
    # Tous les ViewSets gérés par le router
    path('', include(router.urls)),

    # APIView du building (non ViewSet)
    path('buildings/', BuildingAPIView.as_view(), name='building-api'),
]
