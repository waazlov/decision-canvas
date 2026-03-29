from __future__ import annotations

from app.models.question import (
    AnalysisPlan,
    AnalysisStep,
    QuestionIntent,
    QuestionInterpretation,
)


def route_question(interpretation: QuestionInterpretation) -> AnalysisPlan:
    if interpretation.fallback_used and (
        (interpretation.requested_metric and interpretation.metric != interpretation.requested_metric)
        or (interpretation.requested_dimension and interpretation.dimension != interpretation.requested_dimension)
    ):
        return AnalysisPlan(
            intent=QuestionIntent.OVERVIEW,
            metric=interpretation.metric,
            dimension=interpretation.dimension,
            direction=interpretation.direction,
            time_scope=interpretation.time_scope,
            comparison_targets=interpretation.comparison_targets,
            steps=[],
            fallback_used=True,
            notes=interpretation.notes,
        )

    if interpretation.fallback_used or interpretation.intent == QuestionIntent.OVERVIEW:
        return AnalysisPlan(
            intent=QuestionIntent.OVERVIEW,
            metric=interpretation.metric,
            dimension=interpretation.dimension,
            direction=interpretation.direction,
            time_scope=interpretation.time_scope,
            comparison_targets=interpretation.comparison_targets,
            steps=[
                AnalysisStep.TREND,
                AnalysisStep.SEGMENT_RANKING,
                AnalysisStep.ANOMALY,
                AnalysisStep.FUNNEL,
            ],
            fallback_used=True,
            notes=interpretation.notes,
        )

    step_map = {
        QuestionIntent.TREND_ANALYSIS: [AnalysisStep.TREND, AnalysisStep.ANOMALY],
        QuestionIntent.SEGMENT_BEST: [AnalysisStep.SEGMENT_RANKING],
        QuestionIntent.SEGMENT_WORST: [AnalysisStep.SEGMENT_RANKING],
        QuestionIntent.ANOMALY_DETECTION: [AnalysisStep.ANOMALY, AnalysisStep.TREND],
        QuestionIntent.FUNNEL_DROPOFF: [AnalysisStep.FUNNEL],
        QuestionIntent.METRIC_COMPARISON: [AnalysisStep.SEGMENT_RANKING],
    }

    return AnalysisPlan(
        intent=interpretation.intent,
        metric=interpretation.metric,
        dimension=interpretation.dimension,
        direction=interpretation.direction,
        time_scope=interpretation.time_scope,
        comparison_targets=interpretation.comparison_targets,
        steps=step_map[interpretation.intent],
        fallback_used=False,
        notes=interpretation.notes,
    )
