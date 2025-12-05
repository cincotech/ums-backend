from rest_framework import serializers

from services.core_service.academic_module.university_app.models import University
from services.core_service.academic_module.university_app.serializers import (
    UniversitySerializer,
)

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
    university = UniversitySerializer(read_only=True)
    university_id = serializers.PrimaryKeyRelatedField(
        queryset=University.objects.all(), source="university", write_only=True
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
            "university_id",
        ]
