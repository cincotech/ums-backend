from django.db import transaction
from rest_framework import serializers

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.parent_app.models import Parent, Profession
from services.core_service.student_module.student_profile_app.models import (
    Student,
    StudentFile,
    StudentGraduateInfo,
    StudentHsInfo,
    Training,
)


# -------------------- Parent Serializer --------------------
class ParentSerializer(serializers.ModelSerializer):
    profession_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Parent
        fields = [
            "id",
            "parent_name",
            "parent_phone",
            "parent_email",
            "profession_id",
            "parent_type",
            "is_alive",
            "is_contact_person",
        ]


# -------------------- Student File Serializer --------------------
class StudentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFile
        fields = [
            "id",
            "file_type",
            "file_name",
            "file",
            "is_verified",
            "verified_at",
            "verified_by",
            "notes",
        ]


# -------------------- Training Serializer --------------------
class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = ["id", "domaine", "certificate", "training_center"]


# -------------------- Highschool Info Serializer --------------------
class StudentHsInfoSerializer(serializers.ModelSerializer):
    formation_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = StudentHsInfo
        fields = [
            "id",
            "highschool",
            "certificate",
            "se_mark",
            "date_of_obtention",
            "formation_ids",
        ]


# -------------------- Graduate Info Serializer --------------------
class StudentGraduateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGraduateInfo
        fields = ["id", "department", "option", "mention", "degree"]


# -------------------- Student Serializer --------------------
class StudentSerializer(serializers.ModelSerializer):
    parent_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )
    parents = ParentSerializer(many=True, read_only=True)
    files = StudentFileSerializer(many=True, read_only=True)
    hs_infos = StudentHsInfoSerializer(many=True, read_only=True)
    graduate_infos = StudentGraduateInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "matricule",
            "colline",
            "cam",
            "parent_ids",
            "parents",
            "files",
            "hs_infos",
            "graduate_infos",
        ]


# -------------------- Inscription Serializer --------------------
class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
        fields = [
            "id",
            "student",
            "academic_year",
            "class_fk",
            "date_inscription",
            "regist_status",
            "withdrawal_date",
            "is_year_close",
        ]


# -------------------- Full Student Create Serializer --------------------
class StudentCreateSerializer(serializers.Serializer):
    colline = serializers.UUIDField()
    cam = serializers.IntegerField(required=False, allow_null=True)

    # Parents
    parent_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    new_parents = ParentSerializer(many=True, required=False)

    # Files
    file_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    new_files = StudentFileSerializer(many=True, required=False)

    # Highschool Info
    highschool_id = serializers.UUIDField()
    certificate_id = serializers.UUIDField()
    se_mark = serializers.CharField(max_length=6, required=False, allow_blank=True)
    date_of_obtention = serializers.IntegerField()
    training_ids = serializers.ListField(child=serializers.UUIDField(), required=False)

    # Graduate Info
    faculty_id = serializers.UUIDField(required=False)
    option = serializers.CharField(max_length=127, required=False, allow_blank=True)
    mention = serializers.CharField(max_length=45, required=False, allow_blank=True)
    degree_id = serializers.UUIDField(required=False)

    # Inscription
    academic_year_id = serializers.UUIDField()
    class_id = serializers.UUIDField(required=False)
    date_inscription = serializers.DateField()

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get("user")
        if not user:
            raise serializers.ValidationError("Logged-in user is required.")

        # Create Student
        student = Student.objects.create(
            user=user,
            colline_id=validated_data["colline"],
            cam=validated_data.get("cam"),
        )

        # Parents
        parent_ids = validated_data.get("parent_ids", [])
        parents = list(Parent.objects.filter(id__in=parent_ids))
        for p_data in validated_data.get("new_parents", []):
            profession = Profession.objects.get(id=p_data["profession_id"])
            p = Parent.objects.create(
                parent_name=p_data["parent_name"],
                parent_phone=p_data["parent_phone"],
                parent_email=p_data.get("parent_email", ""),
                profession=profession,
                parent_type=p_data["parent_type"],
                is_alive=p_data.get("is_alive", True),
                is_contact_person=p_data.get("is_contact_person", False),
            )
            parents.append(p)
        student.parent.set(parents)

        # Files
        file_ids = validated_data.get("file_ids", [])
        for f in StudentFile.objects.filter(id__in=file_ids):
            f.student = student
            f.save()
        for f_data in validated_data.get("new_files", []):
            StudentFile.objects.create(student=student, **f_data)

        # Highschool Info
        hs_info = StudentHsInfo.objects.create(
            student=student,
            highschool_id=validated_data["highschool_id"],
            certificate_id=validated_data["certificate_id"],
            se_mark=validated_data.get("se_mark"),
            date_of_obtention=validated_data["date_of_obtention"],
        )
        training_ids = validated_data.get("training_ids", [])
        if training_ids:
            trainings = Training.objects.filter(id__in=training_ids)
            hs_info.formation.set(trainings)

        # Graduate Info
        if validated_data.get("faculty_id") and validated_data.get("degree_id"):
            faculty = Faculty.objects.get(id=validated_data["faculty_id"])
            first_department = faculty.departments.order_by("id").first()
            StudentGraduateInfo.objects.create(
                student=student,
                department=first_department if first_department else None,
                option=validated_data.get("option", ""),
                mention=validated_data.get("mention", ""),
                degree_id=validated_data["degree_id"],
            )

        # Inscription
        class_id = validated_data.get("class_id")
        if not class_id and validated_data.get("faculty_id"):
            faculty = Faculty.objects.get(id=validated_data["faculty_id"])
            first_department = faculty.departments.order_by("id").first()
            if first_department:
                first_class = first_department.classes.order_by("id").first()
                if first_class:
                    class_id = first_class.id
        Inscription.objects.create(
            student=student,
            academic_year_id=validated_data["academic_year_id"],
            class_fk_id=class_id,
            date_inscription=validated_data["date_inscription"],
            regist_status="Active",
        )

        return student
