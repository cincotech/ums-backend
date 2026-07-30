from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Sum
from django.utils import timezone

from services.core_service.academic_module.university_app.models import AcademicYear

from .models import CurriculumCourse, CurriculumTeachingUnit, CurriculumTemplate


class CurriculumTemplateService:
    @staticmethod
    def validate(template):
        issues = []
        teaching_units = template.teaching_units.prefetch_related(
            "curriculum_courses__course"
        )

        if not teaching_units.exists():
            issues.append(
                {
                    "code": "required_teaching_units",
                    "severity": "error",
                    "message": "La maquette doit contenir au moins une unité d’enseignement.",
                }
            )

        course_ids = set()
        total_credits = 0
        total_vhp_hours = 0

        for teaching_unit in teaching_units:
            courses = list(teaching_unit.curriculum_courses.all())
            if not courses:
                issues.append(
                    {
                        "code": "empty_teaching_unit",
                        "severity": "warning",
                        "teaching_unit_id": str(teaching_unit.id),
                        "message": f"L’UE {teaching_unit.module.code or teaching_unit.module.module_name} ne contient aucun ECUE.",
                    }
                )

            for curriculum_course in courses:
                if curriculum_course.course_id in course_ids:
                    issues.append(
                        {
                            "code": "duplicate_course",
                            "severity": "error",
                            "course_id": str(curriculum_course.course_id),
                            "message": f"L’ECUE {curriculum_course.course.course_code or curriculum_course.course.course_name} est présent plusieurs fois.",
                        }
                    )
                course_ids.add(curriculum_course.course_id)
                total_credits += curriculum_course.course.credits
                total_vhp_hours += curriculum_course.vhp_hours

        if total_credits != template.expected_credits:
            issues.append(
                {
                    "code": "credits_total",
                    "severity": "error",
                    "message": f"La maquette totalise {total_credits} crédits au lieu des {template.expected_credits} attendus.",
                }
            )

        if (
            template.expected_vhp_hours is not None
            and total_vhp_hours != template.expected_vhp_hours
        ):
            issues.append(
                {
                    "code": "vhp_total",
                    "severity": "warning",
                    "message": f"La maquette totalise {total_vhp_hours} heures présentielles au lieu des {template.expected_vhp_hours} attendues.",
                }
            )

        return {
            "is_valid": not any(issue["severity"] == "error" for issue in issues),
            "issues": issues,
            "totals": {
                "credits": total_credits,
                "vhp_hours": total_vhp_hours,
                "teaching_units": teaching_units.count(),
                "courses": len(course_ids),
            },
        }

    @staticmethod
    @transaction.atomic
    def publish(template, user):
        template = CurriculumTemplate.objects.select_for_update().get(pk=template.pk)
        validation = CurriculumTemplateService.validate(template)
        errors = [
            issue["message"]
            for issue in validation["issues"]
            if issue["severity"] == "error"
        ]
        if errors:
            raise ValidationError({"template": errors})

        CurriculumTemplate.objects.filter(
            class_fk=template.class_fk,
            academic_year=template.academic_year,
            semester=template.semester,
            status=CurriculumTemplate.Status.PUBLISHED,
        ).exclude(pk=template.pk).update(status=CurriculumTemplate.Status.ARCHIVED)

        template.status = CurriculumTemplate.Status.PUBLISHED
        template.published_by = user
        template.published_at = timezone.now()
        template.save(
            update_fields=["status", "published_by", "published_at", "updated_at"]
        )
        return template

    @staticmethod
    @transaction.atomic
    def duplicate(template, user, academic_year=None):
        target_academic_year = academic_year or template.academic_year
        latest_version = (
            CurriculumTemplate.objects.filter(
                class_fk=template.class_fk,
                academic_year=target_academic_year,
                semester=template.semester,
            ).aggregate(max_version=Max("version"))["max_version"]
            or 0
        )
        duplicate = CurriculumTemplate.objects.create(
            program=template.program,
            class_fk=template.class_fk,
            academic_year=target_academic_year,
            semester=template.semester,
            title=template.title,
            version=latest_version + 1,
            status=CurriculumTemplate.Status.DRAFT,
            expected_credits=template.expected_credits,
            expected_vhp_hours=template.expected_vhp_hours,
            duplicated_from=template,
            created_by=user,
        )

        for teaching_unit in template.teaching_units.prefetch_related(
            "curriculum_courses"
        ):
            duplicate_teaching_unit = CurriculumTeachingUnit.objects.create(
                template=duplicate,
                module=teaching_unit.module,
                position=teaching_unit.position,
                is_required=teaching_unit.is_required,
                notes=teaching_unit.notes,
            )
            CurriculumCourse.objects.bulk_create(
                [
                    CurriculumCourse(
                        teaching_unit=duplicate_teaching_unit,
                        course=curriculum_course.course,
                        position=curriculum_course.position,
                        coefficient=curriculum_course.coefficient,
                        tpe_hours=curriculum_course.tpe_hours,
                        tge_hours=curriculum_course.tge_hours,
                        is_mandatory=curriculum_course.is_mandatory,
                        notes=curriculum_course.notes,
                    )
                    for curriculum_course in teaching_unit.curriculum_courses.all()
                ]
            )

        return duplicate

    @staticmethod
    def resolve_academic_year(academic_year_id):
        if not academic_year_id:
            return None
        try:
            return AcademicYear.objects.get(pk=academic_year_id)
        except AcademicYear.DoesNotExist as exc:
            raise ValidationError(
                {"academic_year": "L’année académique demandée n’existe pas."}
            ) from exc


