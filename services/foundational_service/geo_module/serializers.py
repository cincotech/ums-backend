from rest_framework import serializers
from services.foundational_service.geo_module.country_app.models import Country
from  services.foundational_service.geo_module.province_app.models import Province
from  services.foundational_service.geo_module.commune_app.models import Commune
from  services.foundational_service.geo_module.zone_app.models import Zone
from  services.foundational_service.geo_module.colline_app.models import Colline


class CollineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colline
        fields = ['id', 'colline_name']


class ZoneSerializer(serializers.ModelSerializer):
    collines = CollineSerializer(many=True, read_only=True)

    class Meta:
        model = Zone
        fields = ['id', 'zone_name', 'collines']


class CommuneSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)

    class Meta:
        model = Commune
        fields = ['id', 'commune_name', 'zones']


class ProvinceSerializer(serializers.ModelSerializer):
    communes = CommuneSerializer(many=True, read_only=True)

    class Meta:
        model = Province
        fields = ['id', 'province_name', 'communes']


class CountrySerializer(serializers.ModelSerializer):
    provinces = ProvinceSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'code', 'country_name', 'provinces']
