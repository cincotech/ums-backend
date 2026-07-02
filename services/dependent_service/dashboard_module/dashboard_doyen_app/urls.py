from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .course_management_views import CourseByTeacherView, CourseViewSet
from .timetable_v2_views import (
    CourseSessionViewSet,
    TemplateEntryViewSet,
    TimetableTemplateViewSet,
)
from .views import (
    ActivityReportViewSet,
    AttendanceViewSet,
    AttributionStatisticsView,
    ClassGroupViewSet,
    ClassViewSet,
    ComplementRequirementViewSet,
    CompiledResultViewSet,
    CourseAttributionViewSet,
    DeanDashboardStatsView,
    DepartmentViewSet,
    ExamRoomViewSet,
    ExamSupervisorViewSet,
    ExamTypeViewSet,
    ExamViewSet,
    FacultyOverviewView,
    FeesSheetListView,
    GradeComplaintViewSet,
    InscriptionViewSet,
    JuryDecisionViewSet,
    JurySessionViewSet,
    ResultViewSet,
    RoomUtilizationReportView,
    ScheduleSlotViewSet,
    SecretaryNoteViewSet,
    SessionViewSet,
    StudentViewSet,
    SupplementViewSet,
    TeacherPaymentClaimViewSet,
    TeacherWorkloadViewSet,
    TeachingProgressReportView,
    TeachingProgressViewSet,
    TimetableMergeViewSet,
    TimetableOverviewView,
    TimetableViewSet,
)

router = DefaultRouter()
# Teaching Progress & Workload
router.register(r"teaching-progress", TeachingProgressViewSet)
router.register(r"teacher-workload", TeacherWorkloadViewSet)
router.register(r"secretary-notes", SecretaryNoteViewSet)
router.register(r"course-attributions", CourseAttributionViewSet, basename="course-attribution")

# Course Management
router.register(r"courses", CourseViewSet)

# Academic Structure
router.register(r"departments", DepartmentViewSet)
router.register(r"classes", ClassViewSet)
router.register(r"class-groups", ClassGroupViewSet, basename="class-group")
router.register(r"students", StudentViewSet)
router.register(r"inscriptions", InscriptionViewSet)

# Timetable & Attendance (legacy)
router.register(r"schedule-slots", ScheduleSlotViewSet)
router.register(r"timetables", TimetableViewSet)
router.register(r"attendances", AttendanceViewSet)
router.register(r"activity-reports", ActivityReportViewSet)
router.register(r"timetable-merges", TimetableMergeViewSet)

# Timetable v2 — grilles + séances réelles
router.register(r"timetable-templates", TimetableTemplateViewSet, basename="timetable-template")
router.register(r"template-entries", TemplateEntryViewSet, basename="template-entry")
router.register(r"course-sessions", CourseSessionViewSet, basename="course-session")

# Exam Management
router.register(r"exam-types", ExamTypeViewSet)
router.register(r"exams", ExamViewSet)
router.register(r"exam-rooms", ExamRoomViewSet)
router.register(r"exam-supervisors", ExamSupervisorViewSet)

# Result Management
router.register(r"sessions", SessionViewSet)
router.register(r"results", ResultViewSet)
router.register(r"compiled-results", CompiledResultViewSet)
router.register(r"supplements", SupplementViewSet)

# Jury Management
router.register(r"jury-sessions", JurySessionViewSet)
router.register(r"jury-decisions", JuryDecisionViewSet)
router.register(r"complement-requirements", ComplementRequirementViewSet)
router.register(r"grade-complaints", GradeComplaintViewSet)

# Teacher Payment Claims
router.register(r"teacher-payment-claims", TeacherPaymentClaimViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("fees-sheets/", FeesSheetListView.as_view(), name="fees-sheets-list"),
    path("stats/", DeanDashboardStatsView.as_view(), name="dean-dashboard-stats"),
    path(
        "faculty/overview/",
        FacultyOverviewView.as_view(),
        name="faculty-overview",
    ),
    path(
        "timetables/stats/",
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
    # path(
    #     "courses/by_class/",
    #     CourseByClassView.as_view(),
    #     name="courses-by-class",
    # ),
    path(
        "courses/by_teacher/",
        CourseByTeacherView.as_view(),
        name="courses-by-teacher",
    ),
]
