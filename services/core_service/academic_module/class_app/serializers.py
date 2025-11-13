from rest_framework import serializers

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.department_app.serializers import (
    DepartmentSerializer,
)

from .models import Class


class ClassSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )

    class Meta:
        model = Class
        fields = ["id", "class_name", "department", "department_id", "class_group"]
