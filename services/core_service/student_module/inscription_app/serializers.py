from rest_framework import serializers

from services.core_service.academic_module.class_app.serializers import ClassSerializer

from .models import Inscription


class InscriptionSerializer(serializers.ModelSerializer):
    student_first_name = serializers.CharField(
        read_only=True, source="student.user.first_name"
    )
    student_last_name = serializers.CharField(
        read_only=True, source="student.user.last_name"
    )
    student_matricule = serializers.CharField(
        read_only=True, source="student.matricule"
    )
    class_fk = ClassSerializer(read_only=True)
    year = serializers.CharField(read_only=True, source="academic_year.civil_year")
    class_fk_id = serializers.UUIDField(required=False)

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
        ]
