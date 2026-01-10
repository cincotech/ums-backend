from rest_framework import serializers

from services.core_service.academic_module.teacher_app.models import Attribution


class AttributionValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribution
        fields = "__all__"
        read_only_fields = ["id", "validated_by", "validation_date"]


class AttributionValidationDecisionSerializer(serializers.Serializer):
    validation_status = serializers.ChoiceField(choices=["approved", "rejected"])
    comments = serializers.CharField(required=False, allow_blank=True)


class TeacherValidationSerializer(serializers.Serializer):
    """
    Serializer pour valider le teacher principal d'une attribution.
    Si le principal_teacher est approved → status_principal_teacher = "Accepted" 
    et status_substitute_teacher = "Refused" automatiquement.
    Si le principal_teacher est rejected → status_principal_teacher = "Refused".
    """
    principal_teacher_status = serializers.ChoiceField(
        choices=["approved", "rejected"],
        required=True
    )
    comments = serializers.CharField(required=False, allow_blank=True)

    def validate_principal_teacher_status(self, value):
        """Valider que le status est soit approved soit rejected."""
        valid_choices = ["approved", "rejected"]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Le statut doit être l'une des valeurs suivantes: {valid_choices}"
            )
        return value
