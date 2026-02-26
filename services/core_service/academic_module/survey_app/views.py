import json
from collections import Counter

from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.response_handler import error_response, success_response, validate_serializer
from core.views import BaseViewSet

from .models import Survey
from .serializers import (
    SurveyCreateUpdateSerializer,
    SurveyResponseSerializer,
    SurveySerializer,
)


class SurveyViewSet(BaseViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _build_data_dict(self, request):
        """
        DRF's request.data can be a QueryDict for multipart/form-data.
        Convert it into a plain dict so we can safely inject nested structures
        (e.g. `questions` as a list of objects) without Django coercing values
        into strings.
        """
        if hasattr(request.data, "getlist") and hasattr(request.data, "keys"):
            data = {}
            for key in request.data.keys():
                values = request.data.getlist(key)
                data[key] = values[0] if len(values) == 1 else values
            return data
        return dict(request.data)

    def _normalize_questions(self, data):
        """
        Support multipart/form-data where `questions` often arrives as a JSON string.
        Examples:
          - questions='[{"label":"..."}]'
          - questions=['[{"label":"..."}]']
        """
        if "questions" not in data or data["questions"] in (None, ""):
            return data, None

        questions = data["questions"]

        if (
            isinstance(questions, list)
            and len(questions) == 1
            and isinstance(questions[0], str)
        ):
            questions = questions[0]

        if isinstance(questions, str):
            try:
                questions = json.loads(questions)
            except json.JSONDecodeError as exc:
                return (
                    data,
                    error_response(
                        message="Invalid questions JSON",
                        errors={"questions": [str(exc)]},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    ),
                )

        if not isinstance(questions, list):
            return (
                data,
                error_response(
                    message="Invalid questions format",
                    errors={"questions": ["Expected a JSON array of questions."]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                ),
            )

        data["questions"] = questions
        return data, None

    def _normalized_survey_payload(self, request):
        data = self._build_data_dict(request)
        return self._normalize_questions(data)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return SurveyCreateUpdateSerializer
        return SurveySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "submit_response"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        print("Creating survey with data:", request.data)
        data, error = self._normalized_survey_payload(request)
        if error:
            return error

        serializer = self.get_serializer(data=data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        survey = serializer.save(created_by=request.user)
        return success_response(
            data=SurveySerializer(survey).data,
            message="Survey created successfully",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data, error = self._normalized_survey_payload(request)
        if error:
            return error

        serializer = self.get_serializer(instance, data=data)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        survey = serializer.save()
        return success_response(
            data=SurveySerializer(survey).data,
            message="Survey updated successfully",
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data, error = self._normalized_survey_payload(request)
        if error:
            return error

        serializer = self.get_serializer(instance, data=data, partial=True)
        validation_error = validate_serializer(serializer)
        if validation_error:
            return validation_error

        survey = serializer.save()
        return success_response(
            data=SurveySerializer(survey).data,
            message="Survey updated successfully",
        )

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def submit_response(self, request, pk=None):
        """Submit a response to a survey"""
        survey = self.get_object()
        data = {**request.data, "survey_id": str(survey.id)}

        serializer = SurveyResponseSerializer(data=data)
        if serializer.is_valid():
            serializer.save(
                respondent=request.user if request.user.is_authenticated else None
            )
            return success_response(
                data=serializer.data,
                message="Response submitted successfully",
                status_code=status.HTTP_201_CREATED,
            )
        return error_response(message="Invalid data", errors=serializer.errors)

    @action(detail=True, methods=["get"])
    def responses(self, request, pk=None):
        """Get all responses for a survey"""
        survey = self.get_object()
        responses = survey.responses.all()
        serializer = SurveyResponseSerializer(responses, many=True)
        return success_response(
            data=serializer.data, message="Responses retrieved successfully"
        )

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Get statistics for a survey"""

        survey = (
            self.get_queryset()
            .prefetch_related("questions", Prefetch("responses"))
            .get(pk=pk)
        )

        responses = list(survey.responses.all())
        total_responses = len(responses)

        # Parse responses if stored as list with JSON string
        for r in responses:
            if isinstance(r.responses, list) and len(r.responses) > 0:
                try:
                    r.responses = json.loads(r.responses[0])
                except (json.JSONDecodeError, TypeError):
                    r.responses = {}
            elif not isinstance(r.responses, dict):
                r.responses = {}

        question_stats = []

        for question in survey.questions.all():
            q_id = str(question.id)

            stats = {
                "question_id": q_id,
                "question_label": question.label,
                "question_type": question.type,
                "total_responses": 0,
            }

            answers = [
                r.responses.get(q_id)
                for r in responses
                if r.responses.get(q_id) is not None
            ]

            # ✅ Choice questions
            if question.type in ["radio", "select", "checkbox"]:

                flattened = []
                for a in answers:
                    if isinstance(a, list):
                        flattened.extend(a)
                    else:
                        flattened.append(a)

                stats["option_counts"] = dict(Counter(flattened))
                stats["total_responses"] = len(answers)

            # ✅ Rating questions
            elif question.type == "rating":

                ratings = []
                for r in answers:
                    try:
                        ratings.append(float(r))
                    except (ValueError, TypeError):
                        pass

                distribution = Counter(int(r) for r in ratings)

                stats["average_rating"] = (
                    round(sum(ratings) / len(ratings), 2) if ratings else 0
                )
                stats["rating_distribution"] = dict(distribution)
                stats["total_responses"] = len(ratings)

            # ✅ Text-like questions
            else:

                text_responses = [
                    {
                        "value": a,
                        "respondent": (
                            resp.respondent_name or resp.respondent_email or "Anonymous"
                        ),
                        "date": resp.submitted_at.isoformat(),
                    }
                    for resp in responses
                    if (a := resp.responses.get(q_id))
                ]

                stats["text_responses"] = text_responses
                stats["total_responses"] = len(text_responses)

            question_stats.append(stats)

        return success_response(
            data={
                "survey_id": str(survey.id),
                "survey_title": survey.title,
                "total_responses": total_responses,
                "question_stats": question_stats,
            },
            message="Statistics retrieved successfully",
        )

    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def upload_logo(self, request):
        """Upload survey logo"""
        file = request.FILES.get("logo")
        if not file:
            return error_response(message="No file provided")

        # Save file and return URL
        from django.core.files.storage import default_storage

        filename = default_storage.save(f"survey_logos/{file.name}", file)
        url = default_storage.url(filename)

        return success_response(data={"url": url}, message="Logo uploaded successfully")
