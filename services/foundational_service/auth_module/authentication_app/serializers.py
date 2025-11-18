import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import serializers

from services.foundational_service.auth_module.user_app.models import Role, User
from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.country_app.models import Country

logger = logging.getLogger(__name__)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    nationality = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), allow_null=True
    )
    residence = serializers.PrimaryKeyRelatedField(
        queryset=Colline.objects.all(), many=True, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "gender",
            "email",
            "phone_number",
            "birth_date",
            "nationality",
            "residence",
            "marital_status",
            "role",
            "email_verified",
            "requires_2fa",
            "requires_2fa_qr",
            "requires_2fa_email",
            "requires_2fa_static",
            "totp_secret_key",
            "profile_picture",
            "spoken_languages",
        ]
        read_only_fields = [
            "email_verified",
            "requires_2fa",
            "requires_2fa_qr",
            "requires_2fa_email",
            "requires_2fa_static",
            "totp_secret_key",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "birth_date",
            "spoken_languages",
            "gender",
            "marital_status",
            "phone_number",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class SendEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


# Serializer for verifying email OTP
class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=16)


# Serializer for 2FA verification
class Verify2FASerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=16)  # OTP code for 2FA
    email = serializers.EmailField()  # Email associated with the user


# Serializer for token refresh
class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()  # Refresh token to generate new access token


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


# Serializer for user login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Email field for login
    password = serializers.CharField(
        write_only=True
    )  # Password field, write-only for security

    def validate_email(self, value):
        """Ensure email is valid."""
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value.lower()

    def validate_password(self, value):
        """Ensure password is provided."""
        if not value.strip():
            raise serializers.ValidationError("Password is required.")
        return value
