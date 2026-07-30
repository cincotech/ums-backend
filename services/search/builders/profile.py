from typing import Any

from django.db.models import Model

from .base import safe_related


def build_profile(profile: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Profile."""
    user = safe_related(profile, "user")
    first_name = None
    last_name = None
    email = None
    phone_number = None
    if user:
        first = getattr(user, "first_name", "") or ""
        last = getattr(user, "last_name", "") or ""
        first_name = first.strip() or None
        last_name = last.strip() or None
        email = getattr(user, "email", None) or None
        phone_number = getattr(user, "phone_number", None) or None

    return {
        "user_id": str(profile.user_id) if profile.user_id else None,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "position": getattr(profile, "position", None) or None,
    }
