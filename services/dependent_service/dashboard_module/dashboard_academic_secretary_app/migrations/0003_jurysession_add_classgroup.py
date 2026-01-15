# Generated migration for adding ClassGroup to JurySession

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_academic_secretary_app', '0002_initial'),
        ('class_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jurysession',
            name='class_group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='jury_sessions',
                to='class_app.classgroup',
                null=True,  # Allow null temporarily for existing records
                blank=True
            ),
        ),
    ]