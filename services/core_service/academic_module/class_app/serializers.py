from rest_framework import serializers

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.department_app.serializers import (
    DepartmentSerializer,
)
from services.core_service.student_module.inscription_app.models import Inscription

from .models import Class, ClassGroup


class ClassSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )

    class Meta:
        model = Class
        fields = ["id", "class_name", "level", "department", "department_id"]


class ClassGroupSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_fk.class_name", read_only=True)
    class_level = serializers.CharField(source="class_fk.level", read_only=True)
    department_name = serializers.CharField(
        source="class_fk.department.department_name", read_only=True
    )
    faculty_name = serializers.CharField(
        source="class_fk.department.faculty.faculty_name", read_only=True
    )
    academic_year_name = serializers.CharField(
        source="academic_year.academic_year", read_only=True
    )
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = ClassGroup
        fields = [
            "id",
            "class_fk",
            "class_name",
            "class_level",
            "department_name",
            "faculty_name",
            "academic_year",
            "academic_year_name",
            "group_name",
            "created_date",
            "is_default",
            "student_count",
        ]
        read_only_fields = ["id", "created_date"]

    def get_student_count(self, obj):
        return Inscription.objects.filter(
            class_group=obj,
            regist_status="Active",
        ).count()
