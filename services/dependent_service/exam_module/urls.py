from django.urls import include, path
from exam_app.views import (
    ExamRoomViewSet,
    ExamSupervisorViewSet,
    ExamTypeViewSet,
    ExamViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"exam-types", ExamTypeViewSet, basename="exam-type")
router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"exam-rooms", ExamRoomViewSet, basename="exam-room")
router.register(r"exam-supervisors", ExamSupervisorViewSet, basename="exam-supervisor")

urlpatterns = [
    path("", include(router.urls)),
]
