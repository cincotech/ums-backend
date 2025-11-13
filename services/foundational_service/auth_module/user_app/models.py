import logging
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from services.foundational_service.auth_module.authentication_app.services import (
    UserService,
)
from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.country_app.models import Country

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates a new user with the specified email and password.
        Args:
            email (str): The user's email address.
            password (str, optional): The user's password.
            **extra_fields: Additional fields for the user model.
        Returns:
            User: The created user instance.
        Raises:
            ValueError: If the email is not provided.
        """
        if not email:
            logger.error("User creation failed: Email is required")
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        logger.info(f"User created with email: {email}")
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates a new superuser with the specified email and password.
        Args:
            email (str): The superuser's email address.
            password (str, optional): The superuser's password.
            **extra_fields: Additional fields for the user model.
        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("email_verified", True)
        user = self.create_user(email, password, **extra_fields)
        logger.info(f"Superuser created with email: {email}")
        return user


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        MALE = "M", "Homme"
        FEMALE = "F", "Femme"
        OTHER = "O", "Autre"

    class MaritalStatusChoices(models.TextChoices):
        SINGLE = "S", "Célibataire"
        MARRIED = "M", "Marié"
        DIVORCED = "D", "Divorcé"
        WIDOWED = "W", "Veuf"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gender = models.CharField(
        max_length=1, choices=GenderChoices.choices, blank=True, null=True
    )
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    nationality = models.ForeignKey(
        Country, on_delete=models.RESTRICT, related_name="nationals", null=True
    )
    residence = models.ManyToManyField(Colline, related_name="residences", blank=True)
    marital_status = models.CharField(
        max_length=1, choices=MaritalStatusChoices.choices, blank=True, null=True
    )
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="users", null=True, blank=True
    )
    email_verified = models.BooleanField(default=False)
    requires_2fa = models.BooleanField(default=False)
    requires_2fa_qr = models.BooleanField(default=False)
    requires_2fa_email = models.BooleanField(default=False)
    requires_2fa_static = models.BooleanField(default=False)
    totp_secret_key = models.CharField(max_length=32, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    spoken_languages = models.JSONField(default=list, blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None

    def enable_user_email_2fa(self):
        """
        Enables email-based 2FA for the user.
        """
        UserService().setup_email_2fa(self)
        self.requires_2fa = True
        self.requires_2fa_email = True
        self.save()
        logger.info(f"Email 2FA enabled for user: {self.email}")

    def enable_user_totp_2fa(self):
        """
        Enables TOTP-based 2FA for the user.
        Returns:
            dict: QR code data for TOTP setup.
        """
        device, qr_data = UserService().setup_totp_2fa(self)
        self.requires_2fa = True
        self.requires_2fa_qr = True
        self.save()
        logger.info(f"TOTP 2FA enabled for user: {self.email}")
        return qr_data

    def enable_user_static_2fa(self):
        """
        Enables static token-based 2FA for the user.
        Returns:
            list: Generated static tokens.
        """
        tokens = UserService().setup_static_2fa(self)
        self.requires_2fa = True
        self.requires_2fa_static = True
        self.save()
        logger.info(f"Static 2FA enabled for user: {self.email}")
        return tokens

    def disable_user_2fa(self):
        """
        Disables all 2FA methods for the user.
        """
        self.requires_2fa = False
        self.requires_2fa_qr = False
        self.requires_2fa_email = False
        self.requires_2fa_static = False
        self.totp_secret_key = None
        self.save()
        logger.info(f"All 2FA disabled for user: {self.email}")

    def verify_user_email(self):
        """
        Marks the user's email as verified.
        """
        self.email_verified = True
        self.save()
        logger.info(f"Email verified for user: {self.email}")
