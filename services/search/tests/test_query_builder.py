"""Unit tests for SearchQueryBuilder strategy generation and parameter construction."""

from unittest.mock import MagicMock

from django.test import SimpleTestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from services.search.query_builder import SearchQueryBuilder


class StrategyGenerationTests(SimpleTestCase):
    """Test multi-strategy generation without Typesense connectivity."""

    def setUp(self):
        self.builder = SearchQueryBuilder()
        self.factory = APIRequestFactory()

    def _make_request(self, search="", **params):
        wsgi_req = self.factory.get("/", {"search": search, **params})
        return Request(wsgi_req)

    def _mock_model(self, name="Course", app_label="course_app"):
        model = MagicMock()
        model.__name__ = name
        model._meta.app_label = app_label
        model._meta.fields = [
            MagicMock(name="id"),
            MagicMock(name="course_name"),
            MagicMock(name="course_code"),
            MagicMock(name="credits"),
        ]
        for f in model._meta.fields:
            f.name = f._mock_name
        return model

    def test_empty_query_returns_empty_strategies(self):
        request = self._make_request(search="")
        model = self._mock_model()
        strategies = self.builder.build_multiple_strategies(
            model=model,
            query="",
            request=request,
            search_fields=["course_name"],
        )
        self.assertEqual(strategies, [])

    def test_single_token_generates_strategies(self):
        request = self._make_request(search="algorithmique")
        model = self._mock_model()
        strategies = self.builder.build_multiple_strategies(
            model=model,
            query="algorithmique",
            request=request,
            search_fields=["course_name"],
        )
        self.assertGreater(len(strategies), 0)
        names = [s["_strategy_name"] for s in strategies]
        self.assertIn("exact", names)
        self.assertIn("prefix", names)
        self.assertIn("fuzzy", names)

    def test_multi_token_generates_reversed_and_individual(self):
        request = self._make_request(search="administration amenagemen")
        model = self._mock_model()
        strategies = self.builder.build_multiple_strategies(
            model=model,
            query="administration amenagemen",
            request=request,
            search_fields=["course_name"],
        )
        names = [s["_strategy_name"] for s in strategies]
        self.assertIn("reversed", names)
        # Individual tokens generate one per meaningful token
        self.assertTrue(any(name.startswith("single_token_") for name in names))

    def test_strategies_capped_at_ten(self):
        request = self._make_request(search="a b c d e f g h i j k l m")
        model = self._mock_model()
        strategies = self.builder.build_multiple_strategies(
            model=model,
            query="a b c d e f g h i j k l m",
            request=request,
            search_fields=["course_name"],
        )
        self.assertLessEqual(len(strategies), 10)

    def test_strategies_contain_collection(self):
        request = self._make_request(search="algorithmique")
        model = self._mock_model()
        strategies = self.builder.build_multiple_strategies(
            model=model,
            query="algorithmique",
            request=request,
            search_fields=["course_name"],
        )
        for s in strategies:
            self.assertIn("collection", s)

    def test_strategy_exact_no_typos(self):
        request = self._make_request(search="automatess")
        model = self._mock_model()
        strategies = self.builder.build_multiple_strategies(
            model=model,
            query="automatess",
            request=request,
            search_fields=["course_name"],
        )
        exact = next(s for s in strategies if s["_strategy_name"] == "exact")
        self.assertEqual(exact["num_typos"], 0)
        self.assertFalse(exact["prefix"])


class QueryParameterTests(SimpleTestCase):
    """Test the parameter construction in SearchQueryBuilder.build()."""

    def setUp(self):
        self.builder = SearchQueryBuilder()
        self.factory = APIRequestFactory()

    def _mock_model(self, name="Course", app_label="course_app"):
        model = MagicMock()
        model.__name__ = name
        model._meta.app_label = app_label
        model._meta.fields = [
            MagicMock(name="id"),
            MagicMock(name="course_name"),
            MagicMock(name="course_code"),
        ]
        for f in model._meta.fields:
            f.name = f._mock_name
        return model

    def test_build_includes_query_by(self):
        request = Request(self.factory.get("/", {"search": "test"}))
        model = self._mock_model()
        params = self.builder.build(
            model=model,
            query="test",
            request=request,
            search_fields=["course_name"],
        )
        self.assertIn("query_by", params)
        self.assertIn("course_name", params["query_by"])

    def test_build_normalizes_query(self):
        request = Request(self.factory.get("/", {"search": "ÉLECTRONIQUE"}))
        model = self._mock_model()
        params = self.builder.build(
            model=model,
            query="ÉLECTRONIQUE",
            request=request,
            search_fields=["course_name"],
        )
        self.assertEqual(params["q"], "electronique")

    def test_build_includes_filter_is_deleted(self):
        request = Request(self.factory.get("/", {"search": "test"}))
        model = self._mock_model()
        params = self.builder.build(
            model=model,
            query="test",
            request=request,
            search_fields=["course_name"],
        )
        self.assertIn("is_deleted:=", params["filter_by"])

    def test_autocomplete_enables_prefix(self):
        request = Request(
            self.factory.get("/", {"search": "algo", "autocomplete": "true"})
        )
        model = self._mock_model()
        params = self.builder.build(
            model=model,
            query="algo",
            request=request,
            search_fields=["course_name"],
        )
        self.assertTrue(params.get("prefix"))

    def test_ordering_param_maps_to_sort_by(self):
        request = Request(
            self.factory.get("/", {"search": "test", "ordering": "-credits"})
        )
        model = self._mock_model(name="Course")
        params = self.builder.build(
            model=model,
            query="test",
            request=request,
            search_fields=["course_name"],
        )
        self.assertIn("sort_by", params)
        self.assertIn("credits:desc", params["sort_by"])


class CandidatePoolSizeTests(SimpleTestCase):
    """Test candidate pool size calculation."""

    def test_default_pool_size(self):
        request = MagicMock()
        request.query_params = MagicMock()
        request.query_params.get.side_effect = lambda k, d=None: {
            "page": "1",
            "page_size": "10",
        }.get(k, d)
        size = SearchQueryBuilder._get_candidate_pool_size(request)
        self.assertEqual(size, 30)  # page_size * 3 = 30

    def test_large_page(self):
        request = MagicMock()
        request.query_params = MagicMock()
        request.query_params.get.side_effect = lambda k, d=None: {
            "page": "10",
            "page_size": "50",
        }.get(k, d)
        size = SearchQueryBuilder._get_candidate_pool_size(request)
        # page * page_size * 2 = 1000, capped at candidate_pool_limit (250)
        self.assertLessEqual(size, 250)
