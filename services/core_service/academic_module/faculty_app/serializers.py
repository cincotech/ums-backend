from rest_framework import serializers

from .models import Faculty, TypeFormation


class TypeFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeFormation
        fields = "__all__"


class FacultySerializer(serializers.ModelSerializer):

    types = TypeFormationSerializer(read_only=True)
    types_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeFormation.objects.all(), source="types", write_only=True
    )

    class Meta:
        model = Faculty
        fields = [
            "id",
            "faculty_name",
            "faculty_abreviation",
            "types",
            "types_id",
            "university",
        ]
