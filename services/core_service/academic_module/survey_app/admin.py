from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Question, Survey, SurveyResponse


class QuestionInline(TabularInline):
    model = Question
    extra = 1


@admin.register(Survey)
class SurveyAdmin(ModelAdmin):
    list_display = ["title", "created_by", "start_date", "end_date", "created_at"]
    list_filter = ["created_at", "start_date", "end_date"]
    search_fields = ["title", "description"]
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ["label", "survey", "type", "required", "order"]
    list_filter = ["type", "required", "survey"]
    search_fields = ["label"]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(ModelAdmin):
    list_display = ["survey", "respondent_name", "respondent_email", "submitted_at"]
    list_filter = ["survey", "submitted_at"]
    search_fields = ["respondent_name", "respondent_email"]
    readonly_fields = ["responses", "submitted_at"]
