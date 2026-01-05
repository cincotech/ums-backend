from rest_framework import serializers

from services.core_service.academic_module.course_app.models import Course


class CourseBasicSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(
        source="module.class_fk.class_name", read_only=True
    )
    department_name = serializers.CharField(
        source="module.class_fk.department.department_name", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "course_name",
            "course_code",
            "credits",
            "class_name",
            "department_name",
        ]
        read_only_fields = ["id"]


class CourseDetailSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(
        source="module.class_fk.class_name", read_only=True
    )
    department_name = serializers.CharField(
        source="module.class_fk.department.department_name", read_only=True
    )
    faculty_name = serializers.CharField(
        source="module.class_fk.department.faculty.faculty_name", read_only=True
    )
    attribution_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "course_name",
            "course_code",
            "credits",
            "class_name",
            "department_name",
            "faculty_name",
            "attribution_count",
        ]
        read_only_fields = ["id"]

    def get_attribution_count(self, obj):
        return obj.attribution_set.count()


class CourseStatisticsSerializer(serializers.Serializer):
    course_id = serializers.CharField()
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    credits = serializers.IntegerField()
    total_attributions = serializers.IntegerField()
    accepted_attributions = serializers.IntegerField()
    pending_attributions = serializers.IntegerField()
    total_timetables = serializers.IntegerField()
    published_timetables = serializers.IntegerField()
    total_planned_hours = serializers.IntegerField()
    total_delivered_hours = serializers.IntegerField()
    avg_completion_rate = serializers.FloatField()
    total_students = serializers.IntegerField()


class CourseEnrollmentSerializer(serializers.Serializer):
    course_id = serializers.CharField()
    course_name = serializers.CharField()
    total_enrolled = serializers.IntegerField()
    male = serializers.IntegerField()
    female = serializers.IntegerField()
    by_class = serializers.ListField()


class CoursePerformanceSerializer(serializers.Serializer):
    course_id = serializers.CharField()
    course_name = serializers.CharField()
    total_results = serializers.IntegerField()
    average_mark = serializers.FloatField()
    pass_rate = serializers.FloatField()
    fail_rate = serializers.FloatField()


class CourseAttributionDetailSerializer(serializers.Serializer):
    id = serializers.CharField()
    principal_teacher = serializers.CharField()
    substitute_teacher = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    academic_year = serializers.CharField()


class CourseAttributionStatusSerializer(serializers.Serializer):
    course_id = serializers.CharField()
    total_attributions = serializers.IntegerField()
    status_breakdown = serializers.DictField()
    attributions = CourseAttributionDetailSerializer(many=True)


class CourseSummarySerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    total_credits = serializers.IntegerField()
    courses_with_attribution = serializers.IntegerField()
    courses_without_attribution = serializers.IntegerField()


class CourseTeacherSerializer(serializers.Serializer):
    id = serializers.CharField()
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    credits = serializers.IntegerField()
    attribution_id = serializers.CharField()
    status = serializers.CharField()
    delivered_hours = serializers.IntegerField()
    class_name = serializers.CharField()


class CourseClassSerializer(serializers.Serializer):
    id = serializers.CharField()
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    credits = serializers.IntegerField()
    attribution_count = serializers.IntegerField()
    teachers = serializers.ListField()


class CourseActivityReportSerializer(serializers.Serializer):
    id = serializers.CharField()
    timetable_id = serializers.CharField()
    class_group = serializers.CharField(allow_null=True)
    planned_hours = serializers.IntegerField(allow_null=True)
    delivered_hours = serializers.IntegerField(allow_null=True)
    completion_rate = serializers.FloatField()
    observations = serializers.CharField(allow_null=True)
