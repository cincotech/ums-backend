# Generated migration for dashboard_doyen_app

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("faculty_app", "0001_initial"),
        ("course_app", "0001_initial"),
        ("teacher_app", "0001_initial"),
        ("student_profile_app", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Schedule",
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
                ("academic_year", models.CharField(max_length=9)),
                (
                    "semester",
                    models.IntegerField(choices=[(1, "Semester 1"), (2, "Semester 2")]),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("published_date", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedules",
                        to="faculty_app.faculty",
                    ),
                ),
            ],
            options={
                "db_table": "doyen_schedules",
            },
        ),
        migrations.CreateModel(
            name="TeachingProgress",
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
                ("progress_percentage", models.IntegerField(default=0)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "attribution",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="teacher_app.attribution",
                    ),
                ),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="faculty_app.faculty",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "teaching_progress",
            },
        ),
        migrations.CreateModel(
            name="TeacherWorkload",
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
                ("academic_year", models.CharField(max_length=9)),
                ("total_hours", models.IntegerField(default=0)),
                ("assigned_hours", models.IntegerField(default=0)),
                ("is_permanent", models.BooleanField(default=True)),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="faculty_app.faculty",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "teacher_workload",
            },
        ),
        migrations.CreateModel(
            name="StudentGroup",
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
                ("group_name", models.CharField(max_length=100)),
                ("academic_year", models.CharField(max_length=9)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="faculty_app.faculty",
                    ),
                ),
                (
                    "students",
                    models.ManyToManyField(
                        related_name="doyen_groups",
                        to="student_profile_app.studentprofile",
                    ),
                ),
            ],
            options={
                "db_table": "student_groups",
            },
        ),
        migrations.CreateModel(
            name="RoomAllocation",
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
                ("room_name", models.CharField(max_length=100)),
                ("capacity", models.IntegerField()),
                ("allocated_date", models.DateTimeField(auto_now_add=True)),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="faculty_app.faculty",
                    ),
                ),
                (
                    "schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard_doyen_app.schedule",
                    ),
                ),
            ],
            options={
                "db_table": "room_allocations",
            },
        ),
        migrations.CreateModel(
            name="SecretaryNote",
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
                ("subject", models.CharField(max_length=255)),
                ("message", models.TextField()),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("is_resolved", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="faculty_app.faculty",
                    ),
                ),
            ],
            options={
                "db_table": "secretary_notes",
            },
        ),
        migrations.CreateModel(
            name="AcademicProgram",
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
                ("program_name", models.CharField(max_length=255)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("license", "License"),
                            ("master", "Master"),
                            ("doctorate", "Doctorate"),
                        ],
                        max_length=20,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="programs",
                        to="faculty_app.faculty",
                    ),
                ),
            ],
            options={
                "db_table": "academic_programs",
            },
        ),
        migrations.CreateModel(
            name="TeachingUnit",
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
                ("credits", models.IntegerField()),
                (
                    "semester",
                    models.IntegerField(choices=[(1, "Semester 1"), (2, "Semester 2")]),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="course_app.course",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="units",
                        to="dashboard_doyen_app.academicprogram",
                    ),
                ),
            ],
            options={
                "db_table": "teaching_units",
            },
        ),
        migrations.AddConstraint(
            model_name="teacherworkload",
            constraint=models.UniqueConstraint(
                fields=("faculty", "teacher", "academic_year"),
                name="unique_teacher_workload",
            ),
        ),
        migrations.AddConstraint(
            model_name="studentgroup",
            constraint=models.UniqueConstraint(
                fields=("faculty", "group_name", "academic_year"),
                name="unique_student_group",
            ),
        ),
        migrations.AddConstraint(
            model_name="schedule",
            constraint=models.UniqueConstraint(
                fields=("faculty", "academic_year", "semester"), name="unique_schedule"
            ),
        ),
        migrations.AddConstraint(
            model_name="teachingunit",
            constraint=models.UniqueConstraint(
                fields=("program", "course"), name="unique_teaching_unit"
            ),
        ),
    ]
