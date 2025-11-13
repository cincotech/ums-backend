from rest_framework import serializers

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.university_app.models import (
    AcademicYear,
    University,
    UniversityDegree,
)
from services.foundational_service.auth_module.user_app.models import User

from .models import Attribution, Suggestion, Teacher


class TeacherSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )
    degree_id = serializers.PrimaryKeyRelatedField(
        queryset=UniversityDegree.objects.all(), source="degree", write_only=True
    )
    university_id = serializers.PrimaryKeyRelatedField(
        queryset=University.objects.all(), source="university", write_only=True
    )

    class Meta:
        model = Teacher
        fields = [
            "id",
            "user",
            "user_id",
            "teacher_grade",
            "degree",
            "degree_id",
            "university",
            "university_id",
            "speciality",
            "url_cv",
            "url_other",
            "url_diploma",
        ]
        read_only_fields = ["user", "degree", "university"]


class AttributionSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )
    principal_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source="principal_teacher", write_only=True
    )
    substitute_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        source="substitute_teacher",
        write_only=True,
        allow_null=True,
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), source="academic_year", write_only=True
    )
    submitted_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="submitted_by", write_only=True
    )
    authorized_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="authorized_by",
        write_only=True,
        allow_null=True,
    )

    class Meta:
        model = Attribution
        fields = [
            "id",
            "course",
            "course_id",
            "principal_teacher",
            "principal_teacher_id",
            "substitute_teacher",
            "substitute_teacher_id",
            "academic_year",
            "academic_year_id",
            "date_attribution",
            "status_principal_teacher",
            "status_substitute_teacher",
            "commentaire",
            "submitted_by",
            "submitted_by_id",
            "authorized_by",
            "authorized_by_id",
        ]
        read_only_fields = [
            "course",
            "principal_teacher",
            "substitute_teacher",
            "academic_year",
            "submitted_by",
            "authorized_by",
        ]


class SuggestionSerializer(serializers.ModelSerializer):
    attribution_id = serializers.PrimaryKeyRelatedField(
        queryset=Attribution.objects.all(), source="attribution", write_only=True
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source="teacher", write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Suggestion
        fields = [
            "id",
            "suggestion_date",
            "suggestion",
            "attribution",
            "attribution_id",
            "teacher",
            "teacher_id",
            "user",
            "user_id",
        ]
        read_only_fields = ["attribution", "teacher", "user"]
