import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure logs directory exists
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


# Custom filter to exclude template debug messages
class TemplateDebugFilter:
    def filter(self, record):
        # Exclude template file loading debug messages
        message = record.getMessage()
        if "first seen with mtime" in message:
            return False
        # Exclude other file discovery debug messages
        if (
            "DEBUG" in record.levelname
            and "File" in message
            and "site-packages" in message
        ):
            return False
        return True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "template_debug_filter": {
            "()": TemplateDebugFilter,
        }
    },
    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] {name} - {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "debug_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "formatter": "verbose",
            "level": "DEBUG",
            "filters": ["template_debug_filter"],
        },
        "info_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "info.log"),
            "formatter": "verbose",
            "level": "INFO",
        },
        "warning_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "warning.log"),
            "formatter": "verbose",
            "level": "WARNING",
        },
        "error_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "error.log"),
            "formatter": "verbose",
            "level": "ERROR",
        },
        "critical_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "critical.log"),
            "formatter": "verbose",
            "level": "CRITICAL",
        },
        "console": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
            "show_time": True,
            "show_level": True,
            "show_path": True,
        },
    },
    "loggers": {
        "django": {
            "handlers": [
                "console",
                "debug_file",
                "info_file",
                "warning_file",
                "error_file",
                "critical_file",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
        "core": {
            "handlers": [
                "console",
                "debug_file",
                "info_file",
                "warning_file",
                "error_file",
                "critical_file",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "critical_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.template": {
            "handlers": ["warning_file", "error_file", "critical_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["warning_file", "error_file", "critical_file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
