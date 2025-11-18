from rest_framework import serializers

from services.dependent_service.infrastructure_module.building_app.models import (
    Building,
)

from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    # Pour POST/PUT : on envoie l'UUID du bâtiment
    building = serializers.UUIDField(write_only=True)
    # Pour GET : on affiche uniquement le nom du bâtiment
    building_name = serializers.CharField(
        source="building.building_name", read_only=True
    )

    class Meta:
        model = Room
        fields = [
            "id",
            "building",
            "building_name",
            "room_name",
            "capacity",
            "room_type",
            "is_available",
        ]

    def create(self, validated_data):
        building_id = validated_data.pop("building")
        try:
            building = Building.objects.get(pk=building_id)
        except Building.DoesNotExist:
            raise serializers.ValidationError({"building": "Invalid building ID"})

        room = Room.objects.create(building=building, **validated_data)
        return room

    def update(self, instance, validated_data):
        building_id = validated_data.pop("building", None)
        if building_id:
            try:
                building = Building.objects.get(pk=building_id)
                instance.building = building
            except Building.DoesNotExist:
                raise serializers.ValidationError({"building": "Invalid building ID"})
        return super().update(instance, validated_data)
