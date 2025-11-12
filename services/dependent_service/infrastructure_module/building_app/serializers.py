from rest_framework import serializers
from .models import Building
from  services.core_service.academic_module.university_app.models import University


class BuildingSerializer(serializers.ModelSerializer):
    # Pour POST/PUT : l'utilisateur envoie l'UUID de l'université
    university = serializers.UUIDField(write_only=True)
    # Pour GET : on affiche le nom de l'université
    university_name = serializers.CharField(source='university.university_name', read_only=True)

    class Meta:
        model = Building
        fields = [
            'id',
            'university',
            'university_name',
            'building_name',
            'building_code',
            'location',
        ]

    def create(self, validated_data):
        # Récupérer et convertir l'UUID en instance University
        university_id = validated_data.pop('university')
        try:
            university = University.objects.get(pk=university_id)
        except University.DoesNotExist:
            raise serializers.ValidationError({"university": "Invalid university ID"})
        building = Building.objects.create(university=university, **validated_data)
        return building

    def update(self, instance, validated_data):
        # Mettre à jour le bâtiment avec changement éventuel d'université
        university_id = validated_data.pop('university', None)
        if university_id:
            try:
                university = University.objects.get(pk=university_id)
                instance.university = university
            except University.DoesNotExist:
                raise serializers.ValidationError({"university": "Invalid university ID"})
        return super().update(instance, validated_data)
