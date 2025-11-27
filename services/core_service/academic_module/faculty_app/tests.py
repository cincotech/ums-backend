from django.test import TestCase

from services.core_service.academic_module.university_app.models import University

from .models import Faculty, TypeFormation


class FacultyModelTest(TestCase):
    def setUp(self):

        self.university = University.objects.create(name="Test University")

        self.type_formation = TypeFormation.objects.create(name="Licence", code="L")

    def test_create_faculty(self):

        faculty = Faculty.objects.create(
            faculty_name="Science",
            faculty_abreviation="SCI",
            types=self.type_formation,
            university=self.university,
        )
        self.assertEqual(str(faculty), "Science")
        self.assertEqual(faculty.university.name, "Test University")
