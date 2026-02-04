from rest_framework import serializers
from .models import Program
from services.core_service.academic_module.faculty_app.serializers import FacultySerializer


class ProgramSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.UUIDField(write_only=True)  
    class Meta:
        model = Program
        fields = ['id', 'faculty', 'faculty_id', 'presentation', 'content', 'admission_conditions', 'prerequisites', 'internship', 'duration', 'career_opportunities', 'is_active']