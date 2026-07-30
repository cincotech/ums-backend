from typing import Any


class Normalizer:
    """Extrait et normalise les résultats de Typesense."""

    def extract_ids(self, results: dict[str, Any]) -> list[str]:
        """Extrait les IDs des documents dans l'ordre retourné par Typesense."""
        hits = results.get("hits", [])
        if not hits:
            return []
        return [hit["document"]["id"] for hit in hits if "document" in hit]

    def extract_hits(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        """Extrait les hits complets avec leurs documents."""
        return results.get("hits", [])

    def get_found_count(self, results: dict[str, Any]) -> int:
        """Retourne le nombre total de résultats trouvés."""
        return results.get("found", 0)

    def get_search_time_ms(self, results: dict[str, Any]) -> int:
        """Retourne le temps de recherche en millisecondes."""
        return results.get("search_time_ms", 0)

    def get_out_of(self, results: dict[str, Any]) -> int:
        """Retourne le nombre total de documents dans la collection."""
        return results.get("out_of", 0)

    def get_page(self, results: dict[str, Any]) -> int:
        """Retourne la page actuelle."""
        return results.get("page", 1)

    def get_per_page(self, results: dict[str, Any]) -> int:
        """Retourne le nombre d'éléments par page."""
        return results.get("per_page", 20)

    def has_more_results(self, results: dict[str, Any]) -> bool:
        """Vérifie s'il y a plus de résultats après la page actuelle."""
        page = self.get_page(results)
        per_page = self.get_per_page(results)
        found = self.get_found_count(results)
        return (page * per_page) < found

    def extract_documents(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        """Extrait uniquement les documents des hits."""
        hits = results.get("hits", [])
        return [hit["document"] for hit in hits if "document" in hit]

    def get_facet_counts(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        """Extrait les comptages par facette."""
        return results.get("facet_counts", [])
