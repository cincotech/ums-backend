import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv()


def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if value is None:
        raise Exception(f"Set the {var_name} environment variable")
    return value


SECRET_KEY = get_env_variable(
    "DJANGO_SECRET_KEY", "django-insecure-dev-key-change-in-production"
)
AUTH_USER_MODEL = "user_app.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"


INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.location_field",
    "unfold.contrib.constance",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "services.foundational_service.geo_module.country_app",
    "services.foundational_service.geo_module.province_app",
    "services.foundational_service.geo_module.commune_app",
    "services.foundational_service.geo_module.zone_app",
    "services.foundational_service.geo_module.colline_app",
    "services.foundational_service.auth_module.authorization_app",
    "services.foundational_service.auth_module.user_app",
    "services.foundational_service.auth_module.authentication_app",
    "services.core_service.academic_module.class_app",
    "services.core_service.academic_module.course_app",
    "services.core_service.academic_module.department_app",
    "services.core_service.academic_module.faculty_app",
    "services.core_service.academic_module.module_app",
    "services.core_service.academic_module.teacher_app",
    "services.core_service.academic_module.university_app",
    "services.core_service.academic_module.quality_app",
    "services.core_service.student_module.card_app",
    "services.core_service.student_module.highschool_info_app",
    "services.core_service.student_module.inscription_app",
    "services.core_service.student_module.parent_app",
    "services.core_service.student_module.student_profile_app",
    "services.dependent_service.document_module.document_app",
    "services.dependent_service.document_module.request_app",
    "services.dependent_service.exam_module.attendance_app",
    "services.dependent_service.exam_module.exam_app",
    "services.dependent_service.exam_module.result_app",
    "services.dependent_service.infrastructure_module.building_app",
    "services.dependent_service.infrastructure_module.equipment_app",
    "services.dependent_service.infrastructure_module.room_app",
    "services.dependent_service.notification_module.event_notification_app",
    "services.dependent_service.scheduling_module.scheduling_app",
    "services.dependent_service.dashboard_module.dashboard_super_admin_app",
    "services.dependent_service.dashboard_module.dashboard_recteur_app",
    "services.dependent_service.dashboard_module.dashboard_quality_director_app",
    "services.dependent_service.dashboard_module.dashboard_student_services_app",
    "services.dependent_service.dashboard_module.dashboard_collection_agent_app",
    "services.dependent_service.dashboard_module.dashboard_student_app",
    "services.dependent_service.dashboard_module.dashboard_academic_secretary_app",
    "services.dependent_service.dashboard_module.dashboard_alumni_app",
    "services.dependent_service.dashboard_module.dashboard_admin_app",
    "services.dependent_service.dashboard_module.dashboard_doyen_app",
    "services.dependent_service.dashboard_module.dashboard_academic_app",
    "services.dependent_service.dashboard_module.dashboard_shared_app",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_email",
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "import_export",
    "simple_history",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "core",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
]


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "ums.urls"
WSGI_APPLICATION = "ums.wsgi.application"
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.exception_handler.custom_exception_handler",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "UMS API",
    "DESCRIPTION": "University Management System API Documentation",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    # ⏳ Durée de vie du token d'accès
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=3),
    # 🔄 Durée de vie du token de refresh
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    # ♻️ Renouveler le refresh token à chaque utilisation
    "ROTATE_REFRESH_TOKENS": True,
    # ❌ Blacklist l'ancien refresh token
    "BLACKLIST_AFTER_ROTATION": True,
    # 🔐 Type d’auth
    "AUTH_HEADER_TYPES": ("Bearer",),
    # 👤 Optionnel : user_id
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

EMAIL_BACKEND = get_env_variable(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = get_env_variable("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(get_env_variable("EMAIL_PORT", 587))
EMAIL_USE_TLS = get_env_variable("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER", "testcomlab24@gmail.com")
EMAIL_HOST_PASSWORD = get_env_variable("EMAIL_HOST_PASSWORD", "nyhbfgzcvhsadrpp")
COMPANY_NAME = get_env_variable("COMPANY_NAME", "Upg")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
