from rest_framework import serializers

from .models import Module, UniversityProfile, UniversitySubscription


class UniversityProfileSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(
        source="university.university_name", read_only=True
    )

    class Meta:
        model = UniversityProfile
        fields = [
            "id",
            "university",
            "university_name",
            "status",
            "contact_email",
            "contact_phone",
            "website",
            "description",
            "max_users",
            "max_storage_gb",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "name", "description", "code", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class UniversitySubscriptionSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(
        source="university.university_name", read_only=True
    )
    module_name = serializers.CharField(source="module.name", read_only=True)
    module_code = serializers.CharField(source="module.code", read_only=True)
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)
    days_remaining = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = UniversitySubscription
        fields = [
            "id",
            "university",
            "university_name",
            "module",
            "module_name",
            "module_code",
            "status",
            "start_date",
            "end_date",
            "is_trial",
            "created_by_email",
            "days_remaining",
            "is_expired",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_days_remaining(self, obj):
        return obj.days_remaining()

    def get_is_expired(self, obj):
        return obj.is_expired()


class CreateSubscriptionSerializer(serializers.Serializer):
    module_id = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_trial = serializers.BooleanField(default=False)

    def validate(self, data):
        if data["end_date"] <= data["start_date"]:
            raise serializers.ValidationError("End date must be after start date")
        return data


class RenewSubscriptionSerializer(serializers.Serializer):
    new_end_date = serializers.DateField()

    def validate_new_end_date(self, value):
        from django.utils import timezone

        if value <= timezone.now().date():
            raise serializers.ValidationError("End date must be in the future")
        return value
