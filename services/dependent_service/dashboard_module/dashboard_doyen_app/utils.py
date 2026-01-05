from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from services.core_service.academic_module.faculty_app.models import Faculty


def get_faculty_for_request(request):
    """
    Returns a Faculty instance either from query params or fallback to user's profile.
    """
    faculty_id = request.query_params.get("faculty_id")

    if faculty_id:
        # Faculty explicitly provided
        faculty = Faculty.objects.filter(id=faculty_id).first()
        if not faculty:
            raise PermissionDenied("Faculty not found.")
        return faculty

    # Fallback: get first active profile of current user
    profile = request.user.profiles.filter(
        start_date__lte=timezone.now().date()
    ).first()

    if not profile or not profile.faculty:
        raise PermissionDenied("No faculty found for your profile.")

    return profile.faculty
