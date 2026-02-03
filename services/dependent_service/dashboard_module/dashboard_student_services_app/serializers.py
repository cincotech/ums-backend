from rest_framework import serializers


class PopulationDataSerializer(serializers.Serializer):
    """Serializer for student population data with age and gender breakdown"""

    id = serializers.IntegerField()
    faculty_abreviation = serializers.CharField(max_length=20)
    departement_name = serializers.CharField(max_length=255)
    class_name = serializers.CharField(max_length=50)
    sexe = serializers.CharField(max_length=1)
    less_than_nineteen = serializers.IntegerField()
    nineteen = serializers.IntegerField()
    twenty = serializers.IntegerField()
    twenty_one = serializers.IntegerField()
    twenty_two = serializers.IntegerField()
    twenty_three = serializers.IntegerField()
    twenty_four = serializers.IntegerField()
    twenty_five = serializers.IntegerField()
    twenty_six = serializers.IntegerField()
    twenty_seven = serializers.IntegerField()
    twenty_eight = serializers.IntegerField()
    twenty_nine = serializers.IntegerField()
    thirty = serializers.IntegerField()
    thirty_one = serializers.IntegerField()
    greater_than_thirty_one = serializers.IntegerField()
    total_female = serializers.IntegerField()
    total_male = serializers.IntegerField()
    student_count = serializers.IntegerField()


from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
    StudentStatusChange,
)


class DocumentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = [
            "id",
            "student",
            "document_type",
            "purpose",
            "status",
            "processed_by",
            "requested_at",
            "processed_at",
            "notes",
        ]


class AbsenceJustificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceJustification
        fields = [
            "id",
            "student",
            "absence_type",
            "start_date",
            "end_date",
            "reason",
            "supporting_documents",
            "status",
            "reviewed_by",
            "submitted_at",
            "reviewed_at",
        ]


class StudentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentActivity
        fields = [
            "id",
            "activity_type",
            "name",
            "description",
            "organizer",
            "participants",
            "start_date",
            "end_date",
            "location",
            "is_approved",
            "approved_by",
            "created_at",
        ]


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = [
            "id",
            "student",
            "scholarship_type",
            "provider",
            "amount",
            "academic_year",
            "is_active",
            "managed_by",
            "created_at",
        ]


class CounselingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselingSession
        fields = [
            "id",
            "session_type",
            "title",
            "description",
            "counselor",
            "participants",
            "scheduled_date",
            "duration_minutes",
            "location",
            "is_group_session",
            "created_at",
        ]


class StudentStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentStatusChange
        fields = [
            "id",
            "student",
            "inscription",
            "status_type",
            "reason",
            "supporting_documents",
            "requested_by",
            "approved_by",
            "approval_status",
            "effective_date",
            "requested_at",
            "processed_at",
            "notes",
        ]
