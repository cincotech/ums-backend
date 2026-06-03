from django.conf import settings
from django.db import migrations, models


def populate_jury_member_records(apps, schema_editor):
    JurySession = apps.get_model("dashboard_academic_secretary_app", "JurySession")
    JuryMember = apps.get_model("dashboard_academic_secretary_app", "JuryMember")

    for session in JurySession.objects.all().prefetch_related("jury_members"):
        for user in session.jury_members.all():
            JuryMember.objects.get_or_create(
                jury_session_id=session.pk,
                user_id=user.pk,
                defaults={"role": "member"},
            )


def reverse_populate(apps, schema_editor):
    JuryMember = apps.get_model("dashboard_academic_secretary_app", "JuryMember")
    JuryMember.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard_academic_secretary_app", "0005_add_jury_session_fk_to_jury_member"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(populate_jury_member_records, reverse_populate),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="jurysession",
                    name="jury_members",
                    field=models.ManyToManyField(
                        related_name="jury_sessions",
                        through="dashboard_academic_secretary_app.JuryMember",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
