from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        """Paginate the queryset, gracefully handling out-of-range pages.

        When a full-text search (e.g. Typesense) returns fewer results than
        the frontend expects — because it cached a previous ``count`` from an
        unfiltered request — the requested page may not exist.  Instead of
        raising ``NotFound`` (HTTP 400), we return the last available page so
        the UI can display results rather than an error.
        """
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except NotFound:
            # The requested page exceeds the available range — silently
            # redirect to the last page instead of returning a 400.
            pass

        # Build paginator from the already-filtered queryset and jump to the
        # last page.
        self.request = request
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:
            # Queryset is completely empty.
            self.page = paginator.page(1)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True

        return list(self.page)
