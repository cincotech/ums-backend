from .base import get_env_variable

ENVIRONMENT = get_env_variable("DJANGO_ENV", "development")
print(f"{ENVIRONMENT} is on env")

if ENVIRONMENT == "production":
    from .production import *  # noqa F401
else:
    from .development import *  # noqa F401
