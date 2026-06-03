# President permission helper for JurySession

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import JuryMember


class IsPresidentMixin(UserPassesTestMixin):
    """Mixin to check if user is president of the jury session"""
    
    def test_func(self):
        jury_session_id = self.kwargs.get('pk') or self.request.data.get('jury_session')
        user = self.request.user
        
        if not jury_session_id:
            return False
        
        return JuryMember.objects.filter(
            jury_session_id=jury_session_id,
            user=user,
            role="president"
        ).exists()
    
    def handle_no_permission(self):
        from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
        if self.request.headers.get('Accept') == 'application/json':
            raise DRFPermissionDenied("User is not a president of this jury session")
        raise PermissionDenied("User is not a president of this jury session")