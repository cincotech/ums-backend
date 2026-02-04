from rest_framework.routers import DefaultRouter

from services.core_service.academic_module.class_app.views import ClassViewSet
from services.core_service.academic_module.course_app.views import CourseViewSet
from services.core_service.academic_module.department_app.views import DepartmentViewSet
from services.core_service.academic_module.faculty_app.views import (
    FacultyViewSet,
    TypeFormationViewSet,
)
from services.core_service.academic_module.module_app.views import ModuleViewSet
from services.core_service.academic_module.public_app.views import (
    AcademicTeamViewSet,
    ProgramViewSet,
)
from services.core_service.academic_module.teacher_app.views import (
    AttributionViewSet,
    SuggestionViewSet,
    TeacherViewSet,
)
from services.core_service.academic_module.university_app.views import (
    AcademicYearViewSet,
    UniversityDegreeViewSet,
    UniversityViewSet,
)

router = DefaultRouter()
router.register(r"programs", ProgramViewSet, basename="programs")
router.register(r"academic-team", AcademicTeamViewSet, basename="academic-team")
router.register(r"typeformations", TypeFormationViewSet, basename="typeformations")
router.register(r"faculties", FacultyViewSet, basename="faculties")
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("universities", UniversityViewSet, basename="university")
router.register("degrees", UniversityDegreeViewSet, basename="university-degree")

router.register(r"typeformations", TypeFormationViewSet, basename="typeformation")
router.register(r"faculties", FacultyViewSet, basename="faculty")

router.register(r"departments", DepartmentViewSet, basename="department")

router.register(r"classes", ClassViewSet, basename="class")

router.register(r"modules", ModuleViewSet, basename="module")

router.register(r"courses", CourseViewSet, basename="course")

router.register(r"teachers", TeacherViewSet, basename="teacher")
router.register(r"attributions", AttributionViewSet, basename="attribution")
router.register(r"suggestions", SuggestionViewSet, basename="suggestion")


urlpatterns = router.urls
