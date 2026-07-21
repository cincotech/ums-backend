from datetime import datetime, timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter

from core.permissions import IsDean
from core.response_handler import error_response, success_response
from core.views import BaseViewSet
from services.dependent_service.scheduling_module.scheduling_app.models import (
    CourseSession,
    TemplateEntry,
    TimetableTemplate,
)

from .timetable_v2_serializers import (
    CourseSessionSerializer,
    TemplateEntrySerializer,
    TimetableTemplateSerializer,
    TimetableTemplateWriteSerializer,
)
from .utils import get_faculty_for_request


def _get_ay(request):
    return request.query_params.get("academic_year") or request.query_params.get(
        "academic_year_id"
    )


class TimetableTemplateViewSet(BaseViewSet):
    """
    Grilles horaires récurrentes par groupe de classe.
    CRUD + publish/unpublish + génération de séances.
    """

    permission_classes = [IsDean]
    serializer_class = TimetableTemplateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["class_group", "status"]
    search_fields = ["name", "class_group__group_name"]
    ordering_fields = ["created_at", "updated_at", "name"]

    def get_queryset(self):
        faculty = get_faculty_for_request(self.request)
        qs = (
            TimetableTemplate.objects.filter(
                class_group__class_fk__department__faculty=faculty
            )
            .select_related(
                "class_group",
                "class_group__class_fk",
                "class_group__class_fk__department",
                "class_group__class_fk__department__faculty",
                "class_group__academic_year",
                "created_by",
            )
            .prefetch_related("entries", "entries__attribution", "entries__room")
        )
        academic_year = _get_ay(self.request)
        if academic_year:
            qs = qs.filter(class_group__academic_year_id=academic_year)
        return qs

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TimetableTemplateWriteSerializer
        return TimetableTemplateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ── publish / unpublish ───────────────────────────────────────────────────

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        template = self.get_object()
        template.status = TimetableTemplate.STATUS_PUBLISHED
        template.published_at = timezone.now()
        template.save(update_fields=["status", "published_at", "updated_at"])
        return success_response(
            data=TimetableTemplateSerializer(template).data,
            message="Grille publiée avec succès",
        )

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        template = self.get_object()
        template.status = TimetableTemplate.STATUS_DRAFT
        template.published_at = None
        template.save(update_fields=["status", "published_at", "updated_at"])
        return success_response(
            data=TimetableTemplateSerializer(template).data,
            message="Grille dépubliée",
        )

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        template = self.get_object()
        template.status = TimetableTemplate.STATUS_ARCHIVED
        template.save(update_fields=["status", "updated_at"])
        return success_response(
            data=TimetableTemplateSerializer(template).data,
            message="Grille archivée",
        )

    # ── generate sessions ─────────────────────────────────────────────────────

    @action(detail=True, methods=["post"])
    def generate_sessions(self, request, pk=None):
        """
        Génère des CourseSession pour chaque entrée de la grille
        sur la plage [start_date, end_date].
        Si aucune date fournie, utilise les bornes de l'année académique du groupe.
        Skipe les séances déjà existantes (idempotent).
        """
        template = self.get_object()

        start_str = request.data.get("start_date")
        end_str = request.data.get("end_date")

        if start_str and end_str:
            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                return error_response(
                    message="Format de date invalide (YYYY-MM-DD attendu)"
                )
        else:
            ay = template.class_group.academic_year
            start_date = ay.start_date
            end_date = ay.end_date

        if start_date > end_date:
            return error_response(
                message="La date de début doit être antérieure à la date de fin"
            )

        DAY_TO_WEEKDAY = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }

        entries = list(template.entries.select_related("attribution", "room"))
        if not entries:
            return error_response(message="Cette grille ne contient aucun créneau")

        created_count = 0
        skipped_count = 0
        current = start_date

        # Week A = even offset from AY start, week B = odd offset
        ay_start = template.class_group.academic_year.start_date

        while current <= end_date:
            current_weekday = current.weekday()
            week_offset = (current - ay_start).days // 7
            is_week_a = week_offset % 2 == 0

            for entry in entries:
                if DAY_TO_WEEKDAY.get(entry.day_of_week) != current_weekday:
                    continue
                # Week-type filter (A/B alternating weeks)
                if entry.week_type == "A" and not is_week_a:
                    continue
                if entry.week_type == "B" and is_week_a:
                    continue
                # Idempotent: skip if already exists for this entry + date
                already_exists = CourseSession.objects.filter(
                    template_entry=entry, date=current
                ).exists()
                if already_exists:
                    skipped_count += 1
                    continue
                CourseSession.objects.create(
                    template=template,
                    template_entry=entry,
                    class_group=template.class_group,
                    date=current,
                    start_time=entry.start_time,
                    end_time=entry.end_time,
                    attribution=entry.attribution,
                    room=entry.room,
                    session_type=entry.session_type,
                    title=entry.title,
                    status=CourseSession.STATUS_SCHEDULED,
                    created_by=request.user,
                )
                created_count += 1
            current += timedelta(days=1)

        return success_response(
            data={"created": created_count, "skipped": skipped_count},
            message=f"{created_count} séance(s) générée(s), {skipped_count} ignorée(s) (déjà existantes)",
        )


