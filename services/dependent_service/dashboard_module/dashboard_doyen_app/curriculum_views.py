from django.db.models import Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter

from core.permissions import IsDean
from core.response_handler import success_response, validate_serializer
from core.views import BaseViewSet
from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.module_app.models import Module, Semester
from services.core_service.academic_module.public_app.models import Program
from services.search.backends import TypesenseFilterBackend

from .curriculum_serializers import (
    CurriculumCourseOrderSerializer,
    CurriculumCourseSerializer,
    CurriculumDuplicateSerializer,
    CurriculumStructureSerializer,
    CurriculumTeachingUnitOrderSerializer,
    CurriculumTeachingUnitSerializer,
    CurriculumTemplateListSerializer,
    CurriculumTemplateSerializer,
)
from .curriculum_services import CurriculumStructureService, CurriculumTemplateService
from .models import CurriculumCourse, CurriculumTeachingUnit, CurriculumTemplate
from .utils import get_faculty_for_request


class CurriculumTemplateViewSet(BaseViewSet):
    permission_classes = [IsDean]
    filter_backends = [DjangoFilterBackend, TypesenseFilterBackend, OrderingFilter]
    filterset_fields = ["program", "class_fk", "academic_year", "semester", "status"]
    search_fields = [
        "title",
        "class_fk__class_name",
        "program__faculty__faculty_name",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "version",
        "semester__number",
        "class_fk__level",
    ]

    def get_queryset(self):
        faculty = get_faculty_for_request(self.request)
        queryset = (
            CurriculumTemplate.objects.filter(
                class_fk__department__faculty=faculty,
                program__faculty=faculty,
            )
            .select_related(
                "program",
                "program__faculty",
                "class_fk",
                "class_fk__department",
                "academic_year",
                "semester",
                "created_by",
                "published_by",
            )
            .prefetch_related(
                "teaching_units__module",
                "teaching_units__module__semester",
                "teaching_units__curriculum_courses__course",
            )
            .annotate(
                teaching_unit_count=Count("teaching_units", distinct=True),
                course_count=Count("teaching_units__curriculum_courses", distinct=True),
                total_credits=Sum(
                    "teaching_units__curriculum_courses__course__credits"
                ),
            )
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CurriculumTemplateListSerializer
        return CurriculumTemplateSerializer

    def perform_create(self, serializer):
        faculty = get_faculty_for_request(self.request)
        program = serializer.validated_data["program"]
        class_fk = serializer.validated_data["class_fk"]
        if (
            program.faculty_id != faculty.id
            or class_fk.department.faculty_id != faculty.id
        ):
            raise PermissionDenied(
                "Vous ne pouvez créer une maquette que pour votre faculté."
            )
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        self._ensure_draft(self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="validate")
    def validate_template(self, request, pk=None):
        template = self.get_object()
        return success_response(
            data=CurriculumTemplateService.validate(template),
            message="Validation de la maquette terminée.",
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        template = CurriculumTemplateService.publish(self.get_object(), request.user)
        return success_response(
            data=CurriculumTemplateSerializer(
                template, context={"request": request}
            ).data,
            message="La maquette a été publiée.",
        )

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        serializer = CurriculumDuplicateSerializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        duplicate = CurriculumTemplateService.duplicate(
            self.get_object(),
            request.user,
            serializer.validated_data.get("academic_year"),
        )
        return success_response(
            data=CurriculumTemplateSerializer(
                duplicate, context={"request": request}
            ).data,
            message="Une nouvelle version brouillon a été créée.",
        )

    @action(detail=True, methods=["post"], url_path="reorder-teaching-units")
    def reorder_teaching_units(self, request, pk=None):
        template = self.get_object()
        self._ensure_draft(template)
        serializer = CurriculumTeachingUnitOrderSerializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        CurriculumStructureService.reorder_teaching_units(
            template, serializer.validated_data["teaching_unit_ids"]
        )
        return self._template_response(template, request, "Ordre des UE mis à jour.")

    @action(detail=True, methods=["post"], url_path="reorder-courses")
    def reorder_courses(self, request, pk=None):
        template = self.get_object()
        self._ensure_draft(template)
        serializer = CurriculumCourseOrderSerializer(data=request.data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        CurriculumStructureService.reorder_courses(
            template, serializer.validated_data["teaching_units"]
        )
        return self._template_response(template, request, "Ordre des ECUE mis à jour.")

    @action(detail=True, methods=["put"], url_path="structure")
    def save_structure(self, request, pk=None):
        template = self.get_object()
        self._ensure_draft(template)
        serializer = CurriculumStructureSerializer(
            data=request.data, context={"template": template}
        )
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error
        CurriculumStructureService.replace_structure(
            template, serializer.validated_data["teaching_units"]
        )
        return self._template_response(
            template, request, "Structure de la maquette enregistrée."
        )

    @action(detail=False, methods=["get"])
    def catalog(self, request):
        faculty = get_faculty_for_request(request)
        class_id = request.query_params.get("class_fk")
        semester_id = request.query_params.get("semester")
        programs = Program.objects.filter(faculty=faculty, is_active=True)
        classes = Class.objects.filter(department__faculty=faculty).select_related(
            "department"
        )
        semesters = Semester.objects.all()
        modules = Module.objects.filter(class_fk__department__faculty=faculty)
        courses = Course.objects.filter(
            module__class_fk__department__faculty=faculty
        ).select_related("module")
        if class_id and semester_id:
            modules = modules.filter(class_fk_id=class_id)
            courses = courses.filter(module__class_fk_id=class_id)
            modules = modules.filter(semester_id=semester_id)
            courses = courses.filter(module__semester_id=semester_id)
        else:
            modules = modules.none()
            courses = courses.none()

        return success_response(
            data={
                "programs": [
                    {
                        "id": str(program.id),
                        "name": str(program),
                        "faculty_id": str(program.faculty_id),
                    }
                    for program in programs
                ],
                "classes": [
                    {
                        "id": str(class_fk.id),
                        "name": class_fk.class_name,
                        "level": class_fk.level,
                        "department_name": class_fk.department.department_name,
                    }
                    for class_fk in classes
                ],
                "semesters": [
                    {
                        "id": str(semester.id),
                        "number": semester.number,
                        "name": str(semester),
                    }
                    for semester in semesters
                ],
                "modules": [
                    {
                        "id": str(module.id),
                        "code": module.code,
                        "name": module.module_name,
                        "class_fk": str(module.class_fk_id),
                        "semester": str(module.semester_id),
                    }
                    for module in modules
                ],
                "courses": [
                    {
                        "id": str(course.id),
                        "code": course.course_code,
                        "name": course.course_name,
                        "module": str(course.module_id),
                        "credits": course.credits,
                        "cm_hours": course.cm,
                        "td_hours": course.td,
                        "tp_hours": course.tp,
                    }
                    for course in courses
                ],
            },
            message="Catalogue académique récupéré.",
        )

    @staticmethod
    def _ensure_draft(template):
        if template.status != CurriculumTemplate.Status.DRAFT:
            raise PermissionDenied(
                "Seule une maquette en brouillon peut être modifiée."
            )

    @staticmethod
    def _template_response(template, request, message):
        template.refresh_from_db()
        return success_response(
            data=CurriculumTemplateSerializer(
                template, context={"request": request}
            ).data,
            message=message,
        )


class CurriculumTeachingUnitViewSet(BaseViewSet):
    serializer_class = CurriculumTeachingUnitSerializer
    permission_classes = [IsDean]

    def get_queryset(self):
        faculty = get_faculty_for_request(self.request)
        return CurriculumTeachingUnit.objects.filter(
            template__class_fk__department__faculty=faculty
        ).select_related("template", "module", "module__semester")

    def perform_create(self, serializer):
        faculty = get_faculty_for_request(self.request)
        template = serializer.validated_data["template"]
        if template.class_fk.department.faculty_id != faculty.id:
            raise PermissionDenied("Cette maquette n’appartient pas à votre faculté.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.template.status != CurriculumTemplate.Status.DRAFT:
            raise PermissionDenied(
                "Seule une maquette en brouillon peut être modifiée."
            )
        return super().destroy(request, *args, **kwargs)


class CurriculumCourseViewSet(BaseViewSet):
    serializer_class = CurriculumCourseSerializer
    permission_classes = [IsDean]

    def get_queryset(self):
        faculty = get_faculty_for_request(self.request)
        return CurriculumCourse.objects.filter(
            teaching_unit__template__class_fk__department__faculty=faculty
        ).select_related(
            "teaching_unit",
            "teaching_unit__template",
            "teaching_unit__module",
            "course",
            "course__module",
        )

    def perform_create(self, serializer):
        faculty = get_faculty_for_request(self.request)
        teaching_unit = serializer.validated_data["teaching_unit"]
        if teaching_unit.template.class_fk.department.faculty_id != faculty.id:
            raise PermissionDenied("Cette maquette n’appartient pas à votre faculté.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.teaching_unit.template.status != CurriculumTemplate.Status.DRAFT:
            raise PermissionDenied(
                "Seule une maquette en brouillon peut être modifiée."
            )
        return super().destroy(request, *args, **kwargs)
