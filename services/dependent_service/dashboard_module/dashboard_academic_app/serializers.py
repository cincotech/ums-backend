# from rest_framework import serializers

# from .models import AttributionValidation, QualityReport


# class QualityReportSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QualityReport
#         fields = [
#             "id",
#             "report_type",
#             "title",
#             "data",
#             "generated_date",
#             "generated_by",
#         ]
#         read_only_fields = ["id", "generated_date", "generated_by"]


# class AttributionValidationSerializer(serializers.ModelSerializer):
#     attribution_details = serializers.SerializerMethodField()

#     class Meta:
#         model = AttributionValidation
#         fields = [
#             "id",
#             "attribution",
#             "validated_by",
#             "validation_status",
#             "validation_date",
#             "comments",
#             "attribution_details",
#         ]
#         read_only_fields = ["id", "validation_date", "validated_by"]

#     def get_attribution_details(self, obj):
#         return {
#             "course_name": obj.attribution.course.course_name,
#             "teacher_name": f"{obj.attribution.principal_teacher.user.first_name} {obj.attribution.principal_teacher.user.last_name}",
#             "academic_year": str(obj.attribution.academic_year),
#             "status": obj.attribution.status_principal_teacher,
#         }


# class DashboardStatsSerializer(serializers.Serializer):
#     pending_attributions = serializers.IntegerField()
#     approved_attributions = serializers.IntegerField()
#     total_students = serializers.IntegerField()
#     success_rate = serializers.FloatField()
#     retention_rate = serializers.FloatField()
