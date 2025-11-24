# from django.urls import path

# from . import views

# urlpatterns = [
#     path(
#         "student-services/overview/",
#         views.student_services_overview,
#         name="student-services-overview",
#     ),
#     path(
#         "student-services/documents/", views.document_requests, name="document-requests"
#     ),
#     path(
#         "student-services/documents/<uuid:request_id>/process/",
#         views.process_document_request,
#         name="process-document-request",
#     ),
#     path(
#         "student-services/absences/",
#         views.absence_justifications,
#         name="absence-justifications",
#     ),
#     path(
#         "student-services/absences/<uuid:absence_id>/process/",
#         views.process_absence_justification,
#         name="process-absence-justification",
#     ),
#     path(
#         "student-services/activities/",
#         views.student_activities,
#         name="student-activities",
#     ),
#     path(
#         "student-services/activities/<uuid:activity_id>/approve/",
#         views.approve_student_activity,
#         name="approve-student-activity",
#     ),
#     path("student-services/scholarships/", views.scholarships, name="scholarships"),
#     path(
#         "student-services/counseling/",
#         views.counseling_sessions,
#         name="counseling-sessions",
#     ),
#     path(
#         "student-services/reports/enrollment/",
#         views.enrollment_reports,
#         name="enrollment-reports",
#     ),
#     path(
#         "student-services/population/",
#         views.student_population_data,
#         name="student-population-data",
#     ),
#     path(
#         "student-services/students/<uuid:student_id>/update/",
#         views.update_student_profile,
#         name="update-student-profile",
#     ),
# ]
