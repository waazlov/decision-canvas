from __future__ import annotations

import pandas as pd

from app.models.dashboard import DashboardPayload
from app.services.analysis_engine import run_analysis
from app.services.insight_engine import build_findings
from app.services.metric_engine import prepare_analysis_frame, summarize_kpis
from app.services.profiling_service import profile_dataset
from app.services.summary_generator import build_executive_summary
from app.services.visualization_planner import build_kpis, plan_charts


def build_dashboard(dataframe: pd.DataFrame, dataset_name: str, question: str) -> DashboardPayload:
    dataset_profile = profile_dataset(dataframe, dataset_name=dataset_name)
    analysis_frame, field_map, analysis_assumptions = prepare_analysis_frame(dataframe)

    assumptions = list(dict.fromkeys(dataset_profile.assumptions + analysis_assumptions))
    raw_findings = run_analysis(analysis_frame, field_map, question)
    findings = build_findings(raw_findings, assumptions)
    charts = plan_charts(analysis_frame, field_map, findings)
    kpis = build_kpis(summarize_kpis(analysis_frame, field_map))
    executive_summary = build_executive_summary(question, findings, assumptions)

    dashboard_title = question.strip().rstrip("?").title() or "DecisionCanvas Analysis"
    return DashboardPayload(
        dashboard_title=dashboard_title,
        question=question,
        dataset_profile=dataset_profile,
        kpis=kpis,
        findings=findings,
        charts=charts,
        executive_summary=executive_summary,
    )
