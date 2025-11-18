from django.contrib.auth import get_user_model
from django.test import TestCase

from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    SystemConfiguration,
)
from services.foundational_service.auth_module.user_app.models import Role

from .services import SuperAdminDashboardService

User = get_user_model()


class SuperAdminDashboardServiceTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="adminpass123"
        )
        self.role = Role.objects.create(name="Test Role", description="Test")

    def test_get_dashboard_stats(self):
        """Test dashboard statistics retrieval"""
        stats = SuperAdminDashboardService.get_dashboard_stats()

        self.assertIn("total_users", stats)
        self.assertIn("active_users", stats)
        self.assertIn("total_roles", stats)

    def test_manage_user_create(self):
        """Test user creation"""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        user = SuperAdminDashboardService.manage_user(
            None, "create", user_data, self.admin_user
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "newuser@example.com")

    def test_manage_system_config(self):
        """Test system configuration management"""
        config_data = {
            "config_type": "global",
            "key": "test_setting",
            "value": {"enabled": True},
        }

        config = SuperAdminDashboardService.manage_system_config(
            None, "create", config_data, self.admin_user
        )

        self.assertIsInstance(config, SystemConfiguration)
        self.assertEqual(config.key, "test_setting")
