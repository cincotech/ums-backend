from rest_framework import serializers
from .models import InscriptionDraft

class InscriptionDraftSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='user.email', read_only=True)
    modified_by_email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InscriptionDraft
        fields = [
            'id', 'user', 'created_by_email', 'modified_by_email',
            'session_id', 'current_step', 'form_data', 'title',
            'created_at', 'updated_at', 'is_completed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'created_by_email', 'modified_by_email']

    def get_modified_by_email(self, obj):
        if obj.modified_by:
            return obj.modified_by.email
        return None
