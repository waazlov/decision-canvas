from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from app.models.base import StrictBaseModel


class DetectedColumnType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    UNKNOWN = "unknown"


class SemanticRole(str, Enum):
    TIME_DIMENSION = "time_dimension"
    DIMENSION = "dimension"
    METRIC = "metric"
    IDENTIFIER = "identifier"
    FUNNEL_STAGE = "funnel_stage"
    UNKNOWN = "unknown"


class DataIssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DataQualityIssueType(str, Enum):
    MISSING_VALUES = "missing_values"
    MIXED_TYPES = "mixed_types"
    DUPLICATES = "duplicates"
    DATE_PARSE = "date_parse"
    HIGH_CARDINALITY = "high_cardinality"
    UNSUPPORTED = "unsupported"


class ColumnProfile(StrictBaseModel):
    name: str
    detected_type: DetectedColumnType
    semantic_role: SemanticRole = SemanticRole.UNKNOWN
    null_pct: float = Field(ge=0, le=100)
    unique_count: int = Field(ge=0)
    sample_values: list[str] = Field(default_factory=list, max_length=5)


class DataQualityIssue(StrictBaseModel):
    type: DataQualityIssueType
    column: str | None = None
    severity: DataIssueSeverity
    message: str


class DatasetProfile(StrictBaseModel):
    dataset_name: str
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    preview_rows: list[dict[str, Any]] = Field(default_factory=list, max_length=10)
    columns: list[ColumnProfile] = Field(default_factory=list)
    candidate_metrics: list[str] = Field(default_factory=list)
    candidate_dimensions: list[str] = Field(default_factory=list)
    data_quality_issues: list[DataQualityIssue] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
