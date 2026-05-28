from rest_framework import serializers

from services.core_service.academic_module.public_app.serializers import RoleSerializer

from .models import GuestDocument, GuestRequest


class AccountRequestDocumentSerializer(serializers.ModelSerializer):
    """Serializer matching AccountRequestDocument TypeScript type"""

    url = serializers.SerializerMethodField()
    comment = serializers.CharField(source="rejection_reason", read_only=True)
    preview_url = serializers.SerializerMethodField()

    class Meta:
        model = GuestDocument
        fields = [
            "id",
            "name",
            "type",
            "status",
            "uploaded_at",
            "url",
            "comment",
            "preview_url",
        ]

    def get_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

    def get_preview_url(self, obj):
        return self.get_url(obj)


class AccountRequestSerializer(serializers.ModelSerializer):
    """Serializer matching AccountRequest TypeScript type"""

    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    requested_role = RoleSerializer(read_only=True)
    submitted_at = serializers.SerializerMethodField()
    documents = AccountRequestDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = GuestRequest
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "birth_date",
            "address",
            "profile_image_url",
            "requested_role",
            "status",
            "submitted_at",
            "documents",
        ]

    def get_profile_image_url(self, obj):
        if obj.user.profile_picture:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.user.profile_picture.url)
                if request
                else obj.user.profile_picture.url
            )
        return None

    def get_submitted_at(self, obj):
        return obj.profile_submitted_at or obj.created_at


class AccountRequestListItemSerializer(serializers.ModelSerializer):
    """Serializer matching AccountRequestListItem TypeScript type"""

    full_name = serializers.SerializerMethodField()
    requested_role = serializers.CharField(source="requested_role.name", read_only=True)
    submitted_at = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = GuestRequest
        fields = [
            "id",
            "full_name",
            "requested_role",
            "status",
            "submitted_at",
            "profile_image_url",
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_submitted_at(self, obj):
        return obj.profile_submitted_at or obj.created_at

    def get_profile_image_url(self, obj):
        if obj.user.profile_picture:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.user.profile_picture.url)
                if request
                else obj.user.profile_picture.url
            )
        return None


class AccountRequestStatsSerializer(serializers.Serializer):
    """Serializer matching AccountRequestStats TypeScript type"""

    total_requests = serializers.IntegerField()
    total_account_types = serializers.IntegerField()
    pending_review = serializers.IntegerField()
    total_documents = serializers.IntegerField()
    rejected_documents = serializers.IntegerField()
    rejected_accounts = serializers.IntegerField()


class UpdateDocumentStatusSerializer(serializers.Serializer):
    """Serializer matching UpdateDocumentStatusData TypeScript type"""

    status = serializers.ChoiceField(choices=["pending", "accepted", "rejected"])
    comment = serializers.CharField(required=False, allow_blank=True)


class ReviewAccountSerializer(serializers.Serializer):
    """Serializer matching ReviewAccountData TypeScript type"""

    status = serializers.ChoiceField(choices=["approved", "rejected"])
    documents = serializers.DictField(
        child=UpdateDocumentStatusSerializer(), required=False
    )
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
