from django.contrib.auth import get_user_model
from django.test import TestCase

from services.core_service.student_module.student_profile_app.models import Student

from .services import StudentDashboardService

User = get_user_model()


class StudentDashboardServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com", password="studentpass123"
        )
        self.student = Student.objects.create(user=self.user, matricule="STU001")

    def test_get_dashboard_stats(self):
        """Test student dashboard statistics"""
        stats = StudentDashboardService.get_student_dashboard_stats(self.student)

        self.assertIn("unread_notifications", stats)
        self.assertIn("current_gpa", stats)
        self.assertIn("attendance_rate", stats)

    def test_get_student_profile(self):
        """Test student profile retrieval"""
        profile = StudentDashboardService.get_student_profile(self.student)

        self.assertIn("student_id", profile)
        self.assertIn("matricule", profile)
        self.assertEqual(profile["matricule"], "STU001")
