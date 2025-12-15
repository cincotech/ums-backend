from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.teacher_app.models import (
    Attribution,
    Teacher,
)
from services.core_service.academic_module.university_app.models import AcademicYear
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
)
from services.dependent_service.exam_module.result_app.models import (
    CompiledResult,
    Result,
    Supplement,
)
from services.dependent_service.scheduling_module.scheduling_app.models import (
    ActivityReport,
    Attendance,
    Timetable,
)

from .models import SecretaryNote, TeacherWorkload, TeachingProgress


class DeanDashboardService:
    @staticmethod
    def get_dashboard_statistics(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            print(academic_year_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        timetables = Timetable.objects.filter(
            class_group__class_fk__department__faculty=faculty,
            start_date__year=academic_year.civil_year if academic_year else None,
        )

        attributions = Attribution.objects.filter(
            course__module__class_fk__department__faculty=faculty,
            academic_year=academic_year,
        )

        teaching_progress = TeachingProgress.objects.filter(
            faculty=faculty, attribution__academic_year=academic_year
        )

        workloads = TeacherWorkload.objects.filter(
            faculty=faculty, academic_year=academic_year
        )

        teachers = Teacher.objects.filter(
            Q(
                principal_attributions__course__module__class_fk__department__faculty=faculty
            )
            | Q(
                substitute_attributions__course__module__class_fk__department__faculty=faculty
            ),
            Q(principal_attributions__academic_year=academic_year)
            | Q(substitute_attributions__academic_year=academic_year),
        ).distinct()

        students = Student.objects.filter(
            Q(inscriptions__class_fk__department__faculty=faculty)
            & Q(inscriptions__academic_year=academic_year)
        ).distinct()

        active_courses = Course.objects.filter(
            module__class_fk__department__faculty=faculty,
            attribution__academic_year=academic_year,
        ).distinct()

        secretary_notes = SecretaryNote.objects.filter(
            faculty=faculty, is_resolved=False
        )

        avg_progress = (
            teaching_progress.aggregate(avg=Avg("progress_percentage"))["avg"] or 0
        )

        total_workload = workloads.aggregate(
            total=Sum("total_hours"), assigned=Sum("assigned_hours")
        )

        stats = {
            "total_timetables": timetables.count(),
            "published_timetables": timetables.filter(
                published_date__isnull=False
            ).count(),
            "pending_timetables": timetables.filter(status="Planned").count(),
            "teaching_progress_avg": round(avg_progress, 2),
            "total_teachers": teachers.count(),
            "permanent_teachers": workloads.filter(is_permanent=True).count(),
            "visiting_teachers": workloads.filter(is_permanent=False).count(),
            "total_attributions": attributions.count(),
            "pending_attributions": attributions.filter(
                status_principal_teacher="Pending"
            ).count(),
            "accepted_attributions": attributions.filter(
                status_principal_teacher="Accepted"
            ).count(),
            "total_workload_hours": float(total_workload["total"] or 0),
            "assigned_workload_hours": float(total_workload["assigned"] or 0),
            "pending_secretary_notes": secretary_notes.count(),
            "total_students": students.count(),
            "active_courses": active_courses.count(),
        }

        return stats

    @staticmethod
    def get_timetable_overview(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        timetables = Timetable.objects.filter(
            class_group__class_fk__department__faculty=faculty,
            attribution__academic_year=academic_year,
        ).select_related("class_group", "attribution", "room")

        overview_data = []
        for tt in timetables:
            if tt.attribution:
                teacher_name = (
                    f"{tt.attribution.principal_teacher.user.first_name} "
                    f"{tt.attribution.principal_teacher.user.last_name}"
                )
                course_name = tt.attribution.course.course_name
            else:
                teacher_name = "N/A"
                course_name = "N/A"

            overview_data.append(
                {
                    "timetable_id": tt.id,
                    "class_name": (
                        tt.class_group.class_name if tt.class_group else "N/A"
                    ),
                    "course_name": course_name,
                    "teacher_name": teacher_name,
                    "room_name": tt.room.room_name,
                    "start_date": tt.start_date,
                    "end_date": tt.end_date,
                    "status": tt.status,
                    "slot_count": tt.slots.count(),
                }
            )

        return overview_data

    @staticmethod
    def get_teaching_progress_report(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        progress_entries = TeachingProgress.objects.filter(
            faculty=faculty, attribution__academic_year=academic_year
        ).select_related(
            "attribution", "attribution__course", "attribution__principal_teacher"
        )

        report_data = []
        for progress in progress_entries:
            timetables = Timetable.objects.filter(attribution=progress.attribution)
            total_planned = 0
            total_delivered = 0

            for tt in timetables:
                for report in tt.activity_reports.all():
                    if report.planned_hours:
                        total_planned += report.planned_hours
                    if report.delivered_hours:
                        total_delivered += report.delivered_hours

            teacher = progress.attribution.principal_teacher
            report_data.append(
                {
                    "progress_id": progress.id,
                    "course_name": progress.attribution.course.course_name,
                    "course_code": progress.attribution.course.course_code,
                    "teacher_name": f"{teacher.user.first_name} {teacher.user.last_name}",
                    "progress_percentage": float(progress.progress_percentage),
                    "planned_hours": total_planned,
                    "delivered_hours": total_delivered,
                    "last_updated": progress.last_updated,
                }
            )

        return report_data

    @staticmethod
    def get_teacher_workload_summary(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        workloads = TeacherWorkload.objects.filter(
            faculty=faculty, academic_year=academic_year
        ).select_related("teacher")

        summary_data = []
        for workload in workloads:
            workload_percentage = 0
            if workload.total_hours > 0:
                workload_percentage = (
                    float(workload.assigned_hours) / workload.total_hours
                ) * 100

            teacher_profile = Teacher.objects.filter(user=workload.teacher).first()

            summary_data.append(
                {
                    "workload_id": workload.id,
                    "teacher_name": f"{workload.teacher.first_name} {workload.teacher.last_name}",
                    "teacher_email": workload.teacher.email,
                    "teacher_grade": (
                        teacher_profile.teacher_grade if teacher_profile else "N/A"
                    ),
                    "is_permanent": workload.is_permanent,
                    "total_hours": workload.total_hours,
                    "assigned_hours": float(workload.assigned_hours),
                    "workload_percentage": round(workload_percentage, 2),
                    "status": (
                        "Overloaded"
                        if workload_percentage > 100
                        else "Underutilized" if workload_percentage < 70 else "Balanced"
                    ),
                }
            )

        return summary_data

    @staticmethod
    def update_all_teaching_progress(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        progress_entries = TeachingProgress.objects.filter(
            faculty=faculty, attribution__academic_year=academic_year
        )

        updated_count = 0
        for progress in progress_entries:
            progress.update_progress_from_timetable()
            updated_count += 1

        return {"updated_count": updated_count, "message": "Teaching progress updated"}

    @staticmethod
    def update_all_teacher_workloads(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        workloads = TeacherWorkload.objects.filter(
            faculty=faculty, academic_year=academic_year
        )

        updated_count = 0
        for workload in workloads:
            workload.update_from_progress()
            updated_count += 1

        return {"updated_count": updated_count, "message": "Teacher workloads updated"}

    @staticmethod
    def get_attribution_statistics(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        attributions = Attribution.objects.filter(
            course__module__class_fk__department__faculty=faculty,
            academic_year=academic_year,
        )

        stats = {
            "total": attributions.count(),
            "pending": attributions.filter(status_principal_teacher="Pending").count(),
            "accepted": attributions.filter(
                status_principal_teacher="Accepted"
            ).count(),
            "refused": attributions.filter(status_principal_teacher="Refused").count(),
            "with_substitute": attributions.filter(
                substitute_teacher__isnull=False
            ).count(),
            "by_course": list(
                attributions.values("course__course_name")
                .annotate(count=Count("id"))
                .order_by("-count")
            ),
        }

        return stats

    @staticmethod
    def get_room_utilization_report(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        timetables = Timetable.objects.filter(
            class_group__class_fk__department__faculty=faculty,
            attribution__academic_year=academic_year,
        ).select_related("room")

        room_usage = {}
        for tt in timetables:
            room_name = tt.room.room_name
            if room_name not in room_usage:
                room_usage[room_name] = {
                    "room_name": room_name,
                    "room_capacity": tt.room.capacity,
                    "total_allocations": 0,
                    "total_slots": 0,
                }
            room_usage[room_name]["total_allocations"] += 1
            room_usage[room_name]["total_slots"] += tt.slots.count()

        return list(room_usage.values())


class TeachingProgressService:
    @staticmethod
    def create_or_update_progress(attribution_id, faculty_id, submitted_by):
        attribution = Attribution.objects.get(id=attribution_id)
        faculty = Faculty.objects.get(id=faculty_id)

        progress, created = TeachingProgress.objects.get_or_create(
            attribution=attribution,
            faculty=faculty,
            defaults={"submitted_by": submitted_by},
        )

        if not created:
            progress.submitted_by = submitted_by
            progress.save()

        progress.update_progress_from_timetable()

        return progress, created


class TeacherWorkloadService:
    @staticmethod
    def create_or_update_workload(
        teacher_id, faculty_id, academic_year_id, total_hours, is_permanent=True
    ):
        from services.foundational_service.auth_module.user_app.models import User

        teacher = User.objects.get(id=teacher_id)
        faculty = Faculty.objects.get(id=faculty_id)
        academic_year = AcademicYear.objects.get(id=academic_year_id)

        workload, created = TeacherWorkload.objects.get_or_create(
            teacher=teacher,
            faculty=faculty,
            academic_year=academic_year,
            defaults={"total_hours": total_hours, "is_permanent": is_permanent},
        )

        if not created:
            workload.total_hours = total_hours
            workload.is_permanent = is_permanent
            workload.save()

        workload.update_from_progress()

        return workload, created


class StudentManagementService:
    @staticmethod
    def get_faculty_students(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        inscriptions = Inscription.objects.filter(
            class_fk__department__faculty=faculty, academic_year=academic_year
        ).select_related("student", "student__user", "class_fk", "academic_year")

        return inscriptions

    @staticmethod
    def get_student_statistics(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        inscriptions = Inscription.objects.filter(
            class_fk__department__faculty=faculty, academic_year=academic_year
        )

        total_students = inscriptions.count()
        active_students = inscriptions.filter(regist_status="Active").count()
        pending_students = inscriptions.filter(regist_status="Pending").count()
        suspended_students = inscriptions.filter(regist_status="Suspended").count()

        by_class = list(
            inscriptions.filter(regist_status="Active")
            .values("class_fk__class_name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        by_department = list(
            inscriptions.filter(regist_status="Active")
            .values("class_fk__department__department_name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        male_count = inscriptions.filter(
            regist_status="Active", student__user__gender="M"
        ).count()
        female_count = inscriptions.filter(
            regist_status="Active", student__user__gender="F"
        ).count()

        stats = {
            "total_students": total_students,
            "active_students": active_students,
            "pending_students": pending_students,
            "suspended_students": suspended_students,
            "by_class": by_class,
            "by_department": by_department,
            "by_gender": {"male": male_count, "female": female_count},
        }

        return stats

    @staticmethod
    def get_students_by_class(class_id, academic_year_id=None):
        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        inscriptions = Inscription.objects.filter(
            class_fk_id=class_id,
            academic_year=academic_year,
            regist_status="Active",
        ).select_related("student", "student__user")

        return inscriptions


class ClassManagementService:
    @staticmethod
    def get_faculty_classes(faculty_id):
        faculty = Faculty.objects.get(id=faculty_id)
        classes = Class.objects.filter(department__faculty=faculty).select_related(
            "department"
        )
        return classes

    @staticmethod
    def get_class_statistics(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        classes = Class.objects.filter(department__faculty=faculty)
        total_classes = classes.count()

        groups = ClassGroup.objects.filter(
            class_fk__department__faculty=faculty, academic_year=academic_year
        )
        total_groups = groups.count()

        classes_by_department = list(
            classes.values("department__department_name").annotate(count=Count("id"))
        )

        total_students = Inscription.objects.filter(
            class_fk__department__faculty=faculty,
            academic_year=academic_year,
            regist_status="Active",
        ).count()

        avg_students = total_students / total_classes if total_classes > 0 else 0

        stats = {
            "total_classes": total_classes,
            "total_groups": total_groups,
            "classes_by_department": classes_by_department,
            "average_students_per_class": round(avg_students, 2),
        }

        return stats

    @staticmethod
    def get_class_groups(class_id, academic_year_id=None):
        if academic_year_id:
            groups = ClassGroup.objects.filter(
                class_fk_id=class_id, academic_year_id=academic_year_id
            ).select_related("class_fk", "academic_year")
        else:
            groups = ClassGroup.objects.filter(class_fk_id=class_id).select_related(
                "class_fk", "academic_year"
            )
        return groups


class DepartmentManagementService:
    @staticmethod
    def get_faculty_departments(faculty_id):
        faculty = Faculty.objects.get(id=faculty_id)
        departments = faculty.departments.all()
        return departments

    @staticmethod
    def get_department_overview(department_id, academic_year_id=None):
        department = Department.objects.get(id=department_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        classes = department.classes.all()
        total_classes = classes.count()

        total_students = Inscription.objects.filter(
            class_fk__department=department,
            academic_year=academic_year,
            regist_status="Active",
        ).count()

        total_teachers = (
            Attribution.objects.filter(
                course__department=department, academic_year=academic_year
            )
            .values("principal_teacher")
            .distinct()
            .count()
        )

        groups = ClassGroup.objects.filter(
            class_fk__department=department, academic_year=academic_year
        ).count()

        overview = {
            "department_id": department.id,
            "department_name": department.department_name,
            "abreviation": department.abreviation,
            "total_classes": total_classes,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_groups": groups,
        }

        return overview


class FacultyManagementService:
    @staticmethod
    def get_faculty_overview(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        else:
            academic_year = AcademicYear.objects.filter(is_closed=False).first()

        departments = faculty.departments.count()
        classes = Class.objects.filter(department__faculty=faculty).count()

        students = Inscription.objects.filter(
            class_fk__department__faculty=faculty,
            academic_year=academic_year,
            regist_status="Active",
        ).count()

        teachers = (
            Attribution.objects.filter(
                course__module__class_fk__department__faculty=faculty,
                academic_year=academic_year,
            )
            .values("principal_teacher")
            .distinct()
            .count()
        )

        courses = Course.objects.filter(
            module__class_fk__department__faculty=faculty
        ).count()

        overview = {
            "faculty_id": faculty.id,
            "faculty_name": faculty.faculty_name,
            "abreviation": faculty.faculty_abreviation,
            "department_count": departments,
            "class_count": classes,
            "student_count": students,
            "teacher_count": teachers,
            "course_count": courses,
        }

        return overview


class TimetableManagementService:
    @staticmethod
    def check_room_conflict(
        room_id, start_date, end_date, slot_ids, exclude_timetable_id=None
    ):
        conflicts = Timetable.objects.filter(
            room_id=room_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
            slots__id__in=slot_ids,
        )

        if exclude_timetable_id:
            conflicts = conflicts.exclude(id=exclude_timetable_id)

        return conflicts.exists()

    @staticmethod
    def check_teacher_conflict(
        attribution_id, start_date, end_date, slot_ids, exclude_timetable_id=None
    ):
        conflicts = Timetable.objects.filter(
            attribution_id=attribution_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
            slots__id__in=slot_ids,
        )

        if exclude_timetable_id:
            conflicts = conflicts.exclude(id=exclude_timetable_id)

        return conflicts.exists()

    @staticmethod
    def check_class_group_conflict(
        class_group_id, start_date, end_date, slot_ids, exclude_timetable_id=None
    ):
        conflicts = Timetable.objects.filter(
            class_group_id=class_group_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
            slots__id__in=slot_ids,
        )

        if exclude_timetable_id:
            conflicts = conflicts.exclude(id=exclude_timetable_id)

        return conflicts.exists()

    @staticmethod
    def create_timetable(
        class_group_id,
        attribution_id,
        room_id,
        slot_ids,
        start_date,
        end_date,
        status,
        created_by,
    ):
        if TimetableManagementService.check_room_conflict(
            room_id, start_date, end_date, slot_ids
        ):
            raise ValueError("Room conflict detected for the selected time slots")

        if TimetableManagementService.check_teacher_conflict(
            attribution_id, start_date, end_date, slot_ids
        ):
            raise ValueError("Teacher conflict detected for the selected time slots")

        if TimetableManagementService.check_class_group_conflict(
            class_group_id, start_date, end_date, slot_ids
        ):
            raise ValueError(
                "Class group conflict detected for the selected time slots"
            )

        timetable = Timetable.objects.create(
            class_group_id=class_group_id,
            attribution_id=attribution_id,
            room_id=room_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            created_by=created_by,
        )

        timetable.slots.set(slot_ids)
        return timetable

    @staticmethod
    def update_timetable(
        timetable_id,
        class_group_id=None,
        attribution_id=None,
        room_id=None,
        slot_ids=None,
        start_date=None,
        end_date=None,
        status=None,
    ):
        timetable = Timetable.objects.get(id=timetable_id)

        check_room_id = room_id if room_id is not None else timetable.room_id
        check_attribution_id = (
            attribution_id if attribution_id is not None else timetable.attribution_id
        )
        check_class_group_id = (
            class_group_id if class_group_id is not None else timetable.class_group_id
        )
        check_start_date = (
            start_date if start_date is not None else timetable.start_date
        )
        check_end_date = end_date if end_date is not None else timetable.end_date
        check_slot_ids = (
            slot_ids
            if slot_ids is not None
            else list(timetable.slots.values_list("id", flat=True))
        )

        if TimetableManagementService.check_room_conflict(
            check_room_id,
            check_start_date,
            check_end_date,
            check_slot_ids,
            exclude_timetable_id=timetable_id,
        ):
            raise ValueError("Room conflict detected for the selected time slots")

        if TimetableManagementService.check_teacher_conflict(
            check_attribution_id,
            check_start_date,
            check_end_date,
            check_slot_ids,
            exclude_timetable_id=timetable_id,
        ):
            raise ValueError("Teacher conflict detected for the selected time slots")

        if TimetableManagementService.check_class_group_conflict(
            check_class_group_id,
            check_start_date,
            check_end_date,
            check_slot_ids,
            exclude_timetable_id=timetable_id,
        ):
            raise ValueError(
                "Class group conflict detected for the selected time slots"
            )

        if class_group_id is not None:
            timetable.class_group_id = class_group_id
        if attribution_id is not None:
            timetable.attribution_id = attribution_id
        if room_id is not None:
            timetable.room_id = room_id
        if start_date is not None:
            timetable.start_date = start_date
        if end_date is not None:
            timetable.end_date = end_date
        if status is not None:
            timetable.status = status

        timetable.save()

        if slot_ids is not None:
            timetable.slots.set(slot_ids)

        return timetable

    @staticmethod
    def publish_timetable(timetable_id):
        timetable = Timetable.objects.get(id=timetable_id)
        timetable.published_date = timezone.now()
        timetable.save()
        return timetable

    @staticmethod
    def get_timetables_by_class_group(class_group_id, academic_year_id=None):
        timetables = Timetable.objects.filter(class_group_id=class_group_id)

        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        return timetables.select_related(
            "class_group", "attribution", "room"
        ).prefetch_related("slots")

    @staticmethod
    def get_timetables_by_day(day_of_week, faculty_id, academic_year_id=None):
        timetables = Timetable.objects.filter(
            slots__day_of_week=day_of_week,
            class_group__class_fk__department__faculty_id=faculty_id,
        )

        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        return (
            timetables.distinct()
            .select_related("class_group", "attribution", "room")
            .prefetch_related("slots")
        )

    @staticmethod
    def get_timetables_by_class(class_id, academic_year_id=None):
        timetables = Timetable.objects.filter(class_group__class_fk_id=class_id)

        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        return timetables.select_related(
            "class_group", "attribution", "room"
        ).prefetch_related("slots")


class AttendanceManagementService:
    @staticmethod
    def create_attendance(timetable_id, student_id, status, remarks=None):
        if Attendance.objects.filter(
            timetable_id=timetable_id, student_id=student_id
        ).exists():
            raise ValueError("Attendance already exists for this student and timetable")

        attendance = Attendance.objects.create(
            timetable_id=timetable_id,
            student_id=student_id,
            status=status,
            remarks=remarks,
        )
        return attendance

    @staticmethod
    def bulk_create_attendance(timetable_id, attendance_data):
        timetable = Timetable.objects.get(id=timetable_id)
        class_group = timetable.class_group

        if not class_group:
            raise ValueError(
                "Timetable must have a class group to create bulk attendance"
            )

        Inscription.objects.filter(
            class_fk=class_group.class_fk,
            academic_year=class_group.academic_year,
            regist_status="Active",
        ).select_related("student")

        attendance_objects = []
        existing_attendance = set(
            Attendance.objects.filter(timetable_id=timetable_id).values_list(
                "student_id", flat=True
            )
        )

        for data in attendance_data:
            student_id = data.get("student_id")
            status = data.get("status", "Absent")
            remarks = data.get("remarks")

            if student_id not in existing_attendance:
                attendance_objects.append(
                    Attendance(
                        timetable_id=timetable_id,
                        student_id=student_id,
                        status=status,
                        remarks=remarks,
                    )
                )

        Attendance.objects.bulk_create(attendance_objects)
        return len(attendance_objects)

    @staticmethod
    def update_attendance(attendance_id, status=None, remarks=None):
        attendance = Attendance.objects.get(id=attendance_id)

        if status is not None:
            attendance.status = status
        if remarks is not None:
            attendance.remarks = remarks

        attendance.save()
        return attendance

    @staticmethod
    def get_attendance_by_timetable(timetable_id):
        return Attendance.objects.filter(timetable_id=timetable_id).select_related(
            "student", "student__user"
        )

    @staticmethod
    def get_attendance_by_student(student_id, academic_year_id=None):
        attendances = Attendance.objects.filter(student_id=student_id)

        if academic_year_id:
            attendances = attendances.filter(
                timetable__class_group__academic_year_id=academic_year_id
            )

        return attendances.select_related("timetable", "timetable__attribution")

    @staticmethod
    def get_attendance_statistics(class_group_id, academic_year_id=None):
        timetables = Timetable.objects.filter(class_group_id=class_group_id)

        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        total_sessions = timetables.count()
        total_attendances = Attendance.objects.filter(timetable__in=timetables).count()

        present = Attendance.objects.filter(
            timetable__in=timetables, status="Present"
        ).count()
        absent = Attendance.objects.filter(
            timetable__in=timetables, status="Absent"
        ).count()
        excused = Attendance.objects.filter(
            timetable__in=timetables, status="Excused"
        ).count()

        attendance_rate = (
            round((present / total_attendances) * 100, 2)
            if total_attendances > 0
            else 0
        )

        return {
            "total_sessions": total_sessions,
            "total_attendances": total_attendances,
            "present": present,
            "absent": absent,
            "excused": excused,
            "attendance_rate": attendance_rate,
        }


class ActivityReportService:
    @staticmethod
    def create_or_update_report(
        timetable_id, planned_hours=None, delivered_hours=None, observations=None
    ):
        timetable = Timetable.objects.get(id=timetable_id)

        report, created = ActivityReport.objects.get_or_create(
            timetable=timetable,
            defaults={
                "planned_hours": planned_hours,
                "delivered_hours": delivered_hours,
                "observations": observations,
            },
        )

        if not created:
            if planned_hours is not None:
                report.planned_hours = planned_hours
            if delivered_hours is not None:
                report.delivered_hours = delivered_hours
            if observations is not None:
                report.observations = observations

        if report.planned_hours and report.delivered_hours:
            if report.planned_hours > 0:
                completion_rate = (report.delivered_hours / report.planned_hours) * 100
                report.completion_rate = round(min(completion_rate, 100), 2)
            else:
                report.completion_rate = 0

        report.save()
        return report, created

    @staticmethod
    def get_reports_by_attribution(attribution_id):
        timetables = Timetable.objects.filter(attribution_id=attribution_id)
        return ActivityReport.objects.filter(timetable__in=timetables).select_related(
            "timetable"
        )

    @staticmethod
    def get_reports_by_faculty(faculty_id, academic_year_id=None):
        timetables = Timetable.objects.filter(
            class_group__class_fk__department__faculty_id=faculty_id
        )

        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        return ActivityReport.objects.filter(timetable__in=timetables).select_related(
            "timetable", "timetable__attribution"
        )


class ClassGroupManagementService:
    @staticmethod
    def assign_student_to_group(student_id, class_group_id):
        student = Student.objects.get(id=student_id)
        class_group = ClassGroup.objects.get(id=class_group_id)

        inscription = Inscription.objects.filter(
            student=student,
            class_fk=class_group.class_fk,
            academic_year=class_group.academic_year,
        ).first()

        if not inscription:
            raise ValueError(
                "Student does not have an inscription for this class and academic year"
            )

        return {"student_id": str(student.id), "class_group_id": str(class_group.id)}

    @staticmethod
    def move_student_between_groups(student_id, from_group_id, to_group_id):
        student = Student.objects.get(id=student_id)
        from_group = ClassGroup.objects.get(id=from_group_id)
        to_group = ClassGroup.objects.get(id=to_group_id)

        if from_group.academic_year != to_group.academic_year:
            raise ValueError("Cannot move student between different academic years")

        if from_group.class_fk != to_group.class_fk:
            raise ValueError("Cannot move student between groups of different classes")

        return {
            "student_id": str(student.id),
            "from_group_id": str(from_group.id),
            "to_group_id": str(to_group.id),
        }

    @staticmethod
    def get_students_in_group(class_group_id):
        class_group = ClassGroup.objects.get(id=class_group_id)

        inscriptions = Inscription.objects.filter(
            class_fk=class_group.class_fk,
            academic_year=class_group.academic_year,
            regist_status="Active",
        ).select_related("student", "student__user")

        return inscriptions

    @staticmethod
    def bulk_assign_students(class_group_id, student_ids):
        class_group = ClassGroup.objects.get(id=class_group_id)

        inscriptions = Inscription.objects.filter(
            student_id__in=student_ids,
            class_fk=class_group.class_fk,
            academic_year=class_group.academic_year,
            regist_status="Active",
        )

        if inscriptions.count() != len(student_ids):
            raise ValueError(
                "Some students do not have valid inscriptions for this class group"
            )

        return {
            "class_group_id": str(class_group.id),
            "assigned_count": len(student_ids),
        }


class ExamService:
    @staticmethod
    def create_exam(
        course_id,
        exam_type_id,
        academic_year_id,
        exam_date,
        start_time,
        end_time,
        created_by,
    ):
        from django.db import transaction

        with transaction.atomic():
            exam = Exam.objects.create(
                course_id=course_id,
                exam_type_id=exam_type_id,
                academic_year_id=academic_year_id,
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time,
                status="scheduled",
                created_by=created_by,
            )
            return exam

    @staticmethod
    def update_exam_status(exam_id, status):
        valid_transitions = {
            "scheduled": ["in_progress", "cancelled"],
            "in_progress": ["completed", "cancelled"],
            "completed": [],
            "cancelled": [],
        }

        exam = Exam.objects.get(id=exam_id)
        current_status = exam.status

        if status not in valid_transitions.get(current_status, []):
            raise ValueError(
                f"Invalid status transition from {current_status} to {status}"
            )

        exam.status = status
        exam.save()
        return exam

    @staticmethod
    def get_exams_by_faculty(faculty_id, academic_year_id=None):
        exams = Exam.objects.filter(
            course__module__class_fk__department__faculty_id=faculty_id
        )

        if academic_year_id:
            exams = exams.filter(academic_year_id=academic_year_id)

        return exams.select_related(
            "course", "exam_type", "academic_year", "created_by"
        ).prefetch_related("rooms")

    @staticmethod
    def get_exams_by_course(course_id, academic_year_id=None):
        exams = Exam.objects.filter(course_id=course_id)

        if academic_year_id:
            exams = exams.filter(academic_year_id=academic_year_id)

        return exams.select_related("exam_type", "academic_year")


class ExamRoomService:
    @staticmethod
    def assign_rooms(exam_id, room_assignments):
        from django.db import transaction

        with transaction.atomic():
            exam = Exam.objects.get(id=exam_id)

            if exam.status not in ["scheduled"]:
                raise ValueError("Rooms can only be assigned to scheduled exams")

            exam_rooms = []
            for assignment in room_assignments:
                room_id = assignment.get("room_id")
                range_student = assignment.get("range_student")

                exam_room = ExamRoom.objects.create(
                    exam=exam, room_id=room_id, range_student=range_student
                )
                exam_rooms.append(exam_room)

            return exam_rooms

    @staticmethod
    def remove_room(exam_room_id):
        exam_room = ExamRoom.objects.get(id=exam_room_id)

        if exam_room.exam.status not in ["scheduled"]:
            raise ValueError("Cannot remove rooms from non-scheduled exams")

        exam_room.delete()

    @staticmethod
    def get_rooms_for_exam(exam_id):
        return ExamRoom.objects.filter(exam_id=exam_id).select_related(
            "room", "room__building"
        )


class ExamSupervisorService:
    @staticmethod
    def assign_supervisors(exam_room_id, supervisor_ids):
        from django.core.exceptions import ValidationError
        from django.db import transaction

        with transaction.atomic():
            exam_room = ExamRoom.objects.get(id=exam_room_id)

            if exam_room.exam.status not in ["scheduled"]:
                raise ValueError("Supervisors can only be assigned to scheduled exams")

            supervisors = []
            for supervisor_id in supervisor_ids:
                exam_supervisor = ExamSupervisor(
                    exam_room=exam_room, supervisor_id=supervisor_id
                )

                try:
                    exam_supervisor.clean()
                except ValidationError as e:
                    raise ValueError(str(e))

                exam_supervisor.save()
                supervisors.append(exam_supervisor)

            return supervisors

    @staticmethod
    def remove_supervisor(exam_supervisor_id):
        exam_supervisor = ExamSupervisor.objects.get(id=exam_supervisor_id)

        if exam_supervisor.exam_room.exam.status not in ["scheduled"]:
            raise ValueError("Cannot remove supervisors from non-scheduled exams")

        exam_supervisor.delete()

    @staticmethod
    def get_supervisors_for_exam_room(exam_room_id):
        return ExamSupervisor.objects.filter(exam_room_id=exam_room_id).select_related(
            "supervisor", "supervisor__user"
        )

    @staticmethod
    def check_supervisor_availability(supervisor_id, exam_date, start_time, end_time):
        conflicts = ExamSupervisor.objects.filter(
            supervisor_id=supervisor_id,
            exam_room__exam__exam_date=exam_date,
            exam_room__exam__start_time__lt=end_time,
            exam_room__exam__end_time__gt=start_time,
        )
        return not conflicts.exists()


class ResultEntryService:
    @staticmethod
    def enter_mark(course_id, inscription_id, session_id, mark):
        from django.db import transaction

        if mark < 0 or mark > 100:
            raise ValueError("Mark must be between 0 and 100")

        with transaction.atomic():
            result, created = Result.objects.update_or_create(
                course_id=course_id,
                inscription_id=inscription_id,
                session_id=session_id,
                defaults={"mark": mark},
            )
            return result, created

    @staticmethod
    def bulk_enter_marks(marks_data):
        from django.db import transaction

        results = []
        with transaction.atomic():
            for mark_data in marks_data:
                course_id = mark_data.get("course_id")
                inscription_id = mark_data.get("inscription_id")
                session_id = mark_data.get("session_id")
                mark = mark_data.get("mark")

                if mark < 0 or mark > 100:
                    raise ValueError(
                        f"Invalid mark {mark} for inscription {inscription_id}"
                    )

                result, created = Result.objects.update_or_create(
                    course_id=course_id,
                    inscription_id=inscription_id,
                    session_id=session_id,
                    defaults={"mark": mark},
                )
                results.append(result)

        return results

    @staticmethod
    def get_results_by_inscription(inscription_id):
        return Result.objects.filter(inscription_id=inscription_id).select_related(
            "course", "session"
        )

    @staticmethod
    def get_results_by_course(course_id, session_id=None):
        results = Result.objects.filter(course_id=course_id)

        if session_id:
            results = results.filter(session_id=session_id)

        return results.select_related("inscription", "inscription__student", "session")


class ResultCompilationService:
    @staticmethod
    def compile_results(inscription_id):
        from decimal import Decimal

        from django.db import transaction

        with transaction.atomic():
            results = Result.objects.filter(inscription_id=inscription_id)

            if not results.exists():
                raise ValueError("No results found for this inscription")

            total_marks = sum(result.mark for result in results)
            count = results.count()
            average_mark = Decimal(total_marks / count).quantize(Decimal("0.01"))

            status = ResultCompilationService._determine_status(average_mark, results)
            is_promoted = status == "passed"

            results_dict = {
                str(result.course.id): {
                    "course_name": result.course.course_name,
                    "session": result.session.session_name,
                    "mark": result.mark,
                }
                for result in results
            }

            compiled_result, created = CompiledResult.objects.update_or_create(
                inscription_id=inscription_id,
                defaults={
                    "results": results_dict,
                    "average_mark": average_mark,
                    "status": status,
                    "is_promoted": is_promoted,
                },
            )

            return compiled_result

    @staticmethod
    def _determine_status(average_mark, results):
        passing_threshold = 50
        min_course_threshold = 40

        if average_mark >= passing_threshold:
            failed_courses = [r for r in results if r.mark < min_course_threshold]
            if failed_courses:
                return "incomplete"
            return "passed"
        elif average_mark >= 45:
            return "repeat"
        else:
            return "failed"

    @staticmethod
    def get_compiled_results_by_class(class_id, academic_year_id):
        inscriptions = Inscription.objects.filter(
            class_fk_id=class_id, academic_year_id=academic_year_id
        )

        return CompiledResult.objects.filter(
            inscription__in=inscriptions
        ).select_related("inscription", "inscription__student")

    @staticmethod
    def get_promotion_statistics(class_id, academic_year_id):
        compiled_results = ResultCompilationService.get_compiled_results_by_class(
            class_id, academic_year_id
        )

        total = compiled_results.count()
        passed = compiled_results.filter(status="passed").count()
        failed = compiled_results.filter(status="failed").count()
        repeat = compiled_results.filter(status="repeat").count()
        incomplete = compiled_results.filter(status="incomplete").count()

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "repeat": repeat,
            "incomplete": incomplete,
            "pass_rate": round((passed / total * 100), 2) if total > 0 else 0,
        }


class SupplementService:
    @staticmethod
    def create_supplement(inscription_id, course_id):
        from django.db import transaction

        with transaction.atomic():
            compiled_result = CompiledResult.objects.filter(
                inscription_id=inscription_id
            ).first()

            if not compiled_result:
                raise ValueError("No compiled results found. Compile results first.")

            if compiled_result.status not in ["incomplete", "repeat"]:
                raise ValueError(
                    "Supplements can only be created for incomplete or repeat students"
                )

            supplement, created = Supplement.objects.get_or_create(
                inscription_id=inscription_id,
                course_id=course_id,
                defaults={"validation": False},
            )

            return supplement, created

    @staticmethod
    def validate_supplement(supplement_id, mark):
        from django.db import transaction
        from django.utils import timezone

        if mark < 0 or mark > 100:
            raise ValueError("Mark must be between 0 and 100")

        with transaction.atomic():
            supplement = Supplement.objects.get(id=supplement_id)
            supplement.mark = mark
            supplement.validation = mark >= 50
            supplement.validation_date = timezone.now().date()
            supplement.save()

            ResultCompilationService.compile_results(supplement.inscription_id)

            return supplement

    @staticmethod
    def get_supplements_by_inscription(inscription_id):
        return Supplement.objects.filter(inscription_id=inscription_id).select_related(
            "course"
        )

    @staticmethod
    def get_supplements_by_course(course_id):
        return Supplement.objects.filter(course_id=course_id).select_related(
            "inscription", "inscription__student"
        )


class JurySessionService:
    @staticmethod
    def create_jury_session(session_name, session_date, jury_member_ids, created_by):
        from django.db import transaction

        with transaction.atomic():
            jury_session = JurySession.objects.create(
                session_name=session_name,
                session_date=session_date,
                status="scheduled",
                created_by=created_by,
            )

            jury_session.jury_members.set(jury_member_ids)

            return jury_session

    @staticmethod
    def update_jury_status(jury_session_id, status):
        valid_transitions = {
            "scheduled": ["in_progress", "completed"],
            "in_progress": ["completed"],
            "completed": [],
        }

        jury_session = JurySession.objects.get(id=jury_session_id)
        current_status = jury_session.status

        if status not in valid_transitions.get(current_status, []):
            raise ValueError(
                f"Invalid status transition from {current_status} to {status}"
            )

        if status == "completed":
            decisions = JuryDecision.objects.filter(jury_session=jury_session)
            if not decisions.exists():
                raise ValueError("Cannot complete jury session without any decisions")

        jury_session.status = status
        jury_session.save()
        return jury_session

    @staticmethod
    def add_jury_member(jury_session_id, user_id):
        jury_session = JurySession.objects.get(id=jury_session_id)

        if jury_session.status != "scheduled":
            raise ValueError("Can only add jury members to scheduled sessions")

        jury_session.jury_members.add(user_id)
        return jury_session

    @staticmethod
    def get_jury_sessions_by_faculty(faculty_id):
        return JurySession.objects.filter(
            created_by__profiles__faculty_id=faculty_id
        ).prefetch_related("jury_members")


class JuryDecisionService:
    @staticmethod
    def validate_decision(jury_session_id, student_id, decision, notes, validated_by):
        from django.db import transaction

        jury_session = JurySession.objects.get(id=jury_session_id)

        if jury_session.status == "completed":
            raise ValueError("Cannot modify decisions for completed jury sessions")

        valid_decisions = ["admitted", "deferred", "repeat", "excluded"]
        if decision not in valid_decisions:
            raise ValueError(f"Invalid decision. Must be one of {valid_decisions}")

        with transaction.atomic():
            jury_decision, created = JuryDecision.objects.update_or_create(
                jury_session_id=jury_session_id,
                student_id=student_id,
                defaults={
                    "decision": decision,
                    "notes": notes,
                    "validated_by": validated_by,
                },
            )

            return jury_decision, created

    @staticmethod
    def get_decisions_by_jury_session(jury_session_id):
        return JuryDecision.objects.filter(
            jury_session_id=jury_session_id
        ).select_related("student", "student__user", "validated_by")

    @staticmethod
    def get_decisions_by_student(student_id):
        return JuryDecision.objects.filter(student_id=student_id).select_related(
            "jury_session", "validated_by"
        )


class GradeComplaintService:
    @staticmethod
    def create_complaint(student_id, course_id, original_grade, complaint_reason):
        from django.db import transaction

        with transaction.atomic():
            complaint = GradeComplaint.objects.create(
                student_id=student_id,
                course_id=course_id,
                original_grade=original_grade,
                complaint_reason=complaint_reason,
                status="submitted",
            )
            return complaint

    @staticmethod
    def assign_complaint(complaint_id, assigned_to_id):
        complaint = GradeComplaint.objects.get(id=complaint_id)

        if complaint.status != "submitted":
            raise ValueError("Can only assign submitted complaints")

        complaint.assigned_to_id = assigned_to_id
        complaint.status = "assigned"
        complaint.save()

        return complaint

    @staticmethod
    def update_complaint_status(complaint_id, status):
        valid_statuses = ["submitted", "assigned", "in_review", "resolved", "rejected"]

        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")

        complaint = GradeComplaint.objects.get(id=complaint_id)
        complaint.status = status
        complaint.save()

        return complaint

    @staticmethod
    def resolve_complaint(complaint_id, new_grade, resolution_notes, resolved_by):
        from django.db import transaction
        from django.utils import timezone

        with transaction.atomic():
            complaint = GradeComplaint.objects.get(id=complaint_id)

            if complaint.status not in ["assigned", "in_review"]:
                raise ValueError("Can only resolve assigned or in_review complaints")

            if new_grade < 0 or new_grade > 100:
                raise ValueError("New grade must be between 0 and 100")

            complaint.new_grade = new_grade
            complaint.resolution_notes = resolution_notes
            complaint.status = "resolved"
            complaint.resolved_at = timezone.now()
            complaint.save()

            return complaint

    @staticmethod
    def get_complaints_by_faculty(faculty_id, status=None):
        complaints = GradeComplaint.objects.filter(
            course__module__class_fk__department__faculty_id=faculty_id
        )

        if status:
            complaints = complaints.filter(status=status)

        return complaints.select_related(
            "student", "student__user", "course", "assigned_to"
        )

    @staticmethod
    def get_complaints_by_student(student_id):
        return GradeComplaint.objects.filter(student_id=student_id).select_related(
            "course", "assigned_to"
        )


class TeacherClaimService:
    @staticmethod
    def submit_claim(teacher_id, course_id, hours_taught, hourly_rate):
        from decimal import Decimal

        from django.db import transaction

        if hours_taught <= 0:
            raise ValueError("Hours taught must be greater than 0")

        if hourly_rate <= 0:
            raise ValueError("Hourly rate must be greater than 0")

        total_amount = Decimal(hours_taught) * Decimal(hourly_rate)

        with transaction.atomic():
            claim = TeacherPaymentClaim.objects.create(
                teacher_id=teacher_id,
                course_id=course_id,
                hours_taught=hours_taught,
                hourly_rate=hourly_rate,
                total_amount=total_amount,
                status="submitted",
            )
            return claim

    @staticmethod
    def verify_claim(claim_id, verified_by_id):
        from django.db import transaction
        from django.utils import timezone

        with transaction.atomic():
            claim = TeacherPaymentClaim.objects.get(id=claim_id)

            if claim.status != "submitted":
                raise ValueError("Can only verify submitted claims")

            claim.status = "verified"
            claim.verified_by_id = verified_by_id
            claim.processed_at = timezone.now()
            claim.save()

            return claim

    @staticmethod
    def approve_claim(claim_id, approved_by_id):
        from django.db import transaction

        with transaction.atomic():
            claim = TeacherPaymentClaim.objects.get(id=claim_id)

            if claim.status != "verified":
                raise ValueError("Can only approve verified claims")

            claim.status = "approved"
            claim.approved_by_id = approved_by_id
            claim.save()

            return claim

    @staticmethod
    def sign_claim(claim_id):
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status != "approved":
            raise ValueError("Can only sign approved claims")

        claim.status = "signed"
        claim.save()

        return claim

    @staticmethod
    def send_to_finance(claim_id):
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status != "signed":
            raise ValueError("Can only send signed claims to finance")

        claim.status = "sent_to_finance"
        claim.save()

        return claim

    @staticmethod
    def reject_claim(claim_id):
        claim = TeacherPaymentClaim.objects.get(id=claim_id)

        if claim.status in ["sent_to_finance"]:
            raise ValueError("Cannot reject claims that have been sent to finance")

        claim.status = "rejected"
        claim.save()

        return claim

    @staticmethod
    def get_claims_by_teacher(teacher_id):
        return TeacherPaymentClaim.objects.filter(teacher_id=teacher_id).select_related(
            "course", "verified_by", "approved_by"
        )

    @staticmethod
    def get_claims_by_faculty(faculty_id, status=None):
        claims = TeacherPaymentClaim.objects.filter(
            course__module__class_fk__department__faculty_id=faculty_id
        )

        if status:
            claims = claims.filter(status=status)

        return claims.select_related(
            "teacher", "teacher__user", "course", "verified_by", "approved_by"
        )
