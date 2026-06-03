# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter

from core.response_handler import error_response, success_response
from core.views import BaseViewSet

from .filters import ClassFilter
from .models import Class, ClassGroup
from .serializers import ClassGroupSerializer, ClassSerializer


class ClassViewSet(BaseViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClassFilter
    search_fields = [
        "class_name",
        "department__department_name",
        "department__faculty__faculty_name",
    ]
    ordering_fields = ["class_name"]
    ordering = ["class_name"]

    @action(detail=True, methods=["get"])
    def groups(self, request, pk=None):
        groups = (
            ClassGroup.objects.filter(class_fk_id=pk)
            .select_related(
                "class_fk",
                "class_fk__department",
                "class_fk__department__faculty",
                "academic_year",
            )
            .order_by("group_name")
        )

        academic_year_id = request.query_params.get("academic_year_id")
        if academic_year_id:
            groups = groups.filter(academic_year_id=academic_year_id)

        serializer = ClassGroupSerializer(groups, many=True)
        return success_response(
            data=serializer.data,
            message="Class groups retrieved successfully",
        )


class ClassGroupViewSet(BaseViewSet):
    queryset = ClassGroup.objects.all()
    serializer_class = ClassGroupSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["class_fk", "academic_year"]
    search_fields = [
        "group_name",
        "class_fk__class_name",
        "class_fk__department__department_name",
        "class_fk__department__abreviation",
        "class_fk__department__faculty__faculty_name",
        "class_fk__department__faculty__faculty_abreviation",
        "academic_year__academic_year",
    ]
    ordering_fields = ["group_name", "created_date"]
    ordering = ["group_name"]

    def get_queryset(self):
        queryset = ClassGroup.objects.select_related(
            "class_fk",
            "class_fk__department",
            "class_fk__department__faculty",
            "academic_year",
        )

        class_id = self.request.query_params.get("class_id")
        academic_year_id = self.request.query_params.get("academic_year_id")

        if class_id:
            queryset = queryset.filter(class_fk_id=class_id)
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)

        return queryset

    @action(detail=False, methods=["get"])
    def by_class(self, request):
        class_id = request.query_params.get("class_id") or request.query_params.get(
            "class_fk"
        )

        if not class_id:
            return error_response(message="Class ID is required")

        groups = self.filter_queryset(self.get_queryset().filter(class_fk_id=class_id))
        serializer = self.get_serializer(groups, many=True)
        return success_response(
            data=serializer.data,
            message="Class groups retrieved successfully",
        )

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return error_response(message="Class group IDs are required")

        deleted_count, _ = ClassGroup.objects.filter(id__in=ids).delete()
        return success_response(
            data={"deleted_count": deleted_count},
            message=f"{deleted_count} class group(s) deleted successfully",
            status_code=status.HTTP_200_OK,
        )
