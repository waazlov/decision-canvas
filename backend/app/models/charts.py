from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from app.models.base import StrictBaseModel


class ChartTemplate(str, Enum):
    KPI_CARD = "kpi_card"
    LINE = "line"
    BAR = "bar"
    GROUPED_BAR = "grouped_bar"
    SCATTER = "scatter"
    FUNNEL = "funnel"
    HEATMAP = "heatmap"


class ValueFormat(str, Enum):
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    INTEGER = "integer"
    STRING = "string"


class AxisSpec(StrictBaseModel):
    field: str
    label: str
    format: ValueFormat = ValueFormat.NUMBER


class ChartSeries(StrictBaseModel):
    name: str
    field: str


class ChartAnnotation(StrictBaseModel):
    label: str
    x_value: str | float | int | None = None
    y_value: float | int | None = None


class ChartSpec(StrictBaseModel):
    id: str
    template: ChartTemplate
    title: str
    subtitle: str | None = None
    reason_for_selection: str
    x_axis: AxisSpec | None = None
    y_axis: AxisSpec | None = None
    series: list[ChartSeries] = Field(default_factory=list)
    data: list[dict[str, Any]] = Field(default_factory=list, max_length=500)
    annotation: ChartAnnotation | None = None


class KPI(StrictBaseModel):
    label: str
    value: float | int | str
    format: ValueFormat
    delta_pct: float | None = None
    comparison_label: str | None = None
