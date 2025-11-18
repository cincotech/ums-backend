from django.urls import path

from . import views

urlpatterns = [
    path(
        "student/overview/",
        views.student_dashboard_overview,
        name="student-dashboard-overview",
    ),
    path("student/profile/", views.student_profile, name="student-profile"),
    path("student/grades/", views.student_grades, name="student-grades"),
    path("student/transcript/", views.student_transcript, name="student-transcript"),
    path("student/progress/", views.academic_progress, name="academic-progress"),
    path("student/schedule/", views.student_schedule, name="student-schedule"),
    path("student/attendance/", views.student_attendance, name="student-attendance"),
    path(
        "student/notifications/",
        views.student_notifications,
        name="student-notifications",
    ),
    path("student/documents/", views.document_requests, name="document-requests"),
    path("student/messages/", views.student_messages, name="student-messages"),
    path("student/downloads/", views.download_documents, name="download-documents"),
]
