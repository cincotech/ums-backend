from rest_framework import serializers

from .models import Parent, Profession


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ["id", "profession_name"]


class ParentSerializer(serializers.ModelSerializer):
    profession_id = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all(), source="profession", write_only=True
    )

    class Meta:
        model = Parent
        fields = [
            "id",
            "parent_name",
            "parent_phone",
            "parent_email",
            "profession",
            "profession_id",
            "parent_type",
            "is_alive",
            "is_contact_person",
        ]
        read_only_fields = ["profession"]
