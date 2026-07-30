"""Unit tests for the centralized schema registry."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from services.search.schemas import (
    COLLECTION_FIELD_MAPPING,
    COLLECTION_SCHEMAS,
    MODEL_TO_COLLECTION,
    filter_valid_fields,
    get_collection_for_model,
    get_collection_schema,
    get_valid_fields,
    map_django_fields_to_typesense,
)


class SchemaRegistryTests(SimpleTestCase):
    """Verify the authoritative schema definitions are consistent."""

    def test_all_collections_have_fields(self):
        for name, schema in COLLECTION_SCHEMAS.items():
            with self.subTest(collection=name):
                self.assertIn("fields", schema)
                self.assertGreater(len(schema["fields"]), 0)

    def test_all_collections_have_id_field(self):
        for name, schema in COLLECTION_SCHEMAS.items():
            with self.subTest(collection=name):
                field_names = [f["name"] for f in schema["fields"]]
                self.assertIn("id", field_names)

    def test_model_to_collection_covers_indexed_models(self):
        expected = {
            "Course",
            "Module",
            "Teacher",
            "Class",
            "ClassGroup",
            "Department",
            "Faculty",
            "University",
            "User",
            "Inscription",
            "Student",
            "Session",
            "Result",
            "JurySession",
            "Profile",
        }
        self.assertEqual(set(MODEL_TO_COLLECTION.keys()), expected)

    def test_collection_names_unique(self):
        names = list(MODEL_TO_COLLECTION.values())
        self.assertEqual(len(names), len(set(names)))

    def test_field_mapping_has_all_collections(self):
        for collection in MODEL_TO_COLLECTION.values():
            with self.subTest(collection=collection):
                self.assertIn(collection, COLLECTION_FIELD_MAPPING)

    def test_field_mapping_references_schema_fields(self):
        for collection, mapping in COLLECTION_FIELD_MAPPING.items():
            valid = set(get_valid_fields(collection))
            with self.subTest(collection=collection):
                for ts_field in mapping.values():
                    self.assertIn(
                        ts_field,
                        valid,
                        f"{ts_field} not in schema for {collection}",
                    )


class SchemaHelperTests(SimpleTestCase):
    """Tests for the schema helper functions."""

    def test_get_collection_for_model_mock(self):
        mock_model = MagicMock(__name__="Course")
        self.assertEqual(get_collection_for_model(mock_model), "courses")

    def test_get_collection_for_model_fallback(self):
        class UnknownModel:
            pass

        self.assertEqual(get_collection_for_model(UnknownModel), "unknownmodel")

    def test_get_collection_schema_exists(self):
        schema = get_collection_schema("courses")
        self.assertIsNotNone(schema)
        self.assertIn("fields", schema)

    def test_get_collection_schema_missing(self):
        self.assertIsNone(get_collection_schema("nonexistent"))

    def test_get_valid_fields_returns_list(self):
        fields = get_valid_fields("teachers")
        self.assertIsInstance(fields, list)
        self.assertIn("full_name", fields)
        self.assertIn("email", fields)
        self.assertIn("id", fields)

    def test_map_django_fields_flat(self):
        result = map_django_fields_to_typesense("modules", ["code"])
        self.assertEqual(result, ["module_code"])

    def test_map_django_fields_relation(self):
        result = map_django_fields_to_typesense("courses", ["module__module_name"])
        self.assertEqual(result, ["module_name"])

    def test_map_django_fields_unknown_passthrough(self):
        result = map_django_fields_to_typesense("courses", ["unknown_field"])
        self.assertEqual(result, ["unknown_field"])

    def test_filter_valid_fields_keeps_only_schema_fields(self):
        result = filter_valid_fields("courses", ["course_name", "bogus", "id"])
        self.assertIn("course_name", result)
        self.assertIn("id", result)
        self.assertNotIn("bogus", result)

    def test_filter_valid_fields_unknown_collection_passthrough(self):
        result = filter_valid_fields("unknown", ["field1", "field2"])
        self.assertEqual(result, ["field1", "field2"])
