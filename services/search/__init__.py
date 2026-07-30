# Services de recherche Typesense
# Les imports sont faits de manière différée pour éviter les erreurs au démarrage

__all__ = [
    "DocumentSyncer",
    "SearchHealthView",
    "SearchService",
    "TypesenseClient",
    "TypesenseFilterBackend",
]


def __getattr__(name):
    """Import différé pour éviter les erreurs AppRegistryNotReady."""
    if name == "SearchService":
        from .service import SearchService

        return SearchService
    elif name == "TypesenseClient":
        from .client import TypesenseClient

        return TypesenseClient
    elif name == "DocumentSyncer":
        from .sync import DocumentSyncer

        return DocumentSyncer
    elif name == "TypesenseFilterBackend":
        from .backends import TypesenseFilterBackend

        return TypesenseFilterBackend
    elif name == "SearchHealthView":
        from .health import SearchHealthView

        return SearchHealthView
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
