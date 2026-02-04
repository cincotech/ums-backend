import json
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Export all models information to JSON for analysis"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="docs/models_info.json",
            help="Output file path",
        )

    def handle(self, *args, **options):
        output_file = Path(options["output"])
        output_file.parent.mkdir(parents=True, exist_ok=True)

        models_info = {}

        for model in apps.get_models():
            app_label = model._meta.app_label
            model_name = model.__name__

            if app_label not in models_info:
                models_info[app_label] = {}

            fields_info = []
            for field in model._meta.get_fields():
                field_data = {
                    "name": field.name,
                    "type": (
                        field.get_internal_type()
                        if hasattr(field, "get_internal_type")
                        else "Relation"
                    ),
                }

                if hasattr(field, "null"):
                    field_data["null"] = field.null
                if hasattr(field, "blank"):
                    field_data["blank"] = field.blank
                if hasattr(field, "primary_key"):
                    field_data["primary_key"] = field.primary_key
                if hasattr(field, "unique"):
                    field_data["unique"] = field.unique
                if hasattr(field, "max_length"):
                    field_data["max_length"] = field.max_length

                # Relationship info
                if field.many_to_one or field.one_to_one:
                    field_data["relation_type"] = (
                        "ForeignKey" if field.many_to_one else "OneToOne"
                    )
                    field_data["related_model"] = field.related_model.__name__
                elif field.many_to_many:
                    field_data["relation_type"] = "ManyToMany"
                    field_data["related_model"] = field.related_model.__name__

                fields_info.append(field_data)

            models_info[app_label][model_name] = {
                "db_table": model._meta.db_table,
                "verbose_name": str(model._meta.verbose_name),
                "fields": fields_info,
            }

        with open(output_file, "w") as f:
            json.dump(models_info, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Models info exported to {output_file}")
        )
        self.stdout.write(f"Total apps: {len(models_info)}")
        self.stdout.write(
            f"Total models: {sum(len(models) for models in models_info.values())}"
        )
