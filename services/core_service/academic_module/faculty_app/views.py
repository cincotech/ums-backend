from core.views import BaseViewSet

from .models import Faculty, TypeFormation
from .serializers import FacultySerializer, TypeFormationSerializer


class TypeFormationViewSet(BaseViewSet):
    queryset = TypeFormation.objects.all()
    serializer_class = TypeFormationSerializer


class FacultyViewSet(BaseViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def get_queryset(self):
        qs = Faculty.objects.all()
        university_id = self.request.query_params.get("university_id")

        if university_id:
            qs = qs.filter(university_id=university_id)

        return qs
