from rest_framework import serializers

from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.teacher_app.models import (
    Attribution,
    Teacher,
)
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.scheduling_module.scheduling_app.models import Timetable

from .models import SecretaryNote, TeacherWorkload, TeachingProgress


class TeachingProgressSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(
        source="attribution.course.course_name", read_only=True
    )
    course_code = serializers.CharField(
        source="attribution.course.course_code", read_only=True
    )
    teacher_name = serializers.SerializerMethodField()
    academic_year = serializers.CharField(
        source="attribution.academic_year.year_name", read_only=True
    )
    faculty_name = serializers.CharField(source="faculty.faculty_name", read_only=True)

    class Meta:
        model = TeachingProgress
        fields = [
            "id",
            "attribution",
            "faculty",
            "faculty_name",
            "progress_percentage",
            "last_updated",
            "submitted_by",
            "course_name",
            "course_code",
            "teacher_name",
            "academic_year",
        ]
        read_only_fields = ["id", "last_updated", "progress_percentage"]

    def get_teacher_name(self, obj):
        teacher = obj.attribution.principal_teacher
        user = teacher.user
        return f"{user.first_name} {user.last_name}"


class TeachingProgressDetailSerializer(serializers.ModelSerializer):
    attribution_details = serializers.SerializerMethodField()
    timetable_summary = serializers.SerializerMethodField()

    class Meta:
        model = TeachingProgress
        fields = [
            "id",
            "attribution",
            "attribution_details",
            "faculty",
            "progress_percentage",
            "last_updated",
            "submitted_by",
            "timetable_summary",
        ]
        read_only_fields = ["id", "last_updated", "progress_percentage"]

    def get_attribution_details(self, obj):
        attribution = obj.attribution
        return {
            "course": {
                "name": attribution.course.course_name,
                "code": attribution.course.course_code,
            },
            "principal_teacher": f"{attribution.principal_teacher.user.first_name} {attribution.principal_teacher.user.last_name}",
            "substitute_teacher": (
                f"{attribution.substitute_teacher.user.first_name} {attribution.substitute_teacher.user.last_name}"
                if attribution.substitute_teacher
                else None
            ),
            "academic_year": attribution.academic_year.year_name,
            "status": attribution.status_principal_teacher,
        }

    def get_timetable_summary(self, obj):
        timetables = Timetable.objects.filter(attribution=obj.attribution)
        total_planned = 0
        total_delivered = 0

        for timetable in timetables:
            reports = timetable.activity_reports.all()
            for report in reports:
                if report.planned_hours:
                    total_planned += report.planned_hours
                if report.delivered_hours:
                    total_delivered += report.delivered_hours

        return {
            "total_planned_hours": total_planned,
            "total_delivered_hours": total_delivered,
            "timetable_count": timetables.count(),
        }


class TeacherWorkloadSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_email = serializers.CharField(source="teacher.email", read_only=True)
    faculty_name = serializers.CharField(source="faculty.faculty_name", read_only=True)
    academic_year_name = serializers.CharField(
        source="academic_year.year_name", read_only=True
    )
    workload_percentage = serializers.SerializerMethodField()

    class Meta:
        model = TeacherWorkload
        fields = [
            "id",
            "faculty",
            "faculty_name",
            "teacher",
            "teacher_name",
            "teacher_email",
            "academic_year",
            "academic_year_name",
            "total_hours",
            "assigned_hours",
            "workload_percentage",
            "is_permanent",
        ]
        read_only_fields = ["id", "assigned_hours"]

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"

    def get_workload_percentage(self, obj):
        if obj.total_hours > 0:
            return round((float(obj.assigned_hours) / obj.total_hours) * 100, 2)
        return 0


