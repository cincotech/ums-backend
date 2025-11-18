from django.contrib.auth import get_user_model
from django.test import TestCase

from .services import CollectionAgentService

User = get_user_model()


class CollectionAgentServiceTest(TestCase):
    def setUp(self):
        self.collection_agent = User.objects.create_user(
            email="collection@example.com", password="collectionpass123"
        )

    def test_get_dashboard_stats(self):
        """Test collection dashboard statistics"""
        stats = CollectionAgentService.get_dashboard_stats()

        self.assertIn("total_debtors", stats)
        self.assertIn("total_debt_amount", stats)
        self.assertIn("overdue_cases", stats)

    def test_extract_debtor_data(self):
        """Test debtor data extraction"""
        debtor_data = CollectionAgentService.extract_debtor_data()

        self.assertIsInstance(debtor_data, list)
