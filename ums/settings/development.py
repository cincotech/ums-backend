from .base import *  # noqa F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- BASE DE DONNÉES (SQLITE) ---
# SQLite est parfait pour le développement local car il ne nécessite aucun serveur.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ums',
        'USER': 'root',
        'PASSWORD': 'bujumbura',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}




# --- LOGGING (Optionnel mais recommandé) ---
# Pour voir les requêtes SQL dans la console pendant le développement
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
