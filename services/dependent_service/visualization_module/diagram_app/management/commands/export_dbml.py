"""
Management command to export the database schema in DBML-like format.
"""

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


def _field_column(field):
    return field.db_column or field.column


def _clean_default(field):
    v = field.default
    if callable(v):
        name = getattr(v, "__name__", str(v))
        if name in ("uuid4",):
            return None
        return None
    if isinstance(v, type) and v.__module__ == "django.db.models.fields":
        return None
    return v


class Command(BaseCommand):
    help = "Export database schema in DBML-like format"

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

        fk_names = self._load_fk_constraint_names()

        lines = []
        refs = []

        for model in models:
            lines.append(f'Table "{model._meta.db_table}" {{')
            fk_fields = []

            for field in model._meta.local_fields:
                col_name = _field_column(field)
                db_type = self._get_db_type(field)
                if not db_type:
                    continue

                opts = []
                if field.primary_key:
                    opts.append("pk")
                opts.append("not null" if not field.null else "null")

                default = _clean_default(field)
                if default is not None:
                    if isinstance(default, str):
                        opts.append(f'default: "{default}"')
                    elif isinstance(default, bool):
                        opts.append(f"default: {str(default).lower()}")
                    else:
                        opts.append(f"default: {default}")

                lines.append(f'  "{col_name}" {db_type} [{" ".join(opts)}]')

                if field.remote_field and field.remote_field.model:
                    fk_fields.append(field)

            all_indexes = list(model._meta.indexes)
            if model._meta.unique_together:
                pass

            if all_indexes or model._meta.unique_together:
                lines.append("")
                lines.append("  Indexes {")
                for idx in all_indexes:
                    col_list = []
                    for fname in idx.fields:
                        f = model._meta.get_field(fname)
                        col_list.append(_field_column(f))
                    col0 = col_list[0] if col_list else idx.fields[0]
                    lines.append(f'    {col0} [name: "{idx.name}"]')
                for ut in model._meta.unique_together:
                    col_list = []
                    for fname in ut:
                        f = model._meta.get_field(fname)
                        col_list.append(_field_column(f))
                    cols = ", ".join(f'"{c}"' for c in col_list)
                    lines.append(f"    ({cols}) [unique]")
                lines.append("  }")

            lines.append("}")
            lines.append("")

            for field in fk_fields:
                fk_name = self._resolve_fk_name(
                    field, model._meta.db_table, fk_names
                )
                ref_table = field.remote_field.model._meta.db_table
                ref_col = _field_column(field.remote_field.target_field)
                local_col = _field_column(field)
                refs.append((fk_name, ref_table, ref_col, model._meta.db_table, local_col))

        for fk_name, ref_table, ref_col, table, col in refs:
            lines.append(
                f'Ref "{fk_name}":"{ref_table}"."{ref_col}" < "{table}"."{col}"'
            )

        lines.append("")
        output_text = "\n".join(lines)

        if output:
            with open(output, "w") as f:
                f.write(output_text)
            self.stdout.write(self.style.SUCCESS(f"DBML exported to {output}"))
        else:
            self.stdout.write(output_text)

    def _load_fk_constraint_names(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME,
                           REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND REFERENCED_TABLE_NAME IS NOT NULL
                    """
                )
                rows = cursor.fetchall()
            result = {}
            for name, tbl, col, ref_tbl, ref_col in rows:
                key = (tbl, col, ref_tbl, ref_col)
                result[key] = name
            return result
        except Exception:
            return {}

    def _resolve_fk_name(self, field, local_table, fk_names):
        col = _field_column(field)
        ref_table = field.remote_field.model._meta.db_table
        ref_col = _field_column(field.remote_field.target_field)
        key = (local_table, col, ref_table, ref_col)
        if key in fk_names:
            return fk_names[key]
        return f"fk_{local_table}_{col}_{ref_table}_{ref_col}"

    def _get_db_type(self, field):
        try:
            return field.db_type(connection)
        except Exception:
            return None

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
