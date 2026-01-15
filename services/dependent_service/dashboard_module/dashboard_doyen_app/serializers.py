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
from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
    GradeComplaint,
    JuryDecision,
    JurySession,
    TeacherPaymentClaim,
)
from services.dependent_service.exam_module.exam_app.models import (
    Exam,
    ExamRoom,
    ExamSupervisor,
    ExamType,
)
from services.dependent_service.exam_module.result_app.models import (
    CompiledResult,
    Result,
    Session,
    Supplement,
)
from services.dependent_service.scheduling_module.scheduling_app.models import (
    ActivityReport,
    Attendance,
    ScheduleSlot,
    Timetable,
    TimetableMerge,
)
from services.foundational_service.auth_module.authentication_app.serializers import (
    UserSerializer,
)
from services.foundational_service.geo_module.serializers import CollineSerializer

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
        source="attribution.academic_year.academic_year", read_only=True
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
            "academic_year": attribution.academic_year.academic_year,
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
    academic_year = serializers.CharField(
        source="academic_year.academic_year", read_only=True
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
            "academic_year",
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
    academic_year = serializers.CharField(
        source="academic_year.academic_year", read_only=True
    )
    class_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

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
            "date_attribution",
            "status_principal_teacher",
            "status_substitute_teacher",
            "commentaire",
            "class_name",
            "department_name",
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

    def get_class_name(self, obj):
        return obj.course.module.class_fk.class_name

    def get_department_name(self, obj):
        return obj.course.module.class_fk.department.department_name


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
    student_count = serializers.SerializerMethodField()
    timetable_count = serializers.SerializerMethodField()
    department_name = serializers.CharField(source="class_fk.department.department_name", read_only=True)

    class Meta:
        model = ClassGroup
        fields = [
            "id",
            "class_fk",
            "class_name",
            "department_name",
            "academic_year",
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
    user_obj = serializers.SerializerMethodField()
    current_class = serializers.SerializerMethodField()
    inscription_status = serializers.SerializerMethodField()
    student_group = serializers.SerializerMethodField()
    colline = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "user_obj",
            "matricule",
            "current_class",
            "inscription_status",
            "student_group",
            "colline",
        ]
        read_only_fields = ["id"]

    def get_user_obj(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
            "phone_number": obj.user.phone_number,
            "marital_status": obj.user.marital_status,
            "gender": obj.user.gender,
            "role_name": obj.user.role.name,
            "profile_picture": (
                obj.user.profile_picture if obj.user.profile_picture else None
            ),
        }

    def get_student_group(self, obj):
        """
        Get the student's group via their current active class inscription.
        """
        current_inscription = (
            Inscription.objects.filter(
                student=obj,
                regist_status="Active",
                is_year_close=False
            )
            .select_related("class_group")  # follow relation to the assigned group
            .first()
        )

        if current_inscription and current_inscription.class_group:
            group = current_inscription.class_group
            return {
                "id": str(group.id),
                "name": getattr(group, "group_name", "N/A")
            }

        return None

    def get_colline(self, obj):
        return CollineSerializer(obj.user.residence, many=True).data

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
                "academic_year": current_inscription.academic_year.academic_year,
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
    academic_year = serializers.CharField(
        source="academic_year.academic_year", read_only=True
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
            "academic_year",
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


class JurySessionSerializer(serializers.ModelSerializer):
    class_group_info = serializers.SerializerMethodField()
    jury_members_info = serializers.SerializerMethodField()
    created_by_info = serializers.SerializerMethodField()
    decisions_count = serializers.SerializerMethodField()

    class Meta:
        model = JurySession
        fields = [
            "id",
            "session_name",
            "session_date",
            "class_group",
            "class_group_info",
            "jury_members",
            "jury_members_info",
            "status",
            "minutes_document",
            "created_by",
            "created_by_info",
            "created_at",
            "decisions_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_class_group_info(self, obj):
        return {
            "group_name": obj.class_group.group_name,
            "class_name": obj.class_group.class_fk.class_name,
            "department_name": obj.class_group.class_fk.department.department_name,
            "academic_year": obj.class_group.academic_year.academic_year,
        }

    def get_jury_members_info(self, obj):
        return [
            {
                "id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "email": member.email,
            }
            for member in obj.jury_members.all()
        ]

    def get_created_by_info(self, obj):
        return {
            "first_name": obj.created_by.first_name,
            "last_name": obj.created_by.last_name,
            "email": obj.created_by.email,
        }

    def get_decisions_count(self, obj):
        return obj.jury_decisions.count()


class JuryDecisionSerializer(serializers.ModelSerializer):
    student_info = serializers.SerializerMethodField()
    jury_session_info = serializers.SerializerMethodField()
    validated_by_info = serializers.SerializerMethodField()

    class Meta:
        model = JuryDecision
        fields = [
            "id",
            "jury_session",
            "jury_session_info",
            "student",
            "student_info",
            "decision",
            "notes",
            "validated_by",
            "validated_by_info",
            "validated_at",
        ]
        read_only_fields = ["id", "validated_at"]

    def get_student_info(self, obj):
        return {
            "matricule": obj.student.matricule,
            "first_name": obj.student.user.first_name,
            "last_name": obj.student.user.last_name,
            "email": obj.student.user.email,
        }

    def get_jury_session_info(self, obj):
        return {
            "session_name": obj.jury_session.session_name,
            "session_date": obj.jury_session.session_date,
            "status": obj.jury_session.status,
        }

    def get_validated_by_info(self, obj):
        return {
            "first_name": obj.validated_by.first_name,
            "last_name": obj.validated_by.last_name,
            "email": obj.validated_by.email,
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


class ScheduleSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleSlot
        fields = [
            "id",
            "day_of_week",
            "start_time",
            "end_time",
            "schedule_name",
        ]
        read_only_fields = ["id"]


class TimetableSerializer(serializers.ModelSerializer):
    class_group_name = serializers.CharField(
        source="class_group.group_name", read_only=True
    )
    class_name = serializers.CharField(
        source="class_group.class_fk.class_name", read_only=True
    )
    course_name = serializers.CharField(
        source="attribution.course.course_name", read_only=True
    )
    teacher_name = serializers.SerializerMethodField()
    room_name = serializers.CharField(source="room.room_name", read_only=True)
    slot_details = ScheduleSlotSerializer(source="slots", many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Timetable
        fields = [
            "id",
            "class_group",
            "class_group_name",
            "class_name",
            "attribution",
            "course_name",
            "teacher_name",
            "room",
            "room_name",
            "slots",
            "slot_details",
            "start_date",
            "end_date",
            "status",
            "created_by",
            "created_by_name",
            "created_date",
            "published_date",
        ]
        read_only_fields = ["id", "created_date", "created_by"]

    def get_teacher_name(self, obj):
        if obj.attribution and obj.attribution.principal_teacher:
            user = obj.attribution.principal_teacher.user
            return f"{user.first_name} {user.last_name}"
        return None

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class TimetableDetailSerializer(serializers.ModelSerializer):
    class_group_details = serializers.SerializerMethodField()
    attribution_details = serializers.SerializerMethodField()
    room_details = serializers.SerializerMethodField()
    slot_details = ScheduleSlotSerializer(source="slots", many=True, read_only=True)
    attendance_summary = serializers.SerializerMethodField()
    activity_reports = serializers.SerializerMethodField()

    class Meta:
        model = Timetable
        fields = [
            "id",
            "class_group",
            "class_group_details",
            "attribution",
            "attribution_details",
            "room",
            "room_details",
            "slots",
            "slot_details",
            "start_date",
            "end_date",
            "status",
            "created_by",
            "created_date",
            "published_date",
            "attendance_summary",
            "activity_reports",
        ]
        read_only_fields = ["id", "created_date"]

    def get_class_group_details(self, obj):
        if obj.class_group:
            return {
                "id": str(obj.class_group.id),
                "group_name": obj.class_group.group_name,
                "class_name": obj.class_group.class_fk.class_name,
                "academic_year": obj.class_group.academic_year.academic_year,
            }
        return None

    def get_attribution_details(self, obj):
        if obj.attribution:
            attr = obj.attribution
            return {
                "id": str(attr.id),
                "course_name": attr.course.course_name,
                "course_code": attr.course.course_code,
                "teacher_name": f"{attr.principal_teacher.user.first_name} {attr.principal_teacher.user.last_name}",
                "status": attr.status_principal_teacher,
            }
        return None

    def get_room_details(self, obj):
        return {
            "id": str(obj.room.id),
            "room_name": obj.room.room_name,
            "capacity": obj.room.capacity,
            "building": obj.room.building.building_name if obj.room.building else None,
        }

    def get_attendance_summary(self, obj):
        attendances = obj.attendances.all()
        total = attendances.count()
        present = attendances.filter(status="Present").count()
        absent = attendances.filter(status="Absent").count()
        excused = attendances.filter(status="Excused").count()

        return {
            "total_students": total,
            "present": present,
            "absent": absent,
            "excused": excused,
            "attendance_rate": round((present / total * 100), 2) if total > 0 else 0,
        }

    def get_activity_reports(self, obj):
        reports = obj.activity_reports.all()
        return [
            {
                "id": str(report.id),
                "planned_hours": report.planned_hours,
                "delivered_hours": report.delivered_hours,
                "completion_rate": (
                    float(report.completion_rate) if report.completion_rate else 0
                ),
                "observations": report.observations,
            }
            for report in reports
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.CharField(
        source="student.matricule", read_only=True
    )
    timetable_info = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "timetable",
            "timetable_info",
            "student",
            "student_name",
            "student_matricule",
            "status",
            "remarks",
        ]
        read_only_fields = ["id"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_timetable_info(self, obj):
        tt = obj.timetable
        return {
            "id": str(tt.id),
            "class_group": tt.class_group.group_name if tt.class_group else None,
            "course": tt.attribution.course.course_name if tt.attribution else None,
            "start_date": tt.start_date,
            "end_date": tt.end_date,
        }


class ActivityReportSerializer(serializers.ModelSerializer):
    timetable_info = serializers.SerializerMethodField()

    class Meta:
        model = ActivityReport
        fields = [
            "id",
            "timetable",
            "timetable_info",
            "planned_hours",
            "delivered_hours",
            "completion_rate",
            "observations",
        ]
        read_only_fields = ["id", "completion_rate"]

    def get_timetable_info(self, obj):
        tt = obj.timetable
        return {
            "id": str(tt.id),
            "class_group": tt.class_group.group_name if tt.class_group else None,
            "course": tt.attribution.course.course_name if tt.attribution else None,
            "teacher": (
                f"{tt.attribution.principal_teacher.user.first_name} {tt.attribution.principal_teacher.user.last_name}"
                if tt.attribution
                else None
            ),
        }

    def validate(self, data):
        planned_hours = data.get("planned_hours")
        delivered_hours = data.get("delivered_hours")

        if planned_hours is not None and delivered_hours is not None:
            if planned_hours > 0:
                completion_rate = round((delivered_hours / planned_hours) * 100, 2)
                data["completion_rate"] = min(completion_rate, 100)
            else:
                data["completion_rate"] = 0

        return data


class BulkAttendanceSerializer(serializers.Serializer):
    timetable_id = serializers.UUIDField()
    attendances = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
        )
    )


class StudentGroupAssignmentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    class_group_id = serializers.UUIDField()


# Exam Management Serializers
class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = ["id", "exam_type_name", "description"]
        read_only_fields = ["id"]


class ExamSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_code = serializers.CharField(source="course.course_code", read_only=True)
    exam_type_name = serializers.CharField(
        source="exam_type.exam_type_name", read_only=True
    )
    academic_year = serializers.CharField(
        source="academic_year.academic_year", read_only=True
    )
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "id",
            "course",
            "course_name",
            "course_code",
            "exam_type",
            "exam_type_name",
            "academic_year",
            "academic_year",
            "exam_date",
            "start_time",
            "end_time",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class ExamRoomSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.room_name", read_only=True)
    room_capacity = serializers.IntegerField(source="room.capacity", read_only=True)
    building_name = serializers.CharField(
        source="room.building.building_name", read_only=True
    )

    class Meta:
        model = ExamRoom
        fields = [
            "id",
            "exam",
            "room",
            "room_name",
            "room_capacity",
            "building_name",
            "range_student",
        ]
        read_only_fields = ["id"]


class ExamSupervisorSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.SerializerMethodField()
    supervisor_email = serializers.CharField(
        source="supervisor.user.email", read_only=True
    )

    class Meta:
        model = ExamSupervisor
        fields = [
            "id",
            "exam_room",
            "supervisor",
            "supervisor_name",
            "supervisor_email",
        ]
        read_only_fields = ["id"]

    def get_supervisor_name(self, obj):
        return f"{obj.supervisor.supervisor_name} {obj.supervisor.supervisor_surname}"


class ExamDetailSerializer(serializers.ModelSerializer):
    course_details = serializers.SerializerMethodField()
    exam_type_details = serializers.SerializerMethodField()
    rooms = ExamRoomSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "course",
            "course_details",
            "exam_type",
            "exam_type_details",
            "academic_year",
            "exam_date",
            "start_time",
            "end_time",
            "status",
            "created_by",
            "created_at",
            "rooms",
        ]
        read_only_fields = ["id", "created_at"]

    def get_course_details(self, obj):
        return {
            "id": str(obj.course.id),
            "course_name": obj.course.course_name,
            "course_code": obj.course.course_code,
            "credits": obj.course.course_credit,
        }

    def get_exam_type_details(self, obj):
        return {
            "id": str(obj.exam_type.id),
            "exam_type_name": obj.exam_type.exam_type_name,
            "description": obj.exam_type.description,
        }


# Result Management Serializers
class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "session_name"]
        read_only_fields = ["id"]


class ResultSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    session_name = serializers.CharField(source="session.session_name", read_only=True)
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.CharField(
        source="inscription.student.matricule", read_only=True
    )

    class Meta:
        model = Result
        fields = [
            "id",
            "course",
            "course_name",
            "inscription",
            "student_name",
            "student_matricule",
            "session",
            "session_name",
            "mark",
        ]
        read_only_fields = ["id"]

    def get_student_name(self, obj):
        student = obj.inscription.student
        return f"{student.user.first_name} {student.user.last_name}"


class BulkResultEntrySerializer(serializers.Serializer):
    marks = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
        )
    )


class CompiledResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.CharField(
        source="inscription.student.matricule", read_only=True
    )
    class_name = serializers.CharField(
        source="inscription.class_fk.class_name", read_only=True
    )

    class Meta:
        model = CompiledResult
        fields = [
            "id",
            "inscription",
            "student_name",
            "student_matricule",
            "class_name",
            "results",
            "average_mark",
            "status",
            "is_promoted",
        ]
        read_only_fields = ["id"]

    def get_student_name(self, obj):
        student = obj.inscription.student
        return f"{student.user.first_name} {student.user.last_name}"


class SupplementSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.CharField(
        source="inscription.student.matricule", read_only=True
    )

    class Meta:
        model = Supplement
        fields = [
            "id",
            "inscription",
            "student_name",
            "student_matricule",
            "course",
            "course_name",
            "validation",
            "validation_date",
            "mark",
        ]
        read_only_fields = ["id", "validation", "validation_date"]

    def get_student_name(self, obj):
        student = obj.inscription.student
        return f"{student.user.first_name} {student.user.last_name}"


# Jury Management Serializers
class JurySessionSerializer(serializers.ModelSerializer):
    jury_member_names = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    decision_count = serializers.SerializerMethodField()

    class Meta:
        model = JurySession
        fields = [
            "id",
            "session_name",
            "session_date",
            "jury_members",
            "jury_member_names",
            "status",
            "minutes_document",
            "created_by",
            "created_by_name",
            "created_at",
            "decision_count",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    def get_jury_member_names(self, obj):
        return [
            f"{member.first_name} {member.last_name}"
            for member in obj.jury_members.all()
        ]

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_decision_count(self, obj):
        return obj.jurydecision_set.count()


class JuryDecisionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.CharField(
        source="student.matricule", read_only=True
    )
    jury_session_name = serializers.CharField(
        source="jury_session.session_name", read_only=True
    )
    validated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = JuryDecision
        fields = [
            "id",
            "jury_session",
            "jury_session_name",
            "student",
            "student_name",
            "student_matricule",
            "decision",
            "notes",
            "validated_by",
            "validated_by_name",
            "validated_at",
        ]
        read_only_fields = ["id", "validated_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_validated_by_name(self, obj):
        return f"{obj.validated_by.first_name} {obj.validated_by.last_name}"


class GradeComplaintSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.CharField(
        source="student.matricule", read_only=True
    )
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = GradeComplaint
        fields = [
            "id",
            "student",
            "student_name",
            "student_matricule",
            "course",
            "course_name",
            "original_grade",
            "complaint_reason",
            "status",
            "assigned_to",
            "assigned_to_name",
            "new_grade",
            "resolution_notes",
            "submitted_at",
            "resolved_at",
        ]
        read_only_fields = ["id", "submitted_at", "resolved_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


# Teacher Payment Claim Serializers
class TeacherPaymentClaimSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    verified_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPaymentClaim
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "course",
            "course_name",
            "hours_taught",
            "hourly_rate",
            "total_amount",
            "status",
            "verified_by",
            "verified_by_name",
            "approved_by",
            "approved_by_name",
            "submitted_at",
            "processed_at",
        ]
        read_only_fields = [
            "id",
            "total_amount",
            "submitted_at",
            "processed_at",
            "verified_by",
            "approved_by",
        ]

    def get_teacher_name(self, obj):
        return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"

    def get_verified_by_name(self, obj):
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}"
        return None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None


class TimetableMergeSerializer(serializers.ModelSerializer):
    timetable_ids = serializers.PrimaryKeyRelatedField(
        source="timetables", many=True, queryset=Timetable.objects.all()
    )

    created_by = UserSerializer(read_only=True)

    class Meta:
        model = TimetableMerge
        fields = [
            "id",
            "name",
            "timetable_ids",
            "created_at",
            "created_by",
        ]

    def create(self, validated_data):
        """
        created_by vient automatiquement du request.user
        """
        request = self.context["request"]
        timetables = validated_data.pop("timetables")

        instance = TimetableMerge.objects.create(
            created_by=request.user, **validated_data
        )
        instance.timetables.set(timetables)

        return instance
