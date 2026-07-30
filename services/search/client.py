import logging
import time
from typing import Any

import typesense
from django.conf import settings

logger = logging.getLogger(__name__)


class TypesenseClient:
    """Client pour l'interaction avec Typesense avec retry et gestion d'erreurs."""

    def __init__(self):
        config = settings.TYPESENSE_CONFIG
        self.host = config["host"]
        self.port = config["port"]
        self.protocol = config["protocol"]
        self.api_key = config["api_key"]
        self.timeout = config.get("timeout", 10)
        self.max_retries = config.get("max_retries", 3)
        self.enabled = (
            config.get("enabled", True)
            and not config.get("force_fallback", False)
            and bool(self.api_key)
        )

        if self.enabled:
            self._client = typesense.Client(
                {
                    "nodes": [
                        {
                            "host": self.host,
                            "port": self.port,
                            "protocol": self.protocol,
                        }
                    ],
                    "api_key": self.api_key,
                    "connection_timeout_seconds": self.timeout,
                }
            )
        else:
            self._client = None
            if not self.api_key:
                logger.warning("Typesense API key not configured. Client disabled.")

    def _ensure_client(self):
        """Vérifie que le client est disponible."""
        if not self.enabled:
            raise typesense.exceptions.TypesenseClientError("Typesense is disabled")
        if self._client is None:
            raise typesense.exceptions.TypesenseClientError(
                "Typesense client not initialized"
            )

    def _retry_call(self, func, *args, **kwargs):
        """Exécute une fonction avec retry exponentiel."""
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                self._ensure_client()
                return func(*args, **kwargs)
            except typesense.exceptions.TypesenseClientError as e:
                last_exception = e
                if attempt + 1 >= self.max_retries:
                    break
                wait = 2**attempt  # 1s, 2s, 4s
                logger.warning(
                    "Typesense call failed (attempt %d/%d): %s. Retrying in %ds",
                    attempt + 1,
                    self.max_retries,
                    e,
                    wait,
                )
                time.sleep(wait)
            except Exception as e:
                logger.error(f"Unexpected error in Typesense call: {e}")
                raise
        raise last_exception or typesense.exceptions.TypesenseClientError(
            "Max retries exceeded"
        )

    def search(self, collection: str, q: str, **params) -> dict[str, Any]:
        """Effectue une recherche dans une collection."""
        if not q or not q.strip():
            # Si la requête est vide, Typesense ne fonctionne pas, on renvoie un résultat vide
            return {"hits": [], "found": 0, "search_time_ms": 0}

        def _search():
            return self._client.collections[collection].documents.search(
                {"q": q, **params}
            )

        try:
            return self._retry_call(_search)
        except typesense.exceptions.TypesenseClientError as e:
            logger.error(f"Search failed after retries: {e}")
            raise

    def multi_search(
        self,
        collection: str,
        searches: list[dict[str, Any]],
        common_params: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Effectue plusieurs recherches dans une seule requête Typesense."""
        if not searches:
            return []

        base_params = common_params.copy()
        base_params.pop("collection", None)
        base_params.pop("_strategy_name", None)

        search_requests = []
        for search in searches:
            params = base_params.copy()
            params.update(search)
            params.pop("_strategy_name", None)
            params["collection"] = collection
            search_requests.append(params)

        def _multi_search():
            return self._client.multi_search.perform({"searches": search_requests})

        try:
            result = self._retry_call(_multi_search)
            return result.get("results", [])
        except AttributeError:
            logger.warning(
                "Typesense multi_search is unavailable; using sequential searches"
            )
            results = []
            for params in search_requests:
                sequential_params = params.copy()
                sequential_params.pop("collection", None)
                q = sequential_params.pop("q", "")
                results.append(self.search(collection, q, **sequential_params))
            return results
        except typesense.exceptions.TypesenseClientError as e:
            logger.error(f"Multi-search failed after retries: {e}")
            raise

    def index_document(self, collection: str, document: dict[str, Any]) -> None:
        """Indexe ou met à jour un document (upsert)."""
        if not self.enabled:
            logger.info("Typesense disabled, skipping index_document")
            return

        def _index():
            return self._client.collections[collection].documents.upsert(document)

        try:
            self._retry_call(_index)
        except typesense.exceptions.TypesenseClientError as e:
            logger.error(f"Failed to index document in {collection}: {e}")
            raise

    def delete_document(self, collection: str, doc_id: str) -> None:
        """Supprime un document par son ID."""
        if not self.enabled:
            logger.info("Typesense disabled, skipping delete_document")
            return

        def _delete():
            return self._client.collections[collection].documents[doc_id].delete()

        try:
            self._retry_call(_delete)
        except typesense.exceptions.ObjectNotFound:
            logger.warning(
                f"Document {doc_id} not found in {collection}, skipping delete."
            )
        except typesense.exceptions.TypesenseClientError as e:
            logger.error(f"Failed to delete document {doc_id} from {collection}: {e}")
            raise

    def health_check(self) -> dict[str, Any]:
        """Vérifie la santé du cluster Typesense."""
        try:
            self._ensure_client()
            # Utiliser le client typesense directement
            # Le client Python typesense n'a pas de méthode health, on utilise une requête simple
            result = self._client.collections.retrieve()
            return {"status": "ok", "details": {"collections_count": len(result)}}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "details": str(e)}

    def create_collection(self, name: str, schema: dict[str, Any]) -> bool:
        """Crée une collection avec le schéma donné."""
        if not self.enabled:
            return False

        try:
            self._client.collections.create({"name": name, **schema})
            logger.info(f"Collection '{name}' created successfully")
            return True
        except typesense.exceptions.ObjectAlreadyExists:
            logger.info(f"Collection '{name}' already exists")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            return False

    def delete_collection(self, name: str) -> bool:
        """Supprime une collection."""
        if not self.enabled:
            return False

        try:
            self._client.collections[name].delete()
            logger.info(f"Collection '{name}' deleted")
            return True
        except typesense.exceptions.ObjectNotFound:
            logger.warning(f"Collection '{name}' not found")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{name}': {e}")
            return False

    def list_collections(self) -> list:
        """Liste toutes les collections."""
        if not self.enabled:
            return []
        try:
            return self._client.collections.retrieve()
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
