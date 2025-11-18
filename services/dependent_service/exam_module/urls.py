from attendance_app.views import ExamAttendanceViewSet
from django.urls import include, path
from exam_app.views import (
    ExamRoomViewSet,
    ExamSupervisorViewSet,
    ExamTypeViewSet,
    ExamViewSet,
)
from rest_framework.routers import DefaultRouter
from result_app.views import (
    CompiledResultViewSet,
    ResultViewSet,
    SessionViewSet,
    SupplementViewSet,
)

router = DefaultRouter()
router.register(r"exam-types", ExamTypeViewSet, basename="exam-type")
router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"exam-rooms", ExamRoomViewSet, basename="exam-room")
router.register(r"exam-supervisors", ExamSupervisorViewSet, basename="exam-supervisor")
router.register(r"exam-attendances", ExamAttendanceViewSet, basename="exam-attendance")
router.register(r"sessions", SessionViewSet, basename="session")
router.register(r"results", ResultViewSet, basename="result")
router.register(r"compiled-results", CompiledResultViewSet, basename="compiled-result")
router.register(r"supplements", SupplementViewSet, basename="supplement")

urlpatterns = [
    path("", include(router.urls)),
]
