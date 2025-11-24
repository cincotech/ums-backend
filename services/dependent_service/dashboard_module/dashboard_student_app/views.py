# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated

# from core.response_handler import error_response, success_response
# from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
#     Message,
#     Notification,
# )
# from services.dependent_service.dashboard_module.dashboard_student_services_app.models import (
#     DocumentRequest,
# )

# from .serializers import (
#     AcademicProgressSerializer,
#     StudentAttendanceSerializer,
#     StudentDashboardStatsSerializer,
#     StudentDocumentRequestSerializer,
#     StudentGradesSerializer,
#     StudentMessageSerializer,
#     StudentNotificationSerializer,
#     StudentProfileSerializer,
#     StudentScheduleSerializer,
#     StudentTranscriptSerializer,
# )
# from .services import StudentDashboardService


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def student_dashboard_overview(request):
#     """Get student dashboard overview"""
#     try:
#         student = request.user.students_users
#         stats = StudentDashboardService.get_student_dashboard_stats(student)
#         serializer = StudentDashboardStatsSerializer(stats)
#         return success_response(
#             data=serializer.data, message="Student dashboard overview retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "PUT"])
# @permission_classes([IsAuthenticated])
# def student_profile(request):
#     """Get or update student profile"""
#     try:
#         student = request.user.students_users

#         if request.method == "GET":
#             profile_data = StudentDashboardService.get_student_profile(student)
#             serializer = StudentProfileSerializer(profile_data)
#             return success_response(
#                 data=serializer.data, message="Student profile retrieved"
#             )

#         elif request.method == "PUT":
#             updated_student = StudentDashboardService.update_profile(
#                 student, request.data
#             )
#             profile_data = StudentDashboardService.get_student_profile(updated_student)
#             serializer = StudentProfileSerializer(profile_data)
#             return success_response(
#                 data=serializer.data, message="Profile updated successfully"
#             )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def student_grades(request):
#     """Get student grades (conditional on payment)"""
#     try:
#         student = request.user.students_users
#         grades = StudentDashboardService.get_student_grades(student)

#         if isinstance(grades, dict) and "error" in grades:
#             return error_response(
#                 message=grades["error"], status_code=status.HTTP_403_FORBIDDEN
#             )

#         serializer = StudentGradesSerializer(grades, many=True)
#         return success_response(
#             data=serializer.data, message="Student grades retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def student_transcript(request):
#     """Get official transcript (when year is closed)"""
#     try:
#         student = request.user.students_users
#         transcript = StudentDashboardService.get_student_transcript(student)

#         if isinstance(transcript, dict) and "error" in transcript:
#             return error_response(
#                 message=transcript["error"], status_code=status.HTTP_403_FORBIDDEN
#             )

#         serializer = StudentTranscriptSerializer(transcript, many=True)
#         return success_response(
#             data=serializer.data, message="Student transcript retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def academic_progress(request):
#     """Get student academic progression and credits"""
#     try:
#         student = request.user.students_users
#         progress = StudentDashboardService.get_academic_progress(student)

#         if isinstance(progress, dict) and "error" in progress:
#             return error_response(
#                 message=progress["error"], status_code=status.HTTP_404_NOT_FOUND
#             )

#         serializer = AcademicProgressSerializer(progress)
#         return success_response(
#             data=serializer.data, message="Academic progress retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def student_schedule(request):
#     """Get student class schedule"""
#     try:
#         student = request.user.students_users
#         schedule = StudentDashboardService.get_student_schedule(student)
#         serializer = StudentScheduleSerializer(schedule, many=True)
#         return success_response(
#             data=serializer.data, message="Student schedule retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def student_attendance(request):
#     """Get student attendance record"""
#     try:
#         student = request.user.students_users
#         attendance = StudentDashboardService.get_student_attendance(student)
#         serializer = StudentAttendanceSerializer(attendance, many=True)
#         return success_response(
#             data=serializer.data, message="Student attendance retrieved"
#         )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def student_notifications(request):
#     """Get or mark notifications as read"""
#     try:
#         student = request.user.students_users

#         if request.method == "GET":
#             notifications = Notification.objects.filter(
#                 recipient=student.user
#             ).order_by("-created_at")
#             serializer = StudentNotificationSerializer(notifications, many=True)
#             return success_response(
#                 data=serializer.data, message="Notifications retrieved"
#             )

#         elif request.method == "POST":
#             notification_id = request.data.get("notification_id")
#             notification = StudentDashboardService.mark_notification_read(
#                 notification_id, student
#             )
#             serializer = StudentNotificationSerializer(notification)
#             return success_response(
#                 data=serializer.data, message="Notification marked as read"
#             )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def document_requests(request):
#     """Get document requests or submit new request"""
#     try:
#         student = request.user.students_users

#         if request.method == "GET":
#             requests_qs = DocumentRequest.objects.filter(student=student).order_by(
#                 "-requested_at"
#             )
#             serializer = StudentDocumentRequestSerializer(requests_qs, many=True)
#             return success_response(
#                 data=serializer.data, message="Document requests retrieved"
#             )

#         elif request.method == "POST":
#             document_type = request.data.get("document_type")
#             purpose = request.data.get("purpose")
#             supporting_docs = request.data.get("supporting_documents", [])

#             document_request = StudentDashboardService.request_document(
#                 student, document_type, purpose, supporting_docs
#             )

#             serializer = StudentDocumentRequestSerializer(document_request)
#             return success_response(
#                 data=serializer.data, message="Document request submitted"
#             )
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def student_messages(request):
#     """Get messages or send new message"""
#     try:
#         student = request.user.students_users

#         if request.method == "GET":
#             messages = Message.objects.filter(sender=student.user).order_by(
#                 "-sent_at"
#             ) | Message.objects.filter(recipient=student.user).order_by("-sent_at")
#             serializer = StudentMessageSerializer(messages, many=True)
#             return success_response(data=serializer.data, message="Messages retrieved")

#         elif request.method == "POST":
#             recipient_id = request.data.get("recipient_id")
#             subject = request.data.get("subject")
#             content = request.data.get("content")
#             message_type = request.data.get("message_type", "to_teacher")

#             message = StudentDashboardService.send_message(
#                 student, recipient_id, subject, content, message_type
#             )

#             serializer = StudentMessageSerializer(message)
#             return success_response(data=serializer.data, message="Message sent")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def download_documents(request):
#     """Get available documents for download"""
#     try:
#         student = request.user.students_users

#         # Generate available documents
#         documents = {
#             "enrollment_certificate": f"/api/documents/enrollment/{student.id}/",
#             "payment_receipt": f"/api/documents/payment/{student.id}/",
#             "schedule": f"/api/documents/schedule/{student.id}/",
#             "transcript_current": f"/api/documents/transcript/{student.id}/",
#         }

#         return success_response(data=documents, message="Available documents retrieved")
#     except Exception as e:
#         return error_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
