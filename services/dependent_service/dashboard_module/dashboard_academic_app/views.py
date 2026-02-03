from django.db import models
from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsDean, IsDirectorAcademic
from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.quality_app.serializers import (
    QualityReportSerializer,
)
from services.core_service.academic_module.teacher_app.models import Attribution

from .serializers import AttributionValidationSerializer, TeacherValidationSerializer


class QualityReportViewSet(viewsets.ModelViewSet):
    queryset = QualityReport.objects.all()
    serializer_class = QualityReportSerializer
    permission_classes = [IsAuthenticated, IsDean]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


class AttributionValidationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attribution.objects.select_related(
        "principal_teacher__user",
        "substitute_teacher__user",
        "course",
        "academic_year",
    )
    serializer_class = AttributionValidationSerializer
    permission_classes = [IsAuthenticated, IsDirectorAcademic]

    @action(detail=True, methods=["POST"], url_path="validate")
    def validate(self, request, pk=None):
        attribution = self.get_object()

        # 🔒 1. Empêcher toute re-validation
        if attribution.validation_date:
            return Response(
                {
                    "detail": "Cette attribution a déjà été validée",
                    "validated_at": attribution.validation_date,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 📥 2. Validation des données entrantes
        serializer = TeacherValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        teacher_type = serializer.validated_data["teacher_type"]
        comments = serializer.validated_data.get("comments", "")

        # 🧠 3. Logique métier EXCLUSIVE
        if teacher_type == "principal":
            attribution.status_principal_teacher = Attribution.STATUS_ACCEPTED
            attribution.status_substitute_teacher = Attribution.STATUS_REFUSED

        elif teacher_type == "substitute":
            attribution.status_substitute_teacher = Attribution.STATUS_ACCEPTED
            attribution.status_principal_teacher = Attribution.STATUS_REFUSED

        else:
            return Response(
                {"detail": "teacher_type invalide"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🧾 4. Métadonnées de validation
        attribution.validation_comments = comments
        attribution.validated_by = request.user
        attribution.validation_date = timezone.now()
        attribution.save()

        # 📤 5. Réponse claire et cohérente
        return Response(
            {
                "message": "Attribution validée avec succès",
                "attribution_id": str(attribution.id),
                "principal_teacher_status": attribution.status_principal_teacher,
                "substitute_teacher_status": attribution.status_substitute_teacher,
                "validated_by": request.user.email,
                "validation_date": attribution.validation_date,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([IsDirectorAcademic])
def dashboard_overview(request):
    total_attributions = Attribution.objects.count()
    validated_attributions = Attribution.objects.filter(
        validation_date__isnull=False
    ).count()

    pending_attributions = Attribution.objects.filter(
        validation_date__isnull=True
    ).count()

    accepted_teachers = Attribution.objects.filter(
        status_principal_teacher="Accepted"
    ).count()

    refused_teachers = Attribution.objects.filter(
        status_principal_teacher="Refused"
    ).count()

    return Response(
        {
            "total_attributions": total_attributions,
            "validated_attributions": validated_attributions,
            "pending_attributions": pending_attributions,
            "accepted_teachers": accepted_teachers,
            "refused_teachers": refused_teachers,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDean])
def visiting_professors_attributions(request):
    attributions = Attribution.objects.filter(
        principal_teacher__speciality__isnull=False
    )

    data = []
    for attr in attributions:
        data.append({
            "attribution_id": str(attr.id),
            "course": (
            f"{attr.course.course_code} - {attr.course.course_name}"
           if attr.course and attr.course.course_code
          else attr.course.course_name if attr.course else None
            ),
            "principal_teacher": str(attr.principal_teacher),
            "academic_year": str(attr.academic_year),
            "status": attr.status_principal_teacher,
        })

    return Response(
        {
            "count": len(data),
            "results": data
        },
        status=status.HTTP_200_OK
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDean])
def academic_performance_report(request):
    by_year = (
        Attribution.objects
        .values("academic_year")
        .annotate(
            total=Count("id"),
            accepted=Count(
                "id",
                filter=Q(status_principal_teacher="Accepted")
            ),
            refused=Count(
                "id",
                filter=Q(status_principal_teacher="Refused")
            ),
        )
    )

    return Response(
        {"performance_by_academic_year": list(by_year)}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDean])
def generate_quality_report(request):
    academic_year = request.data.get("academic_year")

    if not academic_year:
        return Response(
            {"detail": "academic_year est requis"}, status=status.HTTP_400_BAD_REQUEST
        )

    attributions = Attribution.objects.filter(
        academic_year=academic_year, validation_date__isnull=False
    )

    total = attributions.count()
    accepted = attributions.filter(
        status_principal_teacher="Accepted"
    ).count()
    refused = attributions.filter(
        status_principal_teacher="Refused"
    ).count()

    report_data = {
        "academic_year": academic_year,
        "total_attributions": total,
        "accepted_teachers": accepted,
        "refused_teachers": refused,
        "generated_at": timezone.now().isoformat(),
    }

    report = QualityReport.objects.create(
        report_type="academic_performance",
        title=f"Rapport de performance académique {academic_year}",
        data=report_data,
        summary=(
            f"Année {academic_year} : "
            f"{total} attributions, "
            f"{accepted} acceptées, "
            f"{refused} refusées."
        ),
        generated_by=request.user,
    )

    return Response(
        {
            "message": "Rapport qualité généré avec succès",
            "report_id": str(report.id),
            "title": report.title,
        },
        status=status.HTTP_201_CREATED
    )



@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDean])
def quality_reports_list(request):
   
    reports = QualityReport.objects.all().order_by("-generated_date")

    serializer = QualityReportSerializer(reports, many=True)

    return Response(
        {"count": reports.count(), "results": serializer.data},
        status=status.HTTP_200_OK,
    )
