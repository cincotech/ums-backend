from django.db.models import Avg, Count, Q, Sum

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
from services.dependent_service.scheduling_module.scheduling_app.models import Timetable

from .models import SecretaryNote, TeacherWorkload, TeachingProgress


class DeanDashboardService:
    @staticmethod
    def get_dashboard_statistics(faculty_id, academic_year_id=None):
        faculty = Faculty.objects.get(id=faculty_id)

        if academic_year_id:
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
            inscriptions__class_fk__department__faculty=faculty
        )

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
