"""Tests for SearchService orchestration, aggregation, and scoring."""

from unittest.mock import MagicMock

from django.apps import apps
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

# ---------------------------------------------------------------------------
# Tests that don't need a database (pure unit tests)
# ---------------------------------------------------------------------------


class AggregationScoringTests(SimpleTestCase):
    """Test the aggregation and scoring logic in isolation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from services.search.service import SearchService

        cls.service = SearchService()

    def test_extract_text_match_score_from_text_match_field(self):
        hit = {"text_match": 120.5}
        score = self.service._extract_text_match_score(hit)
        self.assertEqual(score, 120.5)

    def test_extract_text_match_score_from_text_match_info(self):
        hit = {"text_match_info": {"score": 85.0}}
        score = self.service._extract_text_match_score(hit)
        self.assertEqual(score, 85.0)

    def test_extract_text_match_score_from_matches_array(self):
        hit = {"matches": [{"score": 50.0}, {"score": 90.0}]}
        score = self.service._extract_text_match_score(hit)
        self.assertEqual(score, 90.0)  # max

    def test_extract_text_match_score_no_match_returns_zero(self):
        hit = {"document": {"id": "1"}}
        score = self.service._extract_text_match_score(hit)
        self.assertEqual(score, 0.0)

    def test_tokens_appear_in_order_true(self):
        result = self.service._tokens_appear_in_order(
            ["algo", "data"],
            ["algo", "intro", "data", "struct"],
        )
        self.assertTrue(result)

    def test_tokens_appear_in_order_false(self):
        result = self.service._tokens_appear_in_order(
            ["data", "algo"],
            ["algo", "intro", "data"],
        )
        self.assertFalse(result)

    def test_tokens_appear_in_order_empty_query(self):
        result = self.service._tokens_appear_in_order([], ["algo", "data"])
        self.assertFalse(result)

    def test_aggregate_deduplicates_by_document_id(self):
        strategies = [
            {"_strategy_name": "exact"},
            {"_strategy_name": "fuzzy"},
        ]
        multi_results = [
            {
                "hits": [
                    {
                        "document": {
                            "id": "1",
                            "course_name": "Algo",
                        },
                        "text_match": 100.0,
                    }
                ]
            },
            {
                "hits": [
                    {
                        "document": {
                            "id": "1",
                            "course_name": "Algo",
                        },
                        "text_match": 50.0,
                    }
                ]
            },
        ]
        aggregated, _counts = self.service._aggregate_and_score(
            multi_results, strategies, "algo"
        )
        self.assertEqual(len(aggregated), 1)
        self.assertIn("1", aggregated)
        self.assertIn("exact", aggregated["1"]["strategies"])
        self.assertIn("fuzzy", aggregated["1"]["strategies"])

    def test_aggregate_tracks_strategy_counts(self):
        strategies = [
            {"_strategy_name": "exact"},
            {"_strategy_name": "prefix"},
        ]
        multi_results = [
            {
                "hits": [
                    {
                        "document": {"id": "1", "name": "X"},
                        "text_match": 10,
                    }
                ]
            },
            {"hits": []},
        ]
        _, counts = self.service._aggregate_and_score(multi_results, strategies, "test")
        self.assertEqual(counts["exact"], 1)
        self.assertEqual(counts["prefix"], 0)

    def test_aggregate_skips_empty_document_id(self):
        strategies = [{"_strategy_name": "test"}]
        multi_results = [{"hits": [{"document": {"id": ""}, "text_match": 10}]}]
        aggregated, _ = self.service._aggregate_and_score(
            multi_results, strategies, "test"
        )
        self.assertEqual(len(aggregated), 0)

    def test_aggregate_handles_hit_without_document(self):
        strategies = [{"_strategy_name": "test"}]
        multi_results = [{"hits": [{"text_match": 10}]}]
        aggregated, _ = self.service._aggregate_and_score(
            multi_results, strategies, "test"
        )
        self.assertEqual(len(aggregated), 0)

    def test_compute_final_score_exact_phrase_bonus(self):
        data = {
            "text_score": 100.0,
            "rank_score": 1.0,
            "token_coverage": 1.0,
        }
        score = self.service._compute_final_score(
            data=data,
            normalized_query="algorithmique",
            query_tokens=["algorithmique"],
            normalized_document="cours algorithmique avancé",
            maximum_text_score=100.0,
        )
        # Exact phrase match within the document → tier_bonus=100
        self.assertGreater(score, 90.0)
        self.assertIn("exact_phrase_match", data)
        self.assertTrue(data["exact_phrase_match"])

    def test_compute_final_score_partial_match_lower(self):
        data = {
            "text_score": 10.0,
            "rank_score": 0.1,
            "token_coverage": 0.3,
        }
        score = self.service._compute_final_score(
            data=data,
            normalized_query="xyz pdq",
            query_tokens=["xyz", "pdq"],
            normalized_document="un cours différent",
            maximum_text_score=100.0,
        )
        # No fuzzy match → low tier, well below 50
        self.assertLess(score, 50.0)

    def test_compute_final_score_detects_exact_phrase(self):
        """Verify exact_phrase_match is True when query appears verbatim."""
        data = {
            "text_score": 80.0,
            "rank_score": 0.5,
        }
        self.service._compute_final_score(
            data=data,
            normalized_query="reseaux informatiques",
            query_tokens=["reseaux", "informatiques"],
            normalized_document="cours de reseaux informatiques avancés",
            maximum_text_score=80.0,
        )
        self.assertTrue(data.get("exact_phrase_match"))

    def test_typo_distance_within_threshold(self):
        self.assertTrue(self.service._within_typo_distance("automatess", "automates"))

    def test_typo_distance_exceeds_threshold(self):
        self.assertFalse(
            self.service._within_typo_distance("automatessss", "automates")
        )

    def test_typo_distance_exact_match(self):
        self.assertTrue(self.service._within_typo_distance("instrument", "instrument"))

    def test_levenshtein_known_distance(self):
        dist = self.service._levenshtein_distance("kitten", "sitting", 10)
        self.assertEqual(dist, 3)


class PreserveOrderTests(SimpleTestCase):
    """Test the _preserve_order method."""

    def setUp(self):
        from services.search.service import SearchService

        self.service = SearchService()

    def test_preserve_order_annotates_queryset(self):
        mock_qs = MagicMock()
        mock_qs.annotate.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs

        result = self.service._preserve_order(mock_qs, ["id1", "id2", "id3"])
        self.assertIsNotNone(result)
        mock_qs.annotate.assert_called_once()
        mock_qs.order_by.assert_called_once_with("_typesense_order")


class ORMFallbackTests(SimpleTestCase):
    """Test the ORM fallback behavior."""

    def setUp(self):
        from rest_framework.request import Request

        from services.search.service import SearchService

        self.service = SearchService()
        self.factory = APIRequestFactory()
        self.Request = Request

    def _drf_request(self, **params):
        """Create a DRF Request with query_params support."""
        wsgi_req = self.factory.get("/", params)
        return self.Request(wsgi_req)

    def test_fallback_applies_icontains(self):
        request = self._drf_request(search="algo")
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.count.return_value = 3

        _result_qs, count, time_ms = self.service._orm_fallback(
            mock_qs, request, search_fields=["course_name", "course_code"]
        )
        self.assertEqual(count, 3)
        self.assertEqual(time_ms, 0)

    def test_fallback_empty_query_no_filter(self):
        request = self._drf_request(search="")
        mock_qs = MagicMock()
        mock_qs.count.return_value = 10

        _result_qs, count, _time_ms = self.service._orm_fallback(
            mock_qs, request, search_fields=["course_name"]
        )
        mock_qs.filter.assert_not_called()
        self.assertEqual(count, 10)


# ---------------------------------------------------------------------------
# Tests that need a database (integration tests)
# ---------------------------------------------------------------------------


@override_settings(
    TYPESENSE_CONFIG={
        "host": "localhost",
        "port": 8108,
        "protocol": "http",
        "api_key": "",
        "enabled": True,
        "force_fallback": True,
        "fallback_enabled": True,
    }
)
class SearchServiceIntegrationTests(TestCase):
    """Integration tests using the test database.

    Typesense is unreachable in CI/dev without a local instance,
    so we force the ORM fallback path.
    """

    @staticmethod
    def _get_model(label):
        """Get a model using its full Django app label."""
        app_label, model_name = label.rsplit(".", 1)
        return apps.get_model(app_label, model_name)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.Request = Request

        Course = self._get_model("course_app.Course")
        Module = self._get_model("module_app.Module")
        Class = self._get_model("class_app.Class")
        Department = self._get_model("department_app.Department")
        Faculty = self._get_model("faculty_app.Faculty")
        University = self._get_model("university_app.University")
        Country = self._get_model("country_app.Country")
        TypeFormation = self._get_model("faculty_app.TypeFormation")
        Semester = self._get_model("module_app.Semester")

        country = Country.objects.create(country_name="Burundi")
        uni = University.objects.create(
            university_name="Université Test",
            university_abrev="UT",
            country=country,
        )
        type_formation = TypeFormation.objects.create(
            name="Classique",
            code="C",
        )
        faculty = Faculty.objects.create(
            faculty_name="Faculté des Sciences",
            faculty_abreviation="FS",
            types=type_formation,
            university=uni,
        )
        dept = Department.objects.create(
            department_name="Informatique",
            abreviation="INFO",
            faculty=faculty,
        )
        class_obj = Class.objects.create(
            class_name="L1 Info",
            department=dept,
        )
        semester = Semester.objects.create(number=1)
        module = Module.objects.create(
            module_name="Algorithmique",
            code="ALGO101",
            class_fk=class_obj,
            semester=semester,
        )
        Course.objects.create(
            course_name="Algorithmique et Structures de Données",
            course_code="ALGO101-C",
            module=module,
            credits=6,
        )
        Course.objects.create(
            course_name="Réseaux Informatiques",
            course_code="RES101-C",
            module=module,
            credits=4,
        )

    def _drf_request(self, **params):
        """Create a DRF Request with query_params support."""
        wsgi_req = self.factory.get("/", params)
        return self.Request(wsgi_req)

    def test_search_finds_course_by_exact_name(self):
        from services.search.service import SearchService

        Course = self._get_model("course_app.Course")

        request = self._drf_request(search="Algorithmique et Structures de Données")
        qs = Course.objects.all()

        service = SearchService()
        result_qs, found, _time_ms = service.apply_search(
            model=Course,
            queryset=qs,
            request=request,
            search_fields=["course_name", "course_code"],
        )

        self.assertGreaterEqual(found, 1)
        self.assertTrue(
            result_qs.filter(course_name__icontains="Algorithmique").exists()
        )

    def test_search_finds_by_partial_code(self):
        from services.search.service import SearchService

        Course = self._get_model("course_app.Course")

        request = self._drf_request(search="ALGO101")
        qs = Course.objects.all()

        service = SearchService()
        _result_qs, found, _time_ms = service.apply_search(
            model=Course,
            queryset=qs,
            request=request,
            search_fields=["course_name", "course_code"],
        )

        self.assertGreaterEqual(found, 1)

    def test_search_empty_query_returns_all(self):
        from services.search.service import SearchService

        Course = self._get_model("course_app.Course")

        request = self._drf_request(search="")
        qs = Course.objects.all()
        total = qs.count()

        service = SearchService()
        _result_qs, found, time_ms = service.apply_search(
            model=Course,
            queryset=qs,
            request=request,
            search_fields=["course_name"],
        )

        self.assertEqual(found, total)
        self.assertEqual(time_ms, 0)

    def test_search_no_match_returns_empty(self):
        from services.search.service import SearchService

        Course = self._get_model("course_app.Course")

        request = self._drf_request(search="zzzzzzz_nonexistent_zzzzzzz")
        qs = Course.objects.all()

        service = SearchService()
        _result_qs, found, _time_ms = service.apply_search(
            model=Course,
            queryset=qs,
            request=request,
            search_fields=["course_name"],
        )

        self.assertEqual(found, 0)
