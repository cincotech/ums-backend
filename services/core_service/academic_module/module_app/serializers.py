from rest_framework import serializers

from .models import Module, Semester


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["id", "number", "name"]


class ModuleSerializer(serializers.ModelSerializer):
    # Inclure les détails du semestre dans le module
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.UUIDField(write_only=True)  # pour la création

    class Meta:
        model = Module
        fields = [
            "id",
            "module_name",
            "code",
            "semester",
            "semester_id",
            "class_fk",
            "total_credits",
        ]
        read_only_fields = ["total_credits"]
