"""
Typesense Query Builder - Refactored for intelligent search.

This module constructs Typesense search parameters with:
- Query preprocessing (normalization, stop-word removal)
- Weighted field search (query_by_weights)
- Dynamic typo tolerance based on token length
- Token dropping for multi-word queries
- Synonym support
- Relevance-based ranking (instead of arbitrary field sorting)
- Multi-strategy search with progressive fallback
"""

import logging
from typing import Any

from django.conf import settings
from django.db.models import Model

from .field_weights import get_weighted_query_fields
from .preprocessing import QueryPreprocessor, TypoAnalyzer
from .schemas import (
    filter_valid_fields,
    get_collection_for_model,
    get_valid_fields,
    map_django_fields_to_typesense,
)

logger = logging.getLogger(__name__)


class SearchQueryBuilder:
    """
    Constructs intelligent Typesense search queries.

    Key improvements over the previous version:
    1. Query preprocessing - normalizes and removes stop-words
    2. Weighted fields - course_name > module_name > course_code
    3. Dynamic typo tolerance - adapts to token length
    4. Token dropping - allows partial matches for multi-word queries
    5. Relevance ranking - no arbitrary sorting by credits/id
    6. Better prefix handling - for partial word matching
    7. Progressive fallback strategy - tries multiple search approaches
    """

    def __init__(self):
        self.preprocessor = QueryPreprocessor(
            remove_stop_words=True,
            min_token_length=2,
            preserve_academic_terms=True,
        )

    def build_multiple_strategies(
        self,
        model: type[Model],
        query: str,
        request,
        search_fields: list[str] | None = None,
        filter_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Build multiple named search strategies with priority ordering.

        Returns a list of parameter dicts, each with a '_strategy_name' key
        indicating the strategy type for aggregation and scoring.

        Strategy types (in priority order):
        - exact: exact phrase match, no typos, no prefix
        - all_tokens: all tokens present, with typo tolerance
        - any_token: any token present (OR), with token dropping
        - single_token_*: one search per individual token
        - reversed: tokens in reversed order
        - prefix: prefix matching on all tokens
        - fuzzy: aggressive typo tolerance and token dropping
        """
        # Build the base query parameters (common across all strategies)
        base_params = self.build(
            model=model,
            query=query,
            request=request,
            search_fields=search_fields,
            filter_fields=filter_fields,
        )

        normalized_query = base_params.get("q", "")
        if not normalized_query:
            return []

        tokens = normalized_query.split()
        token_count = len(tokens)
        strategies = []

        def add_strategy(name: str, overrides: dict[str, Any]) -> None:
            """Add a strategy with a copy of base params and overrides."""
            params = base_params.copy()
            params.update(overrides)
            params["_strategy_name"] = name
            strategies.append(params)

        # 1. Exact phrase (no typos, no prefix)
        add_strategy("exact", {"q": normalized_query, "num_typos": 0, "prefix": False})

        # 2. All tokens (AND) with typos
        add_strategy(
            "all_tokens", {"q": normalized_query, "num_typos": 2, "prefix": False}
        )

        # 3. Any token (OR) with token dropping
        add_strategy(
            "any_token",
            {
                "q": normalized_query,
                "num_typos": 2,
                "prefix": False,
                "split_join_tokens": "fallback",
                "drop_tokens_threshold": 1,
            },
        )

        # 4. Individual tokens (one search per meaningful token)
        # Only if token_count is manageable (max 5 tokens to avoid explosion)
        if 1 < token_count <= 5:
            for token in tokens:
                add_strategy(
                    f"single_token_{token}",
                    {
                        "q": token,
                        "num_typos": 2,
                        "prefix": False,
                    },
                )

        # 5. Reversed order (for multi-word queries)
        if token_count > 1:
            reversed_q = " ".join(reversed(tokens))
            add_strategy("reversed", {"q": reversed_q, "num_typos": 2, "prefix": False})

        # 6. Prefix (matches partial words)
        add_strategy("prefix", {"q": normalized_query, "num_typos": 0, "prefix": True})

        # 7. Fuzzy (aggressive typo tolerance + token dropping)
        add_strategy(
            "fuzzy",
            {
                "q": normalized_query,
                "num_typos": 2,
                "prefix": False,
                "split_join_tokens": "fallback",
                "drop_tokens_threshold": 1,
            },
        )

        # Cap at 10 strategies to keep latency bounded
        if len(strategies) > 10:
            strategies = strategies[:10]

        return strategies

    def build(
        self,
        model: type[Model],
        query: str,
        request,
        search_fields: list[str] | None = None,
        filter_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Construct Typesense search parameters with intelligent preprocessing.

        Args:
            model: The Django model being searched
            query: The raw search query from the user
            request: DRF Request object
            search_fields: Fields to search (Django notation, e.g., module__module_name)
            filter_fields: Fields to filter by

        Returns:
            Dict of parameters for TypesenseClient.search()
        """
        # 1. Determine search fields
        if not search_fields:
            search_fields = self._get_default_search_fields(model)

        # 2. Get collection name (needed for field validation)
        collection = self._get_collection(model)

        # 3. Convert Django field names to Typesense field names (collection-specific)
        typesense_search_fields = map_django_fields_to_typesense(
            collection, search_fields
        )

        # 4. Filter out fields that don't exist in the Typesense schema
        typesense_search_fields = filter_valid_fields(
            collection, typesense_search_fields
        )

        if not typesense_search_fields:
            logger.warning(
                "No valid search fields for collection %s, using schema defaults",
                collection,
            )
            valid_fields = self._get_valid_fields(collection)
            typesense_search_fields = [
                field
                for field in valid_fields
                if field not in ("id", "created_at", "updated_at", "is_deleted")
            ][:3]

        # 5. Preprocess the query (normalize, remove stop-words)
        normalized_query, preprocessing_meta = self.preprocessor.preprocess(query)

        # 6. Get weighted fields for relevance ranking
        query_by, query_by_weights = get_weighted_query_fields(
            model, typesense_search_fields
        )

        # 7. Analyze the query for optimal typo settings
        typo_settings = TypoAnalyzer.analyze_query(normalized_query)

        # 8. Build the base parameters
        params: dict[str, Any] = {
            "collection": collection,
            "q": normalized_query,
            "query_by": query_by,
            "query_by_weights": query_by_weights,
            "filter_by": self._build_filters(
                model,
                collection,
                request,
                filter_fields or [],
            ),
            # DRF is the only pagination layer. Typesense always returns a page-1
            # candidate pool large enough to rank the requested API page.
            "page": 1,
            "per_page": self._get_candidate_pool_size(request),
        }

        # 9. Configure typo tolerance dynamically
        self._apply_typo_settings(params, normalized_query, typo_settings, request)

        # 10. Configure token handling for better recall
        self._apply_token_settings(params, normalized_query, typo_settings)

        # 11. Configure ranking/relevance
        self._apply_ranking(params, request)

        # 12. Configure prefix search
        self._apply_prefix_settings(params, request)

        # 13. Enable synonyms if configured
        if settings.TYPESENSE_CONFIG.get("synonyms_enabled", False):
            params["enable_synonyms"] = True

        # 14. Improve ranking for exact and full-token matches
        params["prioritize_exact_match"] = True
        params["text_match_type"] = "word_count_superscore"

        # 15. Add autocomplete-specific settings if requested
        if request.query_params.get("autocomplete", "false").lower() == "true":
            self._apply_autocomplete_settings(params)

        # Log the generated query for debugging
        logger.debug(
            f"Typesense query built: q='{normalized_query}' (original='{query}'), "
            f"query_by={query_by}, weights={query_by_weights}, "
            f"num_typos={params.get('num_typos')}, "
            f"drop_tokens_threshold={params.get('drop_tokens_threshold')}, "
            f"removed_tokens={preprocessing_meta.get('removed_tokens', [])}"
        )

        return params

    def _apply_typo_settings(
        self,
        params: dict[str, Any],
        query: str,
        typo_settings: dict,
        request,
    ) -> None:
        """
        Apply dynamic typo tolerance settings.

        Typo tolerance is configured based on:
        - Token length (shorter tokens allow fewer typos)
        - Number of tokens (more tokens = more lenient)
        - User request (autocomplete uses fewer typos)
        """
        if not query:
            return

        is_autocomplete = (
            request.query_params.get("autocomplete", "false").lower() == "true"
        )

        if is_autocomplete:
            # For autocomplete, be more conservative to avoid noise
            params["num_typos"] = 1
            params["typo_tokens_threshold"] = 0
        else:
            # Dynamic typo tolerance based on token analysis
            params["num_typos"] = typo_settings["num_typos"]
            # typo_tokens_threshold=0 means typo tolerance always active
            params["typo_tokens_threshold"] = 0

        # min_len_1typo and min_len_2typo: configure when typos kick in
        # min_len_1typo: minimum length for 1 typo (default 4)
        # min_len_2typo: minimum length for 2 typos (default 7)
        params["min_len_1typo"] = 4
        params["min_len_2typo"] = 7

    def _apply_token_settings(
        self,
        params: dict[str, Any],
        query: str,
        typo_settings: dict,
    ) -> None:
        """
        Configure token handling for better recall.

        - drop_tokens_threshold: when results < threshold, drop tokens and retry
          This helps queries like "ET INSTRUMENTATION" where ET is noise
        - split_join_tokens: handle cases where tokens should be joined or split
        """
        if not query:
            return

        token_count = typo_settings.get("token_count", 0)

        if token_count > 1:
            # Multi-word query: enable token dropping
            # When fewer results than threshold found, Typesense drops tokens
            # and retries. This is crucial for queries like "ET INSTRUMENTATIiO"
            # where ET doesn't match anything.
            #
            # Threshold = number of results below which tokens are dropped
            # Setting to 1 means: if 0 results found, drop a token and retry
            params["drop_tokens_threshold"] = 1

            # Enable split/join tokens for compound words
            # "reseau informatique" might match "réseaux informatiques"
            params["split_join_tokens"] = "fallback"

    def _apply_ranking(self, params: dict[str, Any], request) -> None:
        """Apply explicit, schema-valid ordering or keep pure relevance order."""
        ordering = request.query_params.get("ordering", "").strip()
        if not ordering:
            # Omitting sort_by lets Typesense rank by text relevance.
            return

        collection = params["collection"]
        valid_fields = set(get_valid_fields(collection))
        field_mapping = []

        for requested_field in ordering.split(","):
            requested_field = requested_field.strip()
            if not requested_field:
                continue

            descending = requested_field.startswith("-")
            django_field = requested_field[1:] if descending else requested_field
            mapped_fields = map_django_fields_to_typesense(collection, [django_field])
            if not mapped_fields or mapped_fields[0] not in valid_fields:
                logger.warning(
                    "Ignoring invalid Typesense sort field '%s' for collection %s",
                    django_field,
                    collection,
                )
                continue

            field_mapping.append(
                f"{mapped_fields[0]}:{'desc' if descending else 'asc'}"
            )

        if field_mapping:
            params["sort_by"] = ",".join(field_mapping)

    def _default_relevance_sort(self) -> str:
        """
        Return the default relevance-based sort.

        Instead of sorting by credits or created_at, we sort by:
        1. Text relevance score (Typesense default)
        2. created_at desc as tiebreaker for freshness

        Note: Typesense always sorts by text_score first when sort_by is set.
        To get pure relevance, we can leave sort_by empty, but then there's
        no tiebreaker. Using created_at:desc as a tiebreaker is a good compromise.
        """
        # text_score is implicit, then created_at as tiebreaker
        return "created_at:desc"

    def _apply_prefix_settings(self, params: dict[str, Any], request) -> None:
        """
        Configure prefix search.

        Prefix search allows matching partial words:
        "algo" matches "algorithmique"
        "reseau" matches "reseaux"
        "instrumenta" matches "instrumentation"

        We use "fallback" mode which tries exact match first, then prefix.
        """
        is_autocomplete = (
            request.query_params.get("autocomplete", "false").lower() == "true"
        )

        if is_autocomplete:
            # For autocomplete, prefix must be enabled
            params["prefix"] = True
        else:
            # For regular search, use prefix as fallback
            # This means: try exact match first, if no results, try prefix
            # "instrumenta" will match "instrumentation" even if not exact
            params["prefix"] = "fallback"

    def _apply_autocomplete_settings(self, params: dict[str, Any]) -> None:
        """Configure settings optimized for autocomplete/suggestions."""
        params["prefix"] = True
        params["num_typos"] = 1
        # Limit results for autocomplete
        params["per_page"] = min(params.get("per_page", 10), 10)

    # Mapping des champs Django vers champs Typesense
    # Utilisé quand le nom du champ ne correspond pas (ex: code -> module_code)
    FIELD_MAPPING = {
        # Modules
        "code": "module_code",
        "class_name": "class_name",  # Pas dans le schéma modules, sera filtré
        # Courses
        "module_name": "module_name",
        # Teachers
        "full_name": "full_name",
        # Classes
        "academic_year": "academic_year",
        # Departments
        "department_code": "department_code",
        # Faculties
        "faculty_abreviation": "faculty_abreviation",
        # Universities
        "university_abrev": "university_abrev",
    }

    def _django_to_typesense_field(self, field_name: str) -> str:
        """
        Convert Django field name to Typesense field name.

        Django uses __ for relations: module__module_name
        Typesense uses flat fields: module_name

        This is important because the indexed documents have flat field names.
        """
        if "__" in field_name:
            parts = field_name.split("__")
            # Prendre la dernière partie et vérifier le mapping
            last_part = parts[-1]
            return self.FIELD_MAPPING.get(last_part, last_part)
        # Vérifier le mapping direct
        return self.FIELD_MAPPING.get(field_name, field_name)

    def _build_filters(
        self,
        model: type[Model],
        collection: str,
        request,
        filter_fields: list[str],
    ) -> str:
        """Build a schema-valid Typesense filter expression."""
        filters = []
        valid_fields = set(get_valid_fields(collection))

        if hasattr(model, "is_deleted") and "is_deleted" in valid_fields:
            filters.append("is_deleted:=false")

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            for field in ("faculty_id", "university_id"):
                value = getattr(user, field, None)
                if value and field in valid_fields:
                    filters.append(f"{field}:={self._escape_filter_value(value)}")

        for django_field in filter_fields:
            value = request.query_params.get(django_field)
            if value in (None, ""):
                continue

            mapped_fields = map_django_fields_to_typesense(
                collection,
                [django_field],
            )
            if not mapped_fields or mapped_fields[0] not in valid_fields:
                logger.debug(
                    "Skipping unsupported Typesense filter '%s' for collection %s",
                    django_field,
                    collection,
                )
                continue

            filters.append(f"{mapped_fields[0]}:={self._escape_filter_value(value)}")

        extra_filters = getattr(request, "_typesense_extra_filters", {})
        for key, value in extra_filters.items():
            mapped_fields = map_django_fields_to_typesense(collection, [key])
            if (
                value is None
                or not mapped_fields
                or mapped_fields[0] not in valid_fields
            ):
                continue

            field = mapped_fields[0]
            if isinstance(value, (list, tuple, set)):
                values = ",".join(self._escape_filter_value(item) for item in value)
                filters.append(f"{field}:=[{values}]")
            else:
                filters.append(f"{field}:={self._escape_filter_value(value)}")

        return " && ".join(filters)

    @staticmethod
    def _escape_filter_value(value: Any) -> str:
        """Quote a Typesense filter value so user input cannot alter syntax."""
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)):
            return str(value)

        escaped = str(value).replace("`", "\\`")
        return f"`{escaped}`"

    @staticmethod
    def _get_candidate_pool_size(request) -> int:
        """Return enough page-1 candidates for DRF to paginate after ranking."""
        try:
            page = max(1, int(request.query_params.get("page", 1)))
        except (TypeError, ValueError):
            page = 1

        try:
            page_size = max(1, int(request.query_params.get("page_size", 10)))
        except (TypeError, ValueError):
            page_size = 10

        page_size = min(page_size, 100)
        candidate_limit = settings.TYPESENSE_CONFIG.get(
            "candidate_pool_limit",
            250,
        )
        requested_window = page * page_size
        return min(
            max(requested_window * 2, page_size * 3),
            candidate_limit,
        )

    def _get_collection(self, model: type[Model]) -> str:
        """Return the Typesense collection name for a model."""
        return get_collection_for_model(model)

    def _get_valid_fields(self, collection: str) -> list[str]:
        """
        Get valid field names for a Typesense collection from the authoritative schema registry.
        """
        return get_valid_fields(collection)

    def _get_default_search_fields(self, model: type[Model]) -> list[str]:
        """Return default search fields for a model based on available fields."""
        defaults = []
        fields = [f.name for f in model._meta.fields]

        # Name fields
        for name_field in [
            "name",
            "full_name",
            "course_name",
            "university_name",
            "faculty_name",
            "department_name",
        ]:
            if name_field in fields:
                defaults.append(name_field)
                break

        # Code/abbreviation fields
        for code_field in ["code", "course_code", "abreviation", "university_abrev"]:
            if code_field in fields:
                defaults.append(code_field)

        # Description fields
        for desc_field in ["description", "detail"]:
            if desc_field in fields:
                defaults.append(desc_field)

        return defaults if defaults else ["id"]
