from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from core.response_handler import success_response, error_response
from .models import GuestRequest, GuestDocument, GuestNotification, RoleDocumentRequirement
from .serializers import (
    GuestUserSerializer,
    GuestProfileSerializer,
    GuestDocumentSerializer,
    GuestNotificationSerializer,
    DocumentRequirementSerializer,
    GuestDashboardStatsSerializer,
    DocumentUploadSerializer,
)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def guest_profile(request):
    """Get or update guest profile"""
    try:
        guest_request, created = GuestRequest.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = GuestUserSerializer(guest_request, context={'request': request})
            
            # Get stats
            total_docs = RoleDocumentRequirement.objects.filter(role=guest_request.requested_role).count()
            uploaded_docs = guest_request.documents.count()
            verified_docs = guest_request.documents.filter(status='verified').count()
            rejected_docs = guest_request.documents.filter(status='rejected').count()
            
            profile_fields = ['phone', 'birth_date', 'address']
            filled_fields = sum(1 for field in profile_fields if getattr(guest_request, field))
            profile_completion = int((filled_fields / len(profile_fields)) * 100) if profile_fields else 0
            
            stats = {
                'profile_completion': profile_completion,
                'documents_uploaded': uploaded_docs,
                'documents_required': total_docs,
                'documents_verified': verified_docs,
                'documents_rejected': rejected_docs,
            }
            
            # Get document requirements
            requirements = RoleDocumentRequirement.objects.filter(role=guest_request.requested_role)
            requirements_serializer = DocumentRequirementSerializer(requirements, many=True)
            
            return success_response(data={
                'user': serializer.data,
                'stats': stats,
                'document_requirements': requirements_serializer.data
            }, message='Profile retrieved successfully')
        
        elif request.method == 'PUT':
            serializer = GuestProfileSerializer(guest_request, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                if not guest_request.profile_submitted:
                    guest_request.profile_submitted = True
                    guest_request.profile_submitted_at = timezone.now()
                    guest_request.save()
                return success_response(data=serializer.data, message='Profile updated successfully')
            return error_response(message='Invalid data', errors=serializer.errors)
    
    except GuestRequest.DoesNotExist:
        return error_response(message='Guest request not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_status(request):
    """Get account status"""
    try:
        guest_request = GuestRequest.objects.get(user=request.user)
        return success_response(data={'status': guest_request.status}, message='Status retrieved')
    except GuestRequest.DoesNotExist:
        return error_response(message='Guest request not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request):
    """Get notifications"""
    try:
        guest_request = GuestRequest.objects.get(user=request.user)
        notifications = guest_request.notifications.all()
        serializer = GuestNotificationSerializer(notifications, many=True)
        return success_response(data=serializer.data, message='Notifications retrieved')
    except GuestRequest.DoesNotExist:
        return error_response(message='Guest request not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        guest_request = GuestRequest.objects.get(user=request.user)
        notification = guest_request.notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return success_response(message='Notification marked as read')
    except GuestNotification.DoesNotExist:
        return error_response(message='Notification not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    try:
        guest_request = GuestRequest.objects.get(user=request.user)
        guest_request.notifications.update(is_read=True)
        return success_response(message='All notifications marked as read')
    except GuestRequest.DoesNotExist:
        return error_response(message='Guest request not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def documents(request):
    """Get or upload documents"""
    try:
        guest_request = GuestRequest.objects.get(user=request.user)
        
        if request.method == 'GET':
            docs = guest_request.documents.all()
            serializer = GuestDocumentSerializer(docs, many=True, context={'request': request})
            return success_response(data=serializer.data, message='Documents retrieved')
        
        elif request.method == 'POST':
            serializer = DocumentUploadSerializer(data=request.data)
            if serializer.is_valid():
                file = serializer.validated_data['file']
                doc_type = serializer.validated_data['type']
                
                document = GuestDocument.objects.create(
                    guest_request=guest_request,
                    name=file.name,
                    type=doc_type,
                    file=file,
                    file_size=file.size,
                    mime_type=file.content_type
                )
                
                # Create notification
                GuestNotification.objects.create(
                    guest_request=guest_request,
                    type='success',
                    title='Document Uploaded',
                    message=f'Your {document.get_type_display()} has been uploaded successfully',
                    document=document
                )
                
                result_serializer = GuestDocumentSerializer(document, context={'request': request})
                return success_response(data=result_serializer.data, message='Document uploaded successfully')
            return error_response(message='Invalid data', errors=serializer.errors)
    
    except GuestRequest.DoesNotExist:
        return error_response(message='Guest request not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, document_id):
    """Delete a document"""
    try:
        guest_request = GuestRequest.objects.get(user=request.user)
        document = guest_request.documents.get(id=document_id)
        document.file.delete()
        document.delete()
        return success_response(message='Document deleted successfully')
    except GuestDocument.DoesNotExist:
        return error_response(message='Document not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_support(request):
    """Contact support"""
    try:
        guest_request = GuestRequest.objects.get(user=request.user)
        message = request.data.get('message')
        
        if not message:
            return error_response(message='Message is required')
        
        # Create notification for support
        GuestNotification.objects.create(
            guest_request=guest_request,
            type='info',
            title='Support Message Sent',
            message='Your message has been sent to support. We will respond shortly.'
        )
        
        return success_response(message='Message sent to support')
    except GuestRequest.DoesNotExist:
        return error_response(message='Guest request not found', status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_document_requirements(request, role_id):
    """Get document requirements for a specific role"""
    try:
        requirements = RoleDocumentRequirement.objects.filter(role_id=role_id)
        serializer = DocumentRequirementSerializer(requirements, many=True)
        return success_response(data=serializer.data, message='Requirements retrieved successfully')
    except Exception as e:
        return error_response(message=f'Error: {str(e)}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
