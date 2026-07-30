from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import (
    Faculty,
    TypeFormation,
)
from services.core_service.academic_module.module_app.models import Module, Semester
from services.core_service.academic_module.public_app.models import Program
from services.core_service.academic_module.university_app.models import (
    AcademicYear,
    University,
)

from .curriculum_services import CurriculumStructureService, CurriculumTemplateService
from .models import CurriculumCourse, CurriculumTeachingUnit, CurriculumTemplate


class CurriculumTemplateServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        university = University.objects.create(university_name="Université Test")
        formation_type = TypeFormation.objects.create(name="Licence", code="L")
        faculty = Faculty.objects.create(
            faculty_name="Technologies",
            faculty_abreviation="TIC",
            types=formation_type,
            university=university,
        )
        department = Department.objects.create(
            department_name="Informatique",
            abreviation="INFO",
            faculty=faculty,
        )
        cls.program = Program.objects.create(
            faculty=faculty,
            presentation="Licence en informatique",
            duration="3 ans",
        )
        cls.class_fk = Class.objects.create(
            class_name="Licence 3 Informatique",
            level=3,
            department=department,
        )
        cls.academic_year = AcademicYear.objects.create(
            academic_year="2025-2026",
            university=university,
            civil_year="2025",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
            is_closed=True,
        )
        cls.semester = Semester.objects.create(number=5, name="Semestre 5")
        cls.first_module = Module.objects.create(
            class_fk=cls.class_fk,
            module_name="Ingénierie informatique",
            code="UE1",
            semester=cls.semester,
        )
        cls.second_module = Module.objects.create(
            class_fk=cls.class_fk,
            module_name="Programmation orientée objet",
            code="UE2",
            semester=cls.semester,
        )
        cls.first_course = Course.objects.create(
            module=cls.first_module,
            course_code="BGL3501",
            course_name="Ingénierie du logiciel",
            cm=30,
            td=15,
            tp=15,
            credits=4,
        )
        cls.second_course = Course.objects.create(
            module=cls.second_module,
            course_code="BGL3505",
            course_name="Java",
            cm=30,
            td=10,
            tp=20,
            credits=4,
        )

    def create_template(self, expected_credits=8):
        template = CurriculumTemplate.objects.create(
            program=self.program,
            class_fk=self.class_fk,
            academic_year=self.academic_year,
            semester=self.semester,
            title="Maquette S5",
            expected_credits=expected_credits,
        )
        first_unit = CurriculumTeachingUnit.objects.create(
            template=template,
            module=self.first_module,
            position=1,
        )
        second_unit = CurriculumTeachingUnit.objects.create(
            template=template,
            module=self.second_module,
            position=2,
        )
        first_curriculum_course = CurriculumCourse.objects.create(
            teaching_unit=first_unit,
            course=self.first_course,
            position=1,
            tpe_hours=40,
            tge_hours=100,
        )
        second_curriculum_course = CurriculumCourse.objects.create(
            teaching_unit=second_unit,
            course=self.second_course,
            position=1,
            tpe_hours=40,
            tge_hours=100,
        )
        return (
            template,
            first_unit,
            second_unit,
            first_curriculum_course,
            second_curriculum_course,
        )

    def test_validation_calculates_totals(self):
        template, *_ = self.create_template()

        validation = CurriculumTemplateService.validate(template)

        self.assertTrue(validation["is_valid"])
        self.assertEqual(validation["totals"]["credits"], 8)
        self.assertEqual(validation["totals"]["vhp_hours"], 120)
        self.assertEqual(validation["totals"]["teaching_units"], 2)
        self.assertEqual(validation["totals"]["courses"], 2)

    def test_publication_rejects_invalid_credit_total(self):
        template, *_ = self.create_template(expected_credits=30)

        with self.assertRaises(ValidationError):
            CurriculumTemplateService.publish(template, None)

        template.refresh_from_db()
        self.assertEqual(template.status, CurriculumTemplate.Status.DRAFT)

    def test_reorder_courses_can_move_course_between_teaching_units(self):
        template, first_unit, second_unit, first_course, second_course = (
            self.create_template()
        )

        CurriculumStructureService.reorder_courses(
            template,
            [
                {
                    "teaching_unit_id": first_unit.id,
                    "course_ids": [second_course.id, first_course.id],
                },
                {"teaching_unit_id": second_unit.id, "course_ids": []},
            ],
        )

        first_course.refresh_from_db()
        second_course.refresh_from_db()
        self.assertEqual(second_course.teaching_unit_id, first_unit.id)
        self.assertEqual(second_course.position, 1)
        self.assertEqual(first_course.position, 2)

    def test_duplicate_creates_independent_draft_version(self):
        template, *_ = self.create_template()

        duplicate = CurriculumTemplateService.duplicate(template, None)

        self.assertEqual(duplicate.status, CurriculumTemplate.Status.DRAFT)
        self.assertEqual(duplicate.version, 2)
        self.assertEqual(duplicate.duplicated_from_id, template.id)
        self.assertEqual(duplicate.teaching_units.count(), 2)
        self.assertEqual(
            CurriculumCourse.objects.filter(teaching_unit__template=duplicate).count(),
            2,
        )
