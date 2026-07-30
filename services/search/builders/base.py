from typing import Any


def safe_related(instance, attr):
    """Return a related object or None, swallowing missing/deleted refs."""
    if instance is None:
        return None
    try:
        return getattr(instance, attr, None)
    except Exception:
        return None


def stable_created_at(instance) -> int:
    """Deterministic timestamp used as a freshness tiebreaker.

    These academic models carry no real created_at field. Previously the
    syncer injected int(time.time()) on every save, which made every
    re-index churn the freshness signal. We instead derive a stable int
    from the UUID pk: high bits map to a fixed epoch window, so ordering
    by created_at approximates insertion order without per-save churn.
    """
    pk = getattr(instance, "pk", None)
    # Base epoch chosen in 2024; any positive int keeps sort_by functional.
    base = 1700000000
    try:
        if isinstance(pk, str):
            # Use a stable slice of the UUID's integer value.
            return base + (int(pk.replace("-", "")[:12], 16) % 100_000_000)
        if pk is not None:
            return base + (int(pk) % 100_000_000)
    except (TypeError, ValueError):
        pass
    return base


def sanitize(
    document: dict[str, Any], model_name: str, collection_map: dict[str, str]
) -> dict[str, Any]:
    """Drop None values and fields absent from the collection schema."""
    from ..schemas import MODEL_TO_COLLECTION, get_valid_fields

    collection = MODEL_TO_COLLECTION.get(model_name) or collection_map.get(model_name)
    if collection:
        valid = set(get_valid_fields(collection))
    else:
        valid = set(document.keys())

    cleaned = {}
    for key, value in document.items():
        if key not in valid:
            continue
        if value is None:
            continue
        cleaned[key] = value
    return cleaned
