from __future__ import annotations

from app.models.dashboard import ExecutiveSummary
from app.models.findings import Finding, FindingType


def build_executive_summary(question: str, findings: list[Finding], assumptions: list[str]) -> ExecutiveSummary:
    if not findings:
        return ExecutiveSummary(
            what_happened="The dataset was profiled successfully, but there was not enough structured evidence to produce a strong finding for the selected question.",
            why_it_likely_happened="Available columns did not support a higher-confidence explanation path.",
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

    what_happened = lead.title
    why_it_likely_happened = lead.explanation
    if supporting:
        why_it_likely_happened = f"{lead.explanation} Supporting signal: {supporting}."

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
