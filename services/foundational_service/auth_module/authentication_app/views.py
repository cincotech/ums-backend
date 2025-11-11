# Create your views here.
import logging

from django.contrib.auth import authenticate
from django.db import IntegrityError
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from services.foundational_service.auth_module.user_app.models import Role, User

from .serializers import (
    RegisterSerializer,
    RoleSerializer,
    SendEmailOTPSerializer,
    TokenRefreshSerializer,
    UserSerializer,
    Verify2FASerializer,
    VerifyEmailOTPSerializer,
)
from .services import UserService
from .utils import get_serializer_error_message

logger = logging.getLogger(__name__)

# Initialize service classes for business logic
user_service = UserService()


class AvailableRoleView(APIView):
    """
    Retrieve all active roles available in the system.
    Accessible to anyone (no authentication required).
    """

    permission_classes = [AllowAny]

    def get(self, request):
        # Fetch active roles using RoleService
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        logger.info("Fetched active roles")
        return Response(
            {
                "type": "success",
                "message": "Active roles retrieved successfully",
                "status": status.HTTP_200_OK,
                "data": serializer.data,
            }
        )


class RegisterView(APIView):
    """
    Register a new user and send an OTP for email verification.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Check if email already exists
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            logger.error(f"Registration failed: Email {email} already exists")
            return Response(
                {
                    "type": "error",
                    "typeError": "EmailAlreadyExists",
                    "message": "Email already exists",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate request data
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            logger.error(f"Registration failed: {error_message}")
            return Response(
                {
                    "type": "error",
                    "message": error_message,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        try:
            # Setup email 2FA device
            device = user_service.setup_email_2fa(user)
            device.generate_challenge()
            logger.info(f"User registered and OTP sent to {email}")
            return Response(
                {
                    "type": "success",
                    "typeError": "EmailNotVerified",
                    "message": "User registered and OTP sent to your email",
                    "status": status.HTTP_201_CREATED,
                    "data": {"email": user.email},
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "message": f"Failed to send OTP: {str(e)}",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendEmailOTPView(APIView):
    """
    Send an OTP to the user's email for verification or 2FA.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailOTPSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            logger.error(f"Send OTP failed: {error_message}")
            return Response(
                {
                    "type": "error",
                    "message": error_message,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            device = user_service.setup_email_2fa(user)
            device.generate_challenge()
            logger.info(f"OTP sent to {email}")
            return Response(
                {
                    "type": "success",
                    "message": "OTP sent to your email",
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            logger.error(f"Send OTP failed: User with email {email} not found")
            return Response(
                {
                    "type": "error",
                    "typeError": "UserNotFound",
                    "message": "User not found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Send OTP failed: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "DeviceError",
                    "message": "Failed to setup email OTP device",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class EmailOTPVerificationView(APIView):
    """
    Verify the user's email using an OTP.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailOTPSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            logger.error(f"Email OTP verification failed: {error_message}")
            return Response(
                {
                    "type": "error",
                    "message": error_message,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        otp_token = serializer.validated_data["otp"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_email_otp(user, otp_token):
                message = user_service.verify_user_email(user)
                logger.info(f"Email verified for {email}")
                return Response(
                    {
                        "type": "success",
                        "message": message,
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(f"Email OTP verification failed: Invalid OTP for {email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidOTP",
                    "message": "Invalid OTP",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            logger.error(
                f"Email OTP verification failed: User with email {email} not found"
            )
            return Response(
                {
                    "type": "error",
                    "typeError": "UserNotFound",
                    "message": "User not found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Email OTP verification failed: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "VerificationError",
                    "message": f"Invalid email or no OTP device {str(e)}",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    """
    Authenticate a user and handle 2FA if required.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        if not User.objects.filter(email=email).exists():
            logger.error(f"Login failed: No account found for email {email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "UserNotFound",
                    "message": "No account found with this email. Please create an account.",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        user = authenticate(username=email, password=password)
        if not user:
            logger.error(f"Login failed: Invalid credentials for {email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidCredentials",
                    "message": "Incorrect password. If you forgot your password, please reset it.",
                    "status": status.HTTP_401_UNAUTHORIZED,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.email_verified:
            try:
                device = user_service.setup_email_2fa(user)
                device.generate_challenge()
                logger.info(f"Login failed: Email not verified for {email}, OTP sent")
                return Response(
                    {
                        "type": "error",
                        "typeError": "EmailNotVerified",
                        "message": "Your email is not verified. A verification email has been sent.",
                        "status": status.HTTP_400_BAD_REQUEST,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                logger.error(
                    f"Login failed: Failed to send verification OTP for {email}: {str(e)}"
                )
                return Response(
                    {
                        "type": "error",
                        "typeError": "VerificationFailed",
                        "message": "Failed to send verification email. Please try again later.",
                        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        if user.requires_2fa:
            required_methods = []

            if user.requires_2fa_qr:
                required_methods.append("totp")

            if user.requires_2fa_email:
                required_methods.append("email")
                try:
                    device = user_service.setup_email_2fa(user)
                    device.generate_challenge()
                except Exception as e:
                    logger.error(
                        f"Login failed: Unable to generate email OTP for {email}: {str(e)}"
                    )
                    return Response(
                        {
                            "type": "error",
                            "typeError": "OTPGenerationFailed",
                            "message": "We couldn't send the verification code to your email. Please try again later.",
                            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            if user.requires_2fa_static:
                required_methods.append("static")

            logger.info(
                f"Login requires 2FA for {email}. Required methods: {required_methods}"
            )
            return Response(
                {
                    "type": "info",
                    "message": (
                        "A verification code has been sent to your email. Please enter the code to continue."
                        if user.requires_2fa_email
                        else "Two-factor authentication is required to proceed."
                    ),
                    "status": status.HTTP_403_FORBIDDEN,
                    "data": {
                        "requires_2fa": True,
                        "email": user.email,
                        "methods": required_methods,
                    },
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        logger.info(f"Login successful for {email}")
        return Response(
            {
                "type": "success",
                "message": "Login successful",
                "status": status.HTTP_200_OK,
                "data": {
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_200_OK,
        )


class SetEmail2FAView(APIView):
    """
    Set up email-based 2FA for the authenticated user.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.requires_2fa_email:
            try:
                device = user_service.setup_email_2fa(user)
                device.generate_challenge()
                logger.info(f"Email 2FA setup initiated for {user.email}")
                return Response(
                    {
                        "type": "success",
                        "message": "Email 2FA setup initiated. OTP sent to your email.",
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                logger.error(f"Email 2FA setup failed for {user.email}: {str(e)}")
                return Response(
                    {
                        "type": "error",
                        "message": f"Failed to setup email 2FA: {str(e)}",
                        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        logger.error(f"Email 2FA setup failed: Already enabled for {user.email}")
        return Response(
            {
                "type": "error",
                "typeError": "Email2FAAlready",
                "message": "Email 2FA already set up",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SetTOTP2FAView(APIView):
    """
    Set up TOTP-based 2FA for the authenticated user and return a QR code.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.requires_2fa_qr:

            device, qr_data = user_service.setup_totp_2fa(user)
            logger.info(f"TOTP 2FA setup initiated for {user.email}")
            return Response(
                {
                    "type": "success",
                    "message": "Scan this QR code with your authenticator app",
                    "status": status.HTTP_200_OK,
                    "data": {
                        "qr_code": qr_data["base64_image"],
                        "qr_code_url": qr_data["qr_code_url"],
                        "config_url": device.config_url,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "type": "error",
                "typeError": "TOTP2FAAlready",
                "message": "TOTP 2FA already set up",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SetStatic2FAView(APIView):
    """
    Set up static token-based 2FA for the authenticated user.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.requires_2fa_static:
            try:
                tokens = user_service.setup_static_2fa(user)
                logger.info(f"Static 2FA setup for {user.email}")
                return Response(
                    {
                        "type": "success",
                        "message": "Static 2FA set up successfully",
                        "status": status.HTTP_200_OK,
                        "data": {"backup_codes": tokens},
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                logger.error(f"Static 2FA setup failed for {user.email}: {str(e)}")
                return Response(
                    {
                        "type": "error",
                        "message": f"Failed to setup static 2FA: {str(e)}",
                        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        logger.error(f"Static 2FA setup failed: Already enabled for {user.email}")
        return Response(
            {
                "type": "error",
                "typeError": "Static2FAAlready",
                "message": "Static 2FA already set up",
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyEmail2FAView(APIView):
    """
    Verify email 2FA OTP for the authenticated user.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_token = request.data.get("otp")
        try:
            if user_service.verify_email_2fa(user, otp_token):
                logger.info(f"Email 2FA verified for {user.email}")
                return Response(
                    {
                        "type": "success",
                        "message": "Email 2FA verified successfully",
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(f"Email 2FA verification failed: Invalid OTP for {user.email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidOTP",
                    "message": "Invalid OTP",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Email 2FA verification failed for {user.email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "Email2FANotSet",
                    "message": "Email 2FA not set up",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyTOTP2FAView(APIView):
    """
    Verify TOTP 2FA OTP for the authenticated user.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_token = request.data.get("otp")
        try:
            if user_service.verify_totp_2fa(user, otp_token):
                logger.info(f"TOTP 2FA verified for {user.email}")
                return Response(
                    {
                        "type": "success",
                        "message": "TOTP 2FA verified successfully",
                        "status": status.HTTP_200_OK,
                        "data": {"secret_key": user.totp_secret_key},
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(f"TOTP 2FA verification failed: Invalid OTP for {user.email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidOTP",
                    "message": "Invalid OTP",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"TOTP 2FA verification failed for {user.email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "TOTP2FANotSet",
                    "message": "TOTP 2FA not set up",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyStatic2FAView(APIView):
    """
    Verify static 2FA token for the authenticated user.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_token = request.data.get("otp")
        try:
            if user_service.verify_static_2fa(user, otp_token):
                logger.info(f"Static 2FA verified for {user.email}")
                return Response(
                    {
                        "type": "success",
                        "message": "Static 2FA verified successfully",
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(
                f"Static 2FA verification failed: Invalid token for {user.email}"
            )
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidOTP",
                    "message": "Invalid token",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Static 2FA verification failed for {user.email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "Static2FANotSet",
                    "message": "Static 2FA not set up",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DisableEmail2FAView(APIView):
    """
    Disable email 2FA for the authenticated user after OTP verification.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_token = request.data.get("otp")
        try:
            if user_service.disable_email_2fa(user, otp_token):
                logger.info(f"Email 2FA disabled for {user.email}")
                return Response(
                    {
                        "type": "success",
                        "message": "Email 2FA disabled successfully",
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            logger.info(f"Email 2FA disable initiated: OTP sent to {user.email}")
            return Response(
                {
                    "type": "success",
                    "typeError": "NoOTP",
                    "message": "Please provide the OTP sent to your email to disable 2FA",
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Email 2FA disable failed for {user.email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "Email2FANotEnabled",
                    "message": "Email 2FA not enabled",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DisableTOTP2FAView(APIView):
    """
    Disable TOTP 2FA for the authenticated user after secret key verification.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        secret_key = request.data.get("secret_key")
        try:
            if not secret_key:
                logger.error(
                    f"TOTP 2FA disable failed: No secret key provided for {user.email}"
                )
                return Response(
                    {
                        "type": "error",
                        "typeError": "NoSecretKey",
                        "message": "Please provide your 16-character secret key to disable TOTP 2FA",
                        "status": status.HTTP_400_BAD_REQUEST,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user_service.disable_totp_2fa(user, secret_key):
                logger.info(f"TOTP 2FA disabled for {user.email}")
                return Response(
                    {
                        "type": "success",
                        "message": "TOTP 2FA disabled successfully",
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(
                f"TOTP 2FA disable failed: Invalid secret key for {user.email}"
            )
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidSecretKey",
                    "message": "Invalid secret key",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"TOTP 2FA disable failed for {user.email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "TOTP2FANotEnabled",
                    "message": "TOTP 2FA not enabled",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DisableStatic2FAView(APIView):
    """
    Disable static 2FA for the authenticated user.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            user_service.disable_static_2fa(user)
            logger.info(f"Static 2FA disabled for {user.email}")
            return Response(
                {
                    "type": "success",
                    "message": "Static 2FA disabled successfully",
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Static 2FA disable failed for {user.email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "typeError": "Static2FANotEnabled",
                    "message": "Static 2FA not enabled",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class Email2FALoginView(APIView):
    """
    Verify email 2FA OTP and complete login with JWT tokens.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = Verify2FASerializer(data=request.data)
        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            logger.error(f"Email 2FA login failed: {error_message}")
            return Response(
                {
                    "type": "error",
                    "message": error_message,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_token = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_email_2fa(user, otp_token):
                refresh = RefreshToken.for_user(user)
                logger.info(f"Email 2FA login successful for {email}")
                return Response(
                    {
                        "type": "success",
                        "message": "Email 2FA verified successfully",
                        "status": status.HTTP_200_OK,
                        "data": {
                            "user": UserSerializer(user).data,
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(f"Email 2FA login failed: Invalid OTP for {email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidOTP",
                    "message": "Invalid OTP",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            logger.error(f"Email 2FA login failed: User with email {email} not found")
            return Response(
                {
                    "type": "error",
                    "typeError": "UserNotFound",
                    "message": "User not found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Email 2FA login failed for {email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "message": "Invalid user or device",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class TOTP2FALoginView(APIView):
    """
    Verify TOTP 2FA OTP and complete login with JWT tokens.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = Verify2FASerializer(data=request.data)
        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            logger.error(f"TOTP 2FA login failed: {error_message}")
            return Response(
                {
                    "type": "error",
                    "message": error_message,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_token = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_totp_2fa(user, otp_token):
                refresh = RefreshToken.for_user(user)
                logger.info(f"TOTP 2FA login successful for {email}")
                return Response(
                    {
                        "type": "success",
                        "message": "TOTP 2FA verified and login successfully",
                        "status": status.HTTP_200_OK,
                        "data": {
                            "user": UserSerializer(user).data,
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(f"TOTP 2FA login failed: Invalid OTP for {email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidOTP",
                    "message": "Invalid OTP",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            logger.error(f"TOTP 2FA login failed: User with email {email} not found")
            return Response(
                {
                    "type": "error",
                    "typeError": "UserNotFound",
                    "message": "User not found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"TOTP 2FA login failed for {email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "message": "Invalid user or device",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class Static2FALoginView(APIView):
    """
    Verify static 2FA token and complete login with JWT tokens.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = Verify2FASerializer(data=request.data)
        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            logger.error(f"Static 2FA login failed: {error_message}")
            return Response(
                {
                    "type": "error",
                    "message": error_message,
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_token = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_static_2fa(user, otp_token):
                refresh = RefreshToken.for_user(user)
                logger.info(f"Static 2FA login successful for {email}")
                return Response(
                    {
                        "type": "success",
                        "message": "Static 2FA verified and login successfully",
                        "status": status.HTTP_200_OK,
                        "data": {
                            "user": UserSerializer(user).data,
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            logger.error(f"Static 2FA login failed: Invalid token for {email}")
            return Response(
                {
                    "type": "error",
                    "typeError": "InvalidOTP",
                    "message": "Invalid static code",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            logger.error(f"Static 2FA login failed: User with email {email} not found")
            return Response(
                {
                    "type": "error",
                    "typeError": "UserNotFound",
                    "message": "User not found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Static 2FA login failed for {email}: {str(e)}")
            return Response(
                {
                    "type": "error",
                    "message": "Invalid user or device",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class TokenRefreshView(APIView):
    """
    Refresh JWT tokens using a valid refresh token.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            logger.error(f"Token refresh failed: {error_message}")
            return Response(
                {
                    "type": "error",
                    "message": error_message,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken(serializer.validated_data["refresh"])
        logger.info("Token refreshed successfully")
        return Response(
            {
                "type": "success",
                "message": "Token refreshed successfully",
                "status": status.HTTP_200_OK,
                "data": {"access": str(refresh.access_token), "refresh": str(refresh)},
            },
            status=status.HTTP_200_OK,
        )


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        try:
            role = self.get_object()
            role.delete()
            return Response(
                {"message": f"Role '{role.name}' deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Role.DoesNotExist:
            return Response(
                {"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError:
            user_count = role.users.count()
            return Response(
                {
                    "error": f"Cannot delete role '{role.name}' because it is associated with {user_count} user(s). "
                    "Please reassign or remove these users before deleting."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"], url_path="reassign")
    def reassign(self, request, pk=None):
        try:
            old_role = self.get_object()
            new_role_id = request.data.get("new_role_id")
            new_role = Role.objects.get(id=new_role_id) if new_role_id else None
            users = old_role.users.all()
            user_count = users.count()
            users.update(role=new_role)
            return Response(
                {
                    "message": f"Reassigned {user_count} user(s) from role '{old_role.name}' to '{new_role.name if new_role else 'None'}'."
                },
                status=status.HTTP_200_OK,
            )
        except Role.DoesNotExist:
            return Response(
                {"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND
            )


# ViewSet for managing user data
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        # Return only the current user's data
        return User.objects.filter(id=self.request.user.id)

    @action(detail=True, methods=["post"], url_path="verify-password")
    def verify_password(self, request, pk=None):
        user = self.get_object()

        # Allow only the user themselves or admins
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN
            )

        password = request.data.get("password", "")
        if user.check_password(password):
            return Response({"is_own": True}, status=status.HTTP_200_OK)
        return Response({"is_own": False}, status=status.HTTP_200_OK)


class ResetPasswordWithOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        token = request.data.get("otp")
        new_password = request.data.get("new_password")

        try:
            user = User.objects.get(email=email)
            device = EmailDevice.objects.get(user=user, email=email)

            if device.verify_token(token):
                user.set_password(new_password)
                user.save()
                return Response(
                    {"message": "Password reset successful"}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        except (User.DoesNotExist, EmailDevice.DoesNotExist):
            return Response(
                {"error": "Invalid email or OTP"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
