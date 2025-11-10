# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin

from .models import ActivityReport, Attendance, ScheduleSlot, Timetable

# ----------------------------
# Resources for Import/Export
# ----------------------------


class ScheduleSlotResource(resources.ModelResource):
    class Meta:
        model = ScheduleSlot
        fields = ("id", "day_of_week", "start_time", "end_time", "schedule_name")
        export_order = ("id", "day_of_week", "start_time", "end_time", "schedule_name")


class TimetableResource(resources.ModelResource):
    class Meta:
        model = Timetable
        fields = ("id", "attribution", "room", "start_date", "end_date", "status")
        export_order = ("id", "attribution", "room", "start_date", "end_date", "status")


class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance
        fields = ("id", "timetable", "student", "status", "remarks")
        export_order = ("id", "timetable", "student", "status", "remarks")


class ActivityReportResource(resources.ModelResource):
    class Meta:
        model = ActivityReport
        fields = (
            "id",
            "timetable",
            "planned_hours",
            "delivered_hours",
            "completion_rate",
            "observations",
        )
        export_order = (
            "id",
            "timetable",
            "planned_hours",
            "delivered_hours",
            "completion_rate",
            "observations",
        )


# ----------------------------
# Admin Classes
# ----------------------------


@admin.register(ScheduleSlot)
class ScheduleSlotAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ScheduleSlotResource
    list_display = ("day_of_week", "start_time", "end_time", "schedule_name")
    list_filter = ("day_of_week",)
    search_fields = ("schedule_name",)
    ordering = ("day_of_week",)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
        models.TimeField: {"widget": admin.widgets.AdminTimeWidget()},
    }


@admin.register(Timetable)
class TimetableAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = TimetableResource
    list_display = ("attribution", "room", "start_date", "end_date", "status")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("attribution__id", "room__room_name")
    ordering = ("-start_date",)


@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = AttendanceResource
    list_display = ("timetable", "student", "status")
    list_filter = ("status",)
    search_fields = ("student__user__email",)
    ordering = ("timetable",)


@admin.register(ActivityReport)
class ActivityReportAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ActivityReportResource
    list_display = ("timetable", "planned_hours", "delivered_hours", "completion_rate")
    search_fields = ("timetable__id",)
    ordering = ("timetable",)
