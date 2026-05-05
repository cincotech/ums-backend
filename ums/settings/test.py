import os

from .base import *  # noqa F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- DATABASE — SQLite en mémoire pour les tests ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# --- EMAILS — pas d'envoi réel pendant les tests ---
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# --- LOGS dédiés aux tests ---
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "test": {
            "format": "[{asctime}] [{levelname}] [{name}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "test_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "tests.log"),
            "formatter": "test",
            "level": "DEBUG",
            "mode": "w",  # overwrite at each test run
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "test",
            "level": "WARNING",  # only warnings+ in console during tests
        },
    },
    "loggers": {
        # Capture all inscription_app logs
        "services.core_service.student_module.inscription_app": {
            "handlers": ["test_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Capture all student_profile_app logs
        "services.core_service.student_module.student_profile_app": {
            "handlers": ["test_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Capture test runner logs
        "inscription_tests": {
            "handlers": ["test_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Django DB queries (useful to spot N+1)
        "django.db.backends": {
            "handlers": ["test_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Django general
        "django": {
            "handlers": ["test_file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
