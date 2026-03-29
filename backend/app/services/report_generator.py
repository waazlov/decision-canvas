from __future__ import annotations

import pandas as pd

from app.models.dashboard import DashboardPayload
from app.services.analysis_engine import run_analysis
from app.services.insight_engine import build_findings
from app.services.metric_engine import prepare_analysis_frame, summarize_kpis
from app.services.profiling_service import profile_dataset
from app.services.question_parser import parse_question
from app.services.question_router import route_question
from app.services.summary_generator import build_executive_summary
from app.services.visualization_planner import build_kpis, plan_charts


def _deduplicate_assumptions(assumptions: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for assumption in assumptions:
        normalized = assumption.strip().lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(assumption)
    return deduped


def build_dashboard(dataframe: pd.DataFrame, dataset_name: str, question: str) -> DashboardPayload:
    dataset_profile = profile_dataset(dataframe, dataset_name=dataset_name)
    analysis_frame, field_map, analysis_assumptions = prepare_analysis_frame(dataframe)

    assumptions = _deduplicate_assumptions(dataset_profile.assumptions + analysis_assumptions)
    interpretation = parse_question(question, analysis_frame, field_map)
    plan = route_question(interpretation)
    raw_findings = run_analysis(analysis_frame, field_map, interpretation, plan)
    findings = build_findings(raw_findings, assumptions, interpretation)
    charts = plan_charts(analysis_frame, field_map, findings, interpretation)
    kpis = build_kpis(summarize_kpis(analysis_frame, field_map))
    executive_summary = build_executive_summary(question, findings, assumptions, interpretation)

    dashboard_title = question.strip().rstrip("?").title() or "DecisionCanvas Analysis"
    return DashboardPayload(
        dashboard_title=dashboard_title,
        question=question,
        interpreted_question=interpretation,
        dataset_profile=dataset_profile,
        kpis=kpis,
        findings=findings,
        charts=charts,
        executive_summary=executive_summary,
    )
