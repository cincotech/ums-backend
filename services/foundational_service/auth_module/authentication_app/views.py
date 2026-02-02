# Create your views here.
import logging

from django.contrib.auth import authenticate
from django_otp.plugins.otp_email.models import EmailDevice
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from core.audit import log_login, log_security_event
from core.response_handler import error_response, success_response, validate_serializer
from core.views import BaseViewSet
from services.core_service.academic_module.university_app.models import University
from services.foundational_service.auth_module.user_app.models import Role, User

from .email_service import TwoFactorEmailService
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
from .utils import send_otp_email, send_register_otp
from .filters import UserFilter

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
            return error_response(
                message="Email already exists",
                errors="EmailAlreadyExists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Validate request data
        serializer = RegisterSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error

        user = serializer.save()
        password = request.data.get("password")
        user.set_password(password)
        guest_role, _ = Role.objects.get_or_create(name="guest")
        upg, created = University.objects.get_or_create(
            university_name="Université Polytechnique de Gitega", university_abrev="UPG"
        )
        user.university = upg
        user.role = guest_role
        user.save()

        # log_user_action(user, "create", f"User registered: {email}", "User", user.id)
        try:
            # Setup email 2FA device
            device = user_service.setup_email_2fa(user)
            device.generate_token()
            send_register_otp(device)
            logger.info(f"User registered and OTP sent to {email}")
            return success_response(
                data={"email": user.email},
                message="User registered and OTP sent to your email",
                status_code=status.HTTP_201_CREATED,
                extra={"typeError": "EmailNotVerified"},
            )
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return error_response(
                message=f"Failed to send OTP: {str(e)}",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendEmailOTPView(APIView):
    """@action(detail=False, methods=['post'])
    def transfer(self, request):
        serializer = PaymentTransferSerializer(data=request.data)
        if serializer.is_valid():
            try:
                payment = serializer.create_payment_transfer()
                payment_service = PaymentProviderService()
                result = payment_service.send_transfer(payment)
                if result:
                    return APIResponse.success(
                        data=PaymentSerializer(payment, context={'request': request}).data,
                        message="Transfer initiated successfully"
                    )
                return APIResponse.error(message="Failed to initiate transfer")
            except Exception as e:
                return APIResponse.error(message=f"Error processing transfer: {str(e)}")
        return APIResponse.error(message="Invalid input data", errors=serializer.errors)

        Send an OTP to the user's email for verification or 2FA.
        Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailOTPSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            device = user_service.setup_email_2fa(user)
            device.generate_token()
            send_otp_email(device, purpose="Authentication", valid_minutes=10)
            logger.info(f"OTP sent to {email}")
            return success_response(message="OTP sent to your email")
        except User.DoesNotExist:
            logger.error(f"Send OTP failed: User with email {email} not found")
            return error_response(
                message=f"Send OTP failed: User with email {email} not found",
                errors="NotFund",
            )
        except Exception as e:
            logger.error(f"Send OTP failed: {str(e)}")
            return error_response(message=f"Send OTP failed: {str(e)}", errors=str(e))


class EmailOTPVerificationView(APIView):
    """
    Verify the user's email using an OTP.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailOTPSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error
        email = serializer.validated_data["email"]
        otp_token = serializer.validated_data["otp"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_email_otp(user, otp_token):
                message = user_service.verify_user_email(user)
                logger.info(f"Email verified for {email}")
                # log_user_action(request, "update", f"Email verified: {email}", "User", user.id)
                return success_response(message=message)
            logger.error(f"Email OTP verification failed: Invalid OTP for {email}")
            return error_response(
                message=f"Email OTP verification failed: Invalid OTP for {email}",
                errors="InvalidOTP",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            logger.error(
                f"Email OTP verification failed: User with email {email} not found"
            )
            return error_response(
                message=f"Email OTP verification failed: User with email {email} not found",
                errors="UserNotFound",
            )

        except Exception as e:
            logger.error(f"Email OTP verification failed: {str(e)}")
            return error_response(
                message=f"Invalid email or no OTP device {str(e)}",
                errors="VerificationError",
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
        print(request.data)

        if not User.objects.filter(email=email).exists():
            logger.error(f"Login failed: No account found for email {email}")
            return error_response(
                message="No account found with this email. Please create an account.",
                status_code=status.HTTP_404_NOT_FOUND,
                errors="UserNotFound",
            )

        user = authenticate(username=email, password=password)
        if not user:
            logger.error(f"Login failed: Invalid credentials for {email}")
            log_security_event(
                request,
                "failed_login",
                f"Failed login attempt: {email}",
                severity="warning",
                success=False,
            )
            return error_response(
                message="Incorrect password. If you forgot your password, please reset it.",
                errors="InvalidCredentials",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if not user.email_verified:
            try:
                device = user_service.setup_email_2fa(user)
                device.generate_token()
                send_otp_email(device, purpose="Authentication", valid_minutes=10)
                logger.info(f"Login failed: Email not verified for {email}, OTP sent")
                return success_response(
                    message="Your email is not verified. A verification email has been sent.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    extra={
                        "typeError": "EmailNotVerified",
                    },
                )
            except Exception as e:
                logger.error(
                    f"Login failed: Failed to send verification OTP for {email}: {str(e)}"
                )
                return error_response(
                    message="Failed to send verification email. Please try again later.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    errors="VerificationFailed",
                )
        if user.requires_2fa:
            required_methods = []

            if user.requires_2fa_qr:
                required_methods.append("totp")

            if user.requires_2fa_email:
                required_methods.append("email")
                try:
                    device = user_service.setup_email_2fa(user)
                    device.generate_token()
                    send_otp_email(
                        device, purpose="Authentication Otp", valid_minutes=10
                    )
                except Exception as e:
                    logger.error(
                        f"Login failed: Unable to generate email OTP for {email}: {str(e)}"
                    )
                    return error_response(
                        errors="OTPGenerationFailed",
                        message="We couldn't send the verification code to your email. Please try again later.",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            if user.requires_2fa_static:
                required_methods.append("static")

            logger.info(
                f"Login requires 2FA for {email}. Required methods: {required_methods}"
            )
            message = (
                "A verification code has been sent to your email. Please enter the code to continue."
                if user.requires_2fa_email
                else "Two-factor authentication is required to proceed."
            )
            data = {
                "requires_2fa": True,
                "email": user.email,
                "methods": required_methods,
            }
            return success_response(
                data=data,
                message=message,
                status_code=status.HTTP_403_FORBIDDEN,
                extra={"typeError": "requires_2fa"},
            )

        refresh = RefreshToken.for_user(user)
        logger.info(f"Login successful for {email}")
        log_login(request, user, success=True)
        return success_response(
            data={
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            message="Login successful",
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
                device.generate_token()
                otp_code = device.token
                # Send setup email
                TwoFactorEmailService.send_2fa_setup_email(
                    recipient_email=user.email,
                    user_name=user.get_full_name() or user.email,
                    otp_code=otp_code,
                    setup_type="email",
                )
                logger.info(f"Email 2FA setup initiated for {user.email}")
                # log_user_action(request, "update", f"Email 2FA setup initiated", "User", user.id)
                return success_response(
                    message="Email 2FA setup initiated. OTP sent to your email."
                )

            except Exception as e:
                logger.error(f"Email 2FA setup failed for {user.email}: {str(e)}")
                return error_response(
                    message=f"Failed to setup email 2FA: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        logger.error(f"Email 2FA setup failed: Already enabled for {user.email}")
        return error_response(
            message="Email 2FA already set up",
            errors="Email2FAAlready",
            status_code=status.HTTP_400_BAD_REQUEST,
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
            return success_response(
                message="Scan this QR code with your authenticator app",
                data={"qr_code": qr_data, "config_url": device.config_url},
            )
        return error_response(
            message="TOTP 2FA already set up", errors="TOTP2FAAlready"
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
                return success_response(
                    message="Static 2FA set up successfully",
                    data={"backup_codes": tokens},
                )

            except Exception as e:
                logger.error(f"Static 2FA setup failed for {user.email}: {str(e)}")
                return error_response(message=f"Failed to setup static 2FA: {str(e)}")
        logger.error(f"Static 2FA setup failed: Already enabled for {user.email}")
        return error_response(
            message="Static 2FA already set up", errors="Static2FAAlready"
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
                # log_user_action(request, "update", f"Email 2FA verified", "User", user.id)
                return success_response(message="Email 2FA verified successfully")
            logger.error(f"Email 2FA verification failed: Invalid OTP for {user.email}")
            return error_response(message="Invalid OTP", errors="InvalidOTP")
        except Exception as e:
            logger.error(f"Email 2FA verification failed for {user.email}: {str(e)}")
            return error_response(
                message="Email 2FA not set up", errors="Email2FANotSet"
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
                return success_response(
                    message="TOTP 2FA verified successfully",
                    data={"secret_key": user.totp_secret_key},
                )
            logger.error(f"TOTP 2FA verification failed: Invalid OTP for {user.email}")
            return error_response(message="Invalid OTP", errors="InvalidOTP")

        except Exception as e:
            logger.error(f"TOTP 2FA verification failed for {user.email}: {str(e)}")
            return error_response(message="TOTP 2FA not set up", errors="TOTP2FANotSet")


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
                return success_response(message="Static 2FA verified successfully")
            logger.error(
                f"Static 2FA verification failed: Invalid token for {user.email}"
            )
            return error_response(message="Invalid token", errors="InvalidOTP")
        except Exception as e:
            logger.error(f"Static 2FA verification failed for {user.email}: {str(e)}")
            return error_response(
                message="Static 2FA not set up", errors="Static2FANotSet"
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
                return success_response(message="Email 2FA disabled successfully")
            logger.info(f"Email 2FA disable initiated: OTP sent to {user.email}")
            return success_response(
                messag="Please provide the OTP sent to your email to disable 2FA",
                extra={"typeError": "NoOTP"},
            )

        except Exception as e:
            logger.error(f"Email 2FA disable failed for {user.email}: {str(e)}")
            return error_response(
                message="Email 2FA not enabled", errors="Email2FANotEnabled"
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
                return error_response(
                    message="Please provide your 16-character secret key to disable TOTP 2FA",
                    errors="NoSecretKey",
                )
            if user_service.disable_totp_2fa(user, secret_key):
                logger.info(f"TOTP 2FA disabled for {user.email}")
                return success_response(message="TOTP 2FA disabled successfully")
            logger.error(
                f"TOTP 2FA disable failed: Invalid secret key for {user.email}"
            )
            return error_response(
                message="Invalid secret key", errors="InvalidSecretKey"
            )

        except Exception as e:
            logger.error(f"TOTP 2FA disable failed for {user.email}: {str(e)}")
            return error_response(
                message="TOTP 2FA not enabled", errors="TOTP2FANotEnabled"
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
            return success_response(message="Static 2FA disabled successfully")

        except Exception as e:
            logger.error(f"Static 2FA disable failed for {user.email}: {str(e)}")
            return error_response(
                errors="Static2FANotEnabled",
                message="Static 2FA not enabled",
            )


class Email2FALoginView(APIView):
    """
    Verify email 2FA OTP and complete login with JWT tokens.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = Verify2FASerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error

        otp_token = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_email_2fa(user, otp_token):
                refresh = RefreshToken.for_user(user)
                logger.info(f"Email 2FA login successful for {email}")
                return success_response(
                    message="Email 2FA verified successfully now you have to login",
                    data={
                        "user": UserSerializer(user).data,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                )

            logger.error(f"Email 2FA login failed: Invalid OTP for {email}")
            return error_response(
                message=f"Email 2FA login failed: Invalid OTP for {email}",
                errors="InvalidOTP",
            )

        except User.DoesNotExist:
            logger.error(f"Email 2FA login failed: User with email {email} not found")
            return error_response(
                message=f"Email 2FA login failed: User with email {email} not found",
                errors="UserNotFound",
            )

        except Exception as e:
            logger.error(f"Email 2FA login failed for {email}: {str(e)}")
            return error_response(
                message=f"Email 2FA login failed for {email}: {str(e)}"
            )


class TOTP2FALoginView(APIView):
    """
    Verify TOTP 2FA OTP and complete login with JWT tokens.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = Verify2FASerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error

        otp_token = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_totp_2fa(user, otp_token):
                refresh = RefreshToken.for_user(user)
                logger.info(f"TOTP 2FA login successful for {email}")
                return success_response(
                    message="TOTP 2FA verified and login successfully",
                    data={
                        "user": UserSerializer(user).data,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                )

            logger.error(f"TOTP 2FA login failed: Invalid OTP for {email}")
            return error_response(
                message=f"TOTP 2FA login failed: Invalid OTP for {email}",
                errors="InvalidOTP",
            )

        except User.DoesNotExist:
            logger.error(f"TOTP 2FA login failed: User with email {email} not found")
            return error_response(
                message=f"TOTP 2FA login failed: User with email {email} not found",
                errors="UserNotFound",
            )

        except Exception as e:
            logger.error(f"TOTP 2FA login failed for {email}: {str(e)}")
            return error_response(
                message=f"TOTP 2FA login failed for {email}: {str(e)}"
            )


class Static2FALoginView(APIView):
    """
    Verify static 2FA token and complete login with JWT tokens.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = Verify2FASerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error

        otp_token = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if user_service.verify_static_2fa(user, otp_token):
                refresh = RefreshToken.for_user(user)
                logger.info(f"Static 2FA login successful for {email}")
                return success_response(
                    message="Static 2FA verified and login successfully",
                    data={
                        "user": UserSerializer(user).data,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                )
            logger.error(f"Static 2FA login failed: Invalid token for {email}")
            return error_response(
                message=f"Static 2FA login failed: Invalid token for {email}",
                errors="InvalidOTP",
            )

        except User.DoesNotExist:
            logger.error(f"Static 2FA login failed: User with email {email} not found")
            return error_response(
                message=f"Static 2FA login failed: User with email {email} not found",
                errors="UserNotFound",
            )

        except Exception as e:
            logger.error(f"Static 2FA login failed for {email}: {str(e)}")
            return error_response(
                message=f"Static 2FA login failed for {email}: {str(e)}"
            )


class TokenRefreshView(APIView):
    """
    Refresh JWT tokens using a valid refresh token.
    Accessible to anyone.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        error = validate_serializer(serializer)
        if error:
            return error

        refresh = RefreshToken(serializer.validated_data["refresh"])
        logger.info("Token refreshed successfully")
        return success_response(
            message="Token refreshed successfully",
            data={"access": str(refresh.access_token), "refresh": str(refresh)},
        )


# ViewSet for managing user data
class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['email', 'first_name', 'last_name', 'phone_number', 'role__name']
    ordering_fields = ['email', 'first_name', 'last_name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role.name == "admin":
            return User.objects.all()

        # Case 1: student_service → return student + guest
        if user.role.name == "student_service":
            return User.objects.filter(role__name__in=["student", "guest"])

        # Case 2: everyone else → return only their own data
        return User.objects.filter(id=user.id)

    # Override get_serializer to always pass request in context
    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        GET /users/me/ -> Return current authenticated user's data
        """
        # import time
        # time.sleep(8)
        serializer = self.get_serializer(request.user)
        return success_response(
            message=" current authenticated user's data",
            data=serializer.data,
        )

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
        print(request.data)

        try:
            user = User.objects.get(email=email)
            device = EmailDevice.objects.get(user=user)

            if device.verify_token(token):
                user.set_password(new_password)
                user.save()
                log_security_event(
                    request,
                    "password_reset",
                    f"Password reset for user: {email}",
                    severity="info",
                )
                return success_response(message="Password reset successful")
            return error_response(errors="InvalidOTP", message="Invalid  OTP")

        except (User.DoesNotExist, EmailDevice.DoesNotExist):
            return error_response(
                message="Invalid email or OTP", errors="Invalid email or OTP"
            )

        except Exception:
            return error_response(
                message="Something went wrong",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            # Get all tokens of this user
            tokens = OutstandingToken.objects.filter(user=user)

            # Blacklist all of them
            for token in tokens:
                try:
                    BlacklistedToken.objects.get(token=token)
                except BlacklistedToken.DoesNotExist:
                    BlacklistedToken.objects.create(token=token)

            return success_response(message="Logged out successfully")

        except Exception:
            return error_response(message="Something went wrong")
