from rest_framework import serializers

from .models import Parent, Profession


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ["id", "profession_name"]


class ParentSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    profession_id = serializers.UUIDField(write_only=True)

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
