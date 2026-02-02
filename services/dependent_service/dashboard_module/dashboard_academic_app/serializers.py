from rest_framework import serializers
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.academic_module.teacher_app.serializers import TeacherSerializer


class AttributionValidationSerializer(serializers.ModelSerializer):
    principal_teacher_details = TeacherSerializer(source='principal_teacher', read_only=True)
    substitute_teacher_details = TeacherSerializer(source='substitute_teacher', read_only=True)
    
    # Display fields for course and teachers
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_credits = serializers.IntegerField(source='course.credits', read_only=True)
    principal_teacher_name = serializers.SerializerMethodField(read_only=True)
    substitute_teacher_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Attribution
        fields = [
            "id",
            "course_name",
            "course_code",
            "course_credits",
            "principal_teacher",
            "principal_teacher_name",
            "principal_teacher_details",
            "substitute_teacher",
            "substitute_teacher_name",
            "substitute_teacher_details",
            "academic_year",
            "date_attribution",
            "status_principal_teacher",
            "status_substitute_teacher",
            "commentaire",
            "validated_by",
            "validation_date",
            "validation_comments",
        ]
        read_only_fields = [
            "id",
            "course_name",
            "course_code",
            "course_credits",
            "status_principal_teacher",
            "status_substitute_teacher",
            "validated_by",
            "validation_date",
        ]
    



    
    def get_course(self, obj):
        course = obj.course
        if hasattr(course, "course_code") and course.course_code:
            return f"{course.course_code} - {course.course_name}"
        return course.course_name

    def get_principal_teacher_name(self, obj):
        """Get the principal teacher's display name."""
        if obj.principal_teacher:
            teacher = obj.principal_teacher
            if teacher.user.first_name or teacher.user.last_name:
                return f"{teacher.user.first_name} {teacher.user.last_name}".strip()
            return teacher.user.email
        return None
    

    
    def get_substitute_teacher_name(self, obj):
        """Get the substitute teacher's display name."""
        if obj.substitute_teacher:
            teacher = obj.substitute_teacher
            if teacher.user.first_name or teacher.user.last_name:
                return f"{teacher.user.first_name} {teacher.user.last_name}".strip()
            return teacher.user.email
        return None

    def validate(self, data):
        """Validate that substitute_teacher is different from principal_teacher."""
        principal = data.get('principal_teacher')
        substitute = data.get('substitute_teacher')

        # For updates, we need to check the instance as well
        if self.instance:
            if not substitute and self.instance.substitute_teacher_id:
                substitute = self.instance.substitute_teacher
            if not principal and self.instance.principal_teacher_id:
                principal = self.instance.principal_teacher

        if substitute and principal and substitute.id == principal.id:
            raise serializers.ValidationError({
                "substitute_teacher": "Le professeur remplaçant doit être différent du professeur principal."
            })

        return data



class TeacherValidationSerializer(serializers.Serializer):
    TEACHER_TYPE_CHOICES = [
        ("principal", "Teacher Principal"),
        ("substitute", "Teacher Remplaçant"),
    ]

    teacher_type = serializers.ChoiceField(choices=TEACHER_TYPE_CHOICES)
    comments = serializers.CharField(required=False, allow_blank=True)

