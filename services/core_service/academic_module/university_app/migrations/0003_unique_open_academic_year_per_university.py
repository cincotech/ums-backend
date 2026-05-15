# Generated manually to enforce one open academic year per university.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("university_app", "0002_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="academicyear",
            constraint=models.UniqueConstraint(
                fields=("university",),
                condition=models.Q(is_closed=False),
                name="unique_open_academic_year_per_university",
            ),
        ),
    ]
