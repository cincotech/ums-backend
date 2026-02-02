from rest_framework import serializers

from services.foundational_service.auth_module.user_app.models import User

from .models import Profile, Supervisor


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    faculty_abreviation = serializers.CharField(
        source="faculty.faculty_abreviation", read_only=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "user_id",
            "position",
            "start_date",
            "end_date",
            "room",
            "faculty",
            "university",
            "faculty_abreviation",
        ]
        read_only_fields = ["id"]


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
