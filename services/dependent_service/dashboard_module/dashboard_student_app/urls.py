from django.urls import path

from . import views

urlpatterns = [
    # Dashboard Overview
    path(
        "overview/", views.student_dashboard_overview, name="student-dashboard-overview"
    ),
    # Profile Management
    path("profile/", views.student_profile, name="student-profile"),
    # Academic Records
    path("grades/", views.student_grades, name="student-grades"),
    path("transcript/", views.student_transcript, name="student-transcript"),
    path("progress/", views.academic_progress, name="academic-progress"),
    # Schedule & Attendance
    path("schedule/", views.student_schedule, name="student-schedule"),
    path("attendance/", views.student_attendance, name="student-attendance"),
    # Notifications & Messages
    path("notifications/", views.student_notifications, name="student-notifications"),
    path("messages/", views.student_messages, name="student-messages"),
    # Document Management
    path("documents/requests/", views.document_requests, name="document-requests"),
    path("documents/download/", views.download_documents, name="download-documents"),
]
