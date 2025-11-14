from rest_framework.permissions import IsAuthenticated, BasePermission
from core.views import BaseViewSet
from .models import EquipmentType, Equipment, EquipmentAllocation, EquipmentMaintenance
from core.permissions import IsSuperAdminCreateOnly
from .serializers import (
    EquipmentTypeSerializer,
    EquipmentSerializer,
    EquipmentAllocationSerializer,
    EquipmentMaintenanceSerializer,
)


class EquipmentTypeViewSet(BaseViewSet):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminCreateOnly]


class EquipmentViewSet(BaseViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminCreateOnly]


class EquipmentAllocationViewSet(BaseViewSet):
    queryset = EquipmentAllocation.objects.all()
    serializer_class = EquipmentAllocationSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminCreateOnly]


class EquipmentMaintenanceViewSet(BaseViewSet):
    queryset = EquipmentMaintenance.objects.all()
    serializer_class = EquipmentMaintenanceSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminCreateOnly]
