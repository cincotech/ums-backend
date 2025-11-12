from .base import get_env_variable

ENVIRONMENT = get_env_variable("DJANGO_ENV", "development")

if ENVIRONMENT == "production":
    print(
        "----------------------------running on production-----------------------------------------------------"
    )
    from .production import *  # noqa F401
else:
    print(
        "----------------------------running on local-----------------------------------------------------"
    )
    from .development import *  # noqa F401
