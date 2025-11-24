# from rest_framework import status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated

# from core.response_handler import success_response

# from .models import RoomAllocation, Schedule, SecretaryNote, StudentGroup
# from .serializers import (
#     AcademicProgramSerializer,
#     DoyenDashboardStatsSerializer,
#     RoomAllocationSerializer,
#     ScheduleSerializer,
#     SecretaryNoteSerializer,
#     StudentGroupSerializer,
#     TeacherWorkloadSerializer,
#     TeachingProgressSerializer,
# )
# from .services import DoyenDashboardService


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def dashboard_overview(request):
#     """Get DOYEN dashboard overview"""
#     try:
#         faculty = request.user.faculty
#         stats = DoyenDashboardService.get_dashboard_stats(faculty)
#         serializer = DoyenDashboardStatsSerializer(stats)
#         return success_response(
#             data=serializer.data, message="Dashboard overview retrieved successfully"
#         )
#     except Exception as e:
#         return success_response(
#             message=f"Error retrieving dashboard: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def schedules(request):
#     """Get or create schedules"""
#     try:
#         faculty = request.user.faculty

#         if request.method == "GET":
#             schedules_list = DoyenDashboardService.get_faculty_schedules(faculty)
#             serializer = ScheduleSerializer(schedules_list, many=True)
#             return success_response(data=serializer.data, message="Schedules retrieved")

#         elif request.method == "POST":
#             academic_year = request.data.get("academic_year")
#             semester = request.data.get("semester")

#             schedule = DoyenDashboardService.create_schedule(
#                 faculty, academic_year, semester, request.user
#             )
#             serializer = ScheduleSerializer(schedule)
#             return success_response(
#                 data=serializer.data, message="Schedule created successfully"
#             )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def publish_schedule(request, schedule_id):
#     """Publish a schedule"""
#     try:
#         schedule = Schedule.objects.get(id=schedule_id, faculty=request.user.faculty)
#         schedule = DoyenDashboardService.publish_schedule(schedule)
#         serializer = ScheduleSerializer(schedule)
#         return success_response(
#             data=serializer.data, message="Schedule published successfully"
#         )
#     except Schedule.DoesNotExist:
#         return success_response(
#             message="Schedule not found", status_code=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def teaching_progress(request):
#     """Get teaching progress for all courses"""
#     try:
#         faculty = request.user.faculty
#         progress_list = DoyenDashboardService.get_teaching_progress(faculty)
#         serializer = TeachingProgressSerializer(progress_list, many=True)
#         return success_response(
#             data=serializer.data, message="Teaching progress retrieved"
#         )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def teacher_workload(request):
#     """Get teacher workload"""
#     try:
#         faculty = request.user.faculty
#         academic_year = request.query_params.get("academic_year")

#         workload_list = DoyenDashboardService.get_teacher_workload(
#             faculty, academic_year
#         )
#         serializer = TeacherWorkloadSerializer(workload_list, many=True)
#         return success_response(
#             data=serializer.data, message="Teacher workload retrieved"
#         )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def student_groups(request):
#     """Get or create student groups"""
#     try:
#         faculty = request.user.faculty

#         if request.method == "GET":
#             groups = StudentGroup.objects.filter(faculty=faculty)
#             serializer = StudentGroupSerializer(groups, many=True)
#             return success_response(
#                 data=serializer.data, message="Student groups retrieved"
#             )

#         elif request.method == "POST":
#             group_name = request.data.get("group_name")
#             academic_year = request.data.get("academic_year")

#             group = DoyenDashboardService.create_student_group(
#                 faculty, group_name, academic_year
#             )
#             serializer = StudentGroupSerializer(group)
#             return success_response(
#                 data=serializer.data, message="Student group created successfully"
#             )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def academic_programs(request):
#     """Get or create academic programs"""
#     try:
#         faculty = request.user.faculty

#         if request.method == "GET":
#             programs = DoyenDashboardService.get_academic_programs(faculty)
#             serializer = AcademicProgramSerializer(programs, many=True)
#             return success_response(data=serializer.data, message="Programs retrieved")

#         elif request.method == "POST":
#             program_name = request.data.get("program_name")
#             level = request.data.get("level")
#             description = request.data.get("description")

#             program = DoyenDashboardService.create_academic_program(
#                 faculty, program_name, level, description
#             )
#             serializer = AcademicProgramSerializer(program)
#             return success_response(
#                 data=serializer.data, message="Program created successfully"
#             )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def room_allocations(request):
#     """Get or create room allocations"""
#     try:
#         faculty = request.user.faculty

#         if request.method == "GET":
#             allocations = RoomAllocation.objects.filter(faculty=faculty)
#             serializer = RoomAllocationSerializer(allocations, many=True)
#             return success_response(
#                 data=serializer.data, message="Room allocations retrieved"
#             )

#         elif request.method == "POST":
#             schedule_id = request.data.get("schedule_id")
#             room_name = request.data.get("room_name")
#             capacity = request.data.get("capacity")

#             schedule = Schedule.objects.get(id=schedule_id, faculty=faculty)
#             allocation = DoyenDashboardService.allocate_room(
#                 schedule, faculty, room_name, capacity
#             )
#             serializer = RoomAllocationSerializer(allocation)
#             return success_response(
#                 data=serializer.data, message="Room allocated successfully"
#             )
#     except Schedule.DoesNotExist:
#         return success_response(
#             message="Schedule not found", status_code=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
# def secretary_notes(request):
#     """Get or create secretary notes"""
#     try:
#         faculty = request.user.faculty

#         if request.method == "GET":
#             notes = SecretaryNote.objects.filter(faculty=faculty).order_by(
#                 "-created_date"
#             )
#             serializer = SecretaryNoteSerializer(notes, many=True)
#             return success_response(
#                 data=serializer.data, message="Secretary notes retrieved"
#             )

#         elif request.method == "POST":
#             subject = request.data.get("subject")
#             message = request.data.get("message")

#             note = DoyenDashboardService.create_secretary_note(
#                 faculty, subject, message, request.user
#             )
#             serializer = SecretaryNoteSerializer(note)
#             return success_response(
#                 data=serializer.data, message="Note created successfully"
#             )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def resolve_secretary_note(request, note_id):
#     """Mark secretary note as resolved"""
#     try:
#         note = SecretaryNote.objects.get(id=note_id, faculty=request.user.faculty)
#         note = DoyenDashboardService.resolve_secretary_note(note)
#         serializer = SecretaryNoteSerializer(note)
#         return success_response(data=serializer.data, message="Note marked as resolved")
#     except SecretaryNote.DoesNotExist:
#         return success_response(
#             message="Note not found", status_code=status.HTTP_404_NOT_FOUND
#         )
#     except Exception as e:
#         return success_response(
#             message=f"Error: {str(e)}",
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
