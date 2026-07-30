from rest_framework import serializers

from .models import CompiledResult, Result, ResultComment, Session, Supplement


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "session_name"]


class ResultCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = ResultComment
        fields = ["id", "result", "author", "author_name", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]


class ResultSerializer(serializers.ModelSerializer):
    comments = ResultCommentSerializer(many=True, read_only=True)
    semester = serializers.PrimaryKeyRelatedField(read_only=True)
    semester_name = serializers.CharField(source="semester.name", read_only=True)
    validated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    validated_by_name = serializers.CharField(
        source="validated_by.get_full_name", read_only=True
    )
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    session_name = serializers.CharField(source="session.session_name", read_only=True)
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.CharField(
        source="inscription.student.matricule", read_only=True
    )
    academic_year = serializers.CharField(
        source="inscription.academic_year.id", read_only=True
    )

    class Meta:
        model = Result
        fields = [
            "id",
            "course",
            "inscription",
            "session",
            "semester",
            "semester_name",
            "status",
            "validated_by",
            "validated_by_name",
            "validated_at",
            "comment",
            "mark",
            "comments",
            "course_name",
            "session_name",
            "student_name",
            "student_matricule",
            "academic_year",
        ]

    def get_student_name(self, obj):
        if (
            not obj.inscription
            or not obj.inscription.student
            or not obj.inscription.student.user
        ):
            return None
        user = obj.inscription.student.user
        return f"{user.first_name} {user.last_name}"


class CompiledResultSerializer(serializers.ModelSerializer):
    semester = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CompiledResult
        fields = [
            "id",
            "results",
            "inscription",
            "semester",
            "average_mark",
            "status",
            "is_promoted",
        ]


class SupplementSerializer(serializers.ModelSerializer):
    semester = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Supplement
        fields = [
            "id",
            "inscription",
            "course",
            "semester",
            "validation",
            "validation_date",
            "mark",
        ]
