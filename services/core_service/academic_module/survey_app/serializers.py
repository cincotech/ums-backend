from rest_framework import serializers

from .models import Question, Survey, SurveyResponse


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "label",
            "type",
            "required",
            "section",
            "placeholder",
            "options",
            "max",
            "order",
        ]


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "title",
            "description",
            "logo",
            "multi_step",
            "start_date",
            "end_date",
            "questions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SurveyCreateUpdateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "title",
            "description",
            "logo",
            "multi_step",
            "start_date",
            "end_date",
            "questions",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        survey = Survey.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(survey=survey, **question_data)
        return survey

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if questions_data is not None:
            instance.questions.all().delete()
            for question_data in questions_data:
                Question.objects.create(survey=instance, **question_data)

        return instance


class SurveyResponseSerializer(serializers.ModelSerializer):
    survey_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            "id",
            "survey_id",
            "respondent_name",
            "respondent_email",
            "responses",
            "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]

    def create(self, validated_data):
        survey_id = validated_data.pop("survey_id")
        validated_data["survey_id"] = survey_id
        return super().create(validated_data)
