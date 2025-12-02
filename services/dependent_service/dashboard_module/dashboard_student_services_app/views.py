from core.permissions import IsStaff, IsStudentService
from core.views import BaseViewSet

from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
    StudentStatusChange,
)
from .serializers import (
    AbsenceJustificationSerializer,
    CounselingSessionSerializer,
    DocumentRequestSerializer,
    ScholarshipSerializer,
    StudentActivitySerializer,
    StudentStatusChangeSerializer,
)


class DocumentRequestViewSet(BaseViewSet):
    queryset = DocumentRequest.objects.all()
    serializer_class = DocumentRequestSerializer
    permission_classes = [IsStudentService]


class AbsenceJustificationViewSet(BaseViewSet):
    queryset = AbsenceJustification.objects.all()
    serializer_class = AbsenceJustificationSerializer
    permission_classes = [IsStudentService]


class StudentActivityViewSet(BaseViewSet):
    queryset = StudentActivity.objects.all()
    serializer_class = StudentActivitySerializer
    permission_classes = [IsStudentService]


class ScholarshipViewSet(BaseViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    permission_classes = [IsStudentService]


class CounselingSessionViewSet(BaseViewSet):
    queryset = CounselingSession.objects.all()
    serializer_class = CounselingSessionSerializer
    permission_classes = [IsStudentService]


class StudentStatusChangeViewSet(BaseViewSet):
    queryset = StudentStatusChange.objects.all()
    serializer_class = StudentStatusChangeSerializer
    permission_classes = [IsStaff]
