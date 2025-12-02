from django.urls import include, path
from rest_framework.routers import DefaultRouter

from services.core_service.student_module.card_app.views import (
    StudentCardLogViewSet,
    StudentCardViewSet,
)
from services.core_service.student_module.highschool_info_app.views import (
    CertificateViewSet,
    HighschoolViewSet,
    OptionViewSet,
    SectionViewSet,
    TrainingCenterViewSet,
)
from services.core_service.student_module.inscription_app.views import (
    InscriptionViewSet,
)
from services.core_service.student_module.parent_app.views import (
    ParentViewSet,
    ProfessionViewSet,
)
from services.core_service.student_module.student_profile_app.comprehensive_views import (
    StudentCreateAPIView,
    StudentSiblingsAPIView,
)
from services.core_service.student_module.student_profile_app.views import (
    StudentGraduateInfoViewSet,
    StudentHsInfoViewSet,
    StudentViewSet,
    TrainingViewSet,
)

router = DefaultRouter()
router.register(r"professions", ProfessionViewSet, basename="profession")
router.register(r"parents", ParentViewSet, basename="parent")

router.register(r"highschools", HighschoolViewSet, basename="highschool")
router.register(r"sections", SectionViewSet, basename="section")
router.register(r"certificates", CertificateViewSet, basename="certificate")
router.register(r"options", OptionViewSet, basename="option")
router.register(r"training-centers", TrainingCenterViewSet, basename="trainingcenter")

router.register(r"students", StudentViewSet, basename="student")
router.register(r"trainings", TrainingViewSet, basename="training")
router.register(r"student-hs-info", StudentHsInfoViewSet, basename="studenthsinfo")
router.register(
    r"student-graduate-info", StudentGraduateInfoViewSet, basename="studentgraduateinfo"
)

router.register(r"inscriptions", InscriptionViewSet, basename="inscription")

router.register(r"student-cards", StudentCardViewSet, basename="student-card")
router.register(
    r"student-card-logs", StudentCardLogViewSet, basename="student-card-log"
)


urlpatterns = [
    path("student/", include(router.urls)),
    path("student/create/", StudentCreateAPIView.as_view(), name="student-create"),
    path(
        "student/<str:matricule>/siblings/",
        StudentSiblingsAPIView.as_view(),
        name="student-siblings",
    ),
]
