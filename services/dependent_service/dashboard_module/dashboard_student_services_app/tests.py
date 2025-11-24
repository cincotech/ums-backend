# from django.contrib.auth import get_user_model
# from django.test import TestCase

# from .services import StudentServicesService

# User = get_user_model()


# class StudentServicesServiceTest(TestCase):
#     def setUp(self):
#         self.services_agent = User.objects.create_user(
#             email="services@example.com", password="servicespass123"
#         )

#     def test_get_dashboard_stats(self):
#         """Test student services dashboard statistics"""
#         stats = StudentServicesService.get_dashboard_stats()

#         self.assertIn("total_students", stats)
#         self.assertIn("pending_documents", stats)
#         self.assertIn("pending_absences", stats)

#     def test_generate_enrollment_report(self):
#         """Test enrollment report generation"""
#         report = StudentServicesService.generate_enrollment_report()

#         self.assertIn("total_enrolled", report)
#         self.assertIn("by_program", report)
#         self.assertIn("success_rate", report)
