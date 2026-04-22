from .base import *  # noqa F401

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ums",  # Remplacez par le nom de votre base si différent
        "USER": "root",
        "PASSWORD": "pwd",
        "HOST": "localhost",
        "PORT": "3306",
    }
}
