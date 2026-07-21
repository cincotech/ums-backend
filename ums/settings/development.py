from .base import *  # noqa F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- BASE DE DONNÉES (SQLITE) ---
# SQLite est parfait pour le développement local car il ne nécessite aucun serveur.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ums",
        "USER": "root",
        "PASSWORD": "bujumbura",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
        },
    }
}


# --- LOGGING avec Rich (coloré, structuré) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rich": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
            "formatter": "rich",
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
            "show_time": True,
            "show_level": True,
            "show_path": True,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
