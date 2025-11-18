from django.contrib import admin

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


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("faculty", "academic_year", "semester", "status", "created_date")
    list_filter = ("status", "academic_year", "semester")
    search_fields = ("faculty__faculty_name",)


@admin.register(TeachingProgress)
class TeachingProgressAdmin(admin.ModelAdmin):
    list_display = ("faculty", "progress_percentage", "last_updated")
    list_filter = ("faculty", "progress_percentage")


@admin.register(TeacherWorkload)
class TeacherWorkloadAdmin(admin.ModelAdmin):
    list_display = (
        "faculty",
        "teacher",
        "academic_year",
        "assigned_hours",
        "is_permanent",
    )
    list_filter = ("faculty", "academic_year", "is_permanent")
    search_fields = ("teacher__first_name", "teacher__last_name")


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ("faculty", "group_name", "academic_year", "created_date")
    list_filter = ("faculty", "academic_year")
    search_fields = ("group_name",)


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ("faculty", "program_name", "level", "created_date")
    list_filter = ("faculty", "level")
    search_fields = ("program_name",)


@admin.register(TeachingUnit)
class TeachingUnitAdmin(admin.ModelAdmin):
    list_display = ("program", "course", "credits", "semester")
    list_filter = ("program", "semester")


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ("faculty", "room_name", "capacity", "allocated_date")
    list_filter = ("faculty", "allocated_date")
    search_fields = ("room_name",)


@admin.register(SecretaryNote)
class SecretaryNoteAdmin(admin.ModelAdmin):
    list_display = ("faculty", "subject", "created_by", "created_date", "is_resolved")
    list_filter = ("faculty", "is_resolved", "created_date")
    search_fields = ("subject", "message")
