from rest_framework import serializers

from .models import Inscription


class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
        fields = [
            "id",
            "student",
            "academic_year",
            "class_fk",
            "date_inscription",
            "regist_status",
            "withdrawal_date",
            "is_year_close",
        ]
