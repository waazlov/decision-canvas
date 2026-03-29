from __future__ import annotations

from enum import Enum

from pydantic import Field

from app.models.base import StrictBaseModel


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FindingType(str, Enum):
    TREND_DROP = "trend_drop"
    TREND_GROWTH = "trend_growth"
    SEGMENT_OUTPERFORMANCE = "segment_outperformance"
    SEGMENT_UNDERPERFORMANCE = "segment_underperformance"
    ANOMALY = "anomaly"
    FUNNEL_DROPOFF = "funnel_dropoff"
    RELATIONSHIP = "relationship"


class TimeWindow(StrictBaseModel):
    current_start: str | None = None
    current_end: str | None = None
    comparison_start: str | None = None
    comparison_end: str | None = None


class Finding(StrictBaseModel):
    id: str
    type: FindingType
    title: str
    metric: str
    dimension: str | None = None
    segment: str | None = None
    time_window: TimeWindow | None = None
    value: float | None = None
    comparison_value: float | None = None
    magnitude_pct: float | None = None
    confidence: ConfidenceLevel
    explanation: str
    recommended_action: str
    evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
