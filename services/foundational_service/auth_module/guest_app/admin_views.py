from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.response_handler import error_response, success_response
from core.views import BaseViewSet

from .admin_serializers import (
    AccountRequestDocumentSerializer,
    AccountRequestListItemSerializer,
    AccountRequestSerializer,
    AccountRequestStatsSerializer,
    ReviewAccountSerializer,
    UpdateDocumentStatusSerializer,
)
from .models import GuestDocument, GuestNotification, GuestRequest


class AccountRequestViewSet(BaseViewSet):
    """Admin ViewSet for managing account requests"""

    queryset = GuestRequest.objects.select_related(
        "user", "requested_role", "reviewed_by"
    ).prefetch_related("documents")
    permission_classes = [IsAuthenticated]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "requested_role__name",
    ]
    filterset_fields = ["status", "requested_role", "profile_submitted"]
    ordering_fields = ["created_at", "profile_submitted_at", "reviewed_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return AccountRequestListItemSerializer
        elif self.action == "stats":
            return AccountRequestStatsSerializer
        elif self.action == "review":
            return ReviewAccountSerializer
        elif self.action == "update_document":
            return UpdateDocumentStatusSerializer
        return AccountRequestSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get account request statistics"""
        stats_data = {
            "total_requests": GuestRequest.objects.count(),
            "total_account_types": GuestRequest.objects.values("requested_role")
            .distinct()
            .count(),
            "pending_review": GuestRequest.objects.filter(status="pending").count(),
            "total_documents": GuestDocument.objects.count(),
            "rejected_documents": GuestDocument.objects.filter(
                status="rejected"
            ).count(),
            "rejected_accounts": GuestRequest.objects.filter(status="rejected").count(),
        }
        serializer = AccountRequestStatsSerializer(stats_data)
        return success_response(
            data=serializer.data, message="Stats retrieved successfully"
        )

    @action(detail=True, methods=["patch"])
    def mark_under_review(self, request, pk=None):
        """Mark account request as under review"""
        guest_request = self.get_object()
        guest_request.status = "under_review"
        guest_request.save()

        GuestNotification.objects.create(
            guest_request=guest_request,
            type="info",
            title="Application Under Review",
            message="Your application is now being reviewed by our team.",
        )

        return success_response(message="Marked as under review")

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """Review and approve/reject account request"""
        guest_request = self.get_object()
        serializer = ReviewAccountSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(message="Invalid data", errors=serializer.errors)

        review_status = serializer.validated_data["status"]
        documents_data = serializer.validated_data.get("documents", {})
        rejection_reason = serializer.validated_data.get("rejection_reason")

        # Update document statuses
        for doc_id, doc_data in documents_data.items():
            try:
                document = guest_request.documents.get(id=doc_id)
                document.status = doc_data["status"]
                document.rejection_reason = doc_data.get("comment")
                if document.status == "accepted":
                    document.verified_at = timezone.now()
                    document.verified_by = request.user
                document.save()
            except GuestDocument.DoesNotExist:
                continue

        # Update request status
        guest_request.status = review_status
        guest_request.reviewed_at = timezone.now()
        guest_request.reviewed_by = request.user
        if rejection_reason:
            guest_request.rejection_reason = rejection_reason
        guest_request.save()

        # Create notification
        if review_status == "approved":
            guest_request.user.role = guest_request.requested_role
            guest_request.user.save()

            GuestNotification.objects.create(
                guest_request=guest_request,
                type="success",
                title="Application Approved",
                message=f"Congratulations! Your application for {guest_request.requested_role.name} has been approved.",
            )
        else:
            GuestNotification.objects.create(
                guest_request=guest_request,
                type="error",
                title="Application Rejected",
                message=f"Your application has been rejected. Reason: {rejection_reason}",
            )

        result_serializer = AccountRequestSerializer(
            guest_request, context={"request": request}
        )
        return success_response(
            data=result_serializer.data, message=f"Request {review_status}"
        )

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        """Get all documents for a request"""
        guest_request = self.get_object()
        documents = guest_request.documents.all()
        serializer = AccountRequestDocumentSerializer(
            documents, many=True, context={"request": request}
        )
        return success_response(data=serializer.data, message="Documents retrieved")

    @action(
        detail=True, methods=["patch"], url_path="documents/(?P<document_id>[^/.]+)"
    )
    def update_document(self, request, pk=None, document_id=None):
        """Update document status"""
        guest_request = self.get_object()
        serializer = UpdateDocumentStatusSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(message="Invalid data", errors=serializer.errors)

        try:
            document = guest_request.documents.get(id=document_id)
            doc_status = serializer.validated_data["status"]
            comment = serializer.validated_data.get("comment")

            document.status = doc_status
            if comment:
                document.rejection_reason = comment
            if doc_status == "accepted":
                document.verified_at = timezone.now()
                document.verified_by = request.user

            document.save()

            # Create notification
            GuestNotification.objects.create(
                guest_request=guest_request,
                type="info" if doc_status == "accepted" else "warning",
                title=f"Document {doc_status.title()}",
                message=f"Your {document.get_type_display()} has been {doc_status}.",
                document=document,
            )

            result_serializer = AccountRequestDocumentSerializer(
                document, context={"request": request}
            )
            return success_response(
                data=result_serializer.data, message="Document updated"
            )
        except GuestDocument.DoesNotExist:
            return error_response(message="Document not found", status_code=404)
