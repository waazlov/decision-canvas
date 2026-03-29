from __future__ import annotations

import re
from collections.abc import Iterable

import pandas as pd

from app.models.findings import ConfidenceLevel
from app.models.question import (
    QuestionDirection,
    QuestionIntent,
    QuestionInterpretation,
    QuestionTimeScope,
)
from app.services.semantic_inference import BUSINESS_FIELD_SYNONYMS


INTENT_KEYWORDS: dict[QuestionIntent, tuple[str, ...]] = {
    QuestionIntent.FUNNEL_DROPOFF: (
        "drop off",
        "dropoff",
        "dropping off",
        "funnel",
        "checkout",
        "abandon",
        "abandonment",
        "cart",
    ),
    QuestionIntent.METRIC_COMPARISON: (
        "compare",
        "comparison",
        "versus",
        " vs ",
        "against",
        "relative to",
        "compared to",
        "between",
    ),
    QuestionIntent.SEGMENT_BEST: (
        "best",
        "top",
        "highest",
        "strongest",
        "leading",
        "most revenue",
        "performs best",
        "drive the most",
        "drives the most",
    ),
    QuestionIntent.SEGMENT_WORST: (
        "worst",
        "lowest",
        "weakest",
        "underperform",
        "underperforming",
        "lagging",
        "drop the most",
        "performs worst",
    ),
    QuestionIntent.ANOMALY_DETECTION: (
        "anomaly",
        "anomalies",
        "outlier",
        "outliers",
        "unusual",
        "spike",
        "dip",
        "what changed recently",
        "changed recently",
    ),
    QuestionIntent.TREND_ANALYSIS: (
        "trend",
        "over time",
        "why did",
        "why has",
        "drop",
        "decline",
        "declined",
        "growth",
        "grew",
        "increase",
        "decrease",
        "last month",
        "last week",
        "month over month",
        "week over week",
    ),
}

INTENT_PRIORITY: dict[QuestionIntent, int] = {
    QuestionIntent.FUNNEL_DROPOFF: 7,
    QuestionIntent.METRIC_COMPARISON: 6,
    QuestionIntent.SEGMENT_BEST: 5,
    QuestionIntent.SEGMENT_WORST: 4,
    QuestionIntent.ANOMALY_DETECTION: 3,
    QuestionIntent.TREND_ANALYSIS: 2,
    QuestionIntent.OVERVIEW: 1,
}

DIMENSION_ALIASES: dict[str, tuple[str, ...]] = {
    "region": ("region", "regions", "country", "market", "geo", "state", "territory"),
    "device": ("device", "devices", "platform", "mobile", "desktop", "tablet"),
    "category": ("category", "categories", "product category", "segment", "segments", "plan"),
    "channel": ("channel", "channels", "source", "sources", "campaign", "campaigns"),
    "stage": ("stage", "stages", "step", "steps", "funnel stage"),
}

METRIC_ALIASES: dict[str, tuple[str, ...]] = {
    "revenue": ("revenue", "sales", "gmv", "arr", "mrr"),
    "orders": ("orders", "purchases", "transactions"),
    "sessions": ("sessions", "traffic", "visits", "users", "visitors"),
    "conversion": ("conversion", "conversion rate", "cvr", "cv rate", "checkout rate"),
    "aov": ("aov", "average order value", "avg order value"),
}

TIME_SCOPE_PATTERNS: tuple[tuple[QuestionTimeScope, tuple[str, ...]], ...] = (
    (QuestionTimeScope.LAST_WEEK, ("last week", "past week", "weekly")),
    (QuestionTimeScope.LAST_MONTH, ("last month", "past month", "monthly")),
    (QuestionTimeScope.RECENT, ("recent", "recently", "latest", "just changed")),
    (QuestionTimeScope.OVER_TIME, ("over time", "trend", "month over month", "week over week")),
)


def _normalize_question(question: str) -> str:
    return f" {question.strip().lower()} "


def _extract_time_scope(question_lower: str) -> QuestionTimeScope:
    for time_scope, patterns in TIME_SCOPE_PATTERNS:
        if any(pattern in question_lower for pattern in patterns):
            return time_scope
    return QuestionTimeScope.ALL_TIME if "best" in question_lower or "worst" in question_lower else QuestionTimeScope.UNSPECIFIED


def _score_intents(question_lower: str) -> dict[QuestionIntent, int]:
    scores = {intent: 0 for intent in QuestionIntent}
    for intent, patterns in INTENT_KEYWORDS.items():
        scores[intent] = sum(1 for pattern in patterns if pattern in question_lower)

    if "why did" in question_lower and any(term in question_lower for term in ("drop", "decline", "decrease")):
        scores[QuestionIntent.TREND_ANALYSIS] += 2
    if any(term in question_lower for term in ("best", "top", "highest", "strongest")):
        scores[QuestionIntent.SEGMENT_BEST] += 2
    if any(term in question_lower for term in ("worst", "lowest", "underperform", "weakest", "lagging")):
        scores[QuestionIntent.SEGMENT_WORST] += 2
    if "what changed recently" in question_lower:
        scores[QuestionIntent.ANOMALY_DETECTION] += 3

    return scores


def _pick_intent(question_lower: str) -> tuple[QuestionIntent, int]:
    scores = _score_intents(question_lower)
    ranked = sorted(
        scores.items(),
        key=lambda item: (item[1], INTENT_PRIORITY[item[0]]),
        reverse=True,
    )
    intent, score = ranked[0]
    if score <= 0:
        return QuestionIntent.OVERVIEW, 0
    return intent, score