class TeacherWorkloadDetailSerializer(serializers.ModelSerializer):
    teacher_info = serializers.SerializerMethodField()
    attributions = serializers.SerializerMethodField()

    class Meta:
        model = TeacherWorkload
        fields = [
            "id",
            "faculty",
            "teacher",
            "teacher_info",
            "academic_year",
            "total_hours",
            "assigned_hours",
            "is_permanent",
            "attributions",
        ]
        read_only_fields = ["id", "assigned_hours"]

    def get_teacher_info(self, obj):
        teacher_profile = Teacher.objects.filter(user=obj.teacher).first()
        return {
            "name": f"{obj.teacher.first_name} {obj.teacher.last_name}",
            "email": obj.teacher.email,
            "grade": teacher_profile.teacher_grade if teacher_profile else None,
            "speciality": teacher_profile.speciality if teacher_profile else None,
        }

    def get_attributions(self, obj):
        attributions = Attribution.objects.filter(
            principal_teacher__user=obj.teacher,
            academic_year=obj.academic_year,
        )

        attribution_list = []
        for attr in attributions:
            timetables = Timetable.objects.filter(attribution=attr)
            total_hours = 0
            for tt in timetables:
                for report in tt.activity_reports.all():
                    if report.delivered_hours:
                        total_hours += report.delivered_hours

            attribution_list.append(
                {
                    "id": str(attr.id),
                    "course_name": attr.course.course_name,
                    "course_code": attr.course.course_code,
                    "status": attr.status_principal_teacher,
                    "delivered_hours": total_hours,
                }
            )

        return attribution_list


class SecretaryNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    faculty_name = serializers.CharField(source="faculty.faculty_name", read_only=True)

    class Meta:
        model = SecretaryNote
        fields = [
            "id",
            "faculty",
            "faculty_name",
            "subject",
            "message",
            "created_by",
            "created_by_name",
            "created_date",
            "is_resolved",
        ]
        read_only_fields = ["id", "created_date", "created_by"]

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class DeanDashboardStatsSerializer(serializers.Serializer):
    total_timetables = serializers.IntegerField()
    published_timetables = serializers.IntegerField()
    pending_timetables = serializers.IntegerField()
    teaching_progress_avg = serializers.FloatField()
    total_teachers = serializers.IntegerField()
    permanent_teachers = serializers.IntegerField()
    visiting_teachers = serializers.IntegerField()
    total_attributions = serializers.IntegerField()
    pending_attributions = serializers.IntegerField()
    accepted_attributions = serializers.IntegerField()
    total_workload_hours = serializers.FloatField()
    assigned_workload_hours = serializers.FloatField()
    pending_secretary_notes = serializers.IntegerField()
    total_students = serializers.IntegerField()
    active_courses = serializers.IntegerField()


class TimetableOverviewSerializer(serializers.Serializer):
    timetable_id = serializers.UUIDField()
    class_name = serializers.CharField()
    course_name = serializers.CharField()
    teacher_name = serializers.CharField()
    room_name = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    status = serializers.CharField()
    slot_count = serializers.IntegerField()


class CourseAttributionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_code = serializers.CharField(source="course.course_code", read_only=True)
    principal_teacher_name = serializers.SerializerMethodField()
    substitute_teacher_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(
        source="academic_year.year_name", read_only=True
    )

    class Meta:
        model = Attribution
        fields = [
            "id",
            "course",
            "course_name",
            "course_code",
            "principal_teacher",
            "principal_teacher_name",
            "substitute_teacher",
            "substitute_teacher_name",
            "academic_year",
            "academic_year_name",
            "date_attribution",
            "status_principal_teacher",
            "status_substitute_teacher",
            "commentaire",
        ]
        read_only_fields = ["id", "date_attribution"]

    def get_principal_teacher_name(self, obj):
        user = obj.principal_teacher.user
        return f"{user.first_name} {user.last_name}"

    def get_substitute_teacher_name(self, obj):
        if obj.substitute_teacher:
            user = obj.substitute_teacher.user
            return f"{user.first_name} {user.last_name}"
        return None


class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.faculty_name", read_only=True)
    class_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "department_name",
            "abreviation",
            "faculty",
            "faculty_name",
            "class_count",
        ]
        read_only_fields = ["id"]

    def get_class_count(self, obj):
        return obj.classes.count()


class ClassSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.department_name", read_only=True
    )
    faculty_name = serializers.CharField(
        source="department.faculty.faculty_name", read_only=True
    )
    group_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = [
            "id",
            "class_name",
            "department",
            "department_name",
            "faculty_name",
            "group_count",
            "student_count",
        ]
        read_only_fields = ["id"]

    def get_group_count(self, obj):
        return obj.groups.count()

    def get_student_count(self, obj):
        return Inscription.objects.filter(class_fk=obj, regist_status="Active").count()


class ClassGroupSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="class_fk.class_name", read_only=True)
    academic_year_name = serializers.CharField(
        source="academic_year.year_name", read_only=True
    )
    student_count = serializers.SerializerMethodField()
    timetable_count = serializers.SerializerMethodField()

    class Meta:
        model = ClassGroup
        fields = [
            "id",
            "class_fk",
            "class_name",
            "academic_year",
            "academic_year_name",
            "group_name",
            "created_date",
            "student_count",
            "timetable_count",
        ]
        read_only_fields = ["id", "created_date"]

    def get_student_count(self, obj):
        return Inscription.objects.filter(
            class_fk=obj.class_fk,
            academic_year=obj.academic_year,
            regist_status="Active",
        ).count()

    def get_timetable_count(self, obj):
        return obj.timetables.count()


class StudentSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    current_class = serializers.SerializerMethodField()
    inscription_status = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "user_info",
            "matricule",
            "current_class",
            "inscription_status",
        ]
        read_only_fields = ["id"]

    def get_user_info(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
            "phone": obj.user.phone,
        }

    def get_current_class(self, obj):
        current_inscription = (
            Inscription.objects.filter(
                student=obj, regist_status="Active", is_year_close=False
            )
            .select_related("class_fk", "academic_year")
            .first()
        )
        if current_inscription:
            return {
                "class_name": (
                    current_inscription.class_fk.class_name
                    if current_inscription.class_fk
                    else "N/A"
                ),
                "academic_year": current_inscription.academic_year.year_name,
                "date_inscription": current_inscription.date_inscription,
            }
        return None

    def get_inscription_status(self, obj):
        current_inscription = Inscription.objects.filter(
            student=obj, is_year_close=False
        ).first()
        return current_inscription.regist_status if current_inscription else "N/A"


class InscriptionSerializer(serializers.ModelSerializer):
    student_info = serializers.SerializerMethodField()
    class_name = serializers.CharField(source="class_fk.class_name", read_only=True)
    academic_year_name = serializers.CharField(
        source="academic_year.year_name", read_only=True
    )
    department_name = serializers.CharField(
        source="class_fk.department.department_name", read_only=True
    )

    class Meta:
        model = Inscription
        fields = [
            "id",
            "student",
            "student_info",
            "academic_year",
            "academic_year_name",
            "class_fk",
            "class_name",
            "department_name",
            "date_inscription",
            "regist_status",
            "withdrawal_date",
            "is_year_close",
        ]
        read_only_fields = ["id", "withdrawal_date"]

    def get_student_info(self, obj):
        return {
            "matricule": obj.student.matricule,
            "first_name": obj.student.user.first_name,
            "last_name": obj.student.user.last_name,
            "email": obj.student.user.email,
        }


class FacultyOverviewSerializer(serializers.ModelSerializer):
    department_count = serializers.SerializerMethodField()
    class_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = [
            "id",
            "faculty_name",
            "abreviation",
            "department_count",
            "class_count",
            "student_count",
            "teacher_count",
        ]
        read_only_fields = ["id"]

    def get_department_count(self, obj):
        return obj.departments.count()

    def get_class_count(self, obj):
        return Class.objects.filter(department__faculty=obj).count()

    def get_student_count(self, obj):
        return Inscription.objects.filter(
            class_fk__department__faculty=obj, regist_status="Active"
        ).count()

    def get_teacher_count(self, obj):
        return (
            Attribution.objects.filter(course__faculty=obj)
            .values("principal_teacher")
            .distinct()
            .count()
        )


class StudentStatisticsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    pending_students = serializers.IntegerField()
    suspended_students = serializers.IntegerField()
    by_class = serializers.ListField()
    by_department = serializers.ListField()
    by_gender = serializers.DictField()


class ClassStatisticsSerializer(serializers.Serializer):
    total_classes = serializers.IntegerField()
    total_groups = serializers.IntegerField()
    classes_by_department = serializers.ListField()
    average_students_per_class = serializers.FloatField()
