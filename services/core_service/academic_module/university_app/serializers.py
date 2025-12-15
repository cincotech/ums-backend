from rest_framework import serializers

from .models import AcademicYear, University, UniversityDegree


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        exclude = ["university"]


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = "__all__"


class UniversityDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityDegree
        fields = "__all__"
