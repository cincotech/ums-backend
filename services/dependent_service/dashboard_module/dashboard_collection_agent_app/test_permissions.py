from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from core.permissions import IsStudentOrFinance
from services.foundational_service.auth_module.user_app.models import Role


class IsStudentOrFinancePermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsStudentOrFinance()

        self.student_role = Role.objects.create(name="student")
        self.finance_role = Role.objects.create(name="finance_service")
        self.teacher_role = Role.objects.create(name="teacher")

        User = get_user_model()
        self.student = User.objects.create_user(
            email="student@test.com", password="pass123", role=self.student_role
        )
        self.finance = User.objects.create_user(
            email="finance@test.com", password="pass123", role=self.finance_role
        )
        self.teacher = User.objects.create_user(
            email="teacher@test.com", password="pass123", role=self.teacher_role
        )

    def _request_for(self, user):
        request = self.factory.get("/dummy")
        request.user = user
        return request

    def test_student_allowed(self):
        request = self._request_for(self.student)
        self.assertTrue(self.permission.has_permission(request, None))

    def test_finance_allowed(self):
        request = self._request_for(self.finance)
        self.assertTrue(self.permission.has_permission(request, None))

    def test_other_role_denied(self):
        request = self._request_for(self.teacher)
        self.assertFalse(self.permission.has_permission(request, None))
