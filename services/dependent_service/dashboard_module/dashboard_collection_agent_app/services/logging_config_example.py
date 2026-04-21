# Configuration des logs pour PaymentService
# À ajouter dans votre settings.py

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "colored": {
            "format": "\033[1;36m{asctime}\033[0m {levelname} \033[1;33m{module}\033[0m {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",  # Utilisez 'colored' pour des logs colorés
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/payment_service.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        # Logger pour PaymentService
        "services.dependent_service.dashboard_module.dashboard_collection_agent_app.services.paymentService": {
            "handlers": ["console", "file"],
            "level": "INFO",  # Changez en 'DEBUG' pour plus de détails
            "propagate": False,
        },
        # Logger pour tous les services
        "services": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # Logger Django par défaut
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Créez le dossier logs si nécessaire (optionnel - à décommenter dans settings.py)
# import os
# from pathlib import Path
# BASE_DIR = Path(__file__).resolve().parent.parent
# LOGS_DIR = os.path.join(BASE_DIR, "logs")
# if not os.path.exists(LOGS_DIR):
#     os.makedirs(LOGS_DIR)
