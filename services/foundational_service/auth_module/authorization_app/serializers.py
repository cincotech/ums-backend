from rest_framework import serializers

from services.dependent_service.infrastructure_module.room_app.models import Room
from services.dependent_service.infrastructure_module.room_app.serializers import (
    RoomSerializer,
)
from services.foundational_service.auth_module.authentication_app.serializers import (
    RoleSerializer,
)
from services.foundational_service.auth_module.user_app.models import User
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import University

from .models import Profile, Supervisor


class ProfileUserSerializer(serializers.ModelSerializer):
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
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    user = ProfileUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    room = RoomSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source="room",
        write_only=True,
        required=False,
        allow_null=True,
    )
    faculty_id = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.all(),
        source="faculty",
        write_only=True,
        required=False,
        allow_null=True,
    )
    university_id = serializers.PrimaryKeyRelatedField(
        queryset=University.objects.all(),
        source="university",
        write_only=True,
        required=False,
        allow_null=True,
    )
    faculty_abreviation = serializers.CharField(
        source="faculty.faculty_abreviation", read_only=True
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
            "room",
            "room_id",
            "faculty",
            "faculty_id",
            "university",
            "university_id",
            "faculty_abreviation",
        ]
        read_only_fields = ["id", "user", "room", "faculty_abreviation"]


class SupervisorSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        default=serializers.CurrentUserDefault(),
        required=False,
    )

    class Meta:
        model = Supervisor
        fields = "__all__"
        read_only_fields = ["id", "user"]
