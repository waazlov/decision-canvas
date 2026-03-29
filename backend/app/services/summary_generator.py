from __future__ import annotations

from app.models.dashboard import ExecutiveSummary
from app.models.findings import Finding, FindingType
from app.models.question import QuestionIntent, QuestionInterpretation


def build_executive_summary(
    question: str,
    findings: list[Finding],
    assumptions: list[str],
    interpretation: QuestionInterpretation,
) -> ExecutiveSummary:
    if not findings:
        if interpretation.requested_metric and interpretation.requested_metric != interpretation.metric:
            return ExecutiveSummary(
                what_happened=(
                    f"The dataset was profiled successfully, but it does not contain the requested "
                    f"{interpretation.requested_metric.replace('_', ' ')} metric."
                ),
                why_it_likely_happened="The uploaded data does not expose the metric needed to answer this question directly.",
                what_to_do_next=[
                    "Use one of the detected metrics shown in the schema summary.",
                    "Try a question about available fields such as revenue, orders, conversion, or performance.",
                ],
                assumptions=assumptions,
                uncertainty_notes=[
                    "DecisionCanvas did not substitute a different metric because that would risk a misleading answer."
                ],
            )
        if interpretation.requested_dimension and interpretation.requested_dimension != interpretation.dimension:
            return ExecutiveSummary(
                what_happened=(
                    f"The dataset was profiled successfully, but it does not contain the requested "
                    f"{interpretation.requested_dimension.replace('_', ' ')} dimension."
                ),
                why_it_likely_happened="The uploaded data does not expose the segmentation field needed to answer this question directly.",
                what_to_do_next=[
                    "Use one of the detected dimensions shown in the schema summary.",
                    "Try a question using available dimensions such as region, category, channel, employee, or team.",
                ],
                assumptions=assumptions,
                uncertainty_notes=[
                    "DecisionCanvas did not substitute a different dimension because that would risk a misleading answer."
                ],
            )
        return ExecutiveSummary(
            what_happened="The dataset was profiled successfully, but there was not enough structured evidence to produce a strong finding for the selected question.",
            why_it_likely_happened=(
                "Available columns did not support a higher-confidence explanation path."
                if not interpretation.fallback_used
                else "The question was not resolved confidently, so the system used a broader overview path with limited evidence."
            ),
            what_to_do_next=[
                "Check whether the dataset includes a time column and core business metrics such as revenue, orders, or sessions.",
                "Try a more specific business question aligned to the available fields.",
            ],
            assumptions=assumptions,
            uncertainty_notes=[
                "No executive conclusion was generated beyond the available evidence."
            ],
        )

    lead = findings[0]
    supporting = findings[1].title if len(findings) > 1 else None

    if interpretation.intent == QuestionIntent.SEGMENT_BEST and lead.segment and lead.dimension:
        what_happened = (
            f"{lead.segment} is the strongest {lead.dimension.replace('_', ' ')} "
            f"on {lead.metric.replace('_', ' ')}."
        )
    elif interpretation.intent == QuestionIntent.SEGMENT_WORST and lead.segment and lead.dimension:
        what_happened = (
            f"{lead.segment} is the weakest {lead.dimension.replace('_', ' ')} "
            f"on {lead.metric.replace('_', ' ')}."
        )
    elif interpretation.intent == QuestionIntent.FUNNEL_DROPOFF:
        what_happened = "The funnel loses a meaningful share of sessions before they convert into orders."
    elif interpretation.intent == QuestionIntent.ANOMALY_DETECTION:
        what_happened = lead.title
    else:
        what_happened = lead.title

    why_it_likely_happened = lead.explanation
    if supporting:
        why_it_likely_happened = f"{lead.explanation} Supporting signal: {supporting}."
    if interpretation.fallback_used:
        why_it_likely_happened = (
            f"{why_it_likely_happened} The system used a broader overview path because the question could not be resolved with high confidence."
        )

    next_steps = [finding.recommended_action for finding in findings[:3]]

    return ExecutiveSummary(
        what_happened=what_happened,
        why_it_likely_happened=why_it_likely_happened,
        what_to_do_next=next_steps,
        assumptions=assumptions,
        uncertainty_notes=[
            "Recommendations are directional and should be validated with additional business context before execution."
        ],
    )
