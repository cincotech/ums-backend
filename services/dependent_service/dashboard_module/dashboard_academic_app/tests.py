from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import QualityReport
from .services import DashboardService

User = get_user_model()


class DashboardServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_get_attribution_stats(self):
        """Test attribution statistics retrieval"""
        stats = DashboardService.get_attribution_stats()

        self.assertIn("pending_attributions", stats)
        self.assertIn("approved_attributions", stats)
        self.assertIn("rejected_attributions", stats)
        self.assertIn("total_attributions", stats)

    def test_get_academic_performance_stats(self):
        """Test academic performance statistics"""
        stats = DashboardService.get_academic_performance_stats()

        self.assertIn("total_students", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("retention_rate", stats)

    def test_generate_quality_report(self):
        """Test quality report generation"""
        report = DashboardService.generate_quality_report(
            "academic_performance", self.user
        )

        self.assertIsInstance(report, QualityReport)
        self.assertEqual(report.report_type, "academic_performance")
        self.assertEqual(report.generated_by, self.user)
