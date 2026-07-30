import logging
import time
from collections import defaultdict
from typing import Any

import typesense
from django.conf import settings
from django.db.models import Case, IntegerField, Q, QuerySet, When
from rest_framework.request import Request

from .client import TypesenseClient
from .exceptions import SearchServiceError
from .normalizer import Normalizer
from .query_builder import SearchQueryBuilder
from .sync import DocumentSyncer

logger = logging.getLogger(__name__)


class SearchService:
    """Service principal de recherche orchestrant Typesense et le fallback ORM."""

    def __init__(self):
        self.client = TypesenseClient()
        self.builder = SearchQueryBuilder()
        self.normalizer = Normalizer()

    def apply_search(
        self,
        model: type,
        queryset: QuerySet,
        request: Request,
        search_fields: list[str] | None = None,
        filter_fields: list[str] | None = None,
    ) -> tuple[QuerySet, int, int]:
        """Applique la recherche sur le queryset donné.

        Args:
            model: Le modèle Django concerné
            queryset: Le queryset de base (avec permissions déjà appliquées)
            request: L'objet DRF Request
            search_fields: Champs sur lesquels rechercher
            filter_fields: Champs sur lesquels filtrer

        Returns:
            Tuple (queryset filtré et trié, nombre total de résultats, temps de recherche en ms)
        """
        # Si Typesense n'est pas activé, fallback immédiat
        if not self.client.enabled:
            logger.info("Typesense disabled, using ORM fallback")
            return self._orm_fallback(queryset, request, search_fields)

        # Extraire la requête de recherche
        query = request.query_params.get("search", "").strip()

        # Ordinary filters are handled by DjangoFilterBackend. Typesense is only
        # responsible for non-empty full-text queries.
        if not query:
            return queryset, queryset.count(), 0

        try:
            start_time = time.time()

            # 1. Construire les stratégies de recherche
            strategies = self.builder.build_multiple_strategies(
                model=model,
                query=query,
                request=request,
                search_fields=search_fields,
                filter_fields=filter_fields,
            )

            if not strategies:
                return queryset.none(), 0, 0

            # Each strategy keeps its own typo, prefix and token-dropping
            # parameters. Passing only ``q`` here silently made every strategy
            # inherit the first strategy's exact-search settings.
            collection = strategies[0]["collection"]
            search_requests = []
            for strategy in strategies:
                search_params = {
                    key: value
                    for key, value in strategy.items()
                    if key not in ("collection", "_strategy_name")
                    and value not in (None, "")
                }
                search_requests.append(search_params)

            try:
                multi_results = self.client.multi_search(
                    collection,
                    search_requests,
                    common_params={},
                )
            except typesense.exceptions.TypesenseClientError as e:
                logger.warning("Multi-search failed, falling back to ORM: %s", e)
                if settings.TYPESENSE_CONFIG.get("fallback_enabled", True):
                    return self._orm_fallback(queryset, request, search_fields)
                raise SearchServiceError("Search engine unavailable") from e

            aggregated, strategy_counts = self._aggregate_and_score(
                multi_results,
                strategies,
                query,
            )
            sorted_ids = [
                doc_id
                for doc_id, _ in sorted(
                    aggregated.items(),
                    key=lambda item: (
                        item[1]["score"],
                        -item[1]["best_position"],
                    ),
                    reverse=True,
                )
            ]

            # The incoming queryset is already permission-scoped. Count and
            # order only IDs visible through that queryset, not raw Typesense
            # candidates that the current user cannot access.
            if sorted_ids:
                authorized_values = queryset.filter(id__in=sorted_ids).values_list(
                    "id", flat=True
                )
                authorized_ids = {str(value) for value in authorized_values}
                sorted_ids = [
                    doc_id for doc_id in sorted_ids if str(doc_id) in authorized_ids
                ]
                found = len(sorted_ids)
                queryset = self._preserve_order(
                    queryset.filter(id__in=sorted_ids),
                    sorted_ids,
                )
            else:
                queryset = queryset.none()
                found = 0

            total_time_ms = (time.time() - start_time) * 1000
            logger.info(
                "Typesense multi-search completed: query=%r, normalized=%r, "
                "found=%d, candidate_count=%d, total_time=%.1fms, "
                "collection=%s, strategies_tried=%d, strategy_counts=%s, "
                "top_scores=%s",
                query,
                self.builder.preprocessor.preprocess(query)[0],
                found,
                len(aggregated),
                total_time_ms,
                collection,
                len(strategies),
                strategy_counts,
                [round(aggregated[doc_id]["score"], 2) for doc_id in sorted_ids[:5]],
            )

            return queryset, found, int(total_time_ms)

        except Exception as e:
            logger.exception("Unexpected error during search")
            if settings.TYPESENSE_CONFIG.get("fallback_enabled", True):
                return self._orm_fallback(queryset, request, search_fields)
            else:
                raise SearchServiceError("Search failed") from e

    def _preserve_order(self, queryset: QuerySet, ids: list[str]) -> QuerySet:
        """Annote le queryset avec l'ordre de pertinence de Typesense.

        Utilise Case/When pour conserver l'ordre des IDs retournés par Typesense.
        Gère les UUIDs (format string) correctement.
        """
        # Préparer les conditions When
        conditions = []
        for pos, id_str in enumerate(ids):
            try:
                # Essayer de convertir en UUID si c'est le format attendu
                # Le filtre id__in utilise déjà les IDs string, donc on garde le format string
                conditions.append(When(id=id_str, then=pos))
            except (ValueError, TypeError):
                continue

        if not conditions:
            return queryset

        ordering = Case(
            *conditions,
            default=len(ids),
            output_field=IntegerField(),
        )
        return queryset.annotate(_typesense_order=ordering).order_by("_typesense_order")

    def _orm_fallback(
        self,
        queryset: QuerySet,
        request: Request,
        search_fields: list[str] | None = None,
    ) -> tuple[QuerySet, int, int]:
        """Fallback vers l'ORM avec des recherches insensibles à la casse (icontains)."""
        query = request.query_params.get("search", "").strip()

        if query and search_fields:
            q_objects = Q()
            for field in search_fields:
                # Support pour les champs relationnels (ex: module__module_name)
                q_objects |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(q_objects)

        # Compter les résultats (le count est déjà fait après filtrage)
        count = queryset.count()
        return queryset, count, 0

    def _aggregate_and_score(
        self,
        multi_results: list[dict[str, Any]],
        strategies: list[dict[str, Any]],
        original_query: str,
    ) -> tuple[dict[str, Any], dict[str, int]]:
        """Deduplicate strategy hits and calculate deterministic relevance."""
        aggregated: dict[str, dict[str, Any]] = {}
        strategy_counts = defaultdict(int)
        normalized_query, _ = self.builder.preprocessor.preprocess(original_query)
        tokens = normalized_query.split()
        query_by = strategies[0].get("query_by", "") if strategies else ""
        searchable_fields = [field for field in query_by.split(",") if field]

        for strategy_index, result in enumerate(multi_results):
            if strategy_index >= len(strategies):
                break

            strategy_name = strategies[strategy_index].get(
                "_strategy_name",
                "unknown",
            )
            hits = result.get("hits", [])
            strategy_counts[strategy_name] += len(hits)

            for position, hit in enumerate(hits):
                document = hit.get("document", {})
                document_id = document.get("id")
                if document_id in (None, ""):
                    continue

                document_id = str(document_id)
                text_score = self._extract_text_match_score(hit)
                if document_id not in aggregated:
                    aggregated[document_id] = {
                        "document": document,
                        "strategies": [],
                        "scores": {},
                        "text_score": 0.0,
                        "best_position": position,
                        "rank_score": 0.0,
                        "score": 0.0,
                    }

                data = aggregated[document_id]
                if strategy_name not in data["strategies"]:
                    data["strategies"].append(strategy_name)
                data["scores"][strategy_name] = text_score
                data["text_score"] = max(data["text_score"], text_score)
                data["best_position"] = min(data["best_position"], position)
                data["rank_score"] = max(
                    data["rank_score"],
                    1.0 / (position + 1),
                )

        maximum_text_score = max(
            (data["text_score"] for data in aggregated.values()),
            default=0.0,
        )
        for data in aggregated.values():
            document_text = " ".join(
                str(data["document"].get(field, ""))
                for field in searchable_fields
                if data["document"].get(field) not in (None, "")
            )
            normalized_document, _ = self.builder.preprocessor.preprocess(document_text)
            data["score"] = self._compute_final_score(
                data=data,
                normalized_query=normalized_query,
                query_tokens=tokens,
                normalized_document=normalized_document,
                maximum_text_score=maximum_text_score,
            )

        return aggregated, dict(strategy_counts)

    @staticmethod
    def _extract_text_match_score(hit: dict[str, Any]) -> float:
        """Read relevance from current and older Typesense hit formats."""
        candidates = [
            hit.get("text_match"),
            hit.get("text_match_info", {}).get("score"),
        ]
        candidates.extend(match.get("score") for match in hit.get("matches", []))
        numeric_scores = [
            float(value) for value in candidates if isinstance(value, (int, float))
        ]
        return max(numeric_scores, default=0.0)

    def _compute_final_score(
        self,
        data: dict[str, Any],
        normalized_query: str,
        query_tokens: list[str],
        normalized_document: str,
        maximum_text_score: float,
    ) -> float:
        """Score exact, ordered, prefix, typo and partial matches in tiers."""
        document_tokens = normalized_document.split()
        exact_phrase_match = bool(
            normalized_query and normalized_query in normalized_document
        )
        order_match = self._tokens_appear_in_order(
            query_tokens,
            document_tokens,
        )

        exact_matches = [
            any(query_token == document_token for document_token in document_tokens)
            for query_token in query_tokens
        ]
        prefix_matches = [
            any(
                document_token.startswith(query_token)
                or query_token.startswith(document_token)
                for document_token in document_tokens
            )
            for query_token in query_tokens
        ]
        fuzzy_matches = [
            any(
                self._within_typo_distance(query_token, document_token)
                for document_token in document_tokens
            )
            for query_token in query_tokens
        ]

        token_weights = [max(1.0, min(len(token) / 4.0, 2.5)) for token in query_tokens]
        total_weight = sum(token_weights) or 1.0
        exact_coverage = (
            sum(
                weight
                for weight, matched in zip(token_weights, exact_matches)
                if matched
            )
            / total_weight
        )
        fuzzy_coverage = (
            sum(
                weight
                for weight, matched in zip(token_weights, fuzzy_matches)
                if matched
            )
            / total_weight
        )

        all_exact = bool(query_tokens) and all(exact_matches)
        all_prefix = bool(query_tokens) and all(prefix_matches)
        all_fuzzy = bool(query_tokens) and all(fuzzy_matches)
        matched_token_count = sum(fuzzy_matches)

        if exact_phrase_match:
            tier_bonus = 100.0
        elif all_exact and order_match:
            tier_bonus = 75.0
        elif all_exact:
            tier_bonus = 65.0
        elif all_prefix:
            tier_bonus = 55.0
        elif all_fuzzy:
            tier_bonus = 45.0
        elif matched_token_count:
            tier_bonus = 20.0 + (20.0 * fuzzy_coverage)
        else:
            tier_bonus = 5.0

        normalized_text_score = (
            data.get("text_score", 0.0) / maximum_text_score
            if maximum_text_score
            else 0.0
        )
        typesense_contribution = min(normalized_text_score * 5.0, 5.0)
        rank_contribution = data.get("rank_score", 0.0) * 3.0
        coverage_contribution = max(exact_coverage, fuzzy_coverage) * 10.0
        partial_penalty = 5.0 if len(query_tokens) > 3 and fuzzy_coverage < 0.5 else 0.0

        data["token_coverage"] = fuzzy_coverage
        data["exact_phrase_match"] = exact_phrase_match
        data["order_match"] = order_match
        return max(
            0.0,
            tier_bonus
            + coverage_contribution
            + typesense_contribution
            + rank_contribution
            - partial_penalty,
        )

    @staticmethod
    def _tokens_appear_in_order(
        query_tokens: list[str],
        document_tokens: list[str],
    ) -> bool:
        if not query_tokens:
            return False

        position = 0
        for document_token in document_tokens:
            if document_token == query_tokens[position]:
                position += 1
                if position == len(query_tokens):
                    return True
        return False

    @classmethod
    def _within_typo_distance(cls, query_token: str, document_token: str) -> bool:
        if query_token == document_token:
            return True
        if not query_token or not document_token:
            return False

        maximum_distance = 1 if min(len(query_token), len(document_token)) <= 4 else 2
        if abs(len(query_token) - len(document_token)) > maximum_distance:
            return False
        return (
            cls._levenshtein_distance(
                query_token,
                document_token,
                maximum_distance,
            )
            <= maximum_distance
        )

    @staticmethod
    def _levenshtein_distance(
        left: str,
        right: str,
        maximum_distance: int,
    ) -> int:
        """Calculate edit distance and stop once the threshold is exceeded."""
        if len(left) > len(right):
            left, right = right, left

        previous = list(range(len(left) + 1))
        for right_index, right_character in enumerate(right, start=1):
            current = [right_index]
            row_minimum = current[0]
            for left_index, left_character in enumerate(left, start=1):
                current.append(
                    min(
                        current[left_index - 1] + 1,
                        previous[left_index] + 1,
                        previous[left_index - 1] + (left_character != right_character),
                    )
                )
                row_minimum = min(row_minimum, current[-1])
            if row_minimum > maximum_distance:
                return maximum_distance + 1
            previous = current

        return previous[-1]

    def search_raw(
        self,
        collection: str,
        query: str,
        **params,
    ) -> dict[str, Any]:
        """Recherche brute sans transformation Django."""
        return self.client.search(collection, query, **params)

    def index_instance(self, instance) -> None:
        """Indexe une instance Django dans Typesense.

        Délègue au :class:`DocumentSyncer` afin que toutes les routes
        d'indexation (signaux, commande d'indexation, ce service) empruntent
        un seul chemin produisant des documents plats conformes au schéma.
        """
        self._syncer.index_instance(instance)

    def delete_instance(self, instance) -> None:
        """Supprime une instance Django de Typesense."""
        self._syncer.delete_instance(instance)

    @property
    def _syncer(self) -> DocumentSyncer:
        """DocumentSyncer partagé (lazy pour rester compatible avec les tests)."""
        if not hasattr(self, "_syncer_instance"):
            self._syncer_instance = DocumentSyncer()
        return self._syncer_instance
