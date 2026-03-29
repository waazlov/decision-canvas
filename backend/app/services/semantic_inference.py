from __future__ import annotations

import re
from collections.abc import Iterable

from app.models.dataset import SemanticRole


BUSINESS_FIELD_SYNONYMS: dict[str, tuple[str, ...]] = {
    "revenue": ("revenue", "sales", "gmv", "arr", "mrr", "amount", "net_sales"),
    "orders": ("orders", "order_count", "transactions", "purchases"),
    "sessions": ("sessions", "visits", "traffic", "users", "visitors"),
    "conversion": ("conversion", "conversion_rate", "cv_rate", "cvr"),
    "aov": ("aov", "average_order_value", "avg_order_value"),
    "date": ("date", "day", "week", "month", "timestamp", "order_date"),
    "device": ("device", "platform", "os", "device_type"),
    "region": ("region", "country", "market", "state", "territory", "geo"),
    "category": ("category", "product_category", "segment", "vertical", "plan"),
    "channel": ("channel", "source", "traffic_source", "acquisition_channel"),
    "stage": ("stage", "step", "funnel_stage", "status"),
}


def normalize_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return normalized.strip("_")


def infer_business_field(column_name: str) -> str | None:
    normalized = normalize_name(column_name)
    for business_field, aliases in BUSINESS_FIELD_SYNONYMS.items():
        if normalized == business_field or normalized in aliases:
            return business_field
        if any(alias in normalized for alias in aliases):
            return business_field
    return None


def infer_semantic_role(
    column_name: str,
    detected_type: str,
    unique_count: int,
    row_count: int,
) -> SemanticRole:
    business_field = infer_business_field(column_name)
    high_cardinality_ratio = (unique_count / row_count) if row_count else 0

    if business_field == "date" or detected_type in {"date", "datetime"}:
        return SemanticRole.TIME_DIMENSION
    if business_field == "stage":
        return SemanticRole.FUNNEL_STAGE
    if business_field in {"revenue", "orders", "sessions", "conversion", "aov"}:
        return SemanticRole.METRIC
    if detected_type in {"integer", "float"} and high_cardinality_ratio > 0.9:
        return SemanticRole.IDENTIFIER
    if detected_type in {"integer", "float"}:
        return SemanticRole.METRIC
    if high_cardinality_ratio > 0.95:
        return SemanticRole.IDENTIFIER
    return SemanticRole.DIMENSION


def infer_candidate_metrics(columns: Iterable[tuple[str, str, SemanticRole]]) -> list[str]:
    metrics = [name for name, _dtype, role in columns if role == SemanticRole.METRIC]
    return sorted(dict.fromkeys(metrics))


def infer_candidate_dimensions(columns: Iterable[tuple[str, str, SemanticRole]]) -> list[str]:
    dimensions = [
        name
        for name, _dtype, role in columns
        if role in {SemanticRole.DIMENSION, SemanticRole.TIME_DIMENSION, SemanticRole.FUNNEL_STAGE}
    ]
    return sorted(dict.fromkeys(dimensions))
