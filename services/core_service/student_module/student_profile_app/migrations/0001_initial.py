# Generated migration for StudentFile model

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("parent_app", "0001_initial"),
        ("highschool_info_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentFile",
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
                    "file_type",
                    models.CharField(
                        choices=[
                            ("birth_certificate", "Birth Certificate"),
                            ("highschool_diploma", "Highschool Diploma"),
                            ("transcript", "Transcript/Report Card"),
                            ("id_copy", "Copy of ID/Passport"),
                            ("medical_certificate", "Medical Certificate"),
                            ("photo", "Passport Photo"),
                            ("parent_id_copy", "Parent ID Copy"),
                            ("other", "Other Document"),
                        ],
                        max_length=30,
                    ),
                ),
                ("file_name", models.CharField(max_length=255)),
                ("file", models.FileField(upload_to="student_files/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("is_verified", models.BooleanField(default=False)),
                ("verified_at", models.DateTimeField(null=True, blank=True)),
                ("notes", models.TextField(null=True, blank=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        to="student_profile_app.student",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_student_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "student_files",
            },
        ),
        migrations.AddConstraint(
            model_name="studentfile",
            constraint=models.UniqueConstraint(
                fields=("student", "file_type"), name="unique_student_file_type"
            ),
        ),
    ]
