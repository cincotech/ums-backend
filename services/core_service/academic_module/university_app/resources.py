from import_export import resources

from .models import AcademicYear, University, UniversityDegree


class AcademicYearResource(resources.ModelResource):
    class Meta:
        model = AcademicYear
        fields = ("academic_year", "civil_year", "start_date", "end_date")


class UniversityResource(resources.ModelResource):
    class Meta:
        model = University
        fields = ("university_name", "university_abrev", "country__country_name")


class UniversityDegreeResource(resources.ModelResource):
    class Meta:
        model = UniversityDegree
        fields = ("degree_name", "description")
