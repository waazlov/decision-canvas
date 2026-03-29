from __future__ import annotations

from enum import Enum

from pydantic import Field

from app.models.base import StrictBaseModel
from app.models.findings import ConfidenceLevel


class QuestionIntent(str, Enum):
    TREND_ANALYSIS = "trend_analysis"
    SEGMENT_BEST = "segment_best"
    SEGMENT_WORST = "segment_worst"
    ANOMALY_DETECTION = "anomaly_detection"
    FUNNEL_DROPOFF = "funnel_dropoff"
    METRIC_COMPARISON = "metric_comparison"
    OVERVIEW = "overview"


class QuestionDirection(str, Enum):
    BEST = "best"
    WORST = "worst"
    DROP = "drop"
    GROWTH = "growth"
    INCREASE = "increase"
    DECREASE = "decrease"
    COMPARE = "compare"
    NEUTRAL = "neutral"


class QuestionTimeScope(str, Enum):
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    WEEK_OVER_WEEK = "week_over_week"
    MONTH_OVER_MONTH = "month_over_month"
    RECENT = "recent"
    OVER_TIME = "over_time"
    ALL_TIME = "all_time"
    UNSPECIFIED = "unspecified"


class QuestionInterpretation(StrictBaseModel):
    raw_question: str
    intent: QuestionIntent
    requested_metric: str | None = None
    requested_dimension: str | None = None
    metric: str | None = None
    dimension: str | None = None
    direction: QuestionDirection = QuestionDirection.NEUTRAL
    time_scope: QuestionTimeScope = QuestionTimeScope.UNSPECIFIED
    comparison_targets: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel
    fallback_used: bool = False
    notes: list[str] = Field(default_factory=list)


class AnalysisStep(str, Enum):
    TREND = "trend"
    SEGMENT_RANKING = "segment_ranking"
    ANOMALY = "anomaly"
    FUNNEL = "funnel"
    OVERVIEW = "overview"


class AnalysisPlan(StrictBaseModel):
    intent: QuestionIntent
    metric: str | None = None
    dimension: str | None = None
    direction: QuestionDirection = QuestionDirection.NEUTRAL
    time_scope: QuestionTimeScope = QuestionTimeScope.UNSPECIFIED
    comparison_targets: list[str] = Field(default_factory=list)
    steps: list[AnalysisStep] = Field(default_factory=list)
    fallback_used: bool = False
    notes: list[str] = Field(default_factory=list)
