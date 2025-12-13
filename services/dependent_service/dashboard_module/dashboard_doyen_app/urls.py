from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttributionStatisticsView,
    ClassGroupViewSet,
    ClassViewSet,
    CourseAttributionViewSet,
    DeanDashboardStatsView,
    DepartmentViewSet,
    FacultyOverviewView,
    InscriptionViewSet,
    RoomUtilizationReportView,
    SecretaryNoteViewSet,
    StudentViewSet,
    TeacherWorkloadViewSet,
    TeachingProgressReportView,
    TeachingProgressViewSet,
    TimetableOverviewView,
)

router = DefaultRouter()
router.register(r"teaching-progress", TeachingProgressViewSet)
router.register(r"teacher-workload", TeacherWorkloadViewSet)
router.register(r"secretary-notes", SecretaryNoteViewSet)
router.register(r"course-attributions", CourseAttributionViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"classes", ClassViewSet)
router.register(r"class-groups", ClassGroupViewSet)
router.register(r"students", StudentViewSet)
router.register(r"inscriptions", InscriptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("stats/", DeanDashboardStatsView.as_view(), name="dean-dashboard-stats"),
    path(
        "faculty/overview/",
        FacultyOverviewView.as_view(),
        name="faculty-overview",
    ),
    path(
        "timetable/overview/",
        TimetableOverviewView.as_view(),
        name="timetable-overview",
    ),
    path(
        "reports/teaching-progress/",
        TeachingProgressReportView.as_view(),
        name="teaching-progress-report",
    ),
    path(
        "stats/attributions/",
        AttributionStatisticsView.as_view(),
        name="attribution-statistics",
    ),
    path(
        "reports/room-utilization/",
        RoomUtilizationReportView.as_view(),
        name="room-utilization-report",
    ),
]
