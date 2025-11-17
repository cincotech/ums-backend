from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model with full CRUD operations
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "email",
            "telephone",
            "message",
            "sent_at",
            "delivery_status",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        """
        Ensure at least one contact method (email or telephone) is provided
        """
        if not data.get("email") and not data.get("telephone"):
            raise serializers.ValidationError(
                "At least one contact method (email or telephone) must be provided."
            )
        return data

    def validate_delivery_status(self, value):
        """
        Validate delivery_status is one of the allowed choices
        """
        allowed_statuses = ["sent", "failed"]
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Invalid delivery status. Must be one of: {', '.join(allowed_statuses)}"
            )
        return value


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing notifications
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "email",
            "telephone",
            "sent_at",
            "delivery_status",
        ]
        read_only_fields = ["id"]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications
    """

    class Meta:
        model = Notification
        fields = [
            "email",
            "telephone",
            "message",
            "sent_at",
            "delivery_status",
        ]

    def validate(self, data):
        """
        Ensure at least one contact method is provided
        """
        if not data.get("email") and not data.get("telephone"):
            raise serializers.ValidationError(
                "At least one contact method (email or telephone) must be provided."
            )
        return data
