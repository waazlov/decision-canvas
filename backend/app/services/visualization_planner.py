from __future__ import annotations

from typing import Any

import pandas as pd

from app.models.charts import AxisSpec, ChartAnnotation, ChartSeries, ChartSpec, ChartTemplate, KPI, ValueFormat
from app.models.findings import Finding, FindingType
from app.services.metric_engine import metric_format_for_field


def _format_enum(value: str) -> ValueFormat:
    return ValueFormat(metric_format_for_field(value))


def _build_trend_chart(dataframe: pd.DataFrame, field_map: dict[str, str], finding: Finding) -> ChartSpec | None:
    date_column = field_map.get("date")
    metric_column = field_map.get(finding.metric)
    if not date_column or not metric_column:
        return None

    chart_frame = dataframe[[date_column, metric_column]].dropna().sort_values(date_column).copy()
    chart_frame["period"] = pd.to_datetime(chart_frame[date_column]).dt.strftime("%Y-%m-%d")
    chart_data = chart_frame.rename(columns={"period": "x", metric_column: "y"})[["x", "y"]].tail(24)

    return ChartSpec(
        id=f"chart_{finding.id}",
        template=ChartTemplate.LINE,
        title=f"{finding.metric.replace('_', ' ').title()} trend",
        subtitle=finding.title,
        reason_for_selection="A line chart best communicates how the metric changed over time.",
        x_axis=AxisSpec(field="x", label="Date", format=ValueFormat.STRING),
        y_axis=AxisSpec(
            field="y",
            label=finding.metric.replace("_", " ").title(),
            format=_format_enum(finding.metric),
        ),
        series=[ChartSeries(name=finding.metric.replace("_", " ").title(), field="y")],
        data=chart_data.to_dict(orient="records"),
        annotation=ChartAnnotation(label=finding.title, x_value=chart_data.iloc[-1]["x"], y_value=chart_data.iloc[-1]["y"]),
    )


def _build_segment_chart(dataframe: pd.DataFrame, field_map: dict[str, str], finding: Finding) -> ChartSpec | None:
    metric_column = field_map.get(finding.metric)
    if not metric_column or not finding.segment:
        return None

    segment_dimension = None
    for dimension in ("device", "region", "category"):
        column = field_map.get(dimension)
        if column and finding.segment in dataframe[column].astype(str).unique():
            segment_dimension = column
            break
    if not segment_dimension:
        return None

    chart_frame = (
        dataframe[[segment_dimension, metric_column]]
        .dropna()
        .groupby(segment_dimension)[metric_column]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    chart_frame.columns = ["x", "y"]

    return ChartSpec(
        id=f"chart_{finding.id}",
        template=ChartTemplate.BAR,
        title=f"{finding.metric.replace('_', ' ').title()} by segment",
        subtitle=finding.title,
        reason_for_selection="A bar chart makes segment underperformance easy to compare against peers.",
        x_axis=AxisSpec(field="x", label="Segment", format=ValueFormat.STRING),
        y_axis=AxisSpec(field="y", label=finding.metric.replace("_", " ").title(), format=_format_enum(finding.metric)),
        series=[ChartSeries(name=finding.metric.replace("_", " ").title(), field="y")],
        data=chart_frame.to_dict(orient="records"),
        annotation=ChartAnnotation(label="Weakest segment", x_value=finding.segment, y_value=finding.value),
    )


def _build_funnel_chart(dataframe: pd.DataFrame, field_map: dict[str, str], finding: Finding) -> ChartSpec | None:
    sessions_column = field_map.get("sessions")
    orders_column = field_map.get("orders")
    if not sessions_column or not orders_column:
        return None

    sessions = float(pd.to_numeric(dataframe[sessions_column], errors="coerce").sum())
    orders = float(pd.to_numeric(dataframe[orders_column], errors="coerce").sum())
    chart_data = [
        {"stage": "Sessions", "value": sessions},
        {"stage": "Orders", "value": orders},
    ]

    return ChartSpec(
        id=f"chart_{finding.id}",
        template=ChartTemplate.FUNNEL,
        title="Sessions to orders funnel",
        subtitle=finding.title,
        reason_for_selection="A funnel chart directly shows drop-off between entry traffic and completed orders.",
        x_axis=AxisSpec(field="stage", label="Stage", format=ValueFormat.STRING),
        y_axis=AxisSpec(field="value", label="Volume", format=ValueFormat.INTEGER),
        series=[ChartSeries(name="Volume", field="value")],
        data=chart_data,
        annotation=ChartAnnotation(label="Observed drop-off", x_value="Orders", y_value=orders),
    )


def plan_charts(dataframe: pd.DataFrame, field_map: dict[str, str], findings: list[Finding]) -> list[ChartSpec]:
    charts: list[ChartSpec] = []
    for finding in findings:
        chart = None
        if finding.type in {FindingType.TREND_DROP, FindingType.TREND_GROWTH, FindingType.ANOMALY}:
            chart = _build_trend_chart(dataframe, field_map, finding)
        elif finding.type == FindingType.SEGMENT_UNDERPERFORMANCE:
            chart = _build_segment_chart(dataframe, field_map, finding)
        elif finding.type == FindingType.FUNNEL_DROPOFF:
            chart = _build_funnel_chart(dataframe, field_map, finding)

        if chart:
            charts.append(chart)
        if len(charts) == 5:
            break

    return charts


def build_kpis(kpis: list[dict[str, Any]]) -> list[KPI]:
    return [KPI(**kpi) for kpi in kpis[:8]]
