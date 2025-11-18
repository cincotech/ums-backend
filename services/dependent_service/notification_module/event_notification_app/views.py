from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
)
from .email_service import send_notification_email


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications with CRUD operations and custom actions.

    Endpoints:
    - GET /notifications/ - List all notifications
    - POST /notifications/ - Create a new notification
    - GET /notifications/{id}/ - Retrieve a specific notification
    - PUT /notifications/{id}/ - Update a notification
    - PATCH /notifications/{id}/ - Partial update of a notification
    - DELETE /notifications/{id}/ - Delete a notification
    - GET /notifications/sent/ - Filter sent notifications
    - GET /notifications/failed/ - Filter failed notifications
    - POST /notifications/{id}/mark_as_sent/ - Mark notification as sent
    - POST /notifications/{id}/mark_as_failed/ - Mark notification as failed
    """

    queryset = Notification.objects.all().order_by("-sent_at")
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["delivery_status", "email", "telephone"]
    search_fields = ["email", "telephone", "message"]
    ordering_fields = ["sent_at", "delivery_status"]
    ordering = ["-sent_at"]

    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == "list":
            return NotificationListSerializer
        elif self.action == "create":
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        """
        Send email automatically when creating a notification
        """
        notification = serializer.save()
        if notification.email:
            email_sent = send_notification_email(notification.email, notification.message)
            if email_sent:
                notification.delivery_status = 'sent'
                notification.sent_at = timezone.now()
            else:
                notification.delivery_status = 'failed'
            notification.save()

    @action(detail=False, methods=["get"], url_path="sent")
    def sent_notifications(self, request):
        """
        Get all notifications with 'sent' delivery status
        """
        notifications = self.queryset.filter(delivery_status="sent")
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="failed")
    def failed_notifications(self, request):
        """
        Get all notifications with 'failed' delivery status
        """
        notifications = self.queryset.filter(delivery_status="failed")
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="mark-as-sent")
    def mark_as_sent(self, request, pk=None):
        """
        Mark a notification as sent
        """
        notification = self.get_object()
        notification.delivery_status = "sent"
        notification.sent_at = timezone.now()
        notification.save()

        serializer = self.get_serializer(notification)
        return Response(
            {
                "message": "Notification marked as sent successfully",
                "notification": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="mark-as-failed")
    def mark_as_failed(self, request, pk=None):
        """
        Mark a notification as failed
        """
        notification = self.get_object()
        notification.delivery_status = "failed"
        notification.save()

        serializer = self.get_serializer(notification)
        return Response(
            {
                "message": "Notification marked as failed",
                "notification": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="by-email/(?P<email>[^/.]+)")
    def by_email(self, request, email=None):
        """
        Get all notifications for a specific email address
        """
        notifications = self.queryset.filter(email__iexact=email)
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-phone/(?P<phone>[^/.]+)")
    def by_phone(self, request, phone=None):
        """
        Get all notifications for a specific phone number
        """
        notifications = self.queryset.filter(telephone=phone)
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
