import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("student_profile_app", "0002_initial"),
        ("faculty_app", "0001_initial"),
        ("university_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentMatricule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("matricule", models.CharField(max_length=120, unique=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name="matricules", to="student_profile_app.student")),
                ("type_formation", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name="student_matricules", to="faculty_app.typeformation")),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name="student_matricules", to="university_app.academicyear")),
            ],
            options={"db_table": "student_matricules"},
        ),
        migrations.AlterUniqueTogether(
            name="studentmatricule",
            unique_together={("student", "type_formation")},
        ),
    ]
