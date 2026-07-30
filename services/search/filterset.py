"""Base FilterSet cooperant avec le backend Typesense.

Le problème : ``DjangoFilterBackend`` exécute la méthode ``filter_search`` du
``FilterSet`` (recherche ``icontains`` brute) sur la requête *mal orthographiée*
de l'utilisateur, ce qui vide le queryset avant même que Typesense ne puisse
appliquer sa tolérance aux fautes.

La solution : un ``FilterSet`` de base dont ``filter_search`` devient un no-op
dès que :class:`TypesenseFilterBackend` a signalé (via
``request._typesense_search_applied``) qu'il a pris en charge la recherche plein
texte. Les ``FilterSet`` concrets héritent de cette classe et exposent leur
recherche ORM de secours via ``_orm_filter_search`` (utilisée uniquement quand
Typesense est désactivé ou indisponible).

Utilisation :

    from services.search.filterset import TypesenseSearchFilterSet

    class CourseFilter(TypesenseSearchFilterSet):
        search = django_filters.CharFilter(method="filter_search")

        class Meta:
            model = Course
            fields = []

        def _orm_filter_search(self, queryset, value):
            return queryset.filter(
                Q(course_name__icontains=value) | Q(course_code__icontains=value)
            )
"""

import django_filters


class TypesenseSearchFilterSet(django_filters.FilterSet):
    """FilterSet de base qui évite la double recherche plein texte."""

    def filter_search(self, queryset, name, value):
        # Si Typesense a déjà consommé le paramètre ``search``, on ne ré-applique
        # pas la recherche ORM : cela annulerait la tolérance aux fautes.
        request = getattr(self, "request", None)
        if getattr(request, "_typesense_search_applied", False):
            return queryset

        if not value:
            return queryset

        return self._orm_filter_search(queryset, value)

    def _orm_filter_search(self, queryset, value):
        """Recherche ORM de secours, à surcharger dans les sous-classes.

        N'est utilisée que lorsque Typesense est désactivé ou indisponible.
        """
        return queryset
