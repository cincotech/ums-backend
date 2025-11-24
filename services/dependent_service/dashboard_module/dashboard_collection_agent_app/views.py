# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated

# from core.response_handler import error_response, success_response
# from services.core_service.finance_module.payment_app.models import Payment

# from .models import CollectionCorrespondence, LegalCase, PaymentPlan, PaymentPromise
# from .serializers import (
#     CollectionCorrespondenceSerializer,
#     CollectionStatsSerializer,
#     LegalCaseSerializer,
#     PaymentInstallmentSerializer,
#     PaymentPlanSerializer,
#     PaymentPromiseSerializer,
#     PaymentRecordSerializer,
#     PaymentReminderSerializer,
# )
# from .services import CollectionAgentService


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def collection_dashboard_overview(request):
#     """Get collection agent dashboard overview"""
#     try:
#         stats = CollectionAgentService.get_dashboard_stats()
#         serializer = CollectionStatsSerializer(stats)
#         return success_response(
#             data=serializer.data, message="Collection dashboard overview retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def debtor_students_list(request):
#     """Extract unpaid student data with filtering"""
#     try:
#         filters = {
#             "program": request.GET.get("program"),
#             "academic_year": request.GET.get("academic_year"),
#             "min_amount": request.GET.get("min_amount"),
#             "min_days_overdue": request.GET.get("min_days_overdue"),
#         }

#         # Remove None values
#         filters = {k: v for k, v in filters.items() if v is not None}

#         debtor_data = CollectionAgentService.get_debtors_list(filters)

#         return success_response(
#             data=debtor_data,
#             message=f"Debtor students list retrieved. Found {len(debtor_data)} students with outstanding payments.",
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def record_payment(request):
#     """Record payment and issue receipt"""
#     try:
#         student_id = request.data.get("student_id")
#         amount = request.data.get("amount")
#         payment_method = request.data.get("payment_method", "cash")
#         reference = request.data.get("reference", "")

#         payment = CollectionAgentService.record_payment(
#             student_id, amount, payment_method, reference, request.user
#         )

#         serializer = PaymentRecordSerializer(payment)
#         return success_response(
#             data=serializer.data, message="Payment recorded successfully"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def send_payment_reminder(request, student_id):
#     """Send payment reminder to student"""
#     try:
#         reminder_type = request.data.get(
#             "reminder_type"
#         )  # reminder_7, reminder_30, etc.

#         reminder = CollectionAgentService.send_reminder(
#             student_id, reminder_type, request.user
#         )
#         serializer = PaymentReminderSerializer(reminder)

#         return success_response(data=serializer.data, message="Payment reminder sent")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def send_automatic_reminders(request):
#     """Automatically send reminders to all students with overdue payments

#     This endpoint should be called periodically (e.g., via cron job or celery task)
#     """
#     try:
#         result = CollectionAgentService.send_automatic_reminders(request.user)

#         return success_response(
#             data=result,
#             message=f"Automatic reminders sent. Total: {result['total_reminders_sent']}",
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def payment_installments(request):
#     """Manage payment installments"""
#     try:
#         if request.method == "GET":
#             installments = Payment.objects.select_related("student__user").order_by(
#                 "-created_at"
#             )
#             serializer = PaymentInstallmentSerializer(installments, many=True)
#             return success_response(
#                 data=serializer.data, message="Payment installments retrieved"
#             )

#         elif request.method == "POST":
#             serializer = PaymentInstallmentSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(created_by=request.user)
#                 return success_response(
#                     data=serializer.data, message="Payment installment created"
#                 )
#             return error_response(message="Invalid data", errors=serializer.errors)
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["PUT"])
# @permission_classes([IsAuthenticated])
# def update_installment_due_date(request, installment_id):
#     """Update installment due date for justified cases"""
#     try:
#         new_due_date = request.data.get("new_due_date")

#         installment = CollectionAgentService.update_installment_due_date(
#             installment_id, new_due_date, request.user
#         )

#         serializer = PaymentInstallmentSerializer(installment)
#         return success_response(
#             data=serializer.data, message="Installment due date updated"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_payment_plan(request):
#     """Create payment plan for student"""
#     try:
#         student_id = request.data.get("student_id")
#         total_amount = request.data.get("total_amount")
#         monthly_amount = request.data.get("monthly_amount")
#         start_date = request.data.get("start_date")

#         plan = CollectionAgentService.create_payment_plan(
#             student_id, total_amount, monthly_amount, start_date, request.user
#         )

#         serializer = PaymentPlanSerializer(plan)
#         return success_response(data=serializer.data, message="Payment plan created")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def payment_plans_list(request):
#     """Get list of payment plans"""
#     try:
#         plans = PaymentPlan.objects.select_related("student__user").order_by(
#             "-created_at"
#         )
#         serializer = PaymentPlanSerializer(plans, many=True)
#         return success_response(data=serializer.data, message="Payment plans retrieved")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def record_payment_promise(request):
#     """Record payment promise from student"""
#     try:
#         student_id = request.data.get("student_id")
#         amount = request.data.get("amount")
#         promised_date = request.data.get("promised_date")
#         notes = request.data.get("notes", "")

#         promise = CollectionAgentService.record_payment_promise(
#             student_id, amount, promised_date, notes, request.user
#         )

#         serializer = PaymentPromiseSerializer(promise)
#         return success_response(
#             data=serializer.data, message="Payment promise recorded"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def payment_promises_list(request):
#     """Get list of payment promises"""
#     try:
#         promises = PaymentPromise.objects.select_related("student__user").order_by(
#             "-recorded_at"
#         )
#         serializer = PaymentPromiseSerializer(promises, many=True)
#         return success_response(
#             data=serializer.data, message="Payment promises retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def send_correspondence(request):
#     """Send correspondence to student"""
#     try:
#         student_id = request.data.get("student_id")
#         correspondence_type = request.data.get("correspondence_type")
#         subject = request.data.get("subject")
#         content = request.data.get("content")

#         correspondence = CollectionAgentService.send_correspondence(
#             student_id, correspondence_type, subject, content, request.user
#         )

#         serializer = CollectionCorrespondenceSerializer(correspondence)
#         return success_response(data=serializer.data, message="Correspondence sent")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def correspondence_history(request, student_id):
#     """Get correspondence history for student"""
#     try:
#         correspondence = CollectionCorrespondence.objects.filter(
#             student_id=student_id
#         ).order_by("-sent_at")

#         serializer = CollectionCorrespondenceSerializer(correspondence, many=True)
#         return success_response(
#             data=serializer.data, message="Correspondence history retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def prepare_legal_case(request, student_id):
#     """Prepare legal case for irrecoverable debt"""
#     try:
#         legal_case = CollectionAgentService.prepare_legal_case(student_id, request.user)
#         serializer = LegalCaseSerializer(legal_case)

#         return success_response(data=serializer.data, message="Legal case prepared")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def legal_cases_list(request):
#     """Get list of legal cases"""
#     try:
#         cases = LegalCase.objects.select_related("student__user").order_by(
#             "-prepared_at"
#         )
#         serializer = LegalCaseSerializer(cases, many=True)
#         return success_response(data=serializer.data, message="Legal cases retrieved")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
