from rest_framework import serializers

from .models import (
    GuestDocument,
    GuestNotification,
    GuestRequest,
    RoleDocumentRequirement,
)


class GuestDocumentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = GuestDocument
        fields = [
            "id",
            "name",
            "type",
            "status",
            "uploaded_at",
            "url",
            "file_size",
            "mime_type",
            "rejection_reason",
            "verified_at",
            "verified_by",
        ]
        read_only_fields = ["id", "uploaded_at", "verified_at", "verified_by", "status"]

    def get_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class GuestNotificationSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = GuestNotification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "action_url",
            "is_read",
            "created_at",
            "details",
        ]
        read_only_fields = ["id", "created_at"]

    def get_details(self, obj):
        details = {}
        if obj.document:
            details["document_id"] = str(obj.document.id)
            details["document_name"] = obj.document.name
            if obj.document.rejection_reason:
                details["rejection_reason"] = obj.document.rejection_reason
        return details if details else None


class DocumentRequirementSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="document_type")
    max_size = serializers.IntegerField(source="max_size_mb")
    accepted_formats = serializers.ListField()

    class Meta:
        model = RoleDocumentRequirement
        fields = [
            "type",
            "label",
            "description",
            "required",
            "max_size",
            "accepted_formats",
        ]


class GuestProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    profile_image_url = serializers.SerializerMethodField()
    requested_role = serializers.CharField(source="requested_role.name", read_only=True)

    class Meta:
        model = GuestRequest
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "address",
            "profile_image_url",
            "status",
            "requested_role",
            "profile_submitted",
            "profile_submitted_at",
            "reviewed_at",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "profile_submitted",
            "profile_submitted_at",
            "reviewed_at",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]

    def get_profile_image_url(self, obj):
        if obj.user.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.user.profile_picture.url)
        return None

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class GuestDashboardStatsSerializer(serializers.Serializer):
    profile_completion = serializers.IntegerField()
    documents_uploaded = serializers.IntegerField()
    documents_required = serializers.IntegerField()
    documents_verified = serializers.IntegerField()
    documents_rejected = serializers.IntegerField()
    estimated_wait_days = serializers.IntegerField(required=False)
    position_in_queue = serializers.IntegerField(required=False)


class GuestUserSerializer(serializers.ModelSerializer):
    documents = GuestDocumentSerializer(many=True, read_only=True)
    notifications = GuestNotificationSerializer(many=True, read_only=True)
    progress_steps = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    requested_role = serializers.CharField(source="requested_role.name", read_only=True)
    reviewed_by = serializers.SerializerMethodField()

    class Meta:
        model = GuestRequest
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "address",
            "profile_image_url",
            "created_at",
            "updated_at",
            "status",
            "requested_role",
            "documents",
            "notifications",
            "progress_steps",
            "profile_submitted",
            "profile_submitted_at",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
        ]

    def get_profile_image_url(self, obj):
        if obj.user.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.user.profile_picture.url)
        return None

    def get_reviewed_by(self, obj):
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}"
        return None

    def get_progress_steps(self, obj):
        steps = [
            {
                "id": 1,
                "title": "Create Account",
                "description": "Register and verify email",
                "completed": True,
                "current": False,
            },
            {
                "id": 2,
                "title": "Complete Profile",
                "description": "Fill in personal information",
                "completed": obj.profile_submitted,
                "current": not obj.profile_submitted,
            },
            {
                "id": 3,
                "title": "Upload Documents",
                "description": "Submit required documents",
                "completed": obj.documents.filter(status="verified").count() > 0,
                "current": obj.profile_submitted and obj.status == "pending",
            },
            {
                "id": 4,
                "title": "Under Review",
                "description": "Application being reviewed",
                "completed": obj.status in ["approved", "rejected"],
                "current": obj.status == "under_review",
            },
            {
                "id": 5,
                "title": "Decision",
                "description": "Application approved or rejected",
                "completed": obj.status in ["approved", "rejected"],
                "current": False,
            },
        ]
        return steps


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    type = serializers.ChoiceField(choices=GuestDocument.DOCUMENT_TYPES)
