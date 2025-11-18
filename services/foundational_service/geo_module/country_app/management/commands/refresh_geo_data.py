# management/commands/refresh_geo_data.py
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.country_app.models import Country
from services.foundational_service.geo_module.province_app.models import Province
from services.foundational_service.geo_module.zone_app.models import Zone


class Command(BaseCommand):
    help = "Clear and reload geographical data"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, help="Path to JSON file (optional)")

    def handle(self, *args, **options):
        # Clear existing data
        self.clear_data()

        # Load data
        if options["file"]:
            self.load_from_file(options["file"])
        else:
            self.load_default_data()

    def clear_data(self):
        self.stdout.write("Clearing existing geographical data...")
        Colline.objects.all().delete()
        Zone.objects.all().delete()
        Commune.objects.all().delete()
        Province.objects.all().delete()
        # Country.objects.all().delete()
        self.stdout.write("All geographical data cleared.")

    def load_from_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.load_data(data)
            self.stdout.write(self.style.SUCCESS("Loaded data from file"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading file: {e}"))

    def load_default_data(self):
        try:
            json_path = settings.BASE_DIR / "burundi_administrative_divisions.json"

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.load_data(data)
            self.stdout.write(self.style.SUCCESS("Loaded default data"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading default data: {e}"))

    def load_data(self, data):
        # Load country
        country, _ = Country.objects.get_or_create(country_name=data.get("country"))

        # Load provinces, communes, zones, collines
        for province_data in data["provinces"]:
            province = Province.objects.create(
                province_name=province_data["name"], country=country
            )

            for commune_data in province_data["communes"]:
                commune = Commune.objects.create(
                    commune_name=commune_data["name"], province=province
                )

                for zone_data in commune_data["zones"]:
                    zone = Zone.objects.create(
                        zone_name=zone_data["name"], commune=commune
                    )

                    for colline_name in zone_data["collines"]:
                        Colline.objects.create(colline_name=colline_name, zone=zone)
