from django.db import models
from django.conf import settings

class InscriptionDraft(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscription_drafts')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='inscription_drafts_modified')
    session_id = models.CharField(max_length=100, db_index=True)
    current_step = models.PositiveIntegerField(default=1)
    form_data = models.JSONField(default=dict)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Draft {self.session_id} ({self.user})"
