from rest_framework import serializers

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.class_app.serializers import ClassSerializer

from .models import Module


class ModuleSerializer(serializers.ModelSerializer):
    class_fk = ClassSerializer(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), source="class_fk", write_only=True
    )

    class Meta:
        model = Module
        fields = ["id", "module_name", "code", "semester_id", "class_fk", "class_id"]
