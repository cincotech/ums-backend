from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from core.views import BaseViewSet

from .models import Attribution, Suggestion, Teacher
from .serializers import AttributionSerializer, SuggestionSerializer, TeacherSerializer


class TeacherViewSet(BaseViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [DjangoFilterBackend]

    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
             
            )
        
        return queryset


class AttributionViewSet(BaseViewSet):
    queryset = Attribution.objects.all()
    serializer_class = AttributionSerializer


class SuggestionViewSet(BaseViewSet):
    queryset = Suggestion.objects.all()
    serializer_class = SuggestionSerializer
