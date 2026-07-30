import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "result_app",
            "0003_resultcomment_result_semester_compiledresult_semester_supplement_semester_result_status_result_validated_at_result_validated_by_result_comment",
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="GradeChangeHistory",
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
                (
                    "previous_mark",
                    models.FloatField(help_text="Note avant modification."),
                ),
                ("new_mark", models.FloatField(help_text="Note après modification.")),
                (
                    "reason",
                    models.TextField(blank=True, help_text="Motif de la modification."),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        help_text="Utilisateur à l'origine de la modification.",
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="grade_change_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "result",
                    models.ForeignKey(
                        help_text="Note modifiée.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grade_changes",
                        to="result_app.result",
                    ),
                ),
            ],
            options={
                "db_table": "grade_change_history",
                "ordering": ["-created_at"],
            },
        ),
    ]
