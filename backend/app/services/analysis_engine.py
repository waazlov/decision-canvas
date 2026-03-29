from __future__ import annotations

from typing import Any

import pandas as pd

from app.models.question import (
    AnalysisPlan,
    AnalysisStep,
    QuestionDirection,
    QuestionIntent,
    QuestionInterpretation,
    QuestionTimeScope,
)
from app.services.metric_engine import pick_metric_for_question, pick_primary_metric


def _period_granularity(date_series: pd.Series) -> str:
    unique_days = date_series.dropna().dt.date.nunique()
    if unique_days >= 180:
        return "M"
    if unique_days >= 30:
        return "W"
    return "D"


def _granularity_for_scope(date_series: pd.Series, time_scope: QuestionTimeScope, question: str) -> str:
    if time_scope == QuestionTimeScope.LAST_MONTH:
        return "M"
    if time_scope == QuestionTimeScope.LAST_WEEK:
        return "W"
    if "day" in question.lower() or "daily" in question.lower():
        return "D"
    return _period_granularity(date_series)


def _resolve_metric(
    field_map: dict[str, str],
    interpretation: QuestionInterpretation,
) -> str | None:
    if interpretation.metric and interpretation.metric in field_map:
        return interpretation.metric
    fallback_metric = pick_metric_for_question(field_map, interpretation.raw_question)
    return fallback_metric or pick_primary_metric(field_map)


def _candidate_dimensions(field_map: dict[str, str], interpretation: QuestionInterpretation) -> list[str]:
    ordered_dimensions = [interpretation.dimension] if interpretation.dimension else []
    ordered_dimensions.extend(["region", "device", "category", "channel"])
    return [dimension for dimension in dict.fromkeys(ordered_dimensions) if dimension and dimension in field_map]


def _aggregate_metric(
    grouped: pd.core.groupby.SeriesGroupBy,
    metric: str,
) -> pd.Series:
    return grouped.mean() if metric in {"conversion", "aov"} else grouped.sum()


def analyze_trends(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
    interpretation: QuestionInterpretation,
) -> list[dict[str, Any]]:
    date_column = field_map.get("date")
    metric = _resolve_metric(field_map, interpretation)
    if not date_column or not metric:
        return []

    metric_column = field_map[metric]
    trend_frame = dataframe[[date_column, metric_column]].dropna().sort_values(date_column)
    if len(trend_frame) < 4:
        return []

    granularity = _granularity_for_scope(trend_frame[date_column], interpretation.time_scope, interpretation.raw_question)
    trend_frame["period"] = trend_frame[date_column].dt.to_period(granularity)
    grouped = trend_frame.groupby("period")[metric_column]
    aggregated = _aggregate_metric(grouped, metric)
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
            "metric": metric,
            "dimension": None,
            "segment": None,
            "value": current_value,
            "comparison_value": previous_value,
            "magnitude_pct": round(delta_pct, 2),
            "current_period": str(current_period),
            "previous_period": str(previous_period),
            "granularity": granularity,
        }
    ]


def analyze_segments(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
    interpretation: QuestionInterpretation,
    plan: AnalysisPlan,
) -> list[dict[str, Any]]:
    metric = _resolve_metric(field_map, interpretation)
    if not metric:
        return []

    metric_column = field_map[metric]
    findings: list[dict[str, Any]] = []

    for dimension in _candidate_dimensions(field_map, interpretation):
        dimension_column = field_map[dimension]
        grouped = _aggregate_metric(
            dataframe[[dimension_column, metric_column]].dropna().groupby(dimension_column)[metric_column],
            metric,
        )
        if grouped.empty or len(grouped) < 2:
            continue

        if plan.intent == QuestionIntent.METRIC_COMPARISON and plan.comparison_targets:
            target_lookup = {target.lower(): target for target in plan.comparison_targets}
            filtered = grouped[grouped.index.astype(str).str.lower().isin(target_lookup)]
            if len(filtered) >= 2:
                ranked = filtered.sort_values(ascending=False)
                best_segment = str(ranked.index[0])
                comparison_segment = str(ranked.index[1])
                best_value = float(ranked.iloc[0])
                comparison_value = float(ranked.iloc[1])
                delta_pct = ((best_value - comparison_value) / comparison_value) * 100 if comparison_value else 0
                findings.append(
                    {
                        "type": "segment_outperformance",
                        "metric": metric,
                        "dimension": dimension,
                        "segment": best_segment,
                        "comparison_segment": comparison_segment,
                        "value": best_value,
                        "comparison_value": comparison_value,
                        "magnitude_pct": round(delta_pct, 2),
                    }
                )
                return findings

        ranked = grouped.sort_values(ascending=False)
        overall_value = float(grouped.mean())

        if plan.intent == QuestionIntent.SEGMENT_WORST:
            selected_segment = str(ranked.index[-1])
            selected_value = float(ranked.iloc[-1])
            finding_type = "segment_underperformance"
        else:
            selected_segment = str(ranked.index[0])
            selected_value = float(ranked.iloc[0])
            finding_type = "segment_outperformance"

        delta_pct = ((selected_value - overall_value) / overall_value) * 100 if overall_value else 0
        findings.append(
            {
                "type": finding_type,
                "metric": metric,
                "dimension": dimension,
                "segment": selected_segment,
                "value": selected_value,
                "comparison_value": overall_value,
                "magnitude_pct": round(delta_pct, 2),
            }
        )

        if plan.intent in {
            QuestionIntent.SEGMENT_BEST,
            QuestionIntent.SEGMENT_WORST,
            QuestionIntent.METRIC_COMPARISON,
        }:
            break

    return findings


