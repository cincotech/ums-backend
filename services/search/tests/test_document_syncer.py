"""Tests for DocumentSyncer — flat document builders and signal integrity."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from services.search.builders import (
    build_course,
    build_module,
    build_teacher,
    build_university,
)
from services.search.builders.base import sanitize, stable_created_at


class DocumentBuilderTests(SimpleTestCase):
    """Test the flat document builders produce schema-conformant output."""

    # ----------------------------------------------------------------
    # Course builder
    # ----------------------------------------------------------------

    def test_build_course_produces_flat_document(self):
        mock_module = MagicMock()
        mock_module.id = "module-uuid"
        mock_module.module_name = "Algorithmique"
        mock_module.class_fk = None

        mock_course = MagicMock()
        mock_course.id = "course-uuid"
        mock_course.course_name = "Algo Avancé"
        mock_course.course_code = "ALGO201"
        mock_course.module = mock_module
        mock_course.credits = 6
        mock_course.cm = 30
        mock_course.td = 15
        mock_course.tp = 0

        doc = build_course(mock_course)
        self.assertEqual(doc["course_name"], "Algo Avancé")
        self.assertEqual(doc["course_code"], "ALGO201")
        self.assertEqual(doc["module_name"], "Algorithmique")
        self.assertEqual(doc["module_id"], "module-uuid")
        self.assertEqual(doc["credits"], 6)
        self.assertEqual(doc["cm"], 30)
        self.assertEqual(doc["td"], 15)
        self.assertEqual(doc["tp"], 0)

    def test_build_course_handles_missing_module(self):
        mock_course = MagicMock()
        mock_course.id = "c-1"
        mock_course.course_name = "Standalone"
        mock_course.course_code = "SA101"
        mock_course.module = None
        mock_course.credits = None
        mock_course.cm = None
        mock_course.td = None
        mock_course.tp = None

        doc = build_course(mock_course)
        self.assertEqual(doc["course_name"], "Standalone")
        self.assertIsNone(doc["module_name"])
        self.assertIsNone(doc["module_id"])
        self.assertIsNone(doc["credits"])

    # ----------------------------------------------------------------
    # Module builder
    # ----------------------------------------------------------------

    def test_build_module_produces_flat_document(self):
        mock_class = MagicMock()
        mock_class.class_name = "L2 Info"
        mock_class.department = None

        mock_module = MagicMock()
        mock_module.id = "m-1"
        mock_module.module_name = "Réseaux"
        mock_module.code = "RES301"
        mock_module.class_fk = mock_class

        doc = build_module(mock_module)
        self.assertEqual(doc["module_name"], "Réseaux")
        self.assertEqual(doc["module_code"], "RES301")
        self.assertEqual(doc["class_name"], "L2 Info")

    # ----------------------------------------------------------------
    # Teacher builder
    # ----------------------------------------------------------------

    def test_build_teacher_produces_full_name(self):
        mock_user = MagicMock()
        mock_user.first_name = "Jean"
        mock_user.last_name = "Dupont"
        mock_user.email = "jean@test.com"
        mock_user.phone_number = "+123456"

        mock_teacher = MagicMock()
        mock_teacher.id = "t-1"
        mock_teacher.user = mock_user
        mock_teacher.teacher_grade = "Professeur"
        mock_teacher.speciality = "Réseaux"
        mock_teacher.university = None

        doc = build_teacher(mock_teacher)
        self.assertEqual(doc["full_name"], "Jean Dupont")
        self.assertEqual(doc["email"], "jean@test.com")
        self.assertEqual(doc["phone"], "+123456")
        self.assertEqual(doc["teacher_grade"], "Professeur")

    def test_build_teacher_handles_missing_user(self):
        mock_teacher = MagicMock()
        mock_teacher.id = "t-2"
        mock_teacher.user = None
        mock_teacher.teacher_grade = None
        mock_teacher.speciality = None
        mock_teacher.university = None

        doc = build_teacher(mock_teacher)
        self.assertIsNone(doc["full_name"])
        self.assertIsNone(doc["email"])

    # ----------------------------------------------------------------
    # University builder
    # ----------------------------------------------------------------

    def test_build_university_includes_country(self):
        mock_country = MagicMock()
        mock_country.country_name = "Burundi"

        mock_uni = MagicMock()
        mock_uni.id = "u-1"
        mock_uni.university_name = "Université du Burundi"
        mock_uni.university_abrev = "UB"
        mock_uni.country = mock_country

        doc = build_university(mock_uni)
        self.assertEqual(doc["university_name"], "Université du Burundi")
        self.assertEqual(doc["university_abrev"], "UB")
        self.assertEqual(doc["country"], "Burundi")

    # ----------------------------------------------------------------
    # Sanitization
    # ----------------------------------------------------------------

    def test_sanitize_drops_none_values(self):
        from services.search.schemas import MODEL_TO_COLLECTION

        doc = {"course_name": "Test", "course_code": None, "credits": 6}
        cleaned = sanitize(doc, "Course", MODEL_TO_COLLECTION)
        self.assertIn("course_name", cleaned)
        self.assertIn("credits", cleaned)
        self.assertNotIn("course_code", cleaned)

    def test_sanitize_drops_fields_not_in_schema(self):
        from services.search.schemas import MODEL_TO_COLLECTION

        doc = {"course_name": "Test", "bogus_field": "value"}
        cleaned = sanitize(doc, "Course", MODEL_TO_COLLECTION)
        self.assertIn("course_name", cleaned)
        self.assertNotIn("bogus_field", cleaned)

    # ----------------------------------------------------------------
    # Stable created_at
    # ----------------------------------------------------------------

    def test_stable_created_at_is_deterministic(self):
        mock = MagicMock()
        mock.pk = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        ts1 = stable_created_at(mock)
        ts2 = stable_created_at(mock)
        self.assertEqual(ts1, ts2)


class DispatchTableTests(SimpleTestCase):
    """Verify that all indexed models have a document builder."""

    def test_all_indexed_models_have_builder(self):
        from services.search.sync import DocumentSyncer

        expected = {
            "Course",
            "Module",
            "Teacher",
            "Class",
            "ClassGroup",
            "Department",
            "Faculty",
            "University",
            "User",
            "Inscription",
            "Student",
            "Session",
            "Result",
            "JurySession",
            "Profile",
        }
        self.assertEqual(set(DocumentSyncer._BUILDERS.keys()), expected)


class SignalRegistrationTests(SimpleTestCase):
    """Verify INDEXED_MODEL_LABELS matches the expected indexed models."""

    def test_indexed_model_labels_are_correct(self):
        from services.search.sync import INDEXED_MODEL_LABELS

        labels = set(INDEXED_MODEL_LABELS)
        expected = {
            ("course_app", "Course"),
            ("module_app", "Module"),
            ("teacher_app", "Teacher"),
            ("class_app", "Class"),
            ("class_app", "ClassGroup"),
            ("department_app", "Department"),
            ("faculty_app", "Faculty"),
            ("university_app", "University"),
            ("user_app", "User"),
            ("inscription_app", "Inscription"),
            ("student_profile_app", "Student"),
            ("result_app", "Session"),
            ("result_app", "Result"),
            ("dashboard_academic_secretary_app", "JurySession"),
            ("authorization_app", "Profile"),
        }
        self.assertEqual(labels, expected)
