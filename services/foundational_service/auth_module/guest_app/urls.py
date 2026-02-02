from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import admin_views
from . import views

router = DefaultRouter()
router.register(r'account-requests', admin_views.AccountRequestViewSet, basename='account-request')

urlpatterns = [
    path('', include(router.urls)),
    path('profile', views.guest_profile, name='guest-profile'),
    path('status', views.account_status, name='guest-status'),
    path('notifications', views.notifications, name='guest-notifications'),
    path('notifications/<uuid:notification_id>/read', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/read-all', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('documents', views.documents, name='guest-documents'),
    path('documents/<uuid:document_id>', views.delete_document, name='delete-document'),
    path('support', views.contact_support, name='contact-support'),
    path('roles/<uuid:role_id>/requirements', views.role_document_requirements, name='role-requirements'),
]
