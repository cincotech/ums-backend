import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class TwoFactorEmailService:
    """Service class to handle 2FA email sending with templates"""

    @staticmethod
    def send_2fa_setup_email(recipient_email, user_name, otp_code, setup_type="email"):
        """
        Send 2FA setup email to user

        Args:
            recipient_email (str): User's email address
            user_name (str): User's name for personalization
            otp_code (str): The OTP code to send
            setup_type (str): Type of 2FA setup (email, totp, static)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject_map = {
                "email": "Setup Email Two-Factor Authentication",
                "totp": "Setup Authenticator App Two-Factor Authentication",
                "static": "Your Backup Codes for Two-Factor Authentication",
            }

            subject = (
                f"{subject_map.get(setup_type, '2FA Setup')} - {settings.COMPANY_NAME}"
            )

            context = {
                "user_name": user_name,
                "otp_code": otp_code,
                "setup_type": setup_type,
                "company_name": getattr(settings, "COMPANY_NAME", "Our Company"),
                "support_email": getattr(
                    settings, "SUPPORT_EMAIL", "support@example.com"
                ),
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
        """
        Send 2FA verification email for login or other actions

        Args:
            recipient_email (str): User's email address
            user_name (str): User's name
            otp_code (str): The OTP code to send
            action (str): Type of action (login, disable, verify)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject_map = {
                "login": "Your Login Verification Code",
                "disable": "Confirm Disable Two-Factor Authentication",
                "verify": "Verify Your Two-Factor Authentication",
            }

            subject = f"{subject_map.get(action, 'Verification Code')} - {settings.COMPANY_NAME}"

            context = {
                "user_name": user_name,
                "otp_code": otp_code,
                "action": action,
                "company_name": getattr(settings, "COMPANY_NAME", "Our Company"),
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
        """
        Send static backup codes to user

        Args:
            recipient_email (str): User's email address
            user_name (str): User's name
            backup_codes (list): List of backup codes

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"Your Backup Codes - {settings.COMPANY_NAME}"

            context = {
                "user_name": user_name,
                "backup_codes": backup_codes,
                "company_name": getattr(settings, "COMPANY_NAME", "Our Company"),
                "support_email": getattr(
                    settings, "SUPPORT_EMAIL", "support@example.com"
                ),
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