class TemplateEntryViewSet(BaseViewSet):
    """
    Créneaux récurrents dans une grille horaire.
    """

    permission_classes = [IsDean]
    serializer_class = TemplateEntrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "template",
        "day_of_week",
        "session_type",
        "week_type",
        "attribution",
        "room",
    ]
    search_fields = ["title", "attribution__course__course_name"]
    ordering_fields = ["day_of_week", "start_time"]

    def get_queryset(self):
        faculty = get_faculty_for_request(self.request)
        qs = TemplateEntry.objects.filter(
            template__class_group__class_fk__department__faculty=faculty
        ).select_related(
            "template",
            "attribution",
            "attribution__principal_teacher__user",
            "attribution__course",
            "room",
        )
        academic_year = _get_ay(self.request)
        if academic_year:
            qs = qs.filter(template__class_group__academic_year_id=academic_year)
        return qs


class CourseSessionViewSet(BaseViewSet):
    """
    Séances réelles datées (instances).
    """

    permission_classes = [IsDean]
    serializer_class = CourseSessionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "template",
        "class_group",
        "date",
        "status",
        "session_type",
        "attribution",
        "room",
        "is_makeup",
    ]
    search_fields = ["title", "attribution__course__course_name", "notes"]
    ordering_fields = ["date", "start_time", "status"]

    def get_queryset(self):
        faculty = get_faculty_for_request(self.request)
        qs = CourseSession.objects.filter(
            class_group__class_fk__department__faculty=faculty
        ).select_related(
            "class_group",
            "class_group__class_fk",
            "class_group__class_fk__department",
            "template",
            "template_entry",
            "attribution",
            "attribution__principal_teacher__user",
            "attribution__course",
            "room",
        )

        # Academic year scope
        academic_year = _get_ay(self.request)
        if academic_year:
            qs = qs.filter(class_group__academic_year_id=academic_year)

        # Date range filter from query params
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ── Status transitions ────────────────────────────────────────────────────

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        session = self.get_object()
        session.status = CourseSession.STATUS_COMPLETED
        session.save(update_fields=["status", "updated_at"])
        return success_response(
            data=CourseSessionSerializer(session).data,
            message="Séance marquée comme dispensée",
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        session = self.get_object()
        session.status = CourseSession.STATUS_CANCELLED
        reason = request.data.get("reason")
        if reason:
            session.notes = reason
        session.save(update_fields=["status", "notes", "updated_at"])
        return success_response(
            data=CourseSessionSerializer(session).data,
            message="Séance annulée",
        )

    @action(detail=True, methods=["post"])
    def postpone(self, request, pk=None):
        session = self.get_object()
        session.status = CourseSession.STATUS_POSTPONED
        session.save(update_fields=["status", "updated_at"])
        return success_response(
            data=CourseSessionSerializer(session).data,
            message="Séance reportée",
        )

    # ── Bulk operations ───────────────────────────────────────────────────────

    @action(detail=False, methods=["post"])
    def bulk_upsert(self, request):
        """
        Crée ou met à jour des séances par ID (sync depuis le frontend).
        Si l'ID existe → update, sinon → create.
        Idempotent et safe pour la synchronisation multi-appareils.
        """
        sessions_data = request.data.get("sessions", [])
        if not isinstance(sessions_data, list):
            return error_response(message="«sessions» doit être une liste")

        created, updated, errors = [], [], []

        for item in sessions_data:
            session_id = item.get("id")
            instance = None

            if session_id:
                try:
                    instance = CourseSession.objects.get(id=session_id)
                except CourseSession.DoesNotExist:
                    pass

            serializer = CourseSessionSerializer(
                instance, data=item, partial=(instance is not None)
            )
            if serializer.is_valid():
                obj = serializer.save(created_by=request.user)
                if instance:
                    updated.append(str(obj.id))
                else:
                    created.append(str(obj.id))
            else:
                errors.append({"data": item, "errors": serializer.errors})

        return success_response(
            data={
                "created": len(created),
                "updated": len(updated),
                "errors": len(errors),
                "created_ids": created,
                "updated_ids": updated,
                "error_details": errors,
            },
            message=f"Sync terminée : {len(created)} créées, {len(updated)} mises à jour",
        )

    @action(detail=False, methods=["delete"])
    def bulk_delete(self, request):
        """Supprime des séances par liste d'IDs."""
        ids = request.data.get("ids", [])
        if not isinstance(ids, list):
            return error_response(message="«ids» doit être une liste")
        deleted, _ = CourseSession.objects.filter(id__in=ids).delete()
        return success_response(
            data={"deleted": deleted},
            message=f"{deleted} séance(s) supprimée(s)",
        )

    # ── Conflict detection ────────────────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def conflicts(self, request):
        """
        Détecte les conflits de salle et d'enseignant sur une plage de dates.
        """
        request.query_params.get("date_from")
        request.query_params.get("date_to")

        qs = self.get_queryset().filter(status=CourseSession.STATUS_SCHEDULED)

        sessions = list(qs.select_related("room", "attribution", "class_group"))

        room_conflicts = []
        teacher_conflicts = []

        for i, s1 in enumerate(sessions):
            for s2 in sessions[i + 1 :]:
                if s1.date != s2.date:
                    continue
                overlap = s1.start_time < s2.end_time and s2.start_time < s1.end_time

                if not overlap:
                    continue

                # Room conflict
                if s1.room_id and s1.room_id == s2.room_id:
                    room_conflicts.append(
                        {
                            "type": "room",
                            "room_name": s1.room.room_name if s1.room else None,
                            "date": str(s1.date),
                            "time": f"{s1.start_time}–{s1.end_time}",
                            "session_a": str(s1.id),
                            "session_b": str(s2.id),
                        }
                    )

                # Teacher conflict
                if s1.attribution_id and s1.attribution_id == s2.attribution_id:
                    teacher_conflicts.append(
                        {
                            "type": "teacher",
                            "date": str(s1.date),
                            "time": f"{s1.start_time}–{s1.end_time}",
                            "session_a": str(s1.id),
                            "session_b": str(s2.id),
                        }
                    )

        total = len(room_conflicts) + len(teacher_conflicts)
        return success_response(
            data={
                "total": total,
                "room_conflicts": room_conflicts,
                "teacher_conflicts": teacher_conflicts,
            },
            message=f"{total} conflit(s) détecté(s)",
        )

    # ── Availability check ────────────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="availability-check")
    def availability_check(self, request):
        """
        Vérifie si une salle / un enseignant est disponible pour un créneau donné.
        Params: date, start_time (HH:MM), end_time (HH:MM), room?, attribution?, exclude?
        """
        date = request.query_params.get("date")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")
        room_id = request.query_params.get("room")
        attribution_id = request.query_params.get("attribution")
        exclude_id = request.query_params.get("exclude")

        if not all([date, start_time, end_time]):
            return error_response(
                message="Paramètres date, start_time et end_time requis"
            )

        # Sessions that overlap the requested slot and are not cancelled
        overlap_qs = CourseSession.objects.filter(
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exclude(status=CourseSession.STATUS_CANCELLED)
        if exclude_id:
            overlap_qs = overlap_qs.exclude(id=exclude_id)

        result = {
            "room_available": True,
            "room_conflict": None,
            "teacher_available": True,
            "teacher_conflict": None,
        }

        if room_id:
            conflict = (
                overlap_qs.filter(room_id=room_id).select_related("attribution").first()
            )
            if conflict:
                result["room_available"] = False
                result["room_conflict"] = (
                    conflict.title
                    or getattr(conflict.attribution, "course_name", None)
                    or str(conflict.class_group_id)
                )

        if attribution_id:
            conflict = overlap_qs.filter(attribution_id=attribution_id).first()
            if conflict:
                result["teacher_available"] = False
                result["teacher_conflict"] = conflict.title or str(conflict.date)

        return success_response(data=result, message="Disponibilité vérifiée")
