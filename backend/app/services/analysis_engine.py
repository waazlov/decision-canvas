from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.services.metric_engine import pick_metric_for_question


def _period_granularity(date_series: pd.Series) -> str:
    unique_days = date_series.dropna().dt.date.nunique()
    if unique_days >= 180:
        return "M"
    if unique_days >= 30:
        return "W"
    return "D"


def _period_granularity_for_question(date_series: pd.Series, question: str) -> str:
    question_lower = question.lower()
    if "month" in question_lower:
        return "M"
    if "week" in question_lower:
        return "W"
    if "day" in question_lower or "daily" in question_lower:
        return "D"
    return _period_granularity(date_series)


def analyze_trends(dataframe: pd.DataFrame, field_map: dict[str, str], question: str) -> list[dict[str, Any]]:
    date_column = field_map.get("date")
    if not date_column or date_column not in dataframe.columns:
        return []

    primary_metric = pick_metric_for_question(field_map, question)
    if not primary_metric:
        return []

    metric_column = field_map[primary_metric]
    trend_frame = dataframe[[date_column, metric_column]].dropna().sort_values(date_column)
    if len(trend_frame) < 4:
        return []

    granularity = _period_granularity_for_question(trend_frame[date_column], question)
    trend_frame["period"] = trend_frame[date_column].dt.to_period(granularity)
    aggregated = trend_frame.groupby("period")[metric_column].mean() if primary_metric == "conversion" else trend_frame.groupby("period")[metric_column].sum()
    if len(aggregated) < 2:
        return []

    current_period = aggregated.index[-1]
    previous_period = aggregated.index[-2]
    current_value = float(aggregated.iloc[-1])
    previous_value = float(aggregated.iloc[-2])
    if previous_value == 0:
        return []

    delta_pct = ((current_value - previous_value) / previous_value) * 100
    finding_type = "trend_growth" if delta_pct >= 0 else "trend_drop"
    return [
        {
            "type": finding_type,
            "metric": primary_metric,
            "value": current_value,
            "comparison_value": previous_value,
            "magnitude_pct": round(delta_pct, 2),
            "current_period": str(current_period),
            "previous_period": str(previous_period),
            "granularity": granularity,
        }
    ]


def analyze_segments(dataframe: pd.DataFrame, field_map: dict[str, str], question: str) -> list[dict[str, Any]]:
    primary_metric = pick_metric_for_question(field_map, question)
    if not primary_metric:
        return []

    metric_column = field_map[primary_metric]
    candidate_dimensions = [key for key in ("device", "region", "category") if key in field_map]
    findings: list[dict[str, Any]] = []

    overall_series = dataframe[metric_column].dropna()
    if overall_series.empty:
        return []
    overall_value = float(overall_series.mean()) if primary_metric == "conversion" else float(overall_series.mean())

    for dimension in candidate_dimensions:
        dimension_column = field_map[dimension]
        grouped = dataframe[[dimension_column, metric_column]].dropna().groupby(dimension_column)[metric_column].mean()
        if grouped.empty or len(grouped) < 2:
            continue

        worst_segment = grouped.idxmin()
        worst_value = float(grouped.min())
        delta_pct = ((worst_value - overall_value) / overall_value) * 100 if overall_value else 0
        findings.append(
            {
                "type": "segment_underperformance",
                "metric": primary_metric,
                "dimension": dimension,
                "segment": str(worst_segment),
                "value": worst_value,
                "comparison_value": overall_value,
                "magnitude_pct": round(delta_pct, 2),
            }
        )

    return findings


def analyze_anomalies(dataframe: pd.DataFrame, field_map: dict[str, str], question: str) -> list[dict[str, Any]]:
    date_column = field_map.get("date")
    primary_metric = pick_metric_for_question(field_map, question)
    if not date_column or not primary_metric:
        return []

    metric_column = field_map[primary_metric]
    anomaly_frame = dataframe[[date_column, metric_column]].dropna().sort_values(date_column)
    if len(anomaly_frame) < 8:
        return []

    daily = anomaly_frame.groupby(anomaly_frame[date_column].dt.to_period("D"))[metric_column].mean()
    if len(daily) < 8:
        return []

    zscores = (daily - daily.mean()) / daily.std(ddof=0) if daily.std(ddof=0) else daily * 0
    flagged = zscores.abs() >= 2.0
    if not flagged.any():
        return []

    anomaly_period = daily.index[flagged][-1]
    anomaly_value = float(daily.loc[anomaly_period])
    anomaly_score = float(zscores.loc[anomaly_period])
    return [
        {
            "type": "anomaly",
            "metric": primary_metric,
            "segment": str(anomaly_period),
            "value": anomaly_value,
            "comparison_value": float(daily.mean()),
            "magnitude_pct": round(((anomaly_value - float(daily.mean())) / float(daily.mean())) * 100, 2)
            if daily.mean()
            else None,
            "anomaly_score": round(anomaly_score, 2),
        }
    ]


def analyze_funnel(dataframe: pd.DataFrame, field_map: dict[str, str]) -> list[dict[str, Any]]:
    if not {"sessions", "orders"}.issubset(field_map):
        return []

    sessions = float(pd.to_numeric(dataframe[field_map["sessions"]], errors="coerce").sum())
    orders = float(pd.to_numeric(dataframe[field_map["orders"]], errors="coerce").sum())
    if sessions <= 0 or orders <= 0 or orders >= sessions:
        return []

    dropoff_pct = ((sessions - orders) / sessions) * 100
    return [
        {
            "type": "funnel_dropoff",
            "metric": "orders",
            "segment": "sessions_to_orders",
            "value": orders,
            "comparison_value": sessions,
            "magnitude_pct": round(dropoff_pct, 2),
        }
    ]


def run_analysis(dataframe: pd.DataFrame, field_map: dict[str, str], question: str) -> list[dict[str, Any]]:
    # Question-aware ordering is lightweight and deterministic; it does not invent new analysis paths.
    question_lower = question.lower()
    ranked_outputs: list[dict[str, Any]] = []

    if any(keyword in question_lower for keyword in ("drop", "trend", "month", "week", "performance")):
        ranked_outputs.extend(analyze_trends(dataframe, field_map, question))
    if any(keyword in question_lower for keyword in ("segment", "region", "device", "category", "who")):
        ranked_outputs.extend(analyze_segments(dataframe, field_map, question))
    if any(keyword in question_lower for keyword in ("anomaly", "spike", "dip", "outlier")):
        ranked_outputs.extend(analyze_anomalies(dataframe, field_map, question))
    if any(keyword in question_lower for keyword in ("funnel", "drop-off", "dropoff", "checkout")):
        ranked_outputs.extend(analyze_funnel(dataframe, field_map))

    if not ranked_outputs:
        ranked_outputs.extend(analyze_trends(dataframe, field_map, question))
        ranked_outputs.extend(analyze_segments(dataframe, field_map, question))
        ranked_outputs.extend(analyze_anomalies(dataframe, field_map, question))
        ranked_outputs.extend(analyze_funnel(dataframe, field_map))

    return ranked_outputs
