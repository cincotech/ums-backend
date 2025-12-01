from django.contrib.auth import get_user_model

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import University
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.authorization_app.models import Profile
from services.foundational_service.auth_module.user_app.models import Role

User = get_user_model()

ROLE_PROFILE_MAPPING = {
    "rector": {
        "model": "Rector",
        "fields": ["university", "position", "room", "start_date", "end_date"],
    },
    "dean": {
        "model": "Dean",
        "fields": ["faculty", "position", "room", "start_date", "end_date"],
    },
    "student_service": {
        "model": "StudentService",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "finance_service": {
        "model": "FinanceService",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "general_service": {
        "model": "GeneralService",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "rector_office": {
        "model": "RectorOffice",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "quality_insurance": {
        "model": "QualityInsurance",
        "fields": ["position", "room", "start_date", "end_date"],
    },
    "academic_affairs": {
        "model": "AcademicAffairs",
        "fields": ["position", "room", "start_date", "end_date"],
    },
}


class RoleProfileService:
    """Service for managing role-specific profiles"""

    @staticmethod
    def get_role_by_name(role_name):
        """Get role by name"""
        try:
            return Role.objects.get(name__iexact=role_name)
        except Role.DoesNotExist:
            return None

    @staticmethod
    def create_user_with_profile(
        university, email, first_name, last_name, password, role_name, profile_data=None
    ):
        """Create user with role-specific profile"""
        if User.objects.filter(email=email).exists():
            raise ValueError(f"User with email {email} already exists")

        # Create user
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            university=university,
            is_active=True,
        )

        # Assign role
        role = RoleProfileService.get_role_by_name(role_name)
        if role:
            user.role = role
            user.save()

        # Create profile with role-specific data
        if profile_data:
            RoleProfileService.create_profile_for_user(user, role_name, profile_data)

        return user

    @staticmethod
    def create_profile_for_user(user, role_name, profile_data):
        """Create role-specific profile for user"""
        profile, created = Profile.objects.get_or_create(user=user)

        role_name_lower = role_name.lower().replace(" ", "_")

        # Set common fields
        if "position" in profile_data:
            profile.position = profile_data["position"]

        if "start_date" in profile_data:
            profile.start_date = profile_data["start_date"]

        if "end_date" in profile_data:
            profile.end_date = profile_data["end_date"]

        # Set room if provided
        if "room_id" in profile_data:
            try:
                room = Room.objects.get(id=profile_data["room_id"])
                profile.room = room
            except Room.DoesNotExist:
                pass

        # Set role-specific fields
        if role_name_lower == "rector" and "university_id" in profile_data:
            try:
                university = University.objects.get(id=profile_data["university_id"])
                profile.university = university
            except University.DoesNotExist:
                pass

        elif role_name_lower == "dean" and "faculty_id" in profile_data:
            try:
                faculty = Faculty.objects.get(id=profile_data["faculty_id"])
                profile.faculty = faculty
            except Faculty.DoesNotExist:
                pass

        profile.save()
        return profile

    @staticmethod
    def update_user_profile(user, role_name, profile_data):
        """Update user profile with role-specific data"""
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(
                user=user, start_date=profile_data.get("start_date")
            )

        role_name_lower = role_name.lower().replace(" ", "_")

        # Update common fields
        if "position" in profile_data:
            profile.position = profile_data["position"]

        if "start_date" in profile_data:
            profile.start_date = profile_data["start_date"]

        if "end_date" in profile_data:
            profile.end_date = profile_data["end_date"]

        if "room_id" in profile_data:
            try:
                room = Room.objects.get(id=profile_data["room_id"])
                profile.room = room
            except Room.DoesNotExist:
                pass

        # Update role-specific fields
        if role_name_lower == "rector" and "university_id" in profile_data:
            try:
                university = University.objects.get(id=profile_data["university_id"])
                profile.university = university
            except University.DoesNotExist:
                pass

        elif role_name_lower == "dean" and "faculty_id" in profile_data:
            try:
                faculty = Faculty.objects.get(id=profile_data["faculty_id"])
                profile.faculty = faculty
            except Faculty.DoesNotExist:
                pass

        profile.save()
        return profile

    @staticmethod
    def get_profile_fields_for_role(role_name):
        """Get required and optional fields for a role"""
        role_name_lower = role_name.lower().replace(" ", "_")

        base_fields = {
            "position": "string",
            "start_date": "date",
            "end_date": "date (optional)",
            "room_id": "uuid (optional)",
        }

        role_specific = {}

        if role_name_lower == "rector":
            role_specific["university_id"] = "uuid (required)"
        elif role_name_lower == "dean":
            role_specific["faculty_id"] = "uuid (required)"

        return {**base_fields, **role_specific}

    @staticmethod
    def get_user_profile_data(user):
        """Get complete profile data for user"""
        try:
            profile = Profile.objects.get(user=user)
            data = {
                "id": str(profile.id),
                "position": profile.position,
                "start_date": profile.start_date,
                "end_date": profile.end_date,
                "room": str(profile.room.id) if profile.room else None,
            }

            # Add role-specific data
            if user.role:
                role_name = user.role.name.lower().replace(" ", "_")

                if role_name == "rector" and profile.university:
                    data["university"] = str(profile.university.id)
                elif role_name == "dean" and profile.faculty:
                    data["faculty"] = str(profile.faculty.id)

            return data
        except Profile.DoesNotExist:
            return None

    @staticmethod
    def get_all_roles_with_fields():
        """Get all roles with their required fields"""
        roles = Role.objects.all()
        result = []

        for role in roles:
            result.append(
                {
                    "id": str(role.id),
                    "name": role.name,
                    "description": role.description,
                    "fields": RoleProfileService.get_profile_fields_for_role(role.name),
                }
            )

        return result
