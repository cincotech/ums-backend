from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.module_app.models import Module, Semester
from services.core_service.academic_module.public_app.models import Program
from services.core_service.academic_module.university_app.models import AcademicYear

from .curriculum_services import CurriculumStructureService
from .models import CurriculumCourse, CurriculumTeachingUnit, CurriculumTemplate


class CurriculumCourseSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.course_code", read_only=True)
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    credits = serializers.IntegerField(source="course.credits", read_only=True)
    cm_hours = serializers.IntegerField(source="course.cm", read_only=True)
    td_hours = serializers.IntegerField(source="course.td", read_only=True)
    tp_hours = serializers.IntegerField(source="course.tp", read_only=True)
    vhp_hours = serializers.IntegerField(read_only=True)
    resolved_tge_hours = serializers.IntegerField(read_only=True)
    teaching_unit_id = serializers.UUIDField(read_only=True)
    teaching_unit = serializers.PrimaryKeyRelatedField(
        queryset=CurriculumTeachingUnit.objects.all(), write_only=True
    )

    class Meta:
        model = CurriculumCourse
        fields = [
            "id",
            "teaching_unit_id",
            "teaching_unit",
            "course",
            "course_code",
            "course_name",
            "credits",
            "cm_hours",
            "td_hours",
            "tp_hours",
            "vhp_hours",
            "tpe_hours",
            "tge_hours",
            "resolved_tge_hours",
            "coefficient",
            "position",
            "is_mandatory",
            "notes",
        ]
        read_only_fields = ["id", "position"]

    def validate(self, attrs):
        teaching_unit = attrs.get("teaching_unit") or getattr(
            self.instance, "teaching_unit", None
        )
        course = attrs.get("course") or getattr(self.instance, "course", None)
        if (
            teaching_unit
            and teaching_unit.template.status != CurriculumTemplate.Status.DRAFT
        ):
            raise serializers.ValidationError(
                "Seule une maquette en brouillon peut être modifiée."
            )
        if teaching_unit and course:
            template = teaching_unit.template
            if (
                course.module.class_fk_id != template.class_fk_id
                or course.module.semester_id != template.semester_id
            ):
                raise serializers.ValidationError(
                    {
                        "course": "L’ECUE ne correspond pas à la classe et au semestre de la maquette."
                    }
                )
            duplicate = CurriculumCourse.objects.filter(
                teaching_unit__template=template, course=course
            )
            if self.instance:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {"course": "Cet ECUE existe déjà dans cette maquette semestrielle."}
                )
        return attrs

    def create(self, validated_data):
        teaching_unit = validated_data["teaching_unit"]
        validated_data["position"] = CurriculumStructureService.next_course_position(
            teaching_unit
        )
        return super().create(validated_data)


class CurriculumTeachingUnitSerializer(serializers.ModelSerializer):
    module_code = serializers.CharField(source="module.code", read_only=True)
    module_name = serializers.CharField(source="module.module_name", read_only=True)
    semester_number = serializers.IntegerField(
        source="module.semester.number", read_only=True
    )
    curriculum_courses = CurriculumCourseSerializer(many=True, read_only=True)

    class Meta:
        model = CurriculumTeachingUnit
        fields = [
            "id",
            "template",
            "module",
            "module_code",
            "module_name",
            "semester_number",
            "position",
            "is_required",
            "notes",
            "curriculum_courses",
        ]
        read_only_fields = ["id", "position"]
        extra_kwargs = {"template": {"write_only": True}}

    def validate(self, attrs):
        template = attrs.get("template") or getattr(self.instance, "template", None)
        module = attrs.get("module") or getattr(self.instance, "module", None)
        if template and template.status != CurriculumTemplate.Status.DRAFT:
            raise serializers.ValidationError(
                "Seule une maquette en brouillon peut être modifiée."
            )
        if (
            template
            and module
            and (
                module.class_fk_id != template.class_fk_id
                or module.semester_id != template.semester_id
            )
        ):
            raise serializers.ValidationError(
                {
                    "module": "L’UE ne correspond pas à la classe et au semestre de la maquette."
                }
            )
        return attrs

    def create(self, validated_data):
        template = validated_data["template"]
        validated_data["position"] = (
            CurriculumStructureService.next_teaching_unit_position(template)
        )
        return super().create(validated_data)


class CurriculumTemplateListSerializer(serializers.ModelSerializer):
    program_name = serializers.SerializerMethodField()
    faculty_id = serializers.UUIDField(source="program.faculty_id", read_only=True)
    faculty_name = serializers.CharField(
        source="program.faculty.faculty_name", read_only=True
    )
    class_name = serializers.CharField(source="class_fk.class_name", read_only=True)
    academic_year_label = serializers.CharField(
        source="academic_year.academic_year", read_only=True
    )
    semester_number = serializers.IntegerField(source="semester.number", read_only=True)
    teaching_unit_count = serializers.IntegerField(read_only=True)
    course_count = serializers.IntegerField(read_only=True)
    total_credits = serializers.IntegerField(read_only=True)

    class Meta:
        model = CurriculumTemplate
        fields = [
            "id",
            "program",
            "program_name",
            "faculty_id",
            "faculty_name",
            "class_fk",
            "class_name",
            "academic_year",
            "academic_year_label",
            "semester",
            "semester_number",
            "title",
            "version",
            "status",
            "expected_credits",
            "expected_vhp_hours",
            "teaching_unit_count",
            "course_count",
            "total_credits",
            "published_at",
            "created_at",
            "updated_at",
        ]

    def get_program_name(self, obj):
        return str(obj.program)


