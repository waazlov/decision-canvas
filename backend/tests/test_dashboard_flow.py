from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.services.report_generator import build_dashboard


def test_build_dashboard_returns_demo_ready_payload() -> None:
    dataframe = pd.read_csv(
        Path(__file__).resolve().parents[2] / "data" / "ecommerce_demo.csv"
    )

    dashboard = build_dashboard(
        dataframe,
        dataset_name="ecommerce_demo.csv",
        question="Why did conversion drop last month?",
    )

    assert dashboard.dashboard_title == "Why Did Conversion Drop Last Month"
    assert dashboard.kpis
    assert dashboard.findings
    assert 1 <= len(dashboard.charts) <= 5
    assert dashboard.executive_summary.what_happened
    assert any(finding.type == "trend_drop" for finding in dashboard.findings)
