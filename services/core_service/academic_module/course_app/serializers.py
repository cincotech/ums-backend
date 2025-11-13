from rest_framework import serializers

from services.core_service.academic_module.module_app.models import Module
from services.core_service.academic_module.module_app.serializers import (
    ModuleSerializer,
)

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    module_id = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(), source="module", write_only=True
    )

    class Meta:
        model = Course
        fields = ["id", "course_name", "cm", "td", "tp", "module", "module_id"]
