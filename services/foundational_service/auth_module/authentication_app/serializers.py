import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from services.core_service.academic_module.university_app.models import University
from services.foundational_service.auth_module.user_app.models import Role, User
from services.foundational_service.geo_module.serializers import CollineSerializer
from services.foundational_service.auth_module.authentication_app.services import (
    UserService,
)

logger = logging.getLogger(__name__)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source="role", write_only=True, required=False
    )
    nationality_name = serializers.CharField(
        read_only=True, source="nationality.country_name"
    )
    residence = CollineSerializer(many=True, read_only=True)
    residence_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.residence.field.related_model.objects.all(),
        many=True,
        write_only=True,
        source="residence",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "gender",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "birth_date",
            "nationality",
            "nationality_name",
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
            "role_id",
            "residence_ids",
        ]
        read_only_fields = ["totp_secret_key"]

    SECURITY_FIELDS = {
        "email_verified",
        "requires_2fa",
        "requires_2fa_qr",
        "requires_2fa_email",
        "requires_2fa_static",
    }

    def _is_admin(self) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", None)
        return bool(role and role.name in {"admin", "super_admin"})

    def get_fields(self):
        fields = super().get_fields()
        # Always keep secret key read-only (never writable via API)
        if "totp_secret_key" in fields:
            fields["totp_secret_key"].read_only = True

        # Only admins can edit security flags
        if not self._is_admin():
            for name in self.SECURITY_FIELDS:
                if name in fields:
                    fields[name].read_only = True
        return fields

    def validate(self, attrs):
        # Block non-admins from attempting to update security fields
        if not self._is_admin() and self.instance:
            attempted = self.SECURITY_FIELDS.intersection(self.initial_data.keys())
            if attempted:
                raise serializers.ValidationError(
                    "You are not allowed to update security fields."
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        security_updates = {
            key: validated_data.pop(key)
            for key in list(validated_data.keys())
            if key in self.SECURITY_FIELDS
        }

        instance = super().update(instance, validated_data)

        if not security_updates:
            return instance

        if not self._is_admin():
            # Safety net: non-admin should never reach here
            raise serializers.ValidationError(
                "You are not allowed to update security fields."
            )

        user_service = UserService()

        # Email verification flag
        if "email_verified" in security_updates:
            instance.email_verified = bool(security_updates["email_verified"])

        # Master 2FA disable (admin only)
        if security_updates.get("requires_2fa") is False:
            EmailDevice.objects.filter(user=instance).delete()
            TOTPDevice.objects.filter(user=instance).delete()
            StaticDevice.objects.filter(user=instance).delete()
            instance.requires_2fa = False
            instance.requires_2fa_email = False
            instance.requires_2fa_qr = False
            instance.requires_2fa_static = False
            instance.totp_secret_key = None
            instance.save()
            return instance

        # Email 2FA
        if "requires_2fa_email" in security_updates:
            if security_updates["requires_2fa_email"]:
                user_service.setup_email_2fa(instance)
                instance.requires_2fa_email = True
            else:
                EmailDevice.objects.filter(
                    user=instance, email=instance.email
                ).delete()
                instance.requires_2fa_email = False

        # TOTP 2FA
        if "requires_2fa_qr" in security_updates:
            if security_updates["requires_2fa_qr"]:
                user_service.setup_totp_2fa(instance)
                instance.requires_2fa_qr = True
            else:
                TOTPDevice.objects.filter(user=instance).delete()
                instance.requires_2fa_qr = False
                instance.totp_secret_key = None

        # Static 2FA
        if "requires_2fa_static" in security_updates:
            if security_updates["requires_2fa_static"]:
                user_service.setup_static_2fa(instance)
                instance.requires_2fa_static = True
            else:
                StaticDevice.objects.filter(user=instance).delete()
                instance.requires_2fa_static = False

        instance.requires_2fa = (
            instance.requires_2fa_email
            or instance.requires_2fa_qr
            or instance.requires_2fa_static
        )
        instance.save()
        return instance

    def create(self, validated_data):
        residence_data = validated_data.pop("residence", [])

        user = User.objects.create(**validated_data)

        # Set the many-to-many field
        if residence_data:
            user.residence.set(residence_data)

        # Assign default role
        guest_role, _ = Role.objects.get_or_create(name="guest")
        user.role = guest_role

        # Assign university
        upg, _ = University.objects.get_or_create(
            university_name="Université Polytechnique de Gitega", university_abrev="UPG"
        )
        user.university = upg

        user.save()
        return user


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Registration Example",
            summary="Sample registration payload",
            value={
                "email": "john.doe@example.com",
                "password": "StrongPass123!",
                "first_name": "John",
                "last_name": "Doe",
                "birth_date": "1998-12-01",
                "spoken_languages": ["en", "fr"],
                "gender": "M",
                "marital_status": "S",
                "phone_number": "+257611223344",
            },
        ),
    ]
)
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
