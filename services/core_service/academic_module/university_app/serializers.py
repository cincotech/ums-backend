from rest_framework import serializers

from services.foundational_service.geo_module.country_app.models import Country
from .models import AcademicYear, University, UniversityDegree


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        exclude = ["university"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance

        university = (
            self.context.get("academic_year_university")
            or (instance.university if instance else None)
        )
        start_date = attrs.get("start_date", instance.start_date if instance else None)
        end_date = attrs.get("end_date", instance.end_date if instance else None)
        is_closed = attrs.get("is_closed", instance.is_closed if instance else False)

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin."
            )

        if not university or not start_date or not end_date:
            return attrs

        overlapping_years = AcademicYear.objects.filter(
            university=university,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if instance:
            overlapping_years = overlapping_years.exclude(pk=instance.pk)
        if overlapping_years.exists():
            raise serializers.ValidationError(
                "Cette période chevauche déjà une autre année académique de cette université."
            )

        if not is_closed:
            open_years = AcademicYear.objects.filter(
                university=university,
                is_closed=False,
            )
            if instance:
                open_years = open_years.exclude(pk=instance.pk)
            if open_years.exists():
                raise serializers.ValidationError(
                    "Une année académique est déjà ouverte pour cette université. "
                    "Créez les anciennes années avec le statut Fermée, ou fermez l'année ouverte avant d'en ouvrir une nouvelle."
                )

        return attrs


class UniversitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.country_name', read_only=True, allow_null=True)

    class Meta:
        model = University
        fields = ['id', 'university_name', 'university_abrev', 'country', 'country_name']


class UniversityDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityDegree
        fields = "__all__"
