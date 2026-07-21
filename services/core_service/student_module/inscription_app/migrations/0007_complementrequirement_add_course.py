import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_app", "0001_initial"),
        ("inscription_app", "0006_add_jury_decision_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="complementrequirement",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="complement_requirements",
                to="course_app.course",
            ),
        ),
    ]
