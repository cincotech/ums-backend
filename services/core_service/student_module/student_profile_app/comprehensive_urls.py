from django.urls import path

from .comprehensive_views import (
    AssignSiblingsToParentsAPIView,
    ComprehensiveStudentCreateAPIView,
    StudentSiblingsAPIView,
)

urlpatterns = [
    # Main comprehensive student creation endpoint
    path(
        "comprehensive-create/",
        ComprehensiveStudentCreateAPIView.as_view(),
        name="comprehensive-student-create",
    ),
    # Get sibling information for a student using matricule
    path(
        "siblings/<str:matricule>/",
        StudentSiblingsAPIView.as_view(),
        name="student-siblings",
    ),
    # Assign existing students as siblings to the same parents
    path(
        "assign-siblings/",
        AssignSiblingsToParentsAPIView.as_view(),
        name="assign-siblings-to-parents",
    ),
]
