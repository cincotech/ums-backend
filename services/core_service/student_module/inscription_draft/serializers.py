from rest_framework import serializers
from .models import InscriptionDraft

class InscriptionDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = InscriptionDraft
        fields = [
            'id', 'user', 'session_id', 'current_step', 'form_data', 'title', 'created_at', 'updated_at', 'is_completed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
