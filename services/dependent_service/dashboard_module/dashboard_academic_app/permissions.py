from rest_framework.permissions import BasePermission


class IsDean(BasePermission):
    """Permission pour vérifier que l'utilisateur est un Doyen."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'doyen'


class IsAcademicSecretary(BasePermission):
    """Permission pour vérifier que l'utilisateur est un Secrétaire Académique."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'academic_secretary'
