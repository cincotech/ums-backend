from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter

from core.permissions import (
    IsDoyen,
    IsDoyenOrAdmin,
    IsTeacher,
    IsTeacherOrFinanceOrDoyen,
)
from core.views import BaseViewSet
from services.search.backends import TypesenseFilterBackend

from .models import CompiledResult, Result, ResultComment, Session, Supplement
from .serializers import (
    CompiledResultSerializer,
    ResultCommentSerializer,
    ResultSerializer,
    SessionSerializer,
    SupplementSerializer,
)


class SessionViewSet(BaseViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsTeacherOrFinanceOrDoyen]


class ResultViewSet(BaseViewSet):
    queryset = Result.objects.select_related(
        "course", "inscription", "session", "semester", "validated_by"
    )
    serializer_class = ResultSerializer
    permission_classes = [IsTeacherOrFinanceOrDoyen]
    filter_backends = [DjangoFilterBackend, TypesenseFilterBackend, OrderingFilter]
    filterset_fields = ["semester", "course", "status", "session"]
    search_fields = [
        "comment",
        "course__course_name",
        "inscription__student__first_name",
        "inscription__student__last_name",
    ]
    ordering_fields = ["mark", "validated_at"]

    def get_permissions(self):
        if self.action in {"validate", "reject", "add_comment"}:
            return [IsDoyen()]
        if self.action in {"create", "update", "partial_update"}:
            return [IsTeacher()]
        return [IsTeacherOrFinanceOrDoyen()]

    def get_queryset(self):
        queryset = super().get_queryset()
        class_fk = self.request.query_params.get("class_fk")
        academic_year = self.request.query_params.get("academic_year")
        if class_fk:
            queryset = queryset.filter(inscription__class_fk=class_fk)
        if academic_year:
            queryset = queryset.filter(inscription__academic_year=academic_year)
        return queryset

    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        result = self.get_object()
        action_name = request.data.get("action", "validate")
        if action_name == "reject":
            result.status = "rejected"
        else:
            result.status = "validated"
        result.validated_by = request.user
        result.validated_at = timezone.now()
        if request.data.get("comment"):
            result.comment = request.data.get("comment")
        result.save()
        return self.retrieve(request, pk=pk)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        result = self.get_object()
        result.status = "rejected"
        result.validated_by = request.user
        result.validated_at = timezone.now()
        if request.data.get("comment"):
            result.comment = request.data.get("comment")
        result.save()
        return self.retrieve(request, pk=pk)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        result = self.get_object()
        result.status = "submitted"
        result.save()
        return self.retrieve(request, pk=pk)

    @action(detail=True, methods=["post"])
    def add_comment(self, request, pk=None):
        result = self.get_object()
        comment_text = (request.data.get("comment") or "").strip()
        if not comment_text:
            return self.handle_exception(Exception("Comment text is required"))
        ResultComment.objects.create(
            result=result,
            author=request.user,
            comment=comment_text,
        )
        return self.retrieve(request, pk=pk)


class CompiledResultViewSet(BaseViewSet):
    queryset = CompiledResult.objects.select_related("inscription", "semester")
    serializer_class = CompiledResultSerializer
    permission_classes = [IsDoyenOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["semester"]


class SupplementViewSet(BaseViewSet):
    queryset = Supplement.objects.select_related("inscription", "course", "semester")
    serializer_class = SupplementSerializer
    permission_classes = [IsTeacherOrFinanceOrDoyen]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["semester"]


class ResultCommentViewSet(BaseViewSet):
    queryset = ResultComment.objects.select_related("result", "author")
    serializer_class = ResultCommentSerializer
    permission_classes = [IsTeacherOrFinanceOrDoyen]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["result"]
