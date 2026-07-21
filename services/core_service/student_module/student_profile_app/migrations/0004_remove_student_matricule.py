# Generated manually after removing matricule field from Student model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("student_profile_app", "0003_studentmatricule"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="student",
            name="matricule",
        ),
    ]
