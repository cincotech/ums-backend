from rest_framework import permissions, status
from rest_framework.response import Response

from core.views import BaseViewSet

from .models import InscriptionDraft
from .serializers import InscriptionDraftSerializer

# Create your views here.


class InscriptionDraftViewSet(BaseViewSet):
    serializer_class = InscriptionDraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # By default exclude soft-deleted drafts from queries. If the client
        # includes the `include_deleted=true` query param, return all drafts
        # so the client can detect server-side deletions and reconcile local state.
        qs = InscriptionDraft.objects.filter(user=self.request.user)
        include_deleted = self.request.query_params.get("include_deleted")
        if include_deleted and include_deleted.lower() in {"1", "true", "yes"}:
            return qs
        return qs.exclude(status="deleted")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete: mark the draft as deleted instead of removing from DB."""
        draft = self.get_object()
        draft.status = "deleted"
        draft.modified_by = request.user
        draft.save()
        return Response(
            {"message": "Draft marked as deleted."}, status=status.HTTP_200_OK
        )
