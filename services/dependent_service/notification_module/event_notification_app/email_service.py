from django.conf import settings
from django.core.mail import send_mail


def send_notification_email(email, message):
    """
    Send notification email to the specified email address
    """
    try:
        send_mail(
            subject="Notification UMS",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
