from rest_framework import serializers

from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.country_app.models import Country
from services.foundational_service.geo_module.province_app.models import Province
from services.foundational_service.geo_module.zone_app.models import Zone


class CollineSerializer(serializers.ModelSerializer):
    zone_id = serializers.PrimaryKeyRelatedField(
        queryset=Zone.objects.all(), source="zone", write_only=True
    )

    class Meta:
        model = Colline
        fields = ["id", "colline_name", "zone_id"]


class ZoneSerializer(serializers.ModelSerializer):
    collines = CollineSerializer(many=True, read_only=True)
    commune_id = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all(), source="commune", write_only=True
    )

    class Meta:
        model = Zone
        fields = ["id", "zone_name", "collines", "commune_id"]


class CommuneSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), source="province", write_only=True
    )

    class Meta:
        model = Commune
        fields = ["id", "commune_name", "zones", "province_id"]


class ProvinceSerializer(serializers.ModelSerializer):
    communes = CommuneSerializer(many=True, read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), source="country", write_only=True
    )

    class Meta:
        model = Province
        fields = ["id", "province_name", "communes", "country_id"]


class CountrySerializer(serializers.ModelSerializer):
    provinces = ProvinceSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ["id", "code", "country_name", "provinces"]
