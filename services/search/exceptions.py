class SearchServiceError(Exception):
    """Exception de base pour le service de recherche."""


class TypesenseConnectionError(SearchServiceError):
    """Exception levée quand la connexion à Typesense échoue."""


class TypesenseIndexError(SearchServiceError):
    """Exception levée quand l'indexation échoue."""


class TypesenseSearchError(SearchServiceError):
    """Exception levée quand une recherche échoue."""


class TypesenseConfigurationError(SearchServiceError):
    """Exception levée quand la configuration de Typesense est invalide."""


class CollectionNotFoundError(SearchServiceError):
    """Exception levée quand une collection n'existe pas."""


class DocumentNotFoundError(SearchServiceError):
    """Exception levée quand un document n'existe pas."""
