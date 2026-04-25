from django.shortcuts import render
from rest_framework import permissions
from core.views import BaseViewSet
from .models import InscriptionDraft
from .serializers import InscriptionDraftSerializer

# Create your views here.

class InscriptionDraftViewSet(BaseViewSet):
    serializer_class = InscriptionDraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InscriptionDraft.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)
