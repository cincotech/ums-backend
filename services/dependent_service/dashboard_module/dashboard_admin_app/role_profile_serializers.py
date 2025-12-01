from rest_framework import serializers

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import University
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.authorization_app.models import Profile


class RoleProfileSerializer(serializers.ModelSerializer):
    room_id = serializers.UUIDField(source="room.id", read_only=True, allow_null=True)
    room_name = serializers.CharField(
        source="room.room_number", read_only=True, allow_null=True
    )

    class Meta:
        model = Profile
        fields = ["id", "position", "start_date", "end_date", "room_id", "room_name"]
        read_only_fields = ["id"]


class RectorProfileSerializer(RoleProfileSerializer):
    university_id = serializers.UUIDField(
        source="university.id", read_only=True, allow_null=True
    )
    university_name = serializers.CharField(
        source="university.university_name", read_only=True, allow_null=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "position",
            "start_date",
            "end_date",
            "room_id",
            "room_name",
            "university_id",
            "university_name",
        ]
        read_only_fields = ["id"]


class DeanProfileSerializer(RoleProfileSerializer):
    faculty_id = serializers.UUIDField(
        source="faculty.id", read_only=True, allow_null=True
    )
    faculty_name = serializers.CharField(
        source="faculty.faculty_name", read_only=True, allow_null=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "position",
            "start_date",
            "end_date",
            "room_id",
            "room_name",
            "faculty_id",
            "faculty_name",
        ]
        read_only_fields = ["id"]


class CreateRoleProfileSerializer(serializers.Serializer):
    position = serializers.CharField(max_length=100, required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    room_id = serializers.UUIDField(required=False, allow_null=True)
    university_id = serializers.UUIDField(required=False, allow_null=True)
    faculty_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_room_id(self, value):
        if value and not Room.objects.filter(id=value).exists():
            raise serializers.ValidationError("Room not found")
        return value

    def validate_university_id(self, value):
        if value and not University.objects.filter(id=value).exists():
            raise serializers.ValidationError("University not found")
        return value

    def validate_faculty_id(self, value):
        if value and not Faculty.objects.filter(id=value).exists():
            raise serializers.ValidationError("Faculty not found")
        return value


class CreateUserWithProfileSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    role_name = serializers.CharField(max_length=100)
    position = serializers.CharField(max_length=100, required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    room_id = serializers.UUIDField(required=False, allow_null=True)
    university_id = serializers.UUIDField(required=False, allow_null=True)
    faculty_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_room_id(self, value):
        if value and not Room.objects.filter(id=value).exists():
            raise serializers.ValidationError("Room not found")
        return value

    def validate_university_id(self, value):
        if value and not University.objects.filter(id=value).exists():
            raise serializers.ValidationError("University not found")
        return value

    def validate_faculty_id(self, value):
        if value and not Faculty.objects.filter(id=value).exists():
            raise serializers.ValidationError("Faculty not found")
        return value


class RoleWithFieldsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    fields = serializers.DictField()
