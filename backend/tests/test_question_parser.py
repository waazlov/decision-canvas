from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.models.question import QuestionIntent
from app.services.metric_engine import prepare_analysis_frame
from app.services.question_parser import parse_question
from app.services.question_router import route_question
from app.services.report_generator import build_dashboard


def _load_demo_frame() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "ecommerce_demo.csv")


def test_parser_detects_best_region_intent() -> None:
    dataframe, field_map, _assumptions = prepare_analysis_frame(_load_demo_frame())
    interpretation = parse_question("Which region performs best?", dataframe, field_map)

    assert interpretation.intent == QuestionIntent.SEGMENT_BEST
    assert interpretation.dimension == "region"
    assert interpretation.metric == "revenue"
    assert not interpretation.fallback_used


def test_dashboard_changes_path_for_best_region_question() -> None:
    dashboard = build_dashboard(
        _load_demo_frame(),
        dataset_name="ecommerce_demo.csv",
        question="Which region performs best?",
    )

    assert dashboard.interpreted_question.intent == QuestionIntent.SEGMENT_BEST
    assert dashboard.findings
    assert dashboard.findings[0].type == "segment_outperformance"
    assert dashboard.findings[0].dimension == "region"
    assert dashboard.charts
    assert dashboard.charts[0].template in {"bar", "grouped_bar"}


def test_low_confidence_questions_fall_back_to_overview() -> None:
    dataframe, field_map, _assumptions = prepare_analysis_frame(_load_demo_frame())
    interpretation = parse_question("Can you help me?", dataframe, field_map)
    plan = route_question(interpretation)

    assert interpretation.intent == QuestionIntent.OVERVIEW
    assert interpretation.fallback_used
    assert plan.fallback_used


def test_explicit_missing_metric_does_not_substitute_revenue() -> None:
    dataframe = pd.DataFrame(
        {
            "invoiceDate": pd.date_range("2024-01-01", periods=8, freq="D"),
            "revenue": [100, 120, 110, 130, 125, 140, 150, 145],
            "region": ["East", "West", "East", "West", "East", "West", "East", "West"],
        }
    )
    analysis_frame, field_map, _assumptions = prepare_analysis_frame(dataframe)

    interpretation = parse_question("How are sessions trending week over week?", analysis_frame, field_map)
    plan = route_question(interpretation)
    dashboard = build_dashboard(dataframe, dataset_name="retail.csv", question="How are sessions trending week over week?")

    assert interpretation.requested_metric == "sessions"
    assert interpretation.metric is None
    assert interpretation.fallback_used
    assert plan.steps == []
    assert dashboard.findings == []
    assert dashboard.interpreted_question.metric is None
    assert "does not contain the requested sessions metric" in dashboard.executive_summary.what_happened
