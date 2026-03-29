from __future__ import annotations

from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_numeric_dtype,
)

from app.models.dataset import (
    ColumnProfile,
    DataIssueSeverity,
    DataQualityIssue,
    DataQualityIssueType,
    DatasetProfile,
    DetectedColumnType,
)
from app.services.semantic_inference import (
    infer_business_field,
    infer_candidate_dimensions,
    infer_candidate_metrics,
    infer_semantic_role,
)


def _detect_type(series: pd.Series) -> DetectedColumnType:
    non_null = series.dropna()
    if non_null.empty:
        return DetectedColumnType.UNKNOWN
    if is_bool_dtype(series):
        return DetectedColumnType.BOOLEAN
    if is_integer_dtype(series):
        return DetectedColumnType.INTEGER
    if is_float_dtype(series):
        return DetectedColumnType.FLOAT
    if is_datetime64_any_dtype(series):
        return DetectedColumnType.DATETIME

    if series.dtype == "object":
        parsed_dates = pd.to_datetime(non_null, errors="coerce", utc=False, format="mixed")
        parse_rate = parsed_dates.notna().mean()
        if parse_rate >= 0.9:
            return DetectedColumnType.DATE

        numeric_cast = pd.to_numeric(non_null, errors="coerce")
        numeric_rate = numeric_cast.notna().mean()
        if numeric_rate >= 0.9:
            whole_numbers = numeric_cast.dropna().apply(float.is_integer).mean()
            return DetectedColumnType.INTEGER if whole_numbers >= 0.95 else DetectedColumnType.FLOAT

    return DetectedColumnType.STRING


def _sample_values(series: pd.Series) -> list[str]:
    samples = series.dropna().astype(str).head(5).tolist()
    return [value[:60] for value in samples]


def _normalize_preview_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            return str(value)
    return value.item() if hasattr(value, "item") else value


def _derive_assumptions(dataframe: pd.DataFrame) -> list[str]:
    assumptions: list[str] = []
    columns_lower = {column.lower(): column for column in dataframe.columns}

    if "conversion_rate" not in columns_lower:
        if {"orders", "sessions"}.issubset(columns_lower):
            assumptions.append(
                "conversion_rate can be derived as orders / sessions because no explicit conversion column exists."
            )

    if "date" not in columns_lower:
        temporal_columns = [
            column for column in dataframe.columns if infer_business_field(column) == "date"
        ]
        if temporal_columns:
            assumptions.append(
                f"'{temporal_columns[0]}' is treated as the primary time dimension based on column naming."
            )

    return assumptions


def _build_quality_issues(dataframe: pd.DataFrame, detected_types: dict[str, DetectedColumnType]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    row_count = len(dataframe.index)

    duplicate_rows = int(dataframe.duplicated().sum())
    if duplicate_rows:
        issues.append(
            DataQualityIssue(
                type=DataQualityIssueType.DUPLICATES,
                severity=DataIssueSeverity.MEDIUM,
                message=f"{duplicate_rows} duplicate rows detected.",
            )
        )

    for column in dataframe.columns:
        series = dataframe[column]
        null_pct = round(float(series.isna().mean() * 100), 2)
        if null_pct > 0:
            severity = DataIssueSeverity.HIGH if null_pct >= 20 else DataIssueSeverity.MEDIUM
            issues.append(
                DataQualityIssue(
                    type=DataQualityIssueType.MISSING_VALUES,
                    column=column,
                    severity=severity,
                    message=f"{null_pct}% of rows have missing values in '{column}'.",
                )
            )

        if detected_types[column] == DetectedColumnType.STRING:
            numeric_parse_rate = pd.to_numeric(series.dropna(), errors="coerce").notna().mean() if series.dropna().size else 0
            if 0.2 <= numeric_parse_rate <= 0.8:
                issues.append(
                    DataQualityIssue(
                        type=DataQualityIssueType.MIXED_TYPES,
                        column=column,
                        severity=DataIssueSeverity.MEDIUM,
                        message=f"'{column}' appears to contain mixed numeric and text values.",
                    )
                )

        unique_count = int(series.nunique(dropna=True))
        if row_count and unique_count / row_count > 0.95 and not is_numeric_dtype(series):
            issues.append(
                DataQualityIssue(
                    type=DataQualityIssueType.HIGH_CARDINALITY,
                    column=column,
                    severity=DataIssueSeverity.LOW,
                    message=f"'{column}' has very high cardinality and may behave like an identifier.",
                )
            )

    return issues


def profile_dataset(dataframe: pd.DataFrame, dataset_name: str) -> DatasetProfile:
    working_frame = dataframe.copy()
    row_count = len(working_frame.index)
    detected_types: dict[str, DetectedColumnType] = {}
    column_profiles: list[ColumnProfile] = []
    candidate_column_tuples: list[tuple[str, str, Any]] = []

    for column in working_frame.columns:
        series = working_frame[column]
        detected_type = _detect_type(series)
        detected_types[column] = detected_type

        if detected_type in {DetectedColumnType.DATE, DetectedColumnType.DATETIME} and not is_datetime64_any_dtype(series):
            working_frame[column] = pd.to_datetime(series, errors="coerce", format="mixed")
            series = working_frame[column]

        semantic_role = infer_semantic_role(
            column_name=column,
            detected_type=detected_type.value,
            unique_count=int(series.nunique(dropna=True)),
            row_count=row_count,
        )

        column_profiles.append(
            ColumnProfile(
                name=column,
                detected_type=detected_type,
                semantic_role=semantic_role,
                null_pct=round(float(series.isna().mean() * 100), 2),
                unique_count=int(series.nunique(dropna=True)),
                sample_values=_sample_values(series),
            )
        )
        candidate_column_tuples.append((column, detected_type.value, semantic_role))

    preview_rows = [
        {column: _normalize_preview_value(value) for column, value in row.items()}
        for row in working_frame.head(8).to_dict(orient="records")
    ]

    return DatasetProfile(
        dataset_name=dataset_name,
        row_count=row_count,
        column_count=len(working_frame.columns),
        preview_rows=preview_rows,
        columns=column_profiles,
        candidate_metrics=infer_candidate_metrics(candidate_column_tuples),
        candidate_dimensions=infer_candidate_dimensions(candidate_column_tuples),
        data_quality_issues=_build_quality_issues(working_frame, detected_types),
        assumptions=_derive_assumptions(working_frame),
    )