class CurriculumTemplateSerializer(serializers.ModelSerializer):
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())
    class_fk = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all()
    )
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    program_name = serializers.SerializerMethodField()
    faculty_id = serializers.UUIDField(source="program.faculty_id", read_only=True)
    faculty_name = serializers.CharField(
        source="program.faculty.faculty_name", read_only=True
    )
    class_name = serializers.CharField(source="class_fk.class_name", read_only=True)
    academic_year_label = serializers.CharField(
        source="academic_year.academic_year", read_only=True
    )
    semester_number = serializers.IntegerField(source="semester.number", read_only=True)
    teaching_units = CurriculumTeachingUnitSerializer(many=True, read_only=True)

    class Meta:
        model = CurriculumTemplate
        fields = [
            "id",
            "program",
            "program_name",
            "faculty_id",
            "faculty_name",
            "class_fk",
            "class_name",
            "academic_year",
            "academic_year_label",
            "semester",
            "semester_number",
            "title",
            "version",
            "status",
            "expected_credits",
            "expected_vhp_hours",
            "duplicated_from",
            "created_by",
            "published_by",
            "published_at",
            "created_at",
            "updated_at",
            "teaching_units",
        ]
        read_only_fields = [
            "id",
            "status",
            "version",
            "duplicated_from",
            "created_by",
            "published_by",
            "published_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        if self.instance and self.instance.status != CurriculumTemplate.Status.DRAFT:
            raise serializers.ValidationError(
                "Seule une maquette en brouillon peut être modifiée."
            )
        candidate = CurriculumTemplate(
            program=attrs.get("program", getattr(self.instance, "program", None)),
            class_fk=attrs.get("class_fk", getattr(self.instance, "class_fk", None)),
            academic_year=attrs.get(
                "academic_year", getattr(self.instance, "academic_year", None)
            ),
            semester=attrs.get("semester", getattr(self.instance, "semester", None)),
        )
        try:
            candidate.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        return attrs

    def get_program_name(self, obj):
        return str(obj.program)

    def create(self, validated_data):
        latest_version = (
            CurriculumTemplate.objects.filter(
                class_fk=validated_data["class_fk"],
                academic_year=validated_data["academic_year"],
                semester=validated_data["semester"],
            )
            .order_by("-version")
            .values_list("version", flat=True)
            .first()
            or 0
        )
        validated_data["version"] = latest_version + 1
        return super().create(validated_data)


class CurriculumTeachingUnitOrderSerializer(serializers.Serializer):
    teaching_unit_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=True
    )


class CurriculumCourseStructureItemSerializer(serializers.Serializer):
    teaching_unit_id = serializers.UUIDField()
    course_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)


class CurriculumCourseOrderSerializer(serializers.Serializer):
    teaching_units = CurriculumCourseStructureItemSerializer(many=True)


class CurriculumDuplicateSerializer(serializers.Serializer):
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), required=False
    )


class CurriculumStructureCourseSerializer(serializers.Serializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    position = serializers.IntegerField(min_value=1)
    coefficient = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0.01"), default=1
    )
    tpe_hours = serializers.IntegerField(min_value=0, default=0)
    tge_hours = serializers.IntegerField(min_value=0, default=0)
    is_mandatory = serializers.BooleanField(default=True)
    notes = serializers.CharField(allow_blank=True, default="")


class CurriculumStructureTeachingUnitSerializer(serializers.Serializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all())
    position = serializers.IntegerField(min_value=1)
    is_required = serializers.BooleanField(default=True)
    notes = serializers.CharField(allow_blank=True, default="")
    courses = CurriculumStructureCourseSerializer(many=True)


class CurriculumStructureSerializer(serializers.Serializer):
    teaching_units = CurriculumStructureTeachingUnitSerializer(many=True)

    def validate_teaching_units(self, teaching_units):
        template = self.context["template"]
        module_ids = [item["module"].id for item in teaching_units]
        positions = [item["position"] for item in teaching_units]
        course_ids = [
            course_item["course"].id
            for teaching_unit in teaching_units
            for course_item in teaching_unit["courses"]
        ]

        if len(module_ids) != len(set(module_ids)):
            raise serializers.ValidationError("Une UE ne peut apparaître qu’une fois.")
        if sorted(positions) != list(range(1, len(positions) + 1)):
            raise serializers.ValidationError(
                "Les positions des UE doivent être continues."
            )
        if len(course_ids) != len(set(course_ids)):
            raise serializers.ValidationError(
                "Un ECUE ne peut apparaître qu’une fois dans le semestre."
            )

        for item in teaching_units:
            module = item["module"]
            if (
                module.class_fk_id != template.class_fk_id
                or module.semester_id != template.semester_id
            ):
                raise serializers.ValidationError(
                    f"L’UE {module.code or module.module_name} ne correspond pas à la maquette."
                )
            course_positions = [course["position"] for course in item["courses"]]
            if sorted(course_positions) != list(range(1, len(course_positions) + 1)):
                raise serializers.ValidationError(
                    "Les positions des ECUE doivent être continues dans chaque UE."
                )
            for course_item in item["courses"]:
                course = course_item["course"]
                if (
                    course.module.class_fk_id != template.class_fk_id
                    or course.module.semester_id != template.semester_id
                ):
                    raise serializers.ValidationError(
                        f"L’ECUE {course.course_code or course.course_name} ne correspond pas à la maquette."
                    )

        return teaching_units
