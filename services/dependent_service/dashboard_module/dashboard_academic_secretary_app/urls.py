# from django.urls import path

# from . import views

# urlpatterns = [
#     path(
#         "academic-secretary/overview/",
#         views.academic_secretary_overview,
#         name="academic-secretary-overview",
#     ),
#     path("academic-secretary/exams/", views.exam_sessions, name="exam-sessions"),
#     path(
#         "academic-secretary/exams/<uuid:exam_id>/attendance/",
#         views.record_exam_attendance,
#         name="record-exam-attendance",
#     ),
#     path(
#         "academic-secretary/grades/status/",
#         views.grade_entry_status,
#         name="grade-entry-status",
#     ),
#     path("academic-secretary/juries/", views.jury_sessions, name="jury-sessions"),
#     path(
#         "academic-secretary/juries/<uuid:jury_id>/decisions/",
#         views.record_jury_decision,
#         name="record-jury-decision",
#     ),
#     path(
#         "academic-secretary/complaints/",
#         views.grade_complaints,
#         name="grade-complaints",
#     ),
#     path(
#         "academic-secretary/complaints/<uuid:complaint_id>/assign/",
#         views.assign_complaint,
#         name="assign-complaint",
#     ),
#     path(
#         "academic-secretary/complaints/<uuid:complaint_id>/resolve/",
#         views.resolve_complaint,
#         name="resolve-complaint",
#     ),
#     path(
#         "academic-secretary/documents/",
#         views.official_documents,
#         name="official-documents",
#     ),
#     path(
#         "academic-secretary/documents/<uuid:document_id>/sign/",
#         views.sign_document,
#         name="sign-document",
#     ),
#     path("academic-secretary/claims/", views.payment_claims, name="payment-claims"),
#     path(
#         "academic-secretary/claims/<uuid:claim_id>/verify/",
#         views.verify_payment_claim,
#         name="verify-payment-claim",
#     ),
#     path(
#         "academic-secretary/claims/<uuid:claim_id>/approve/",
#         views.approve_payment_claim,
#         name="approve-payment-claim",
#     ),
#     path(
#         "academic-secretary/claims/<uuid:claim_id>/send-finance/",
#         views.send_claim_to_finance,
#         name="send-claim-to-finance",
#     ),
# ]
