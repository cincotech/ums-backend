from django.db.models import Avg, Count, Sum

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.scheduling_module.scheduling_app.models import (
    ActivityReport,
    Timetable,
)


class CourseManagementService:
    @staticmethod
    def get_faculty_courses(faculty_id, academic_year_id=None):
        """Get all courses for a faculty with attribution details"""
        courses = Course.objects.filter(
            module__class_fk__department__faculty_id=faculty_id
        ).distinct()

        if academic_year_id:
            courses = courses.filter(
                attribution__academic_year_id=academic_year_id
            ).distinct()

        return courses.select_related(
            "module", "module__class_fk", "module__class_fk__department"
        )

    @staticmethod
    def get_course_with_attributions(course_id, academic_year_id=None):
        """Get course with all its attributions"""
        course = Course.objects.get(id=course_id)
        attributions = Attribution.objects.filter(course=course)

        if academic_year_id:
            attributions = attributions.filter(academic_year_id=academic_year_id)

        return {
            "course": course,
            "attributions": attributions.select_related(
                "principal_teacher", "substitute_teacher", "academic_year"
            ),
        }

    @staticmethod
    def get_course_statistics(course_id, academic_year_id=None):
        """Get comprehensive statistics for a course"""
        course = Course.objects.get(id=course_id)
        attributions = Attribution.objects.filter(course=course)

        if academic_year_id:
            attributions = attributions.filter(academic_year_id=academic_year_id)

        total_attributions = attributions.count()
        accepted_attributions = attributions.filter(
            status_principal_teacher="Accepted"
        ).count()
        pending_attributions = attributions.filter(
            status_principal_teacher="Pending"
        ).count()

        # Get timetables for this course
        timetables = Timetable.objects.filter(attribution__course=course)
        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        total_timetables = timetables.count()
        published_timetables = timetables.filter(published_date__isnull=False).count()

        # Get activity reports
        activity_reports = ActivityReport.objects.filter(timetable__in=timetables)
        total_planned_hours = sum(
            r.planned_hours for r in activity_reports if r.planned_hours
        )
        total_delivered_hours = sum(
            r.delivered_hours for r in activity_reports if r.delivered_hours
        )

        avg_completion_rate = (
            activity_reports.aggregate(avg=Avg("completion_rate"))["avg"] or 0
        )

        # Get students enrolled
        total_students = Inscription.objects.filter(
            class_fk__module__course=course,
            regist_status="Active",
        ).count()

        return {
            "course_id": str(course.id),
            "course_name": course.course_name,
            "course_code": course.course_code,
            "credits": course.credits,
            "total_attributions": total_attributions,
            "accepted_attributions": accepted_attributions,
            "pending_attributions": pending_attributions,
            "total_timetables": total_timetables,
            "published_timetables": published_timetables,
            "total_planned_hours": total_planned_hours,
            "total_delivered_hours": total_delivered_hours,
            "avg_completion_rate": round(avg_completion_rate, 2),
            "total_students": total_students,
        }

    @staticmethod
    def get_course_by_class(class_id, academic_year_id=None):
        """Get all courses assigned to a class"""
        courses = Course.objects.filter(module__class_fk_id=class_id).distinct()

        # if academic_year_id:
        #     courses = courses.filter(
        #         attribution__academic_year_id=academic_year_id
        #     ).distinct()

        course_list = []
        for course in courses:
            attributions = Attribution.objects.filter(course=course)
            if academic_year_id:
                attributions = attributions.filter(academic_year_id=academic_year_id)

            course_list.append(
                {
                    "id": str(course.id),
                    "course_name": course.course_name,
                    "course_code": course.course_code,
                    "credits": course.credits,
                    "attribution_count": attributions.count(),
                    "teachers": [
                        {
                            "id": str(attr.principal_teacher.id),
                            "name": f"{attr.principal_teacher.user.first_name} {attr.principal_teacher.user.last_name}",
                            "status": attr.status_principal_teacher,
                        }
                        for attr in attributions
                    ],
                }
            )

        return course_list

    @staticmethod
    def get_course_by_teacher(teacher_id, academic_year_id=None):
        """Get all courses taught by a teacher"""
        attributions = Attribution.objects.filter(principal_teacher_id=teacher_id)

        if academic_year_id:
            attributions = attributions.filter(academic_year_id=academic_year_id)

        courses = []
        for attr in attributions:
            course = attr.course
            timetables = Timetable.objects.filter(attribution=attr)
            total_hours = sum(
                r.delivered_hours
                for r in ActivityReport.objects.filter(timetable__in=timetables)
                if r.delivered_hours
            )

            courses.append(
                {
                    "id": str(course.id),
                    "course_name": course.course_name,
                    "course_code": course.course_code,
                    "credits": course.credits,
                    "attribution_id": str(attr.id),
                    "status": attr.status_principal_teacher,
                    "delivered_hours": total_hours,
                    "class_name": course.module.class_fk.class_name,
                }
            )

        return courses

    @staticmethod
    def get_course_enrollment(course_id, academic_year_id=None):
        """Get enrollment statistics for a course"""
        course = Course.objects.get(id=course_id)

        inscriptions = Inscription.objects.filter(
            class_fk__module__course=course,
            regist_status="Active",
        )

        if academic_year_id:
            inscriptions = inscriptions.filter(academic_year_id=academic_year_id)

        total_enrolled = inscriptions.count()
        male_count = inscriptions.filter(student__user__gender="M").count()
        female_count = inscriptions.filter(student__user__gender="F").count()

        by_class = list(
            inscriptions.values("class_fk__class_name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return {
            "course_id": str(course.id),
            "course_name": course.course_name,
            "total_enrolled": total_enrolled,
            "male": male_count,
            "female": female_count,
            "by_class": by_class,
        }

    @staticmethod
    def get_course_performance(course_id, academic_year_id=None):
        """Get performance metrics for a course"""
        from services.dependent_service.exam_module.result_app.models import Result

        course = Course.objects.get(id=course_id)

        results = Result.objects.filter(course=course)
        if academic_year_id:
            results = results.filter(inscription__academic_year_id=academic_year_id)

        total_results = results.count()
        if total_results == 0:
            return {
                "course_id": str(course.id),
                "course_name": course.course_name,
                "total_results": 0,
                "average_mark": 0,
                "pass_rate": 0,
                "fail_rate": 0,
            }

        avg_mark = results.aggregate(avg=Avg("mark"))["avg"] or 0
        passed = results.filter(mark__gte=50).count()
        failed = results.filter(mark__lt=50).count()

        return {
            "course_id": str(course.id),
            "course_name": course.course_name,
            "total_results": total_results,
            "average_mark": round(avg_mark, 2),
            "pass_rate": round((passed / total_results) * 100, 2),
            "fail_rate": round((failed / total_results) * 100, 2),
        }

    @staticmethod
    def get_course_timetables(course_id, academic_year_id=None):
        """Get all timetables for a course"""
        timetables = Timetable.objects.filter(attribution__course_id=course_id)

        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        return timetables.select_related(
            "class_group", "attribution", "room"
        ).prefetch_related("slots")

    @staticmethod
    def get_course_activity_reports(course_id, academic_year_id=None):
        """Get all activity reports for a course"""
        timetables = Timetable.objects.filter(attribution__course_id=course_id)

        if academic_year_id:
            timetables = timetables.filter(
                class_group__academic_year_id=academic_year_id
            )

        reports = ActivityReport.objects.filter(timetable__in=timetables)

        report_list = []
        for report in reports:
            report_list.append(
                {
                    "id": str(report.id),
                    "timetable_id": str(report.timetable.id),
                    "class_group": (
                        report.timetable.class_group.group_name
                        if report.timetable.class_group
                        else None
                    ),
                    "planned_hours": report.planned_hours,
                    "delivered_hours": report.delivered_hours,
                    "completion_rate": (
                        float(report.completion_rate) if report.completion_rate else 0
                    ),
                    "observations": report.observations,
                }
            )

        return report_list

    @staticmethod
    def get_course_summary(faculty_id, academic_year_id=None):
        """Get summary of all courses in a faculty"""
        courses = Course.objects.filter(
            module__class_fk__department__faculty_id=faculty_id
        ).distinct()

        if academic_year_id:
            courses = courses.filter(
                attribution__academic_year_id=academic_year_id
            ).distinct()

        summary = {
            "total_courses": courses.count(),
            "total_credits": courses.aggregate(total=Sum("credits"))["total"] or 0,
            "courses_with_attribution": Attribution.objects.filter(course__in=courses)
            .values("course")
            .distinct()
            .count(),
            "courses_without_attribution": courses.exclude(
                id__in=Attribution.objects.filter(course__in=courses).values_list(
                    "course_id", flat=True
                )
            ).count(),
        }

        return summary

    @staticmethod
    def get_course_attribution_status(course_id, academic_year_id=None):
        """Get detailed attribution status for a course"""
        attributions = Attribution.objects.filter(course_id=course_id)

        if academic_year_id:
            attributions = attributions.filter(academic_year_id=academic_year_id)

        status_breakdown = {
            "pending": attributions.filter(status_principal_teacher="Pending").count(),
            "accepted": attributions.filter(
                status_principal_teacher="Accepted"
            ).count(),
            "refused": attributions.filter(status_principal_teacher="Refused").count(),
            "with_substitute": attributions.filter(
                substitute_teacher__isnull=False
            ).count(),
        }

        return {
            "course_id": str(course_id),
            "total_attributions": attributions.count(),
            "status_breakdown": status_breakdown,
            "attributions": [
                {
                    "id": str(attr.id),
                    "principal_teacher": f"{attr.principal_teacher.user.first_name} {attr.principal_teacher.user.last_name}",
                    "substitute_teacher": (
                        f"{attr.substitute_teacher.user.first_name} {attr.substitute_teacher.user.last_name}"
                        if attr.substitute_teacher
                        else None
                    ),
                    "status": attr.status_principal_teacher,
                    "academic_year": attr.academic_year.year_name,
                }
                for attr in attributions
            ],
        }
