import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailService:
    """Comprehensive email service for UMS authentication module"""

    @staticmethod
    def _send_email(subject, template_name, context, recipient_email):
        """Base method to send emails"""
        try:
            context.update(
                {
                    "company_name": getattr(
                        settings, "COMPANY_NAME", "University Management System"
                    ),
                    "support_email": getattr(
                        settings, "SUPPORT_EMAIL", "support@ums.com"
                    ),
                    "site_url": getattr(
                        settings, "SITE_URL", "https://ums.example.com"
                    ),
                    "year": timezone.now().year,
                }
            )

            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Email sent to {recipient_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    @staticmethod
    def send_welcome_email(user, otp_code=None, otp_expiry=None):
        """Send welcome email with optional OTP"""
        subject = f"Welcome to {getattr(settings, 'COMPANY_NAME', 'UMS')}"
        context = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "otp": otp_code,
            "otp_expiry": otp_expiry,
            "login_url": getattr(
                settings, "LOGIN_URL", "https://ums.example.com/login"
            ),
            "current_year": timezone.now().year,
        }
        return EmailService._send_email(
            subject, "emails/ums_send_register_otp.html", context, user.email
        )

    @staticmethod
    def send_otp_email(user, otp_code, purpose="authentication", valid_minutes=10):
        """Send OTP verification email"""
        subject = f"Your OTP for {purpose.capitalize()}"
        context = {
            "user": user,
            "otp": otp_code,
            "purpose": purpose.capitalize(),
            "valid_minutes": valid_minutes,
        }
        return EmailService._send_email(
            subject, "emails/ums_send_otp.html", context, user.email
        )

    @staticmethod
    def send_password_reset_email(user, otp_code, expiry_minutes=10):
        """Send password reset email"""
        subject = "Password Reset Request"
        context = {
            "user_name": user.get_full_name() or user.email,
            "otp_code": otp_code,
            "expiry_minutes": expiry_minutes,
        }
        return EmailService._send_email(
            subject, "emails/password_reset.html", context, user.email
        )

    @staticmethod
    def send_password_changed_email(user):
        """Send password changed confirmation email"""
        subject = "Password Changed Successfully"
        context = {
            "user_name": user.get_full_name() or user.email,
            "change_date": timezone.now().strftime("%B %d, %Y at %I:%M %p"),
        }
        return EmailService._send_email(
            subject, "emails/password_changed.html", context, user.email
        )


class TwoFactorEmailService:
    """Service class to handle 2FA email sending with templates"""

    @staticmethod
    def send_2fa_setup_email(recipient_email, user_name, otp_code, setup_type="email"):
        """Send 2FA setup email to user"""
        try:
            subject_map = {
                "email": "Setup Email Two-Factor Authentication",
                "totp": "Setup Authenticator App Two-Factor Authentication",
                "static": "Your Backup Codes for Two-Factor Authentication",
            }

            subject = f"{subject_map.get(setup_type, '2FA Setup')} - {getattr(settings, 'COMPANY_NAME', 'UMS')}"

            context = {
                "user_name": user_name,
                "otp_code": otp_code,
                "setup_type": setup_type,
                "company_name": getattr(
                    settings, "COMPANY_NAME", "University Management System"
                ),
                "support_email": getattr(settings, "SUPPORT_EMAIL", "support@ums.com"),
                "expiry_minutes": getattr(settings, "OTP_EXPIRY_MINUTES", 10),
            }

            template_name = f"emails/2fa_{setup_type}_setup.html"
            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"2FA {setup_type} setup email sent to {recipient_email}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to send 2FA setup email to {recipient_email}: {str(e)}"
            )
            return False

    @staticmethod
    def send_2fa_verification_email(
        recipient_email, user_name, otp_code, action="login"
    ):
        """Send 2FA verification email for login or other actions"""
        try:
            subject_map = {
                "login": "Your Login Verification Code",
                "disable": "Confirm Disable Two-Factor Authentication",
                "verify": "Verify Your Two-Factor Authentication",
            }

            subject = f"{subject_map.get(action, 'Verification Code')} - {getattr(settings, 'COMPANY_NAME', 'UMS')}"

            context = {
                "user_name": user_name,
                "otp_code": otp_code,
                "action": action,
                "company_name": getattr(
                    settings, "COMPANY_NAME", "University Management System"
                ),
                "expiry_minutes": getattr(settings, "OTP_EXPIRY_MINUTES", 10),
            }

            html_content = render_to_string("emails/2fa_verification.html", context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(
                f"2FA verification email sent to {recipient_email} for {action}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to send 2FA verification email to {recipient_email}: {str(e)}"
            )
            return False

    @staticmethod
    def send_static_backup_codes(recipient_email, user_name, backup_codes):
        """Send static backup codes to user"""
        try:
            subject = f"Your Backup Codes - {getattr(settings, 'COMPANY_NAME', 'UMS')}"

            context = {
                "user_name": user_name,
                "backup_codes": backup_codes,
                "company_name": getattr(
                    settings, "COMPANY_NAME", "University Management System"
                ),
                "support_email": getattr(settings, "SUPPORT_EMAIL", "support@ums.com"),
            }

            html_content = render_to_string("emails/2fa_static_codes.html", context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Static backup codes sent to {recipient_email}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to send static backup codes to {recipient_email}: {str(e)}"
            )
            return False
