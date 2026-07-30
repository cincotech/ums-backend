from django_filters.rest_framework import DjangoFilterBackend

from core.views import BaseViewSet
from services.search.backends import TypesenseFilterBackend, TypesenseOrderingFilter

from .filters import CourseFilter
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # Typesense doit s'exécuter AVANT DjangoFilterBackend pour consommer la
    # recherche plein texte (et éviter que filter_search ne vide les résultats
    # typo via icontains), et l'OrderingFilter doit préserver l'ordre de
    # pertinence quand aucun ordering explicite n'est demandé.
    filter_backends = [
        TypesenseFilterBackend,
        DjangoFilterBackend,
        TypesenseOrderingFilter,
    ]
    filterset_class = CourseFilter
    search_fields = ["course_name", "course_code", "module__module_name"]
    filter_fields = ["faculty_id", "university_id", "department_id"]
    ordering_fields = ["course_name", "course_code"]
    ordering = ["course_name"]
