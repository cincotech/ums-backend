from rest_framework import serializers

from services.core_service.student_module.parent_app.serializers import ParentSerializer
from services.foundational_service.auth_module.authentication_app.serializers import (
    UserSerializer,
)
from services.foundational_service.auth_module.user_app.models import User

from .models import Student, StudentFile, StudentGraduateInfo, StudentHsInfo, Training


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = ["id", "domaine", "certificate", "training_center"]


class StudentSerializer(serializers.ModelSerializer):
    parent_ids = serializers.PrimaryKeyRelatedField(
        queryset=Student.parent.field.related_model.objects.all(),
        many=True,
        write_only=True,
        source="parent",
    )
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_obj = UserSerializer(source="user", read_only=True)
    colline_name = serializers.CharField(source="colline.colline_name", read_only=True)
    parent_obj = ParentSerializer(source="parent", many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "matricule",
            "colline",
            "colline_name",
            "cam",
            "parent",
            "parent_ids",
            "user_obj",
            "parent_obj",
        ]
        read_only_fields = ["parent"]

    def create(self, validated_data):
        parents = validated_data.pop("parent", [])
        print(parents)

        # Check if student already exists
        student, created = Student.objects.get_or_create(
            user=validated_data.get("user"),
            defaults=validated_data,  # Only used if creating a new student
        )
        print(student)

        # Assign parents (existing only)
        if parents:
            student.parent.set(parents)  # replaces any existing parents

        return student


class StudentHsInfoSerializer(serializers.ModelSerializer):
    formation_ids = serializers.PrimaryKeyRelatedField(
        queryset=Training.objects.all(), many=True, write_only=True, source="formation"
    )

    class Meta:
        model = StudentHsInfo
        fields = [
            "id",
            "student",
            "highschool",
            "certificate",
            "se_mark",
            "date_of_obtention",
            "formation",
            "formation_ids",
        ]
        read_only_fields = ["formation"]

    def create(self, validated_data):
        formations = validated_data.pop("formation", [])
        student = validated_data.get("student")

        # ✔ GET OR CREATE
        obj, created = StudentHsInfo.objects.get_or_create(
            student=student, defaults=validated_data
        )

        # If the object already exists → update it
        if not created:
            for key, value in validated_data.items():
                setattr(obj, key, value)
            obj.save()

        # Assign M2M formations
        if formations:
            obj.formation.set(formations)

        return obj


class StudentGraduateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGraduateInfo
        fields = ["id", "student", "department", "option", "mention", "degree"]

    def create(self, validated_data):
        student = validated_data.get("student")

        obj, created = StudentGraduateInfo.objects.get_or_create(
            student=student, defaults=validated_data
        )

        if not created:
            for key, value in validated_data.items():
                setattr(obj, key, value)
            obj.save()

        return obj


class StudentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFile
        fields = "__all__"
