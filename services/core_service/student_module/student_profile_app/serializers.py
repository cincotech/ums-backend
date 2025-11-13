from rest_framework import serializers

from .models import Student, StudentGraduateInfo, StudentHsInfo, Training


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

    class Meta:
        model = Student
        fields = ["id", "user", "matricule", "colline", "cam", "parent", "parent_ids"]
        read_only_fields = ["parent"]


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


class StudentGraduateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGraduateInfo
        fields = ["id", "student", "department", "option", "mention", "degree"]
