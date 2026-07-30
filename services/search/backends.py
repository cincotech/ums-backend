import logging

from django.db.models import QuerySet
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from rest_framework.request import Request
from rest_framework.views import APIView

from .service import SearchService

logger = logging.getLogger(__name__)


class TypesenseFilterBackend(BaseFilterBackend):
    """Backend DRF pour appliquer la recherche Typesense sur un viewset.

    Ce backend doit être placé **en premier** dans ``filter_backends`` afin que :

    - il consomme le paramètre ``search`` avant que le ``FilterSet`` n'applique
      sa propre méthode ``filter_search`` (qui ferait une recherche ``icontains``
      brute sur la requête mal orthographiée et viderait les résultats typo) ;
    - il matérialise l'ordre de pertinence via l'annotation ``_typesense_order``
      qu'un éventuel ``OrderingFilter`` ultérieur doit préserver.

    Utilise les attributs suivants du viewset :
    - ``search_fields`` : liste des champs sur lesquels rechercher
    - ``filter_fields`` : liste des champs sur lesquels filtrer (optionnel)

    Exemple :
        class CourseViewSet(ModelViewSet):
            filter_backends = [
                TypesenseFilterBackend,
                DjangoFilterBackend,
                TypesenseOrderingFilter,
            ]
            search_fields = ["course_name", "course_code", "module__module_name"]
            filter_fields = ["faculty_id", "university_id"]
    """

    # Paramètres que DjangoFilterBackend traitera lui-même via le FilterSet.
    # On ne touche donc pas à la valeur dans query_params, mais on signale au
    # FilterSet qu'il ne doit pas re-filtrer la recherche quand Typesense l'a
    # déjà prise en charge (voir ``TypesenseSearchPassthroughFilterSet``).
    SEARCH_PARAM = "search"

    def filter_queryset(
        self, request: Request, queryset: QuerySet, view: APIView
    ) -> QuerySet:
        search_fields = getattr(view, "search_fields", None)
        if not search_fields:
            return queryset

        filter_fields = getattr(view, "filter_fields", [])
        search_query = request.query_params.get(self.SEARCH_PARAM, "").strip()

        # Le backend Typesense ne s'active QUE pour une recherche plein texte.
        # Les filtres ordinaires (faculty_id, university_id, ...) restent gérés
        # par DjangoFilterBackend.
        if not search_query:
            return queryset

        service = SearchService()
        try:
            filtered_queryset, total, search_time_ms = service.apply_search(
                model=queryset.model,
                queryset=queryset,
                request=request,
                search_fields=search_fields,
                filter_fields=filter_fields,
            )
        except Exception as e:
            logger.error("Typesense filter failed: %s", e, exc_info=True)
            # Le service applique déjà son fallback ORM ; si une exception
            # remonte néanmoins, on conserve le queryset inchangé plutôt que
            # d'exposer une erreur 500.
            return queryset

        # Signaler que la recherche a été consommée par Typesense pour que le
        # FilterSet n'applique pas sa méthode filter_search en doublon.
        request._typesense_search_applied = True

        view._typesense_metadata = {
            "total": total,
            "search_time_ms": search_time_ms,
            "search_query": search_query,
            "search_fields": search_fields,
        }
        request._typesense_metadata = {
            "total": total,
            "search_time_ms": search_time_ms,
        }

        return filtered_queryset


class TypesenseOrderingFilter(OrderingFilter):
    """OrderingFilter qui préserve l'ordre de pertinence Typesense.

    Quand une recherche plein texte est active et qu'aucun ``ordering`` explicite
    n'est demandé par l'utilisateur, on conserve l'annotation ``_typesense_order``
    posée par :class:`SearchService`. Sinon, on retombe sur le comportement
    standard de DRF (ordering déclaré ou paramètre ``ordering``).
    """

    def filter_queryset(
        self, request: Request, queryset: QuerySet, view: APIView
    ) -> QuerySet:
        search_applied = getattr(request, "_typesense_search_applied", False)
        explicit_ordering = self.get_ordering(request, queryset, view)

        if search_applied and not explicit_ordering:
            # Préserver l'ordre de pertinence si l'annotation existe.
            if any(
                field.name == "_typesense_order"
                for field in queryset.query.annotations.values()
                if hasattr(field, "name")
            ) or "_typesense_order" in {name for name in queryset.query.annotations}:
                return queryset.order_by("_typesense_order")
            return queryset

        return super().filter_queryset(request, queryset, view)


class SearchMetadataMixin:
    """Mixin ajoutant les métadonnées de recherche à la réponse du sérialiseur.

    Utilisation :
        class CourseViewSet(SearchMetadataMixin, ModelViewSet):
            ...
    """

    def get_serializer_context(self):
        context = super().get_serializer_context()
        metadata = getattr(self, "_typesense_metadata", None)
        if metadata:
            context["search_metadata"] = metadata
        return context

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        metadata = getattr(self, "_typesense_metadata", None)
        if metadata:
            response.data["_search"] = metadata
        return response


class TypesenseSearchFilterBackend(TypesenseFilterBackend):
    """Alias pour TypesenseFilterBackend (compatibilité ascendante)."""
