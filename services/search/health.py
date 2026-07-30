import logging
from typing import Any

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .client import TypesenseClient

logger = logging.getLogger(__name__)


class SearchHealthView(APIView):
    """
    Endpoint de santé pour le service de recherche Typesense.

    GET /api/search/health/
    Retourne l'état du cluster Typesense.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Vérifie la santé de Typesense et retourne un statut."""
        client = TypesenseClient()

        # Vérifier si Typesense est configuré
        if not client.api_key:
            return Response(
                {
                    "status": "unconfigured",
                    "message": "Typesense API key not configured",
                    "enabled": client.enabled,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Vérifier si Typesense est désactivé via feature flag
        if not client.enabled:
            return Response(
                {
                    "status": "disabled",
                    "message": "Typesense is disabled by configuration",
                    "enabled": client.enabled,
                    "force_fallback": settings.TYPESENSE_CONFIG.get(
                        "force_fallback", False
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Effectuer le health check
        health = client.health_check()

        if health.get("status") == "ok":
            return Response(
                {
                    "status": "ok",
                    "message": "Typesense is healthy",
                    "details": health.get("details", {}),
                    "host": client.host,
                    "port": client.port,
                    "enabled": client.enabled,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status": "unhealthy",
                    "message": "Typesense is not responding",
                    "details": health.get("details", "Unknown error"),
                    "host": client.host,
                    "port": client.port,
                    "enabled": client.enabled,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class SearchCollectionsView(APIView):
    """
    Endpoint pour lister les collections Typesense.

    GET /api/search/collections/
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Liste toutes les collections Typesense."""
        client = TypesenseClient()

        if not client.enabled or not client.api_key:
            return Response(
                {"status": "error", "message": "Typesense not available"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            collections = client.list_collections()
            return Response(
                {
                    "status": "ok",
                    "count": len(collections),
                    "collections": collections,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Fonction utilitaire pour le monitoring
def get_search_stats() -> dict[str, Any]:
    """Retourne les statistiques du service de recherche."""
    client = TypesenseClient()

    stats = {
        "enabled": client.enabled,
        "host": client.host,
        "port": client.port,
        "configured": bool(client.api_key),
    }

    if client.enabled and client.api_key:
        try:
            health = client.health_check()
            stats["status"] = health.get("status", "unknown")
            stats["details"] = health.get("details", {})
        except Exception as e:
            stats["status"] = "error"
            stats["details"] = str(e)

    return stats
