"""
Management command to export the database skeleton as SQL.
Generates CREATE TABLE, constraints, and indexes — structure only, no data.
"""

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Export database skeleton as SQL (structure only, no data)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            "-a",
            type=str,
            default=None,
            help="Export only models from this app label",
        )
        parser.add_argument(
            "--model",
            "-m",
            type=str,
            default=None,
            help="Export only a specific model name (case-sensitive)",
        )
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default=None,
            help="Output file path (default: stdout)",
        )

    def handle(self, *args, **options):
        app_label = options["app"]
        model_name = options["model"]
        output = options["output"]

        models = self._get_filtered_models(app_label, model_name)
        if not models:
            msg = "No managed models found"
            if app_label:
                msg += f" for app '{app_label}'"
            if model_name:
                msg += f" for model '{model_name}'"
            raise CommandError(msg)

        lines = [
            "-- ============================================================",
            f"-- Database skeleton export -- {len(models)} model(s)",
            "-- Structure only -- no data",
            "-- ============================================================",
            "",
        ]

        with connection.schema_editor(collect_sql=True) as schema_editor:
            for model in models:
                schema_editor.execute(
                    f"-- app: {model._meta.app_label} / model: {model.__name__} / table: {model._meta.db_table}"  # noqa: E501
                )
                try:
                    schema_editor.create_model(model)
                except Exception as e:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Skipping {model._meta.app_label}.{model.__name__}: {e}"
                        )
                    )

        for sql in schema_editor.collected_sql:
            lines.append(sql)

        lines.append("")
        output_text = "\n".join(lines)

        if output:
            with open(output, "w") as f:
                f.write(output_text)
            self.stdout.write(self.style.SUCCESS(f"Skeleton exported to {output}"))
        else:
            self.stdout.write(output_text)

    def _get_filtered_models(self, app_label, model_name):
        models = []
        for config in apps.get_app_configs():
            if app_label and config.label != app_label:
                continue
            for model in config.get_models():
                if model._meta.managed is False:
                    continue
                if model._meta.proxy:
                    continue
                if model_name and model.__name__ != model_name:
                    continue
                models.append(model)
        return models
