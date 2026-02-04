from rest_framework import serializers

from services.core_service.academic_module.faculty_app.serializers import (
    FacultySerializer,
)
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.authorization_app.models import Profile
from services.foundational_service.auth_module.user_app.models import Role, User

from .models import Program, ProgramImage


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "room_name", "room_type", "building"]


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "role",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    room = RoomSerializer(read_only=True)
    room_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    faculty_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    university_id = serializers.UUIDField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "user_id",
            "position",
            "start_date",
            "end_date",
            "faculty",
            "faculty_id",
            "university",
            "university_id",
            "room",
            "room_id",
        ]


class ProgramImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProgramImage
        fields = [
            "id",
            "image_url",
            "title",
            "description",
            "is_cover",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProgramSerializer(serializers.ModelSerializer):
    images = ProgramImageSerializer(many=True, read_only=True)
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Program
        fields = [
            "id",
            "faculty",
            "faculty_id",
            "presentation",
            "content",
            "admission_conditions",
            "prerequisites",
            "internship",
            "duration",
            "career_opportunities",
            "is_active",
            "images",
        ]
