# from rest_framework import serializers

# from services.core_service.academic_module.teacher_app.models import Attribution

# from .models import PaymentDerogation, RecteurDecision


# class PaymentDerogationSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()
#     requested_by_name = serializers.SerializerMethodField()

#     class Meta:
#         model = PaymentDerogation
#         fields = [
#             "id",
#             "student",
#             "student_name",
#             "derogation_type",
#             "amount",
#             "reason",
#             "status",
#             "requested_by",
#             "requested_by_name",
#             "decision_notes",
#             "created_at",
#             "reviewed_at",
#         ]
#         read_only_fields = ["id", "created_at", "reviewed_at", "reviewed_by"]

#     def get_student_name(self, obj):
#         return f"{obj.student.user.first_name} {obj.student.user.last_name}"

#     def get_requested_by_name(self, obj):
#         return f"{obj.requested_by.first_name} {obj.requested_by.last_name}"


# class AttributionValidationSerializer(serializers.ModelSerializer):
#     course_name = serializers.CharField(source="course.course_name", read_only=True)
#     teacher_name = serializers.SerializerMethodField()

#     class Meta:
#         model = Attribution
#         fields = [
#             "id",
#             "course_name",
#             "teacher_name",
#             "academic_year",
#             "date_attribution",
#             "status_principal_teacher",
#             "commentaire",
#         ]
#         read_only_fields = ["id", "date_attribution"]

#     def get_teacher_name(self, obj):
#         return f"{obj.principal_teacher.user.first_name} {obj.principal_teacher.user.last_name}"


# class RecteurDecisionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RecteurDecision
#         fields = [
#             "id",
#             "decision_type",
#             "reference_id",
#             "decision",
#             "notes",
#             "decided_by",
#             "decided_at",
#         ]
#         read_only_fields = ["id", "decided_at", "decided_by"]


# class RecteurDashboardStatsSerializer(serializers.Serializer):
#     pending_derogations = serializers.IntegerField()
#     pending_attributions = serializers.IntegerField()
#     total_payments_collected = serializers.DecimalField(max_digits=15, decimal_places=2)
#     payment_collection_rate = serializers.FloatField()
#     academic_success_rate = serializers.FloatField()
#     total_students = serializers.IntegerField()


# class PaymentOverviewSerializer(serializers.Serializer):
#     total_expected = serializers.DecimalField(max_digits=15, decimal_places=2)
#     total_collected = serializers.DecimalField(max_digits=15, decimal_places=2)
#     collection_rate = serializers.FloatField()
#     outstanding_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
#     students_with_arrears = serializers.IntegerField()
