from django.urls import path

from . import views

urlpatterns = [
    # Dashboard Overview
    path(
        "overview/",
        views.teacher_dashboard_overview,
        name="teacher-dashboard-overview",
    ),
    # Profile
    path("profile/", views.teacher_profile, name="teacher-profile"),
    # Attributions
    path("attributions/", views.teacher_attributions, name="teacher-attributions"),
    path(
        "attributions/<uuid:attribution_id>/accept/",
        views.accept_attribution,
        name="accept-attribution",
    ),
    path(
        "attributions/<uuid:attribution_id>/refuse/",
        views.refuse_attribution,
        name="refuse-attribution",
    ),
    # Courses
    path("courses/", views.teacher_courses, name="teacher-courses"),
    path(
        "courses/<uuid:course_id>/students/",
        views.course_students,
        name="course-students",
    ),
    # Grades
    path(
        "courses/<uuid:course_id>/grades/enter/",
        views.enter_grade,
        name="enter-grade",
    ),
    path(
        "courses/<uuid:course_id>/grades/bulk-enter/",
        views.bulk_enter_grades,
        name="bulk-enter-grades",
    ),
    # Exams
    path("exams/", views.teacher_exams, name="teacher-exams"),
    # Schedule
    path("schedule/", views.teacher_schedule, name="teacher-schedule"),
    # Payment Claims
    path(
        "payment-claims/",
        views.teacher_payment_claims,
        name="teacher-payment-claims",
    ),
    # Attendance
    path(
        "courses/<uuid:course_id>/attendance/record/",
        views.record_attendance,
        name="record-attendance",
    ),
    path(
        "courses/<uuid:course_id>/attendance/",
        views.course_attendance,
        name="course-attendance",
    ),
    # Notifications & Messages
    path("notifications/", views.teacher_notifications, name="teacher-notifications"),
    path("messages/", views.teacher_messages, name="teacher-messages"),
    # Statistics
    path("statistics/", views.teaching_statistics, name="teaching-statistics"),
]
