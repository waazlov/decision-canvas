from __future__ import annotations

from itertools import count

from app.models.findings import ConfidenceLevel, Finding, FindingType, TimeWindow
from app.models.question import QuestionIntent, QuestionInterpretation


def _confidence_from_magnitude(magnitude_pct: float | None) -> ConfidenceLevel:
    magnitude = abs(magnitude_pct or 0)
    if magnitude >= 15:
        return ConfidenceLevel.HIGH
    if magnitude >= 5:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def _action_for_finding(finding_type: str, metric: str, dimension: str | None = None) -> str:
    if finding_type == "trend_drop":
        if metric == "conversion":
            return "Investigate UX friction, landing page performance, and campaign quality for the affected period."
        if metric == "revenue":
            return "Review pricing, merchandising, and demand-generation changes that affected the latest period."
        return "Inspect operational or acquisition changes that reduced performance in the latest period."
    if finding_type == "trend_growth":
        return "Identify the drivers behind the improvement and determine whether they can be repeated in the next planning cycle."
    if finding_type == "segment_outperformance":
        if dimension == "device":
            return "Use the strongest device experience as a benchmark for weaker device journeys."
        if dimension == "region":
            return "Review what the leading region is doing differently in pricing, targeting, or local demand capture."
        if dimension == "category":
            return "Validate whether assortment, pricing, or retention drivers from the strongest category can be scaled."
        if dimension == "channel":
            return "Audit the highest-performing acquisition channel and test whether its tactics can be expanded efficiently."
    if finding_type == "segment_underperformance":
        if dimension == "device":
            return "Prioritize UX improvements for the weakest device experience and review conversion blockers."
        if dimension == "region":
            return "Review regional targeting, local pricing, and market-specific demand drivers."
        if dimension == "category":
            return "Reassess category positioning, pricing, and retention levers for the weakest category."
    if finding_type == "anomaly":
        return "Validate whether the spike or dip is caused by instrumentation, campaign changes, or operational incidents."
    if finding_type == "funnel_dropoff":
        return "Audit the funnel step with the largest drop-off and test UX or targeting improvements to reduce abandonment."
    return "Review the affected area and validate the likely driver before making changes."


def build_findings(
    raw_findings: list[dict],
    assumptions: list[str],
    interpretation: QuestionInterpretation,
) -> list[Finding]:
    findings: list[Finding] = []
    id_counter = count(1)

    for raw in raw_findings[:10]:
        finding_type = FindingType(raw["type"])
        metric = raw["metric"]
        magnitude_pct = raw.get("magnitude_pct")
        confidence = _confidence_from_magnitude(magnitude_pct)
        segment = raw.get("segment")
        dimension = raw.get("dimension")

        title = {
            "trend_drop": f"{metric.replace('_', ' ').title()} declined in the latest period",
            "trend_growth": f"{metric.replace('_', ' ').title()} improved in the latest period",
            "segment_outperformance": f"{segment} leads on {metric.replace('_', ' ')}",
            "segment_underperformance": f"{segment} underperforms on {metric.replace('_', ' ')}",
            "anomaly": f"Anomalous {metric.replace('_', ' ')} movement detected",
            "funnel_dropoff": "Funnel drop-off detected between sessions and orders",
        }[raw["type"]]

        explanation = {
            "trend_drop": f"The latest period is {abs(magnitude_pct or 0):.2f}% below the previous comparable period.",
            "trend_growth": f"The latest period is {abs(magnitude_pct or 0):.2f}% above the previous comparable period.",
            "segment_outperformance": f"{segment} is outperforming the comparison baseline by {abs(magnitude_pct or 0):.2f}%.",
            "segment_underperformance": f"{segment} is underperforming the overall baseline by {abs(magnitude_pct or 0):.2f}%.",
            "anomaly": f"The selected metric deviates materially from its recent baseline with a z-score of {raw.get('anomaly_score', 0):.2f}.",
            "funnel_dropoff": f"Approximately {magnitude_pct or 0:.2f}% of sessions do not reach an order outcome.",
        }[raw["type"]]

        evidence = []
        if raw.get("comparison_value") is not None:
            evidence.append(f"Current value: {raw.get('value')}")
            evidence.append(f"Comparison value: {raw.get('comparison_value')}")
        if dimension:
            evidence.append(f"Dimension analyzed: {dimension}")
        if raw.get("comparison_segment"):
            evidence.append(f"Compared against: {raw['comparison_segment']}")

        if interpretation.fallback_used:
            evidence.append("The question could not be fully resolved, so the dashboard used a broader fallback analysis path.")

        if interpretation.intent == QuestionIntent.METRIC_COMPARISON and raw.get("comparison_segment"):
            explanation = (
                f"{segment} leads {raw['comparison_segment']} on {metric.replace('_', ' ')} "
                f"by {abs(magnitude_pct or 0):.2f}%."
            )

        findings.append(
            Finding(
                id=f"finding_{next(id_counter):03d}",
                type=finding_type,
                title=title,
                metric=metric,
                dimension=dimension,
                segment=segment,
                time_window=TimeWindow(
                    current_start=raw.get("current_period"),
                    current_end=raw.get("current_period"),
                    comparison_start=raw.get("previous_period"),
                    comparison_end=raw.get("previous_period"),
                )
                if raw.get("current_period")
                else None,
                value=raw.get("value"),
                comparison_value=raw.get("comparison_value"),
                magnitude_pct=magnitude_pct,
                confidence=confidence,
                explanation=explanation,
                recommended_action=_action_for_finding(raw["type"], metric, dimension),
                evidence=evidence,
                assumptions=assumptions,
                uncertainty_notes=[
                    "Findings are based on available tabular data and should not be interpreted as confirmed causality."
                ],
            )
        )

    return findings
