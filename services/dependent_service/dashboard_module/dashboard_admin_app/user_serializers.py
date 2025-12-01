from django.contrib.auth import get_user_model
from rest_framework import serializers

from services.foundational_service.auth_module.authorization_app.models import Profile
from services.foundational_service.auth_module.user_app.models import Role
from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.country_app.models import Country

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "position", "start_date", "end_date"]
        read_only_fields = ["id"]


class UserListSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    nationality = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), allow_null=True
    )
    residence = serializers.PrimaryKeyRelatedField(
        queryset=Colline.objects.all(), many=True, allow_null=True
    )
    profile = ProfileSerializer(source="profiles", read_only=True)

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
            "phone_number",
            "is_active",
            "profile",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserDetailSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    profile = ProfileSerializer(source="profiles", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "birth_date",
            "gender",
            "is_active",
            "role",
            "role_name",
            "profile",
            "email_verified",
            "created_at",
            "last_login",
        ]
        read_only_fields = ["id", "created_at", "last_login", "email_verified"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "phone_number",
            "role_id",
        ]

    def create(self, validated_data):
        role_id = validated_data.pop("role_id", None)
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)

        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                user.role = role
                user.save()
            except Role.DoesNotExist:
                pass

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "is_active"]


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data


class AssignRoleSerializer(serializers.Serializer):
    role_id = serializers.UUIDField()


class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user_email", "position", "start_date", "end_date"]
        read_only_fields = ["id"]
