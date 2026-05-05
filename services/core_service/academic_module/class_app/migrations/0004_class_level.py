from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("class_app", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="level",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Level 1"),
                    (2, "Level 2"),
                    (3, "Level 3"),
                    (4, "Level 4"),
                    (5, "Level 5"),
                    (6, "Level 6"),
                    (7, "Level 7"),
                    (8, "Level 8"),
                    (9, "Level 9"),
                    (10, "Level 10"),
                ],
                default=1,
                help_text="Academic level of this class (1 = first year, up to 10)",
            ),
        ),
    ]
