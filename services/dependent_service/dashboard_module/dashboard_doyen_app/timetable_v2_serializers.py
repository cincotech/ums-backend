from rest_framework import serializers

from services.dependent_service.scheduling_module.scheduling_app.models import (
    CourseSession,
    TemplateEntry,
    TimetableTemplate,
)


class TemplateEntrySerializer(serializers.ModelSerializer):
    attribution_name = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    room_building = serializers.SerializerMethodField()

    class Meta:
        model = TemplateEntry
        fields = [
            "id",
            "template",
            "day_of_week",
            "start_time",
            "end_time",
            "attribution",
            "attribution_name",
            "course_name",
            "room",
            "room_name",
            "room_building",
            "session_type",
            "week_type",
            "title",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_attribution_name(self, obj):
        if not obj.attribution:
            return None
        u = obj.attribution.principal_teacher.user
        return f"{u.first_name} {u.last_name}"

    def get_course_name(self, obj):
        if not obj.attribution:
            return None
        return obj.attribution.course.course_name

    def get_room_name(self, obj):
        return obj.room.room_name if obj.room else None

    def get_room_building(self, obj):
        if not obj.room:
            return None
        return getattr(obj.room, "building_name", None)


class TimetableTemplateSerializer(serializers.ModelSerializer):
    entries = TemplateEntrySerializer(many=True, read_only=True)
    class_group_name = serializers.CharField(
        source="class_group.group_name", read_only=True
    )
    class_name = serializers.CharField(
        source="class_group.class_fk.class_name", read_only=True
    )
    class_level = serializers.CharField(
        source="class_group.class_fk.class_name", read_only=True
    )
    department_name = serializers.CharField(
        source="class_group.class_fk.department.department_name", read_only=True
    )
    faculty_name = serializers.CharField(
        source="class_group.class_fk.department.faculty.faculty_name", read_only=True
    )
    academic_year_id = serializers.CharField(
        source="class_group.academic_year.id", read_only=True
    )
    academic_year_label = serializers.CharField(
        source="class_group.academic_year.academic_year", read_only=True
    )
    session_count = serializers.IntegerField(source="sessions.count", read_only=True)
    entry_count = serializers.IntegerField(source="entries.count", read_only=True)

    class Meta:
        model = TimetableTemplate
        fields = [
            "id",
            "name",
            "class_group",
            "class_group_name",
            "class_name",
            "class_level",
            "department_name",
            "faculty_name",
            "academic_year_id",
            "academic_year_label",
            "status",
            "entries",
            "entry_count",
            "session_count",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "published_at"]


class TimetableTemplateWriteSerializer(serializers.ModelSerializer):
    """Lightweight serializer for create/update (no nested reads)."""

    class Meta:
        model = TimetableTemplate
        fields = ["id", "name", "class_group", "status"]
        read_only_fields = ["id"]


class CourseSessionSerializer(serializers.ModelSerializer):
    attribution_name = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    room_building = serializers.SerializerMethodField()
    class_group_name = serializers.CharField(
        source="class_group.group_name", read_only=True
    )
    class_name = serializers.CharField(
        source="class_group.class_fk.class_name", read_only=True
    )
    department_name = serializers.CharField(
        source="class_group.class_fk.department.department_name", read_only=True
    )
    template_name = serializers.CharField(source="template.name", read_only=True)

    class Meta:
        model = CourseSession
        fields = [
            "id",
            "template",
            "template_name",
            "template_entry",
            "class_group",
            "class_group_name",
            "class_name",
            "department_name",
            "date",
            "start_time",
            "end_time",
            "attribution",
            "attribution_name",
            "course_name",
            "room",
            "room_name",
            "room_building",
            "session_type",
            "title",
            "status",
            "is_makeup",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_attribution_name(self, obj):
        if not obj.attribution:
            return None
        u = obj.attribution.principal_teacher.user
        return f"{u.first_name} {u.last_name}"

    def get_course_name(self, obj):
        if not obj.attribution:
            return None
        return obj.attribution.course.course_name

    def get_room_name(self, obj):
        return obj.room.room_name if obj.room else None

    def get_room_building(self, obj):
        if not obj.room:
            return None
        return getattr(obj.room, "building_name", None)


class BulkUpsertSessionSerializer(serializers.Serializer):
    """Used by the bulk_upsert action — accepts a list of session payloads."""

    sessions = CourseSessionSerializer(many=True)


class ConflictCheckSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    template = serializers.UUIDField(required=False)
