import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):

    dependencies = [
        ("result_app", "0002_alter_compiledresult_average_mark_and_more"),
        ("module_app", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="result",
            name="comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="result",
            name="semester",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="results",
                to="module_app.semester",
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("submitted", "Submitted"),
                    ("validated", "Validated"),
                    ("rejected", "Rejected"),
                ],
                default="draft",
                help_text="Statut du workflow de validation des notes.",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="validated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="result",
            name="validated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="validated_results",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="compiledresult",
            name="semester",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="compiled_results",
                to="module_app.semester",
            ),
        ),
        migrations.AddField(
            model_name="supplement",
            name="semester",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="supplements",
                to="module_app.semester",
            ),
        ),
        migrations.CreateModel(
            name="ResultComment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("comment", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="result_comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "result",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="result_app.result",
                    ),
                ),
            ],
            options={
                "db_table": "result_comments",
                "ordering": ["-created_at"],
            },
        ),
    ]
