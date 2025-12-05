from rest_framework.permissions import BasePermission


class IsDirectorQuality(BasePermission):
    """
    Permission pour le Directeur Assurance Qualité (DAQ)
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "IsDirectorQuality", False)
        )
