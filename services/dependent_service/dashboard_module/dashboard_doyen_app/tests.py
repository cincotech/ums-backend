from django.contrib.auth import get_user_model
from django.test import TestCase

from services.core_service.academic_module.faculty_app.models import (
    Faculty,
    TypeFormation,
)
from services.core_service.academic_module.university_app.models import University

from .services import DoyenDashboardService

User = get_user_model()


class DoyenDashboardServiceTestCase(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Test University")
        self.type_formation = TypeFormation.objects.create(name="License", code="L")
        self.faculty = Faculty.objects.create(
            faculty_name="Engineering",
            faculty_abreviation="ENG",
            types=self.type_formation,
            university=self.university,
        )
        self.user = User.objects.create_user(
            email="doyen@test.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

    def test_create_schedule(self):
        schedule = DoyenDashboardService.create_schedule(
            self.faculty, "2024-2025", 1, self.user
        )
        self.assertEqual(schedule.faculty, self.faculty)
        self.assertEqual(schedule.academic_year, "2024-2025")
        self.assertEqual(schedule.semester, 1)

    def test_publish_schedule(self):
        schedule = DoyenDashboardService.create_schedule(
            self.faculty, "2024-2025", 1, self.user
        )
        published = DoyenDashboardService.publish_schedule(schedule)
        self.assertEqual(published.status, "published")
        self.assertIsNotNone(published.published_date)

    def test_create_academic_program(self):
        program = DoyenDashboardService.create_academic_program(
            self.faculty, "Computer Science", "license", "CS Program"
        )
        self.assertEqual(program.faculty, self.faculty)
        self.assertEqual(program.program_name, "Computer Science")
        self.assertEqual(program.level, "license")

    def test_create_secretary_note(self):
        note = DoyenDashboardService.create_secretary_note(
            self.faculty, "Test Subject", "Test message", self.user
        )
        self.assertEqual(note.faculty, self.faculty)
        self.assertEqual(note.subject, "Test Subject")
        self.assertFalse(note.is_resolved)

    def test_resolve_secretary_note(self):
        note = DoyenDashboardService.create_secretary_note(
            self.faculty, "Test Subject", "Test message", self.user
        )
        resolved = DoyenDashboardService.resolve_secretary_note(note)
        self.assertTrue(resolved.is_resolved)
