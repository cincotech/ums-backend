from rest_framework import serializers

from .models import Certificate, Highschool, Option, Section, TrainingCenter


class HighschoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highschool
        fields = ["id", "hs_name", "zone", "code"]


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "section_name"]


class CertificateSerializer(serializers.ModelSerializer):
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), source="section", write_only=True
    )

    class Meta:
        model = Certificate
        fields = ["id", "certificate_name", "section", "section_id"]
        read_only_fields = ["section"]


class OptionSerializer(serializers.ModelSerializer):
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), source="section", write_only=True
    )

    class Meta:
        model = Option
        fields = ["id", "option_name", "section", "section_id"]
        read_only_fields = ["section"]


class TrainingCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCenter
        fields = ["id", "name", "commune"]
