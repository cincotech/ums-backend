import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling_app", "0004_initial"),
        ("class_app", "0003_initial"),
        ("room_app", "0001_initial"),
        ("teacher_app", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── TimetableTemplate ──────────────────────────────────────────────────
        migrations.CreateModel(
            name="TimetableTemplate",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("status", models.CharField(
                    choices=[("draft", "Brouillon"), ("published", "Publié"), ("archived", "Archivé")],
                    default="draft",
                    max_length=10,
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("class_group", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="timetable_templates",
                    to="class_app.classgroup",
                )),
                ("created_by", models.ForeignKey(
                    on_delete=django.db.models.deletion.RESTRICT,
                    related_name="created_timetable_templates",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"db_table": "timetable_templates", "ordering": ["-created_at"]},
        ),

        # ── TemplateEntry ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name="TemplateEntry",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("day_of_week", models.CharField(
                    choices=[
                        ("Monday", "Lundi"), ("Tuesday", "Mardi"), ("Wednesday", "Mercredi"),
                        ("Thursday", "Jeudi"), ("Friday", "Vendredi"),
                        ("Saturday", "Samedi"), ("Sunday", "Dimanche"),
                    ],
                    max_length=9,
                )),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("session_type", models.CharField(
                    choices=[
                        ("CM", "Cours magistral"), ("TD", "Travaux dirigés"),
                        ("TP", "Travaux pratiques"), ("Seminar", "Séminaire"), ("Other", "Autre"),
                    ],
                    default="CM",
                    max_length=10,
                )),
                ("week_type", models.CharField(
                    choices=[("all", "Toutes les semaines"), ("A", "Semaine A"), ("B", "Semaine B")],
                    default="all",
                    max_length=3,
                )),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("template", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="entries",
                    to="scheduling_app.timetabletemplate",
                )),
                ("attribution", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.RESTRICT,
                    to="teacher_app.attribution",
                )),
                ("room", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.RESTRICT,
                    to="room_app.room",
                )),
            ],
            options={"db_table": "template_entries", "ordering": ["day_of_week", "start_time"]},
        ),

        # ── CourseSession ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name="CourseSession",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("session_type", models.CharField(
                    choices=[
                        ("CM", "Cours magistral"), ("TD", "Travaux dirigés"),
                        ("TP", "Travaux pratiques"), ("Seminar", "Séminaire"), ("Other", "Autre"),
                    ],
                    default="CM",
                    max_length=10,
                )),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("status", models.CharField(
                    choices=[
                        ("scheduled", "Planifiée"), ("completed", "Dispensée"),
                        ("cancelled", "Annulée"), ("postponed", "Reportée"),
                    ],
                    default="scheduled",
                    max_length=10,
                )),
                ("is_makeup", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("template", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="sessions",
                    to="scheduling_app.timetabletemplate",
                )),
                ("template_entry", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="sessions",
                    to="scheduling_app.templateentry",
                )),
                ("class_group", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="course_sessions",
                    to="class_app.classgroup",
                )),
                ("attribution", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.RESTRICT,
                    to="teacher_app.attribution",
                )),
                ("room", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.RESTRICT,
                    to="room_app.room",
                )),
                ("created_by", models.ForeignKey(
                    on_delete=django.db.models.deletion.RESTRICT,
                    related_name="created_course_sessions",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"db_table": "course_sessions", "ordering": ["date", "start_time"]},
        ),
    ]
