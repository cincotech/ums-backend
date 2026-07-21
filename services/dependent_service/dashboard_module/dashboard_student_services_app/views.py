from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from core.pagination import StandardResultsSetPagination
from core.permissions import IsStaff, IsStudentService
from core.response_handler import error_response, success_response
from core.views import BaseViewSet

from .filters import (
    AbsenceJustificationFilter,
    CounselingSessionFilter,
    DocumentRequestFilter,
    ScholarshipFilter,
    StudentActivityFilter,
    StudentStatusChangeFilter,
)
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
    DashboardStatsSerializer,
    DocumentRequestSerializer,
    PopulationDataSerializer,
    ScholarshipSerializer,
    StudentActivitySerializer,
    StudentStatusChangeSerializer,
)
from .services import PopulationDataService, StudentServicesService


class DashboardStatsViewSet(viewsets.GenericViewSet):
    """ViewSet for dashboard statistics"""

    serializer_class = DashboardStatsSerializer

    def list(self, request, *args, **kwargs):
        try:
            academic_year_id = request.query_params.get("academic_year_id")
            stats = StudentServicesService.get_dashboard_stats(
                academic_year_id=academic_year_id
            )
            serializer = self.get_serializer(stats)
            return success_response(
                data=serializer.data,
                message="Dashboard statistics retrieved successfully",
            )
        except ValueError as e:
            return error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return error_response(
                message=f"Error retrieving dashboard statistics: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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

            queryset = PopulationDataService.get_population_data(
                filters, request.query_params.get("academic_year_id")
            )

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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentRequestFilter
    permission_classes = [IsStudentService]


class AbsenceJustificationViewSet(BaseViewSet):
    queryset = AbsenceJustification.objects.all()
    serializer_class = AbsenceJustificationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AbsenceJustificationFilter
    permission_classes = [IsStudentService]


class StudentActivityViewSet(BaseViewSet):
    queryset = StudentActivity.objects.all()
    serializer_class = StudentActivitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentActivityFilter
    permission_classes = [IsStudentService]


class ScholarshipViewSet(BaseViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ScholarshipFilter
    permission_classes = [IsStudentService]


class CounselingSessionViewSet(BaseViewSet):
    queryset = CounselingSession.objects.all()
    serializer_class = CounselingSessionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CounselingSessionFilter
    permission_classes = [IsStudentService]


class StudentStatusChangeViewSet(BaseViewSet):
    queryset = StudentStatusChange.objects.all()
    serializer_class = StudentStatusChangeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentStatusChangeFilter
    permission_classes = [IsStaff]
