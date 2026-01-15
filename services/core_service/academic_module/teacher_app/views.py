

from core.views import BaseViewSet

from .models import Attribution, Suggestion, Teacher
from .serializers import AttributionSerializer, SuggestionSerializer, TeacherSerializer


class TeacherViewSet(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class AttributionViewSet(BaseViewSet):
    queryset = Attribution.objects.all()
    serializer_class = AttributionSerializer


class SuggestionViewSet(BaseViewSet):
    queryset = Suggestion.objects.all()
    serializer_class = SuggestionSerializer
