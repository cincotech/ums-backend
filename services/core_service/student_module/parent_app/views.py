from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from core.views import BaseViewSet

from .models import Parent, Profession
from .serializers import ParentSerializer, ProfessionSerializer
from .filters import ParentFilter, ProfessionFilter


class ProfessionViewSet(BaseViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProfessionFilter
    search_fields = ['profession_name']
    ordering_fields = ['profession_name']
    ordering = ['profession_name']


class ParentViewSet(BaseViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ParentFilter
    search_fields = ['parent_name', 'parent_phone', 'parent_email']
    ordering_fields = ['parent_name']
    ordering = ['parent_name']
