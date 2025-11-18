from django.db.models import Avg, Count
from django.utils import timezone

from .models import (
    AcademicProgram,
    RoomAllocation,
    Schedule,
    SecretaryNote,
    StudentGroup,
    TeacherWorkload,
    TeachingProgress,
)


class DoyenDashboardService:
    @staticmethod
    def get_faculty_schedules(faculty):
        """Get all schedules for a faculty"""
        return Schedule.objects.filter(faculty=faculty).order_by("-created_date")

    @staticmethod
    def create_schedule(faculty, academic_year, semester, created_by):
        """Create a new schedule"""
        schedule, created = Schedule.objects.get_or_create(
            faculty=faculty,
            academic_year=academic_year,
            semester=semester,
            defaults={"created_by": created_by},
        )
        return schedule

    @staticmethod
    def publish_schedule(schedule):
        """Publish a schedule"""
        schedule.status = "published"
        schedule.published_date = timezone.now()
        schedule.save()
        return schedule

    @staticmethod
    def get_teaching_progress(faculty):
        """Get teaching progress for all courses in faculty"""
        return TeachingProgress.objects.filter(faculty=faculty).select_related(
            "attribution", "submitted_by"
        )

    @staticmethod
    def update_teaching_progress(
        attribution, faculty, progress_percentage, submitted_by
    ):
        """Update or create teaching progress"""
        progress, created = TeachingProgress.objects.update_or_create(
            attribution=attribution,
            faculty=faculty,
            defaults={
                "progress_percentage": progress_percentage,
                "submitted_by": submitted_by,
            },
        )
        return progress

    @staticmethod
    def get_teacher_workload(faculty, academic_year):
        """Get teacher workload for faculty"""
        return TeacherWorkload.objects.filter(
            faculty=faculty, academic_year=academic_year
        )

    @staticmethod
    def update_teacher_workload(
        faculty, teacher, academic_year, assigned_hours, is_permanent
    ):
        """Update or create teacher workload"""
        workload, created = TeacherWorkload.objects.update_or_create(
            faculty=faculty,
            teacher=teacher,
            academic_year=academic_year,
            defaults={
                "assigned_hours": assigned_hours,
                "is_permanent": is_permanent,
            },
        )
        return workload

    @staticmethod
    def create_student_group(faculty, group_name, academic_year):
        """Create a student group"""
        group = StudentGroup.objects.create(
            faculty=faculty,
            group_name=group_name,
            academic_year=academic_year,
        )
        return group

    @staticmethod
    def add_students_to_group(group, students):
        """Add students to a group"""
        group.students.add(*students)
        return group

    @staticmethod
    def get_academic_programs(faculty):
        """Get all academic programs for faculty"""
        return AcademicProgram.objects.filter(faculty=faculty).prefetch_related("units")

    @staticmethod
    def create_academic_program(faculty, program_name, level, description=None):
        """Create an academic program"""
        program = AcademicProgram.objects.create(
            faculty=faculty,
            program_name=program_name,
            level=level,
            description=description,
        )
        return program

    @staticmethod
    def allocate_room(schedule, faculty, room_name, capacity):
        """Allocate a room for schedule"""
        allocation = RoomAllocation.objects.create(
            schedule=schedule,
            faculty=faculty,
            room_name=room_name,
            capacity=capacity,
        )
        return allocation

    @staticmethod
    def create_secretary_note(faculty, subject, message, created_by):
        """Create a note for secretary"""
        note = SecretaryNote.objects.create(
            faculty=faculty,
            subject=subject,
            message=message,
            created_by=created_by,
        )
        return note

    @staticmethod
    def resolve_secretary_note(note):
        """Mark secretary note as resolved"""
        note.is_resolved = True
        note.save()
        return note

    @staticmethod
    def get_dashboard_stats(faculty):
        """Get dashboard statistics for faculty"""
        schedules = Schedule.objects.filter(faculty=faculty)
        teaching_progress = TeachingProgress.objects.filter(faculty=faculty)
        programs = AcademicProgram.objects.filter(faculty=faculty)
        secretary_notes = SecretaryNote.objects.filter(faculty=faculty)

        avg_progress = (
            teaching_progress.aggregate(Avg("progress_percentage"))[
                "progress_percentage__avg"
            ]
            or 0
        )

        return {
            "total_schedules": schedules.count(),
            "published_schedules": schedules.filter(status="published").count(),
            "teaching_progress_avg": round(avg_progress, 2),
            "total_teachers": TeacherWorkload.objects.filter(faculty=faculty)
            .values("teacher")
            .distinct()
            .count(),
            "total_students": StudentGroup.objects.filter(faculty=faculty).aggregate(
                Count("students", distinct=True)
            )["students__count"]
            or 0,
            "total_programs": programs.count(),
            "pending_secretary_notes": secretary_notes.filter(
                is_resolved=False
            ).count(),
        }