def _extract_direction(intent: QuestionIntent, question_lower: str) -> QuestionDirection:
    if intent == QuestionIntent.SEGMENT_BEST:
        return QuestionDirection.BEST
    if intent == QuestionIntent.SEGMENT_WORST:
        return QuestionDirection.WORST
    if intent == QuestionIntent.METRIC_COMPARISON:
        return QuestionDirection.COMPARE
    if any(term in question_lower for term in ("drop", "decline")):
        return QuestionDirection.DROP
    if any(term in question_lower for term in ("growth", "grew")):
        return QuestionDirection.GROWTH
    if "increase" in question_lower:
        return QuestionDirection.INCREASE
    if "decrease" in question_lower:
        return QuestionDirection.DECREASE
    return QuestionDirection.NEUTRAL


def _extract_business_field(
    question_lower: str,
    field_map: dict[str, str],
    aliases_by_field: dict[str, Iterable[str]],
) -> str | None:
    for business_field, aliases in aliases_by_field.items():
        if business_field in field_map and any(alias in question_lower for alias in aliases):
            return business_field
    return None


def _candidate_dimensions(field_map: dict[str, str]) -> list[str]:
    ordered = ["region", "device", "category", "channel", "stage"]
    return [dimension for dimension in ordered if dimension in field_map]


def _extract_dimension(question_lower: str, field_map: dict[str, str]) -> str | None:
    for dimension, aliases in DIMENSION_ALIASES.items():
        if dimension in field_map and any(alias in question_lower for alias in aliases):
            return dimension
    return None


def _extract_comparison_targets(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
    question_lower: str,
    dimension: str | None,
) -> list[str]:
    normalized_targets: list[str] = []
    parsed_targets = re.findall(r"\b([\w-]+)\b\s+(?:vs|versus)\s+\b([\w-]+)\b", question_lower)
    if parsed_targets:
        for left, right in parsed_targets:
            normalized_targets.extend([left, right])

    if dimension and dimension in field_map:
        dimension_column = field_map[dimension]
        values = (
            dataframe[dimension_column]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )
        if len(values) <= 30:
            value_lookup = {value.lower(): value for value in values}
            for candidate in value_lookup:
                if f" {candidate.lower()} " in question_lower and value_lookup[candidate] not in normalized_targets:
                    normalized_targets.append(value_lookup[candidate])

    return normalized_targets[:4]


def parse_question(
    question: str,
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
) -> QuestionInterpretation:
    raw_question = question.strip()
    question_lower = _normalize_question(raw_question)
    notes: list[str] = []

    intent, intent_score = _pick_intent(question_lower)
    metric = _extract_business_field(question_lower, field_map, METRIC_ALIASES)
    dimension = _extract_dimension(question_lower, field_map)
    direction = _extract_direction(intent, question_lower)
    time_scope = _extract_time_scope(question_lower)

    if metric is None and intent in {
        QuestionIntent.TREND_ANALYSIS,
        QuestionIntent.SEGMENT_BEST,
        QuestionIntent.SEGMENT_WORST,
        QuestionIntent.METRIC_COMPARISON,
        QuestionIntent.ANOMALY_DETECTION,
    }:
        for fallback_metric in ("revenue", "conversion", "orders", "sessions", "aov"):
            if fallback_metric in field_map:
                metric = fallback_metric
                notes.append(f"No explicit metric was found in the question; using '{fallback_metric}'.")
                break

    if dimension is None and intent in {
        QuestionIntent.SEGMENT_BEST,
        QuestionIntent.SEGMENT_WORST,
        QuestionIntent.METRIC_COMPARISON,
    }:
        available_dimensions = _candidate_dimensions(field_map)
        if available_dimensions:
            dimension = available_dimensions[0]
            notes.append(f"No explicit segment dimension was found; using '{dimension}'.")

    comparison_targets = _extract_comparison_targets(dataframe, field_map, question_lower, dimension)
    if intent == QuestionIntent.METRIC_COMPARISON and len(comparison_targets) < 2 and dimension:
        notes.append("The comparison question did not specify two clear comparison targets.")

    fallback_used = False
    confidence = ConfidenceLevel.HIGH

    if intent_score == 0:
        intent = QuestionIntent.OVERVIEW
        fallback_used = True
        confidence = ConfidenceLevel.LOW
        notes.append("The question did not map confidently to a specific analysis intent, so a broader overview path was used.")
    elif intent in {QuestionIntent.SEGMENT_BEST, QuestionIntent.SEGMENT_WORST, QuestionIntent.METRIC_COMPARISON} and not dimension:
        intent = QuestionIntent.OVERVIEW
        fallback_used = True
        confidence = ConfidenceLevel.LOW
        notes.append("A segment-oriented question was detected, but no supported segment dimension was available in the dataset.")
    elif intent == QuestionIntent.FUNNEL_DROPOFF and not {"sessions", "orders"}.issubset(field_map):
        intent = QuestionIntent.OVERVIEW
        fallback_used = True
        confidence = ConfidenceLevel.LOW
        notes.append("A funnel question was detected, but the dataset does not include both sessions and orders.")
    elif metric is None and intent != QuestionIntent.OVERVIEW:
        confidence = ConfidenceLevel.MEDIUM
        notes.append("The requested metric was not available, so the analysis uses the strongest available fallback metric.")
    elif notes:
        confidence = ConfidenceLevel.MEDIUM

    return QuestionInterpretation(
        raw_question=raw_question,
        intent=intent,
        metric=metric,
        dimension=dimension,
        direction=direction,
        time_scope=time_scope,
        comparison_targets=comparison_targets,
        confidence=confidence,
        fallback_used=fallback_used,
        notes=notes,
    )
