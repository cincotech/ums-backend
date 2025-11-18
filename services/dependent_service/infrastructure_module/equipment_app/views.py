from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsGeneralService, IsSuperAdminCreateOnly
from core.response_handler import success_response, validate_serializer
from core.views import BaseViewSet

from .models import Equipment, EquipmentAllocation, EquipmentMaintenance, EquipmentType
from .serializers import (
    EquipmentAllocationSerializer,
    EquipmentMaintenanceSerializer,
    EquipmentSerializer,
    EquipmentTypeSerializer,
)


class EquipmentTypeViewSet(BaseViewSet):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminCreateOnly]


class EquipmentViewSet(BaseViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated, IsGeneralService]

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data["status"] = "available"  # par défaut
        return super().create(request, *args, **kwargs)


class EquipmentAllocationViewSet(BaseViewSet):
    queryset = EquipmentAllocation.objects.all()
    serializer_class = EquipmentAllocationSerializer
    permission_classes = [IsAuthenticated, IsGeneralService]

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data["status"] = "active"

        serializer = self.get_serializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        allocation = serializer.save()

        # L'équipement devient "working" lors de l'allocation
        equipment = allocation.equipment
        equipment.status = "working"
        equipment.save()

        return success_response(
            data=serializer.data,
            message="Equipment allocated successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        allocation = serializer.save()

        # Si l'équipement est retourné
        if allocation.status == "returned" and old_status != "returned":
            equipment = allocation.equipment
            equipment.status = "available"  # redeviens disponible
            equipment.save()

        return success_response(
            data=serializer.data,
            message="Equipment allocation updated successfully",
        )


class EquipmentMaintenanceViewSet(BaseViewSet):
    queryset = EquipmentMaintenance.objects.all()
    serializer_class = EquipmentMaintenanceSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminCreateOnly]
