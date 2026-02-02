from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.views import APIView

from core.response_handler import success_response, validate_serializer
from services.dependent_service.scheduling_module.serializers import (
    ActivityReportSerializer,
    AttendanceSerializer,
    ScheduleSlotSerializer,
    TimetableSerializer,
)

from .models import ActivityReport, Attendance, ScheduleSlot, Timetable


# --- ScheduleSlot Views ---
class ScheduleSlotListCreateAPIView(APIView):
    def get(self, request):
        slots = ScheduleSlot.objects.all()
        serializer = ScheduleSlotSerializer(slots, many=True)
        return success_response(
            data=serializer.data, message="Slots retrieved successfully"
        )

    def post(self, request):
        serializer = ScheduleSlotSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Slot created successfully",
            status_code=status.HTTP_201_CREATED,
        )


# --- Timetable Views ---
class TimetableListCreateAPIView(APIView):
    def get(self, request):
        timetables = Timetable.objects.all()
        serializer = TimetableSerializer(timetables, many=True)
        return success_response(
            data=serializer.data, message="Timetables retrieved successfully"
        )

    def post(self, request):
        serializer = TimetableSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Timetable created successfully",
            status_code=status.HTTP_201_CREATED,
        )


# --- Attendance Views ---
class AttendanceListCreateAPIView(APIView):
    def get(self, request):
        attendances = Attendance.objects.all()
        serializer = AttendanceSerializer(attendances, many=True)
        return success_response(
            data=serializer.data, message="Attendances retrieved successfully"
        )

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Attendance recorded successfully",
            status_code=status.HTTP_201_CREATED,
        )


# --- ActivityReport Views ---
class ActivityReportListCreateAPIView(APIView):
    def get(self, request):
        reports = ActivityReport.objects.all()
        serializer = ActivityReportSerializer(reports, many=True)
        return success_response(
            data=serializer.data, message="Reports retrieved successfully"
        )

    def post(self, request):
        serializer = ActivityReportSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Report created successfully",
            status_code=status.HTTP_201_CREATED,
        )
