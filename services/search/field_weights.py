"""
Field Weight Configuration for Typesense Search.

Field weights control search relevance by prioritizing certain fields over others.
A higher weight means the field is more important for ranking.

Typesense uses query_by_weights parameter: query_by=field1,field2&query_by_weights=2,1
"""

from django.db.models import Model

# Field weights configuration by model/collection
# Higher weight = more important for search relevance
FIELD_WEIGHTS: dict[str, dict[str, int]] = {
    "courses": {
        "course_name": 10,  # Most important - main course title
        "module_name": 5,  # Secondary - module context
        "course_code": 3,  # Lower - exact code match
        "department_name": 2,  # Context
        "faculty_name": 1,  # Less important for course search
    },
    "modules": {
        "module_name": 10,
        "module_code": 5,
        "department_name": 3,
        "faculty_name": 2,
    },
    "teachers": {
        "full_name": 10,
        "email": 5,
        "phone": 3,
        "teacher_grade": 4,
        "speciality": 2,
    },
    "classes": {
        "class_name": 10,
        "department_name": 2,
        "faculty_name": 1,
    },
    "departments": {
        "department_name": 10,
        "department_code": 5,
        "faculty_name": 3,
    },
    "faculties": {
        "faculty_name": 10,
        "faculty_abreviation": 8,
        "university_name": 2,
    },
    "universities": {
        "university_name": 10,
        "university_abrev": 8,
        "country": 3,
    },
}

# Default weights for models not explicitly configured
DEFAULT_WEIGHTS: dict[str, int] = {
    "name": 10,
    "title": 10,
    "full_name": 10,
    "code": 5,
    "description": 3,
}


def get_field_weights(collection_name: str) -> dict[str, int]:
    """
    Get field weights for a specific collection.

    Args:
        collection_name: Name of the Typesense collection

    Returns:
        Dict mapping field names to their weights
    """
    return FIELD_WEIGHTS.get(collection_name, DEFAULT_WEIGHTS)


def get_weighted_query_fields(
    model: Model, search_fields: list[str]
) -> tuple[str, str]:
    """
    Build the query_by and query_by_weights parameters for Typesense.

    Args:
        model: Django model being searched
        search_fields: List of field names to search

    Returns:
        Tuple of (query_by string, query_by_weights string)
    """
    from django.conf import settings

    # Get collection name
    model_name = model.__name__
    collection = settings.SEARCH_COLLECTION_MAP.get(model_name, model_name.lower())

    # Get weights for this collection
    weights = get_field_weights(collection)

    # Build weighted field list
    weighted_fields = []
    for field in search_fields:
        weight = weights.get(field, 1)  # Default weight of 1
        weighted_fields.append((field, weight))

    # Sort by weight (highest first) for better relevance
    weighted_fields.sort(key=lambda x: x[1], reverse=True)

    # Build the query_by and query_by_weights strings
    query_by = ",".join(f[0] for f in weighted_fields)
    query_by_weights = ",".join(str(f[1]) for f in weighted_fields)

    return query_by, query_by_weights


def get_search_priority_score(collection_name: str, field_name: str) -> int:
    """
    Get the search priority score for a specific field.

    Higher scores indicate fields that should be prioritized in results.

    Args:
        collection_name: Name of the collection
        field_name: Name of the field

    Returns:
        Integer priority score (1-10)
    """
    weights = get_field_weights(collection_name)
    return weights.get(field_name, 1)
