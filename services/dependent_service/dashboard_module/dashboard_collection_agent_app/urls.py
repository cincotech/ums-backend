from django.urls import path

from . import views

urlpatterns = [
    path(
        "collection-agent/overview/",
        views.collection_dashboard_overview,
        name="collection-dashboard-overview",
    ),
    path(
        "collection-agent/debtors/",
        views.debtor_students_list,
        name="debtor-students-list",
    ),
    path(
        "collection-agent/payments/record/", views.record_payment, name="record-payment"
    ),
    path(
        "collection-agent/reminders/<uuid:student_id>/send/",
        views.send_payment_reminder,
        name="send-payment-reminder",
    ),
    path(
        "collection-agent/reminders/send-automatic/",
        views.send_automatic_reminders,
        name="send-automatic-reminders",
    ),
    path(
        "collection-agent/installments/",
        views.payment_installments,
        name="payment-installments",
    ),
    path(
        "collection-agent/installments/<uuid:installment_id>/update-date/",
        views.update_installment_due_date,
        name="update-installment-due-date",
    ),
    path(
        "collection-agent/payment-plans/",
        views.payment_plans_list,
        name="payment-plans-list",
    ),
    path(
        "collection-agent/payment-plans/create/",
        views.create_payment_plan,
        name="create-payment-plan",
    ),
    path(
        "collection-agent/promises/",
        views.payment_promises_list,
        name="payment-promises-list",
    ),
    path(
        "collection-agent/promises/record/",
        views.record_payment_promise,
        name="record-payment-promise",
    ),
    path(
        "collection-agent/correspondence/send/",
        views.send_correspondence,
        name="send-correspondence",
    ),
    path(
        "collection-agent/correspondence/<uuid:student_id>/",
        views.correspondence_history,
        name="correspondence-history",
    ),
    path(
        "collection-agent/legal-cases/", views.legal_cases_list, name="legal-cases-list"
    ),
    path(
        "collection-agent/legal-cases/<uuid:student_id>/prepare/",
        views.prepare_legal_case,
        name="prepare-legal-case",
    ),
]
