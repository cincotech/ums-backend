import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from services.foundational_service.auth_module.user_app.models import Role, User


class GuestRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="guest_request"
    )
    requested_role = models.ForeignKey(
        Role, on_delete=models.RESTRICT, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    phone = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_submitted = models.BooleanField(default=False)
    profile_submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_guests",
    )
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "guest_requests"

    def __str__(self):
        return f"{self.user.email} -  ({self.status})"


class GuestDocument(models.Model):
    DOCUMENT_TYPES = (
        ("identity", "Identity Document"),
        ("photo", "Profile Photo"),
        ("diploma", "Diploma"),
        ("transcript", "Transcript"),
        ("cv", "CV"),
        ("cover_letter", "Cover Letter"),
        ("teaching_cert", "Teaching Certificate"),
        ("work_contract", "Work Contract"),
        ("recommendation", "Recommendation Letter"),
        ("research_proposal", "Research Proposal"),
        ("admin_appointment", "Admin Appointment Letter"),
        ("other", "Other"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest_request = models.ForeignKey(
        GuestRequest, on_delete=models.CASCADE, related_name="documents"
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    file = models.FileField(upload_to="guest_documents/")
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_guest_docs",
    )
    rejection_reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "guest_documents"

    def __str__(self):
        return f"{self.guest_request.user.email} - {self.get_type_display()}"

    def check_and_assign_role(self):
        """Check if all required documents are verified and assign role to user"""
        if self.status == "verified":
            guest_request = self.guest_request

            # Get all required documents for the requested role
            required_docs = RoleDocumentRequirement.objects.filter(
                role=guest_request.requested_role, required=True
            )

            # Check if all required documents are verified
            verified_docs = guest_request.documents.filter(status="verified")
            required_types = set(required_docs.values_list("document_type", flat=True))
            verified_types = set(verified_docs.values_list("type", flat=True))

            # If all required documents are verified, assign role
            if required_types.issubset(verified_types):
                user = guest_request.user
                user.role = guest_request.requested_role
                user.save(update_fields=["role"])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.check_and_assign_role()


@receiver(post_save, sender=GuestDocument)
def update_user_profile_picture(sender, instance, created, **kwargs):
    """
    Automatically set user profile_picture when a photo document is uploaded.
    """
    if instance.type == "photo" and instance.file:
        user = instance.guest_request.user
        user.profile_picture = instance.file
        user.save(update_fields=["profile_picture"])


class GuestNotification(models.Model):
    TYPE_CHOICES = (
        ("info", "Info"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("action_required", "Action Required"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest_request = models.ForeignKey(
        GuestRequest, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="info")
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.CharField(max_length=500, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    document = models.ForeignKey(
        GuestDocument, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "guest_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.guest_request.user.email} - {self.title}"


class RoleDocumentRequirement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="document_requirements"
    )
    document_type = models.CharField(
        max_length=30, choices=GuestDocument.DOCUMENT_TYPES
    )
    label = models.CharField(max_length=255)
    description = models.TextField()
    required = models.BooleanField(default=True)
    max_size_mb = models.IntegerField(default=5)
    accepted_formats = models.JSONField(default=list)

    class Meta:
        db_table = "role_document_requirements"
        unique_together = ("role", "document_type")

    def __str__(self):
        return f"{self.role.name} - {self.label}"
