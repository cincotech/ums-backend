# from django.contrib.auth import get_user_model
# from django.test import TestCase

# from .services import RecteurDashboardService

# User = get_user_model()


# class RecteurDashboardServiceTest(TestCase):
#     def setUp(self):
#         self.recteur_user = User.objects.create_user(
#             email="recteur@example.com", password="recteurpass123"
#         )

#     def test_get_dashboard_stats(self):
#         """Test recteur dashboard statistics"""
#         stats = RecteurDashboardService.get_dashboard_stats()

#         self.assertIn("pending_derogations", stats)
#         self.assertIn("pending_attributions", stats)
#         self.assertIn("payment_collection_rate", stats)

#     def test_get_payment_overview(self):
#         """Test payment overview functionality"""
#         overview = RecteurDashboardService.get_payment_overview()

#         self.assertIn("total_expected", overview)
#         self.assertIn("total_collected", overview)
#         self.assertIn("collection_rate", overview)
