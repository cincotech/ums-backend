from rest_framework import serializers

from .models import (
    AcademicProgram,
    RoomAllocation,
    Schedule,
    SecretaryNote,
    StudentGroup,
    TeacherWorkload,
    TeachingProgress,
    TeachingUnit,
)


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = [
            "id",
            "faculty",
            "academic_year",
            "semester",
            "status",
            "created_by",
            "created_date",
            "published_date",
        ]
        read_only_fields = ["id", "created_date", "created_by"]


class TeachingProgressSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(
        source="attribution.course.course_name", read_only=True
    )
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = TeachingProgress
        fields = [
            "id",
            "attribution",
            "faculty",
            "progress_percentage",
            "last_updated",
            "submitted_by",
            "course_name",
            "teacher_name",
        ]
        read_only_fields = ["id", "last_updated"]

    def get_teacher_name(self, obj):
        user = obj.attribution.principal_teacher.user
        return f"{user.first_name} {user.last_name}"


class TeacherWorkloadSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)

    class Meta:
        model = TeacherWorkload
        fields = [
            "id",
            "faculty",
            "teacher",
            "teacher_name",
            "academic_year",
            "total_hours",
            "assigned_hours",
            "is_permanent",
        ]
        read_only_fields = ["id"]


class StudentGroupSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroup
        fields = [
            "id",
            "faculty",
            "group_name",
            "academic_year",
            "students",
            "student_count",
            "created_date",
        ]
        read_only_fields = ["id", "created_date"]

    def get_student_count(self, obj):
        return obj.students.count()


class TeachingUnitSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)

    class Meta:
        model = TeachingUnit
        fields = [
            "id",
            "program",
            "course",
            "course_name",
            "credits",
            "semester",
        ]
        read_only_fields = ["id"]


class AcademicProgramSerializer(serializers.ModelSerializer):
    units = TeachingUnitSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicProgram
        fields = [
            "id",
            "faculty",
            "program_name",
            "level",
            "description",
            "units",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "created_date", "updated_date"]


class RoomAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAllocation
        fields = [
            "id",
            "schedule",
            "faculty",
            "room_name",
            "capacity",
            "allocated_date",
        ]
        read_only_fields = ["id", "allocated_date"]


class SecretaryNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )

    class Meta:
        model = SecretaryNote
        fields = [
            "id",
            "faculty",
            "subject",
            "message",
            "created_by",
            "created_by_name",
            "created_date",
            "is_resolved",
        ]
        read_only_fields = ["id", "created_date", "created_by"]


class DoyenDashboardStatsSerializer(serializers.Serializer):
    total_schedules = serializers.IntegerField()
    published_schedules = serializers.IntegerField()
    teaching_progress_avg = serializers.FloatField()
    total_teachers = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_programs = serializers.IntegerField()
    pending_secretary_notes = serializers.IntegerField()
