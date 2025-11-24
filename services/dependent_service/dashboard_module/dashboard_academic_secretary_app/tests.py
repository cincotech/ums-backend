# from django.contrib.auth import get_user_model
# from django.test import TestCase

# from .services import AcademicSecretaryService

# User = get_user_model()


# class AcademicSecretaryServiceTest(TestCase):
#     def setUp(self):
#         self.secretary = User.objects.create_user(
#             email="secretary@example.com", password="secretarypass123"
#         )

#     def test_get_dashboard_stats(self):
#         """Test academic secretary dashboard statistics"""
#         stats = AcademicSecretaryService.get_dashboard_stats()

#         self.assertIn("pending_exams", stats)
#         self.assertIn("pending_complaints", stats)
#         self.assertIn("pending_documents", stats)

#     def test_check_grade_entry_status(self):
#         """Test grade entry status checking"""
#         grade_status = AcademicSecretaryService.check_grade_entry_status()

#         self.assertIsInstance(grade_status, list)
