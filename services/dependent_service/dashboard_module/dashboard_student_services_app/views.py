from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.paginator import Paginator
from core.response_handler import success_response, error_response
from core.permissions import IsStaff, IsStudentService
from core.views import BaseViewSet

from .serializers import (
    AbsenceJustificationSerializer,
    CounselingSessionSerializer,
    DocumentRequestSerializer,
    ScholarshipSerializer,
    StudentActivitySerializer,
    StudentStatusChangeSerializer,
    PopulationDataSerializer,
)
from .services import PopulationDataService, StudentServicesService
from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
    StudentStatusChange,
)
from core.pagination import StandardResultsSetPagination



class PopulationDataViewSet(viewsets.GenericViewSet):
    """ViewSet for student population data"""

    serializer_class = PopulationDataSerializer
    pagination_class = StandardResultsSetPagination
    pagination_enabled = True  # ✅ DEFAULT
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            # Extract filters
            filters = {
                "academic_year": request.query_params.get("academic_year_id"),
                "faculty": request.query_params.get("faculty"),
                "department": request.query_params.get("department"),
                "class_name": request.query_params.get("class_name"),
                "sexe": request.query_params.get("sexe"),
                "age_range": request.query_params.get("age_range"),
                "search": request.query_params.get("search"),
            }

            filters = {k: v for k, v in filters.items() if v}

         
            queryset = PopulationDataService.get_population_data(filters)

           
            if (
                not self.pagination_enabled
                or request.query_params.get("pagination") == "false"
            ):
                serializer = self.get_serializer(queryset, many=True)
                return success_response(
                    data=serializer.data,
                    message="Population data retrieved successfully",
                )

         
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)

            return success_response(
                data=serializer.data,
                message="Population data retrieved successfully",
                extra={
                    "pagination": {
                        "count": self.paginator.page.paginator.count,
                        "page_size": self.paginator.page.paginator.per_page,
                        "current_page": self.paginator.page.number,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                    }
                },
            )

        except Exception as e:
            return error_response(
                message=f"Error retrieving population data: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
