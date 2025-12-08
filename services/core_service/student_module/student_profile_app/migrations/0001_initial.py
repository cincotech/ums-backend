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
        ("colline_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Student",
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
                ("matricule", models.CharField(blank=True, max_length=120, null=True, unique=True)),
                ("cam", models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            options={
                "db_table": "students",
            },
        ),
        migrations.CreateModel(
            name="Training",
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
                ("domaine", models.CharField(max_length=255)),
                ("certificate", models.CharField(max_length=255)),
                (
                    "training_center",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="highschool_info_app.trainingcenter",
                    ),
                ),
            ],
            options={
                "db_table": "trainings",
            },
        ),
        migrations.CreateModel(
            name="StudentHsInfo",
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
                ("se_mark", models.CharField(blank=True, max_length=6, null=True)),
                ("date_of_obtention", models.PositiveSmallIntegerField()),
                (
                    "certificate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="highschool_info_app.certificate",
                    ),
                ),
                (
                    "formation",
                    models.ManyToManyField(
                        related_name="formations", to="student_profile_app.training"
                    ),
                ),
                (
                    "highschool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="highschool_info_app.highschool",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hs_infos",
                        to="student_profile_app.student",
                    ),
                ),
            ],
            options={
                "db_table": "student_hs_info",
            },
        ),
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
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        to=settings.AUTH_USER_MODEL,
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
    ]
