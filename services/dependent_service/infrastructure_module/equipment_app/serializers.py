from rest_framework import serializers
from .models import EquipmentType, Equipment, EquipmentAllocation, EquipmentMaintenance
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.user_app.models import User


# -------------------------------
# EquipmentType Serializer
# -------------------------------
class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ['id', 'name']


# -------------------------------
# Equipment Serializer
# -------------------------------
class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type = serializers.UUIDField(write_only=True)
    equipment_type_name = serializers.CharField(source='equipment_type.name', read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id',
            'equipment_name',
            'equipment_type',
            'equipment_type_name',
            'serial_number',
            'equipment_number',
            'purchase_date',
            'status',
        ]

    def create(self, validated_data):
        type_id = validated_data.pop('equipment_type')
        try:
            type_obj = EquipmentType.objects.get(pk=type_id)
        except EquipmentType.DoesNotExist:
            raise serializers.ValidationError({"equipment_type": "Invalid EquipmentType ID"})
        equipment = Equipment.objects.create(equipment_type=type_obj, **validated_data)
        return equipment

    def update(self, instance, validated_data):
        type_id = validated_data.pop('equipment_type', None)
        if type_id:
            try:
                instance.equipment_type = EquipmentType.objects.get(pk=type_id)
            except EquipmentType.DoesNotExist:
                raise serializers.ValidationError({"equipment_type": "Invalid EquipmentType ID"})
        return super().update(instance, validated_data)


# -------------------------------
# Equipment Allocation Serializer
# -------------------------------
class EquipmentAllocationSerializer(serializers.ModelSerializer):
    equipment = serializers.UUIDField(write_only=True)
    room = serializers.UUIDField(write_only=True)
    allocated_to = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    equipment_name = serializers.CharField(source='equipment.equipment_name', read_only=True)
    room_name = serializers.CharField(source='room.room_name', read_only=True)
    user_name = serializers.CharField(source='allocated_to.username', read_only=True)

    class Meta:
        model = EquipmentAllocation
        fields = [
            'id',
            'equipment',
            'equipment_name',
            'room',
            'room_name',
            'allocated_to',
            'user_name',
            'allocation_date',
            'return_date',
            'status',
        ]

    def create(self, validated_data):
        equipment = Equipment.objects.get(pk=validated_data.pop('equipment'))
        room = Room.objects.get(pk=validated_data.pop('room'))
        user_id = validated_data.pop('allocated_to', None)
        user = User.objects.get(pk=user_id) if user_id else None

        return EquipmentAllocation.objects.create(
            equipment=equipment,
            room=room,
            allocated_to=user,
            **validated_data
        )


# -------------------------------
# Equipment Maintenance Serializer
# -------------------------------
class EquipmentMaintenanceSerializer(serializers.ModelSerializer):
    equipment = serializers.UUIDField(write_only=True)
    equipment_name = serializers.CharField(source='equipment.equipment_name', read_only=True)

    class Meta:
        model = EquipmentMaintenance
        fields = [
            'id',
            'equipment',
            'equipment_name',
            'maintenance_date',
            'return_date',
            'description',
            'performed_by',
            'cost',
        ]

    def create(self, validated_data):
        equipment_id = validated_data.pop('equipment')
        try:
            equipment = Equipment.objects.get(pk=equipment_id)
        except Equipment.DoesNotExist:
            raise serializers.ValidationError({"equipment": "Invalid Equipment ID"})
        return EquipmentMaintenance.objects.create(equipment=equipment, **validated_data)
