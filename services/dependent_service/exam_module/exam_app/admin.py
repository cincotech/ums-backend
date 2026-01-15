from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ExamType, Exam, ExamRoom, ExamSupervisor

@admin.register(ExamType)
class ExamTypeAdmin(ModelAdmin):
    list_display = ['exam_type_name', 'description']
    search_fields = ['exam_type_name']

@admin.register(Exam)
class ExamAdmin(ModelAdmin):
    list_display = ['course', 'exam_type', 'exam_date', 'start_time', 'status']
    list_filter = ['status', 'exam_type', 'academic_year']
    search_fields = ['course__course_name']
    date_hierarchy = 'exam_date'

@admin.register(ExamRoom)
class ExamRoomAdmin(ModelAdmin):
    list_display = ['exam', 'room', 'range_student']
    list_filter = ['room']

@admin.register(ExamSupervisor)
class ExamSupervisorAdmin(ModelAdmin):
    list_display = ['exam_room', 'supervisor']
    list_filter = ['supervisor']
