from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from services.core_service.academic_module.university_app.models import (
    AcademicYear,
    University,
)
from services.foundational_service.auth_module.user_app.models import Role


class FinanceOverviewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.university = University.objects.create(university_name="Test University")

        self.academic_year = AcademicYear.objects.create(
            academic_year="2025-2026",
            university=self.university,
            civil_year="2025",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=300),
            is_closed=False,
        )

        finance_role = Role.objects.create(name="finance_service")
        student_role = Role.objects.create(name="student")

        User = get_user_model()
        self.finance_user = User.objects.create_user(
            email="finance@test.com",
            password="pass123",
            role=finance_role,
            university=self.university,
        )
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="pass123",
            role=student_role,
            university=self.university,
        )

    def test_finance_can_access_overview(self):
        self.client.force_authenticate(user=self.finance_user)
        response = self.client.get("/dashboard/finance/overview/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("kpis", response.data["data"])

    def test_student_cannot_access_overview(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get("/dashboard/finance/overview/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_overview_fallbacks_to_active_academic_year(self):
        self.client.force_authenticate(user=self.finance_user)
        response = self.client.get("/dashboard/finance/overview/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        academic_year = response.data["data"].get("academic_year")
        self.assertIsNotNone(academic_year)
        self.assertEqual(str(self.academic_year.id), academic_year.get("id"))