def analyze_anomalies(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
    interpretation: QuestionInterpretation,
) -> list[dict[str, Any]]:
    date_column = field_map.get("date")
    metric = _resolve_metric(field_map, interpretation)
    if not date_column or not metric:
        return []

    metric_column = field_map[metric]
    anomaly_frame = dataframe[[date_column, metric_column]].dropna().sort_values(date_column)
    if len(anomaly_frame) < 8:
        return []

    daily = _aggregate_metric(
        anomaly_frame.groupby(anomaly_frame[date_column].dt.to_period("D"))[metric_column],
        metric,
    )
    if len(daily) < 8:
        return []

    standard_deviation = daily.std(ddof=0)
    if not standard_deviation:
        return []

    zscores = (daily - daily.mean()) / standard_deviation
    flagged = zscores.abs() >= 2.0
    if not flagged.any():
        return []

    anomaly_period = daily.index[flagged][-1]
    anomaly_value = float(daily.loc[anomaly_period])
    anomaly_score = float(zscores.loc[anomaly_period])
    baseline = float(daily.mean())
    return [
        {
            "type": "anomaly",
            "metric": metric,
            "dimension": None,
            "segment": str(anomaly_period),
            "value": anomaly_value,
            "comparison_value": baseline,
            "magnitude_pct": round(((anomaly_value - baseline) / baseline) * 100, 2) if baseline else None,
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
            "dimension": "stage",
            "segment": "sessions_to_orders",
            "value": orders,
            "comparison_value": sessions,
            "magnitude_pct": round(dropoff_pct, 2),
        }
    ]


def run_analysis(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
    interpretation: QuestionInterpretation,
    plan: AnalysisPlan,
) -> list[dict[str, Any]]:
    ranked_outputs: list[dict[str, Any]] = []
    for step in plan.steps:
        if step == AnalysisStep.TREND:
            ranked_outputs.extend(analyze_trends(dataframe, field_map, interpretation))
        elif step == AnalysisStep.SEGMENT_RANKING:
            ranked_outputs.extend(analyze_segments(dataframe, field_map, interpretation, plan))
        elif step == AnalysisStep.ANOMALY:
            ranked_outputs.extend(analyze_anomalies(dataframe, field_map, interpretation))
        elif step == AnalysisStep.FUNNEL:
            ranked_outputs.extend(analyze_funnel(dataframe, field_map))

    if not ranked_outputs and plan.intent != QuestionIntent.OVERVIEW:
        overview_plan = AnalysisPlan(
            intent=QuestionIntent.OVERVIEW,
            metric=plan.metric,
            dimension=plan.dimension,
            direction=QuestionDirection.NEUTRAL,
            time_scope=plan.time_scope,
            comparison_targets=plan.comparison_targets,
            steps=[
                AnalysisStep.TREND,
                AnalysisStep.SEGMENT_RANKING,
                AnalysisStep.ANOMALY,
                AnalysisStep.FUNNEL,
            ],
            fallback_used=True,
            notes=plan.notes,
        )
        return run_analysis(dataframe, field_map, interpretation, overview_plan)

    return ranked_outputs
