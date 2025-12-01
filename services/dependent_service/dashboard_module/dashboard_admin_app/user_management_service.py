from django.contrib.auth import get_user_model

from services.foundational_service.auth_module.authorization_app.models import Profile
from services.foundational_service.auth_module.user_app.models import Role

User = get_user_model()


class UniversityUserManagementService:
    """Service for managing users within a university"""

    @staticmethod
    def create_user(university, email, first_name, last_name, password, role_id=None):
        """Create new user for university"""
        if User.objects.filter(email=email).exists():
            raise ValueError(f"User with email {email} already exists")

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            university=university,
            is_active=True,
        )

        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                user.role = role
                user.save()
            except Role.DoesNotExist:
                pass

        return user

    @staticmethod
    def get_university_users(university):
        """Get all users for university"""
        return User.objects.filter(university=university).select_related("role")

    @staticmethod
    def update_user(user, **kwargs):
        """Update user information"""
        allowed_fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_active",
        ]

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        user.save()
        return user

    @staticmethod
    def change_user_password(user, new_password):
        """Change user password"""
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def assign_role(user, role_id):
        """Assign role to user"""
        try:
            role = Role.objects.get(id=role_id)
            user.role = role
            user.save()
            return user
        except Role.DoesNotExist:
            raise ValueError(f"Role {role_id} not found")

    @staticmethod
    def get_available_roles():
        """Get all available roles"""
        return Role.objects.all()

    @staticmethod
    def deactivate_user(user):
        """Deactivate user"""
        user.is_active = False
        user.save()
        return user

    @staticmethod
    def activate_user(user):
        """Activate user"""
        user.is_active = True
        user.save()
        return user

    @staticmethod
    def create_user_profile(user, position=None, start_date=None):
        """Create profile for user"""
        profile, created = Profile.objects.get_or_create(user=user)

        if position:
            profile.position = position
        if start_date:
            profile.start_date = start_date

        profile.save()
        return profile

    @staticmethod
    def get_user_profile(user):
        """Get user profile"""
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return None

    @staticmethod
    def update_user_profile(user, **kwargs):
        """Update user profile"""
        profile = UniversityUserManagementService.get_user_profile(user)
        if not profile:
            profile = UniversityUserManagementService.create_user_profile(user)

        allowed_fields = ["position", "start_date", "end_date"]

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(profile, field, value)

        profile.save()
        return profile
