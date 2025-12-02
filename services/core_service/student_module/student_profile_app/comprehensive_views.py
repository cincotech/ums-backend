from django.db import transaction
from rest_framework import permissions, status
from rest_framework.views import APIView

from core.response_handler import error_response, success_response, validate_serializer
from services.core_service.student_module.student_profile_app.models import Student

from .comprehensive_serializers import StudentCreateSerializer, StudentSerializer


class StudentCreateAPIView(APIView):
    """
    API view to create a full student profile including optional parents, files, highschool info,
    graduate info, and inscription.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StudentCreateSerializer(
            data=request.data, context={"user": request.user}
        )

        # Validate serializer using standardized handler
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        try:
            with transaction.atomic():
                student = serializer.save()
                output_serializer = StudentSerializer(student)

                return success_response(
                    data=output_serializer.data,
                    message="Student created successfully",
                    status_code=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return error_response(
                message="An error occurred while creating the student.",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StudentSiblingsAPIView(APIView):
    """
    API view to get sibling information AND parent data for a student.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, matricule):
        try:
            student = Student.objects.get(matricule=matricule)
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
