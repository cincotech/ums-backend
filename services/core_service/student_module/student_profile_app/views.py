# Create your views here.


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView

from core.response_handler import error_response, success_response, validate_serializer
from core.views import BaseViewSet

from .filters import StudentFilter
from .models import Student, StudentFile, StudentGraduateInfo, StudentHsInfo, StudentMatricule, Training
from .serializers import (
    StudentFileSerializer,
    StudentGraduateInfoSerializer,
    StudentHsInfoSerializer,
    StudentMatriculeSerializer,
    StudentSerializer,
    TrainingSerializer,
)


class StudentViewSet(BaseViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ["user__first_name", "user__last_name", "user__email", "matricules__matricule"]
    ordering_fields = ["user__last_name", "user__first_name"]
    ordering = ["user__last_name", "user__first_name"]

    def perform_create(self, serializer):
        return serializer.save()

    @action(detail=True, methods=["get"], url_path="matricules")
    def matricules(self, request, pk=None):
        """Returns all matricules of a student grouped by formation type with inscription status."""
        student = self.get_object()
        status_filter = request.query_params.get("status")  # Active, Replaced, Completed, etc.

        matricules_qs = StudentMatricule.objects.filter(
            student=student
        ).select_related("type_formation", "academic_year")

        # Filter by inscription status if provided
        if status_filter:
            from services.core_service.student_module.inscription_app.models import Inscription
            matching_types = Inscription.objects.filter(
                student=student,
                regist_status__iexact=status_filter,
            ).values_list("class_fk__department__faculty__types", flat=True).distinct()
            matricules_qs = matricules_qs.filter(type_formation__in=matching_types)

        serializer = StudentMatriculeSerializer(matricules_qs, many=True)
        return success_response(
            data=serializer.data,
            message=f"{matricules_qs.count()} matricule(s) found",
        )


class TrainingViewSet(BaseViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["domaine", "training_center__name"]
    ordering_fields = ["id", "domaine"]
    ordering = ["id"]


class StudentHsInfoViewSet(BaseViewSet):
    queryset = StudentHsInfo.objects.all()
    serializer_class = StudentHsInfoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["highschool_name", "highschool_location"]
    ordering_fields = ["graduation_year"]
    ordering = ["-graduation_year"]


class StudentGraduateInfoViewSet(BaseViewSet):
    queryset = StudentGraduateInfo.objects.all()
    serializer_class = StudentGraduateInfoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["university_name", "degree_obtained"]
    ordering_fields = ["graduation_year"]
    ordering = ["-graduation_year"]


class StudentSiblingsAPIView(APIView):
    """
    API view to get sibling information AND parent data for a student.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, matricule):
        try:
            # Chercher l'étudiant via StudentMatricule (source de vérité)
            student_matricule = StudentMatricule.objects.filter(matricule=matricule).first()
            if not student_matricule:
                raise Student.DoesNotExist
            student = student_matricule.student
            # Get parent data
            parents = student.parent.all()
            parents_data = [
                {
                    "id": str(p.id),
                    "name": p.parent_name,
                    "phone": p.parent_phone,
                    "email": p.parent_email,
                    "type": p.get_parent_type_display(),
                    "profession": (
                        p.profession.profession_name if p.profession else None
                    ),
                    "is_alive": p.is_alive,
                    "is_contact_person": p.is_contact_person,
                }
                for p in parents
            ]

            return success_response(
                data={
                    "parents": parents_data,
                },
                message=f"Found  siblings and parent data for student {matricule}",
            )

        except Student.DoesNotExist:
            return error_response(
                message="Student not found",
                errors={"matricule": matricule},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return error_response(
                message="An error occurred while fetching sibling and parent data",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StudentFileViewSet(viewsets.ModelViewSet):
    queryset = StudentFile.objects.all()
    serializer_class = StudentFileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["file_name", "file_type"]
    ordering_fields = ["uploaded_at"]
    ordering = ["-uploaded_at"]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        self.perform_create(serializer)

        return success_response(
            data=serializer.data,
            message=f"{self.queryset.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED,
        )
