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
    payment_status = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    modified_by = serializers.SerializerMethodField(read_only=True)

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
            "payment_status",
            "created_by",
            "modified_by",
            "modified_at",
        ]

    def get_created_by(self, obj):
        if obj.created_by:
            return {"id": str(obj.created_by.id), "email": obj.created_by.email}
        return None

    def get_modified_by(self, obj):
        if obj.modified_by:
            return {"id": str(obj.modified_by.id), "email": obj.modified_by.email}
        return None

    def get_payment_status(self, obj):
        return obj.payments_inscription.filter(
            paymentplan__feessheet__wording__wording_name__icontains="inscription",
            payment_status="verified",
        ).exists()

    # ---------------------------
    # CREATE METHOD
    # ---------------------------
    def create(self, validated_data):
        from django.utils import timezone
        from services.core_service.academic_module.university_app.models import (
            AcademicYear,
        )
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        student = validated_data.get("student")
        faculty_id = validated_data.pop("faculty_id", None)

        # Set current academic year if not provided
        if (
            "academic_year" not in validated_data
            or validated_data.get("academic_year") is None
        ):
            current_year = AcademicYear.objects.filter(
                start_date__lte=timezone.now(), end_date__gte=timezone.now()
            ).first()
            if current_year:
                validated_data["academic_year"] = current_year

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

            default_department = faculty.departments.filter(is_default=True).first()
            if default_department:
                default_class = default_department.classes.filter(
                    is_default=True
                ).first()
                if default_class:
                    class_fk = default_class

        # Create or get inscription
        existing = Inscription.objects.filter(
            student=student,
            academic_year=validated_data.get("academic_year"),
            class_fk=class_fk,
        ).first()

        if existing:
            for key, value in validated_data.items():
                setattr(existing, key, value)
            existing.save(user=user)
            inscription = existing
        else:
            inscription = Inscription(
                student=student,
                academic_year=validated_data.get("academic_year"),
                class_fk=class_fk,
                date_inscription=validated_data.get("date_inscription"),
                regist_status=validated_data.get("regist_status", "Pending"),
                withdrawal_date=validated_data.get("withdrawal_date"),
                is_year_close=validated_data.get("is_year_close", False),
            )
            inscription.save(user=user)

        # ---------------------------
        # Generate matricule if status is Active
        # ---------------------------
        if inscription.regist_status == "Active" and not student.matricule:
            inscription.generate_matricule()

        return inscription

    # ---------------------------
    # UPDATE METHOD
    # ---------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data.pop('faculty_id', None)
        validated_data.pop('class_fk_id', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save(user=user)
        return instance
