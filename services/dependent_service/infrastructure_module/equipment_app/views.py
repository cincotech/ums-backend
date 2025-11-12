from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EquipmentType, Equipment, EquipmentAllocation, EquipmentMaintenance
from .serializers import (
    EquipmentTypeSerializer,
    EquipmentSerializer,
    EquipmentAllocationSerializer,
    EquipmentMaintenanceSerializer,
)


class EquipmentTypeViewSet(viewsets.ModelViewSet):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated]


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.select_related('equipment_type').all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Si plusieurs filtres sont fournis, ils viennent du corps JSON.
        """
        filters = request.data or {}
        queryset = self.queryset.filter(**filters) if filters else self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class EquipmentAllocationViewSet(viewsets.ModelViewSet):
    queryset = EquipmentAllocation.objects.select_related('equipment', 'room', 'allocated_to').all()
    serializer_class = EquipmentAllocationSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        filters = request.data or {}
        queryset = self.queryset.filter(**filters) if filters else self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class EquipmentMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = EquipmentMaintenance.objects.select_related('equipment').all()
    serializer_class = EquipmentMaintenanceSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        filters = request.data or {}
        queryset = self.queryset.filter(**filters) if filters else self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
