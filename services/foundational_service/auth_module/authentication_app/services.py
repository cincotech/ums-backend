import logging
import secrets

from django_otp.plugins.otp_email.models import EmailDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from .utils import generate_custom_token, generate_qr_code_base64

logger = logging.getLogger(__name__)


def random_hex(length=8):
    return secrets.token_hex(length)


class UserService:

    def setup_email_2fa(self, user):
        """
        Sets up email-based 2FA for the user.
        Args:
            user (User): The user to set up 2FA for.
        Returns:
            EmailDevice: The created email 2FA device.
        """
        # Use only `user` as lookup key to avoid duplicates on MySQL
        # (get_or_create with multiple fields creates duplicates when any field differs)
        device, _ = EmailDevice.objects.update_or_create(
            user=user,
            defaults={
                "name": f"{user.email}_email_2fa",
                "email": user.email,
            },
        )
        logger.info(f"Email 2FA device created for user: {user.email}")
        return device

    def verify_email_2fa(self, user, otp_token):
        """
        Verifies the email 2FA OTP for the user.
        Args:
            user (User): The user to verify 2FA for.
            otp_token (str): The OTP to verify.
        Returns:
            bool: True if verification succeeds, False otherwise.
        Raises:
            EmailDevice.DoesNotExist: If no email 2FA device exists.
        """
        try:
            device = EmailDevice.objects.filter(user=user).first()
            if device is None:
                raise EmailDevice.DoesNotExist("Email 2FA device not found")
            if device.verify_token(otp_token):
                device.confirmed = True
                device.save()
                user.requires_2fa_email = True
                user.requires_2fa = True
                user.save()
                logger.info(f"Email 2FA verified for user: {user.email}")
                return True
            logger.error(
                f"Email 2FA verification failed for user: {user.email} - Invalid OTP"
            )
            return False
        except EmailDevice.DoesNotExist:
            logger.error(
                f"Email 2FA verification failed for user: {user.email} - No device found"
            )
            raise EmailDevice.DoesNotExist("Email 2FA device not found")

    def disable_email_2fa(self, user, otp_token=None):
        """
        Disables email 2FA for the user after OTP verification.
        Args:
            user (User): The user to disable 2FA for.
            otp_token (str, optional): The OTP to verify before disabling.
        Returns:
            bool: True if disabled successfully, False if OTP is required or invalid.
        Raises:
            EmailDevice.DoesNotExist: If no email 2FA device exists.
        """
        try:
            device = EmailDevice.objects.filter(user=user).first()
            if device is None:
                raise EmailDevice.DoesNotExist("Email 2FA device not found")
            if not otp_token:
                device.generate_challenge()
                logger.info(
                    f"Email 2FA disable initiated for user: {user.email} - OTP sent"
                )
                return False
            if device.verify_token(otp_token):
                device.confirmed = False
                device.save()
                user.requires_2fa_email = False
                user.requires_2fa = user.requires_2fa_qr or user.requires_2fa_static
                user.save()
                logger.info(f"Email 2FA disabled for user: {user.email}")
                return True
            logger.error(
                f"Email 2FA disable failed for user: {user.email} - Invalid OTP"
            )
            return False
        except EmailDevice.DoesNotExist:
            logger.error(
                f"Email 2FA disable failed for user: {user.email} - No device found"
            )
            raise EmailDevice.DoesNotExist("Email 2FA device not found")

    def setup_totp_2fa(self, user):
        """
        Sets up TOTP-based 2FA for the user without saving files.
        Returns (device, base64_qr_code)
        """
        device, _ = TOTPDevice.objects.get_or_create(
            user=user,
            name=f"{user.email}_totp_2fa",
        )

        qr_url = device.config_url
        qr_data = generate_qr_code_base64(qr_url)

        user.totp_secret_key = random_hex(15)
        user.save()

        logger.info(f"TOTP 2FA device created for user: {user.email}")
        return device, qr_data

    def verify_totp_2fa(self, user, otp_token):
        """
        Verifies the TOTP 2FA OTP for the user.
        Args:
            user (User): The user to verify 2FA for.
            otp_token (str): The OTP to verify.
        Returns:
            bool: True if verification succeeds, False otherwise.
        Raises:
            TOTPDevice.DoesNotExist: If no TOTP 2FA device exists.
        """

        try:
            device = TOTPDevice.objects.get(user=user)
            if device.verify_token(str(otp_token)):
                device.confirmed = True
                device.save()
                user.requires_2fa_qr = True
                user.requires_2fa = True
                user.save()
                logger.info(f"TOTP 2FA verified for user: {user.email}")
                return True
            logger.error(
                f"TOTP 2FA verification failed for user: {user.email} - Invalid OTP"
            )
            return False
        except TOTPDevice.DoesNotExist:
            logger.error(
                f"TOTP 2FA verification failed for user: {user.email} - No device found"
            )
            raise TOTPDevice.DoesNotExist("TOTP 2FA device not found")

    def disable_totp_2fa(self, user, secret_key):
        """
        Disables TOTP 2FA for the user after secret key verification.
        Args:
            user (User): The user to disable 2FA for.
            secret_key (str): The TOTP secret key to verify.
        Returns:
            bool: True if disabled successfully, False if secret key is invalid.
        Raises:
            TOTPDevice.DoesNotExist: If no TOTP 2FA device exists.
        """
        try:
            device = TOTPDevice.objects.get(user=user)
            if secret_key == user.totp_secret_key:
                device.delete()
                user.totp_secret_key = None
                user.requires_2fa_qr = False
                user.requires_2fa = user.requires_2fa_email or user.requires_2fa_static
                user.save()
                logger.info(f"TOTP 2FA disabled for user: {user.email}")
                return True
            logger.error(
                f"TOTP 2FA disable failed for user: {user.email} - Invalid secret key"
            )
            return False
        except TOTPDevice.DoesNotExist:
            logger.error(
                f"TOTP 2FA disable failed for user: {user.email} - No device found"
            )
            raise TOTPDevice.DoesNotExist("TOTP 2FA device not found")

    def setup_static_2fa(self, user):
        """
        Sets up static token-based 2FA for the user.
        Args:
            user (User): The user to set up 2FA for.
        Returns:
            list: The generated static tokens.
        """
        device, _ = StaticDevice.objects.get_or_create(
            user=user, name=f"{user.email}_static_2fa"
        )
        tokens = []
        for _ in range(10):
            token = generate_custom_token()
            StaticToken.objects.create(device=device, token=token)
            tokens.append(token)
        logger.info(f"Static 2FA tokens created for user: {user.email}")
        return tokens

    def verify_static_2fa(self, user, otp_token):
        """
        Verifies the static 2FA token for the user.
        Args:
            user (User): The user to verify 2FA for.
            otp_token (str): The static token to verify.
        Returns:
            bool: True if verification succeeds, False otherwise.
        Raises:
            StaticDevice.DoesNotExist: If no static 2FA device exists.
        """
        try:
            device = StaticDevice.objects.get(user=user)
            if device.verify_token(otp_token):
                user.requires_2fa_static = True
                user.requires_2fa = True
                user.save()
                logger.info(f"Static 2FA verified for user: {user.email}")
                return True
            logger.error(
                f"Static 2FA verification failed for user: {user.email} - Invalid token"
            )
            return False
        except StaticDevice.DoesNotExist:
            logger.error(
                f"Static 2FA verification failed for user: {user.email} - No device found"
            )
            raise StaticDevice.DoesNotExist("Static 2FA device not found")

    def disable_static_2fa(self, user):
        """
        Disables static 2FA for the user.
        Args:
            user (User): The user to disable 2FA for.
        Returns:
            bool: True if disabled successfully.
        Raises:
            StaticDevice.DoesNotExist: If no static 2FA device exists.
        """
        try:
            device = StaticDevice.objects.get(user=user)
            device.delete()
            user.requires_2fa_static = False
            user.requires_2fa = user.requires_2fa_email or user.requires_2fa_qr
            user.save()
            logger.info(f"Static 2FA disabled for user: {user.email}")
            return True
        except StaticDevice.DoesNotExist:
            logger.error(
                f"Static 2FA disable failed for user: {user.email} - No device found"
            )
            raise StaticDevice.DoesNotExist("Static 2FA device not found")

    def disable_2fa(self, user):
        """
        Disables all 2FA methods for the user.
        Args:
            user (User): The user to disable 2FA for.
        """
        device = EmailDevice.objects.filter(user=user)
        device.confirmed = False
        device.save()
        TOTPDevice.objects.filter(user=user).delete()
        StaticDevice.objects.filter(user=user).delete()
        user.requires_2fa = False
        user.requires_2fa_qr = False
        user.requires_2fa_email = False
        user.requires_2fa_static = False
        user.totp_secret_key = None
        user.save()
        logger.info(f"All 2FA disabled for user: {user.email}")

    def verify_email_otp(self, user, otp_token):
        """
        Verifies the email the user.
        Args:
            user (User): The user to verify email for.
            otp_token (str): The OTP to verify.
        Returns:
            bool: True if verification succeeds, False otherwise.
        Raises:
            EmailDevice.DoesNotExist: If no email device exists.
        """
        try:
            device = EmailDevice.objects.filter(user=user).first()
            if device is None:
                raise EmailDevice.DoesNotExist("Email 2FA device not found")
            if device.verify_token(otp_token):
                device.confirmed = False
                device.save()
                logger.info(f"Email 2FA verified for user: {user.email}")
                return True
            logger.error(
                f"Email 2FA verification failed for user: {user.email} - Invalid OTP"
            )
            return False
        except EmailDevice.DoesNotExist:
            logger.error(
                f"Email 2FA verification failed for user: {user.email} - No device found"
            )
            raise EmailDevice.DoesNotExist("Email 2FA device not found")

    def verify_user_email(self, user):
        """
        Marks the user's email as verified.
        Args:
            user (User): The user to verify.
        """
        if user.email_verified:
            return f"The email {user.email} is already verified."
        user.email_verified = True
        user.save()
        return f"The email {user.email} has been successfully verified."
