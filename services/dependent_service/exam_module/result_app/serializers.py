from rest_framework import serializers

from .models import CompiledResult, Result, Session, Supplement


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "session_name"]


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["id", "course", "inscription", "session", "mark"]


class CompiledResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompiledResult
        fields = [
            "id",
            "results",
            "inscription",
            "average_mark",
            "status",
            "is_promoted",
        ]


class SupplementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplement
        fields = [
            "id",
            "inscription",
            "course",
            "validation",
            "validation_date",
            "mark",
        ]
