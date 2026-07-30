"""
Authoritative Typesense collection schemas and field mappings.

This module centralizes schema definitions to avoid duplication and
per-request network lookups. It is imported by:
- query_builder (for field validation)
- management commands (create_collections, index)
"""

from django.db.models import Model

# =============================================================================
# Collection schemas
# =============================================================================

# Each schema is a dict with "fields" and optionally "default_sorting_field".
# Fields are in the format expected by Typesense's collection create API.

# All fields except `id` are declared optional so that indexing never fails
# when a particular attribute is absent on a given row. Search simply will not
# match on a missing field. `created_at` is a synthetic, stable tiebreaker
# (see DocumentSyncer._stable_created_at): these academic models carry no real
# creation timestamp, so we derive a deterministic int from the primary key
# instead of injecting time.time() on every save (which churned freshness).
COLLECTION_SCHEMAS: dict[str, dict] = {
    "courses": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "course_name", "type": "string", "optional": True},
            {"name": "course_code", "type": "string", "optional": True},
            {"name": "module_name", "type": "string", "optional": True},
            {"name": "module_id", "type": "string", "optional": True},
            {"name": "department_name", "type": "string", "optional": True},
            {"name": "faculty_name", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "credits", "type": "int32", "optional": True, "sort": True},
            {"name": "cm", "type": "int32", "optional": True},
            {"name": "td", "type": "int32", "optional": True},
            {"name": "tp", "type": "int32", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
            {"name": "updated_at", "type": "int64", "optional": True},
        ],
        "default_sorting_field": "created_at",
    },
    "modules": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "module_name", "type": "string", "optional": True},
            {"name": "module_code", "type": "string", "optional": True},
            {"name": "class_name", "type": "string", "optional": True},
            {"name": "department_name", "type": "string", "optional": True},
            {"name": "faculty_name", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "teachers": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "full_name", "type": "string", "optional": True},
            {"name": "email", "type": "string", "optional": True},
            {"name": "phone", "type": "string", "optional": True},
            {"name": "teacher_grade", "type": "string", "optional": True},
            {"name": "speciality", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "academic_year", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "classes": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "class_name", "type": "string", "optional": True},
            {"name": "department_name", "type": "string", "optional": True},
            {"name": "faculty_name", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "departments": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "department_name", "type": "string", "optional": True},
            {"name": "department_code", "type": "string", "optional": True},
            {"name": "faculty_name", "type": "string", "optional": True},
            {"name": "faculty_id", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "faculties": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "faculty_name", "type": "string", "optional": True},
            {"name": "faculty_abreviation", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "university_name", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "universities": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "university_name", "type": "string", "optional": True},
            {"name": "university_abrev", "type": "string", "optional": True},
            {"name": "country", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "students": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "full_name", "type": "string", "optional": True},
            {"name": "email", "type": "string", "optional": True},
            {"name": "phone_number", "type": "string", "optional": True},
            {"name": "matricule", "type": "string", "optional": True},
            {"name": "birthdate", "type": "string", "optional": True},
            {"name": "birthplace", "type": "string", "optional": True},
            {"name": "gender", "type": "string", "optional": True},
            {"name": "colline_name", "type": "string", "optional": True},
            {"name": "academic_year", "type": "string", "optional": True},
            {"name": "is_active", "type": "bool", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "inscriptions": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "student_id", "type": "string", "optional": True},
            {"name": "student_full_name", "type": "string", "optional": True},
            {"name": "student_matricule", "type": "string", "optional": True},
            {"name": "academic_year", "type": "string", "optional": True},
            {"name": "class_name", "type": "string", "optional": True},
            {"name": "class_group_name", "type": "string", "optional": True},
            {"name": "department_name", "type": "string", "optional": True},
            {"name": "faculty_name", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "regist_status", "type": "string", "optional": True},
            {"name": "date_inscription", "type": "int64", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "class_groups": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "group_name", "type": "string", "optional": True},
            {"name": "class_name", "type": "string", "optional": True},
            {"name": "academic_year", "type": "string", "optional": True},
            {"name": "department_name", "type": "string", "optional": True},
            {"name": "faculty_name", "type": "string", "optional": True},
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "student_count", "type": "int32", "optional": True, "sort": True},
            {"name": "is_default", "type": "bool", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "users": {
        "fields": [
            {"name": "id", "type": "string"},
            # Identité — recherchable
            {"name": "username", "type": "string", "optional": True},
            {"name": "first_name", "type": "string", "optional": True},
            {"name": "last_name", "type": "string", "optional": True},
            {"name": "full_name", "type": "string", "optional": True},
            {"name": "email", "type": "string", "optional": True},
            {"name": "phone_number", "type": "string", "optional": True},
            # Infos administratives
            {"name": "matricule", "type": "string", "optional": True},
            {"name": "cni", "type": "string", "optional": True},
            {"name": "birthdate", "type": "string", "optional": True},
            {"name": "birthplace", "type": "string", "optional": True},
            {"name": "gender", "type": "string", "optional": True},
            # Académique
            {"name": "grade", "type": "string", "optional": True},
            {"name": "speciality", "type": "string", "optional": True},
            # Rôles — booléens dérivés des profils OneToOne
            {"name": "is_teacher", "type": "bool", "optional": True},
            {"name": "is_student", "type": "bool", "optional": True},
            {"name": "is_faculty_admin", "type": "bool", "optional": True},
            {"name": "is_university_admin", "type": "bool", "optional": True},
            # Rattachement université (dénormalisé)
            {"name": "university_id", "type": "string", "optional": True},
            {"name": "university_name", "type": "string", "optional": True},
            # Rattachement étudiant (dénormalisé depuis Student → ClassGroup → Class → Dept → Faculty)
            {"name": "student_class_group", "type": "string", "optional": True},
            {"name": "student_class", "type": "string", "optional": True},
            {"name": "student_department", "type": "string", "optional": True},
            {"name": "student_faculty", "type": "string", "optional": True},
            # Rattachement FacultyAdmin
            {"name": "admin_faculty_id", "type": "string", "optional": True},
            {"name": "admin_faculty_name", "type": "string", "optional": True},
            # Système
            {"name": "is_active", "type": "bool", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "profiles": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "user_id", "type": "string", "optional": True},
            {"name": "first_name", "type": "string", "optional": True},
            {"name": "last_name", "type": "string", "optional": True},
            {"name": "email", "type": "string", "optional": True},
            {"name": "phone_number", "type": "string", "optional": True},
            {"name": "position", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "sessions": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "session_name", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "results": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "mark", "type": "float", "optional": True, "sort": True},
            {"name": "status", "type": "string", "optional": True},
            {"name": "comment", "type": "string", "optional": True},
            {"name": "course_name", "type": "string", "optional": True},
            {"name": "student_first_name", "type": "string", "optional": True},
            {"name": "student_last_name", "type": "string", "optional": True},
            {"name": "student_email", "type": "string", "optional": True},
            {"name": "session_name", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
    "jury_sessions": {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "session_name", "type": "string", "optional": True},
            {"name": "status", "type": "string", "optional": True},
            {"name": "is_deleted", "type": "bool", "optional": True},
            {"name": "created_at", "type": "int64"},
        ],
        "default_sorting_field": "created_at",
    },
}


# =============================================================================
# Model-to-collection mapping (matches Django settings)
# =============================================================================

MODEL_TO_COLLECTION = {
    "Course": "courses",
    "Module": "modules",
    "Teacher": "teachers",
    "Class": "classes",
    "ClassGroup": "class_groups",
    "Department": "departments",
    "Faculty": "faculties",
    "University": "universities",
    "User": "users",
    "Inscription": "inscriptions",
    "Student": "students",
    "Session": "sessions",
    "Result": "results",
    "JurySession": "jury_sessions",
    "Profile": "profiles",
}


# =============================================================================
# Field mapping: Django field names -> Typesense field names (per collection)
# =============================================================================

# Collection-specific mappings. Keys are Django field names, values are Typesense field names.
# If a Django field is not listed here, it is assumed to have the same name in Typesense.

COLLECTION_FIELD_MAPPING = {
    "courses": {
        "course_name": "course_name",
        "course_code": "course_code",
        "module_name": "module_name",
        "module_id": "module_id",
        "module__module_name": "module_name",
        "department_name": "department_name",
        "department__department_name": "department_name",
        "faculty_name": "faculty_name",
        "university_id": "university_id",
        "credits": "credits",
        "cm": "cm",
        "td": "td",
        "tp": "tp",
        "created_at": "created_at",
        "updated_at": "updated_at",
    },
    "modules": {
        "module_name": "module_name",
        "module_code": "module_code",
        "code": "module_code",  # Django uses 'code', Typesense uses 'module_code'
        "class_name": "class_name",
        "class_fk__class_name": "class_name",
        "department_name": "department_name",
        "faculty_name": "faculty_name",
        "university_id": "university_id",
        "created_at": "created_at",
    },
    "teachers": {
        "full_name": "full_name",
        "email": "email",
        "phone": "phone",
        "teacher_grade": "teacher_grade",
        "speciality": "speciality",
        "university_id": "university_id",
        "academic_year": "academic_year",
        "academic_year_id": "academic_year",
        "created_at": "created_at",
    },
    "classes": {
        "class_name": "class_name",
        "department_name": "department_name",
        "department__department_name": "department_name",
        "faculty_name": "faculty_name",
        "university_id": "university_id",
        "created_at": "created_at",
    },
    "departments": {
        "department_name": "department_name",
        "department_code": "department_code",
        "abreviation": "department_code",  # Django uses 'abreviation', schema uses 'department_code'
        "faculty_name": "faculty_name",
        "faculty__faculty_name": "faculty_name",
        "faculty_id": "faculty_id",
        "university_id": "university_id",
        "created_at": "created_at",
    },
    "faculties": {
        "faculty_name": "faculty_name",
        "faculty_abreviation": "faculty_abreviation",
        "university_id": "university_id",
        "university_name": "university_name",
        "created_at": "created_at",
    },
    "universities": {
        "university_name": "university_name",
        "university_abrev": "university_abrev",
        "country": "country",
        "country__country_name": "country",
        "created_at": "created_at",
    },
    "students": {
        "full_name": "full_name",
        "user__first_name": "full_name",
        "user__last_name": "full_name",
        "email": "email",
        "user__email": "email",
        "phone_number": "phone_number",
        "user__phone_number": "phone_number",
        "matricule": "matricule",
        "birthdate": "birthdate",
        "user__birth_date": "birthdate",
        "birthplace": "birthplace",
        "user__birth_place": "birthplace",
        "gender": "gender",
        "user__gender": "gender",
        "colline_name": "colline_name",
        "colline__name": "colline_name",
        "academic_year": "academic_year",
        "academic_year_id": "academic_year",
        "is_active": "is_active",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
    "inscriptions": {
        "student_id": "student_id",
        "student_full_name": "student_full_name",
        "first_name": "student_full_name",
        "last_name": "student_full_name",
        "student__user__first_name": "student_full_name",
        "student__user__last_name": "student_full_name",
        "student_matricule": "student_matricule",
        "matricule": "student_matricule",
        "student__matricules__matricule": "student_matricule",
        "academic_year": "academic_year",
        "academic_year_id": "academic_year",
        "academic_year__name": "academic_year",
        "class_name": "class_name",
        "class_fk__class_name": "class_name",
        "class_group_name": "class_group_name",
        "class_group__group_name": "class_group_name",
        "department_name": "department_name",
        "class_fk__department__department_name": "department_name",
        "faculty_name": "faculty_name",
        "class_fk__department__faculty__faculty_name": "faculty_name",
        "university_id": "university_id",
        "class_fk__department__faculty__university_id": "university_id",
        "regist_status": "regist_status",
        "date_inscription": "date_inscription",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
    "class_groups": {
        "group_name": "group_name",
        "class_name": "class_name",
        "class_fk__class_name": "class_name",
        "academic_year": "academic_year",
        "academic_year_id": "academic_year",
        "academic_year__name": "academic_year",
        "department_name": "department_name",
        "class_fk__department__department_name": "department_name",
        "faculty_name": "faculty_name",
        "class_fk__department__faculty__faculty_name": "faculty_name",
        "university_id": "university_id",
        "class_fk__department__faculty__university_id": "university_id",
        "student_count": "student_count",
        "is_default": "is_default",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
    "users": {
        "username": "username",
        "first_name": "first_name",
        "last_name": "last_name",
        "full_name": "full_name",
        "email": "email",
        "phone_number": "phone_number",
        "matricule": "matricule",
        "cni": "cni",
        "birthdate": "birthdate",
        "birthplace": "birthplace",
        "gender": "gender",
        "grade": "grade",
        "speciality": "speciality",
        "is_teacher": "is_teacher",
        "is_student": "is_student",
        "is_faculty_admin": "is_faculty_admin",
        "is_university_admin": "is_university_admin",
        "university_id": "university_id",
        "university_name": "university_name",
        "student_class_group": "student_class_group",
        "student_class": "student_class",
        "student_department": "student_department",
        "student_faculty": "student_faculty",
        "admin_faculty_id": "admin_faculty_id",
        "admin_faculty_name": "admin_faculty_name",
        "is_active": "is_active",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
    "profiles": {
        "user__first_name": "first_name",
        "user__last_name": "last_name",
        "user__email": "email",
        "user__phone_number": "phone_number",
        "first_name": "first_name",
        "last_name": "last_name",
        "position": "position",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
    "sessions": {
        "session_name": "session_name",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
    "results": {
        "comment": "comment",
        "course__course_name": "course_name",
        "inscription__student__user__first_name": "student_first_name",
        "inscription__student__user__last_name": "student_last_name",
        "inscription__student__user__email": "student_email",
        "session__session_name": "session_name",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
    "jury_sessions": {
        "session_name": "session_name",
        "status": "status",
        "is_deleted": "is_deleted",
        "created_at": "created_at",
    },
}


# =============================================================================
# Helper functions
# =============================================================================


def get_collection_for_model(model: type[Model]) -> str:
    """Return the Typesense collection name for a Django model."""
    model_name = model.__name__
    return MODEL_TO_COLLECTION.get(model_name, model_name.lower())


def get_collection_schema(collection: str) -> dict | None:
    """Return the schema for a collection, or None if not found."""
    return COLLECTION_SCHEMAS.get(collection)


def get_valid_fields(collection: str) -> list[str]:
    """Return the list of field names (strings) for a collection."""
    schema = get_collection_schema(collection)
    if not schema:
        return []
    return [f["name"] for f in schema.get("fields", [])]


def map_django_fields_to_typesense(
    collection: str, django_fields: list[str]
) -> list[str]:
    """
    Convert Django field names (with __ notation) to Typesense flat field names.

    Tries full dotted path first, then falls back to last component.
    Example:
        ["module__module_name", "code"] -> ["module_name", "module_code"]
        ["student__matricules__matricule"] -> ["student_matricule"]
    """
    mapping = COLLECTION_FIELD_MAPPING.get(collection, {})
    typesense_fields = []
    for field in django_fields:
        if "__" in field:
            mapped = mapping.get(field)
            if mapped is None:
                parts = field.split("__")
                last_part = parts[-1]
                mapped = mapping.get(last_part, last_part)
            typesense_fields.append(mapped)
        else:
            mapped = mapping.get(field, field)
            typesense_fields.append(mapped)
    return typesense_fields


def filter_valid_fields(collection: str, fields: list[str]) -> list[str]:
    """Return only the fields that exist in the collection schema."""
    valid = get_valid_fields(collection)
    if not valid:
        return fields  # no schema info, trust the input
    return [f for f in fields if f in valid]
