from typing import Any

from django.db.models import Model


def build_session(session: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a Session."""
    return {
        "session_name": session.session_name or None,
    }
