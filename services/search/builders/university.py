from typing import Any

from django.db.models import Model

from .base import safe_related


def build_university(university: Model) -> dict[str, Any]:
    """Build a flat Typesense document for a University."""
    country = safe_related(university, "country")

    return {
        "university_name": university.university_name or None,
        "university_abrev": university.university_abrev or None,
        "country": getattr(country, "country_name", None) if country else None,
    }
