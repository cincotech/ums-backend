from django.urls import path

from services.dependent_service.scheduling_module.scheduling_app.views import (
    ActivityReportListCreateAPIView,
    AttendanceListCreateAPIView,
    ScheduleSlotListCreateAPIView,
    TimetableListCreateAPIView,
)

urlpatterns = [
    path("slots/", ScheduleSlotListCreateAPIView.as_view(), name="slots_list_create"),
    path(
        "timetables/",
        TimetableListCreateAPIView.as_view(),
        name="timetables_list_create",
    ),
    path(
        "attendances/",
        AttendanceListCreateAPIView.as_view(),
        name="attendances_list_create",
    ),
    path(
        "reports/",
        ActivityReportListCreateAPIView.as_view(),
        name="reports_list_create",
    ),
]
