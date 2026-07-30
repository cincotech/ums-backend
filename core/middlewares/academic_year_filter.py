"""
Middleware that injects the active academic year into request._typesense_extra_filters.

When a user is authenticated and belongs to a university, this middleware
automatically resolves the currently open (non-closed) academic year for that
university and stores its ID in request._typesense_extra_filters. The
TypesenseFilterBackend / SearchQueryBuilder then applies it as a filter_by
condition during Typesense queries.

If the client explicitly passes ``academic_year_id`` as a query parameter, the
middleware respects that value and does NOT override it.
"""

import logging

from django.conf import settings

from services.core_service.academic_module.university_app.models import AcademicYear

logger = logging.getLogger(__name__)


class AcademicYearFilterMiddleware:
    """Injects the active academic year into the Typesense extra-filters pipeline.

    Place this middleware AFTER AuthenticationMiddleware so request.user is
    available.

    Design decisions:
    - Only injects when the request carries a ``search`` query param (Typesense
      search), avoiding unnecessary DB queries on every request.
    - Respects an explicit ``academic_year_id`` query param — if the frontend
      passes it, the middleware does not override.
    - If no open academic year exists for the user's university, no filter is
      injected (searches return results across all years).
    - The injected filter is a plain string ID, compatible with
      ``_typesense_extra_filters`` as processed by ``SearchQueryBuilder._build_filters()``.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only inject when a full-text search is active
        search = request.GET.get("search", "").strip()
        if not search:
            return self.get_response(request)

        # If the client already passed academic_year_id explicitly, do nothing
        if request.GET.get("academic_year_id"):
            return self.get_response(request)

        # We need an authenticated user with a university
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return self.get_response(request)

        university_id = getattr(user, "university_id", None)
        if not university_id:
            return self.get_response(request)

        try:
            active_year = AcademicYear.objects.filter(
                university_id=university_id,
                is_closed=False,
            ).first()
        except Exception as exc:
            if settings.DEBUG:
                logger.warning(
                    "Could not resolve active academic year for university %s: %s",
                    university_id,
                    exc,
                )
            return self.get_response(request)

        if active_year:
            extra_filters = getattr(request, "_typesense_extra_filters", None)
            if extra_filters is None:
                request._typesense_extra_filters = {}
            request._typesense_extra_filters["academic_year"] = str(active_year.id)

        return self.get_response(request)
