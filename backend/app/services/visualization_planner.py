from __future__ import annotations

from typing import Any

import pandas as pd

from app.models.charts import AxisSpec, ChartAnnotation, ChartSeries, ChartSpec, ChartTemplate, KPI, ValueFormat
from app.models.findings import Finding, FindingType
from app.models.question import QuestionIntent, QuestionInterpretation
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


def _build_segment_chart(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
    finding: Finding,
    interpretation: QuestionInterpretation,
) -> ChartSpec | None:
    metric_column = field_map.get(finding.metric)
    segment_dimension = field_map.get(finding.dimension or "")
    if not metric_column or not finding.segment or not segment_dimension:
        return None

    grouped = dataframe[[segment_dimension, metric_column]].dropna().groupby(segment_dimension)[metric_column]
    aggregated = grouped.mean() if finding.metric in {"conversion", "aov"} else grouped.sum()
    chart_frame = aggregated.sort_values(ascending=False).reset_index()
    chart_frame.columns = ["x", "y"]

    if interpretation.intent == QuestionIntent.METRIC_COMPARISON and len(interpretation.comparison_targets) >= 2:
        requested_targets = []
        lookup = {target.lower(): target for target in interpretation.comparison_targets}
        for row in chart_frame.to_dict(orient="records"):
            key = str(row["x"]).lower()
            if key in lookup:
                requested_targets.append({"target": str(row["x"]), "value": row["y"]})
        if len(requested_targets) >= 2:
            comparison_data = [{"x": "Requested comparison"}]
            series: list[ChartSeries] = []
            for target in requested_targets[:2]:
                field_name = target["target"].replace(" ", "_").lower()
                comparison_data[0][field_name] = target["value"]
                series.append(ChartSeries(name=target["target"], field=field_name))

            return ChartSpec(
                id=f"chart_{finding.id}",
                template=ChartTemplate.GROUPED_BAR,
                title=f"{finding.metric.replace('_', ' ').title()} comparison",
                subtitle=finding.title,
                reason_for_selection="A grouped bar chart highlights the requested comparison targets clearly.",
                x_axis=AxisSpec(field="x", label="Comparison set", format=ValueFormat.STRING),
                y_axis=AxisSpec(
                    field=series[0].field,
                    label=finding.metric.replace("_", " ").title(),
                    format=_format_enum(finding.metric),
                ),
                series=series,
                data=comparison_data,
                annotation=ChartAnnotation(
                    label="Leading comparison target",
                    x_value="Requested comparison",
                    y_value=finding.value,
                ),
            )

    annotation_label = "Leading segment" if finding.type == FindingType.SEGMENT_OUTPERFORMANCE else "Weakest segment"

    return ChartSpec(
        id=f"chart_{finding.id}",
        template=ChartTemplate.BAR,
        title=f"{finding.metric.replace('_', ' ').title()} by {finding.dimension or 'segment'}",
        subtitle=finding.title,
        reason_for_selection="A bar chart makes segment performance easy to compare across peer groups.",
        x_axis=AxisSpec(
            field="x",
            label=(finding.dimension or "segment").replace("_", " ").title(),
            format=ValueFormat.STRING,
        ),
        y_axis=AxisSpec(field="y", label=finding.metric.replace("_", " ").title(), format=_format_enum(finding.metric)),
        series=[ChartSeries(name=finding.metric.replace("_", " ").title(), field="y")],
        data=chart_frame.to_dict(orient="records"),
        annotation=ChartAnnotation(label=annotation_label, x_value=finding.segment, y_value=finding.value),
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


def plan_charts(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
    findings: list[Finding],
    interpretation: QuestionInterpretation,
) -> list[ChartSpec]:
    charts: list[ChartSpec] = []
    for finding in findings:
        chart = None
        if finding.type in {FindingType.TREND_DROP, FindingType.TREND_GROWTH, FindingType.ANOMALY}:
            chart = _build_trend_chart(dataframe, field_map, finding)
        elif finding.type in {FindingType.SEGMENT_UNDERPERFORMANCE, FindingType.SEGMENT_OUTPERFORMANCE}:
            chart = _build_segment_chart(dataframe, field_map, finding, interpretation)
        elif finding.type == FindingType.FUNNEL_DROPOFF:
            chart = _build_funnel_chart(dataframe, field_map, finding)

        if chart:
            charts.append(chart)
        if len(charts) == 5:
            break

    return charts


def build_kpis(kpis: list[dict[str, Any]]) -> list[KPI]:
    return [KPI(**kpi) for kpi in kpis[:8]]
