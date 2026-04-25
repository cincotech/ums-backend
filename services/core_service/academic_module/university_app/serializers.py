from rest_framework import serializers

from services.foundational_service.geo_module.country_app.models import Country
from .models import AcademicYear, University, UniversityDegree


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        exclude = ["university"]


class UniversitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.country_name', read_only=True, allow_null=True)

    class Meta:
        model = University
        fields = ['id', 'university_name', 'university_abrev', 'country', 'country_name']


class UniversityDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityDegree
        fields = "__all__"
