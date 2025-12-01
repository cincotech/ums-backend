from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Check if user is Super Admin"""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.is_superuser
        )
