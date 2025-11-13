from rest_framework import serializers

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.faculty_app.serializers import (
    FacultySerializer,
)

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.all(), source="faculty", write_only=True
    )

    class Meta:
        model = Department
        fields = ["id", "department_name", "abreviation", "faculty", "faculty_id"]
