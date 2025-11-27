from rest_framework.permissions import BasePermission


class IsUniversityAdmin(BasePermission):
    """Permission to check if user is a university admin"""

    def has_permission(self, request, view):
        """Check if user has active university admin profile"""
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            admin_profile = request.user.university
            return admin_profile
        except AttributeError:  # Likely cause if 'university' does not exist
            return False
