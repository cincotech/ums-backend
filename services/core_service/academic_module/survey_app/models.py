import uuid

from django.db import models

from services.foundational_service.auth_module.user_app.models import User


class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to="survey_logos/", null=True, blank=True)
    multi_step = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="surveys_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "surveys"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ("text", "Text"),
        ("textarea", "Textarea"),
        ("radio", "Radio"),
        ("checkbox", "Checkbox"),
        ("select", "Select"),
        ("rating", "Rating"),
        ("date", "Date"),
        ("email", "Email"),
        ("number", "Number"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="questions"
    )
    label = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    section = models.CharField(max_length=100, default="default")
    placeholder = models.CharField(max_length=255, null=True, blank=True)
    options = models.JSONField(default=list, blank=True)
    max = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = "survey_questions"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.survey.title} - {self.label}"


class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="responses"
    )
    respondent_name = models.CharField(max_length=255, null=True, blank=True)
    respondent_email = models.EmailField(null=True, blank=True)
    respondent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
    )
    responses = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "survey_responses"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.survey.title} - {self.respondent_name or self.respondent_email or 'Anonymous'}"
