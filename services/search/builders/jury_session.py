from typing import Any

from django.db.models import Model


def build_jury_session(jury_session: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a JurySession."""
    return {
        "session_name": jury_session.session_name or None,
        "status": jury_session.status or None,
    }