class CurriculumStructureService:
    @staticmethod
    @transaction.atomic
    def replace_structure(template, teaching_units):
        template = CurriculumTemplate.objects.select_for_update().get(pk=template.pk)
        if template.status != CurriculumTemplate.Status.DRAFT:
            raise ValidationError(
                {"template": "Seule une maquette en brouillon peut être modifiée."}
            )

        template.teaching_units.all().delete()
        for teaching_unit_data in teaching_units:
            courses = teaching_unit_data.pop("courses")
            teaching_unit = CurriculumTeachingUnit.objects.create(
                template=template, **teaching_unit_data
            )
            CurriculumCourse.objects.bulk_create(
                [
                    CurriculumCourse(teaching_unit=teaching_unit, **course_data)
                    for course_data in courses
                ]
            )

        return template

    @staticmethod
    @transaction.atomic
    def reorder_teaching_units(template, ordered_ids):
        teaching_units = list(template.teaching_units.select_for_update())
        CurriculumStructureService._validate_complete_order(
            teaching_units, ordered_ids, "teaching_units"
        )
        temporary_offset = len(teaching_units) + 100
        for index, teaching_unit in enumerate(teaching_units):
            teaching_unit.position = temporary_offset + index
            teaching_unit.save(update_fields=["position"])
        by_id = {
            str(teaching_unit.id): teaching_unit for teaching_unit in teaching_units
        }
        for position, teaching_unit_id in enumerate(ordered_ids, start=1):
            teaching_unit = by_id[str(teaching_unit_id)]
            teaching_unit.position = position
            teaching_unit.save(update_fields=["position"])

    @staticmethod
    @transaction.atomic
    def reorder_courses(template, structure):
        teaching_units = {
            str(teaching_unit.id): teaching_unit
            for teaching_unit in template.teaching_units.select_for_update()
        }
        courses = list(
            CurriculumCourse.objects.select_for_update().filter(
                teaching_unit__template=template
            )
        )
        submitted_course_ids = [
            str(course_id)
            for item in structure
            for course_id in item.get("course_ids", [])
        ]
        CurriculumStructureService._validate_complete_order(
            courses, submitted_course_ids, "course_ids"
        )
        submitted_teaching_unit_ids = {
            str(item.get("teaching_unit_id")) for item in structure
        }
        if not submitted_teaching_unit_ids.issubset(teaching_units):
            raise ValidationError(
                {"teaching_unit_id": "Une UE ne fait pas partie de cette maquette."}
            )

        temporary_offset = len(courses) + 100
        for index, course in enumerate(courses):
            course.position = temporary_offset + index
            course.save(update_fields=["position"])

        courses_by_id = {str(course.id): course for course in courses}
        for item in structure:
            destination = teaching_units[str(item["teaching_unit_id"])]
            for position, course_id in enumerate(item.get("course_ids", []), start=1):
                curriculum_course = courses_by_id[str(course_id)]
                course = curriculum_course.course
                if (
                    course.module.class_fk_id != template.class_fk_id
                    or course.module.semester_id != template.semester_id
                ):
                    raise ValidationError(
                        {
                            "course_ids": "Un ECUE ne correspond pas à la classe et au semestre."
                        }
                    )
                curriculum_course.teaching_unit = destination
                curriculum_course.position = position
                curriculum_course.save(update_fields=["teaching_unit", "position"])

    @staticmethod
    def next_teaching_unit_position(template):
        return (
            template.teaching_units.aggregate(max_position=Max("position"))[
                "max_position"
            ]
            or 0
        ) + 1

    @staticmethod
    def next_course_position(teaching_unit):
        return (
            teaching_unit.curriculum_courses.aggregate(max_position=Max("position"))[
                "max_position"
            ]
            or 0
        ) + 1

    @staticmethod
    def total_credits(template):
        return (
            CurriculumCourse.objects.filter(teaching_unit__template=template).aggregate(
                total=Sum("course__credits")
            )["total"]
            or 0
        )

    @staticmethod
    def _validate_complete_order(objects, ordered_ids, field_name):
        existing_ids = {str(item.id) for item in objects}
        submitted_ids = [str(item_id) for item_id in ordered_ids]
        if len(submitted_ids) != len(set(submitted_ids)):
            raise ValidationError(
                {field_name: "La liste contient des identifiants dupliqués."}
            )
        if set(submitted_ids) != existing_ids:
            raise ValidationError(
                {
                    field_name: "La liste doit contenir exactement tous les éléments de la maquette."
                }
            )
