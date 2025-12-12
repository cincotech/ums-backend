from rest_framework import serializers

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.class_app.serializers import ClassSerializer
from services.core_service.academic_module.faculty_app.models import Faculty

from .models import Inscription


class InscriptionSerializer(serializers.ModelSerializer):
    # ---------------------------
    # Read-only student fields
    # ---------------------------
    student_first_name = serializers.CharField(
        read_only=True, source="student.user.first_name"
    )
    student_last_name = serializers.CharField(
        read_only=True, source="student.user.last_name"
    )
    student_matricule = serializers.CharField(
        read_only=True, source="student.matricule"
    )

    # ---------------------------
    # Class
    # ---------------------------
    class_fk = ClassSerializer(read_only=True)
    class_fk_id = serializers.UUIDField(
        required=False, allow_null=True, write_only=True
    )

    # ---------------------------
    # Academic year
    # ---------------------------
    year = serializers.CharField(read_only=True, source="academic_year.civil_year")

    # ---------------------------
    # Extra fields
    # ---------------------------
    faculty_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Inscription
        fields = [
            "id",
            "student",
            "academic_year",
            "class_fk",
            "class_fk_id",
            "date_inscription",
            "regist_status",
            "withdrawal_date",
            "is_year_close",
            "student_first_name",
            "student_last_name",
            "student_matricule",
            "year",
            "faculty_id",
        ]

    # ---------------------------
    # CREATE METHOD
    # ---------------------------
    def create(self, validated_data):
        student = validated_data.get("student")
        faculty_id = validated_data.pop("faculty_id", None)

        # Resolve class_fk
        class_fk_id = validated_data.pop("class_fk_id", None)
        if class_fk_id:
            try:
                class_fk = Class.objects.get(id=class_fk_id)
            except Class.DoesNotExist:
                raise serializers.ValidationError({"class_fk_id": "Invalid class ID"})
        else:
            class_fk = validated_data.get("class_fk")

        # Auto-resolve class if missing
        if not class_fk and faculty_id:
            faculty = Faculty.objects.get(id=faculty_id)
            first_department = faculty.departments.order_by("id").first()
            if first_department:
                class_fk = first_department.classes.order_by("id").first()

        # Create or get inscription
        inscription, created = Inscription.objects.get_or_create(
            student=student,
            academic_year=validated_data.get("academic_year"),
            class_fk=class_fk,
            defaults={
                "date_inscription": validated_data.get("date_inscription"),
                "regist_status": validated_data.get("regist_status", "Pending"),
                "withdrawal_date": validated_data.get("withdrawal_date"),
                "is_year_close": validated_data.get("is_year_close", False),
            },
        )

        # Update fields if already exists
        if not created:
            for key, value in validated_data.items():
                setattr(inscription, key, value)
            inscription.save()

        # ---------------------------
        # Generate matricule if status is Active
        # ---------------------------
        if inscription.regist_status == "Active" and not student.matricule:
            inscription.generate_matricule()

        return inscription
