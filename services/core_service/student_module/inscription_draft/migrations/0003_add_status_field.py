# Generated manually to add status field for soft-delete
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inscription_draft", "0002_inscriptiondraft_modified_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="inscriptiondraft",
            name="status",
            field=models.CharField(
                choices=[("active", "Active"), ("deleted", "Supprim\u00e9")],
                default="active",
                max_length=20,
                db_index=True,
            ),
        ),
    ]
