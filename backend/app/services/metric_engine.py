from __future__ import annotations

from collections import OrderedDict
from typing import Any

import numpy as np
import pandas as pd

from app.services.semantic_inference import BUSINESS_FIELD_SYNONYMS, infer_business_field


def infer_field_map(dataframe: pd.DataFrame) -> dict[str, str]:
    field_map: "OrderedDict[str, str]" = OrderedDict()

    for column in dataframe.columns:
        business_field = infer_business_field(column)
        if business_field and business_field not in field_map:
            field_map[business_field] = column

    lower_columns = {column.lower(): column for column in dataframe.columns}
    if "date" not in field_map:
        for alias in BUSINESS_FIELD_SYNONYMS["date"]:
            if alias in lower_columns:
                field_map["date"] = lower_columns[alias]
                break

    return dict(field_map)


def prepare_analysis_frame(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str], list[str]]:
    working_frame = dataframe.copy()
    assumptions: list[str] = []
    field_map = infer_field_map(working_frame)

    if "date" in field_map:
        date_column = field_map["date"]
        working_frame[date_column] = pd.to_datetime(working_frame[date_column], errors="coerce")
        if working_frame[date_column].notna().any():
            assumptions.append(f"'{date_column}' is used as the primary time dimension.")

    for business_field in ("revenue", "orders", "sessions"):
        if business_field in field_map:
            column = field_map[business_field]
            working_frame[column] = pd.to_numeric(working_frame[column], errors="coerce")

    if "conversion" not in field_map and {"orders", "sessions"}.issubset(field_map):
        orders_column = field_map["orders"]
        sessions_column = field_map["sessions"]
        safe_sessions = working_frame[sessions_column].replace({0: np.nan})
        working_frame["derived_conversion_rate"] = working_frame[orders_column] / safe_sessions
        field_map["conversion"] = "derived_conversion_rate"
        assumptions.append(
            "conversion_rate is derived as orders / sessions because no explicit conversion column exists."
        )
    elif "conversion" in field_map:
        conversion_column = field_map["conversion"]
        working_frame[conversion_column] = pd.to_numeric(working_frame[conversion_column], errors="coerce")

    if "aov" not in field_map and {"revenue", "orders"}.issubset(field_map):
        revenue_column = field_map["revenue"]
        orders_column = field_map["orders"]
        safe_orders = working_frame[orders_column].replace({0: np.nan})
        working_frame["derived_aov"] = working_frame[revenue_column] / safe_orders
        field_map["aov"] = "derived_aov"
        assumptions.append(
            "aov is derived as revenue / orders because no explicit average order value column exists."
        )
    elif "aov" in field_map:
        aov_column = field_map["aov"]
        working_frame[aov_column] = pd.to_numeric(working_frame[aov_column], errors="coerce")

    return working_frame, field_map, assumptions


def pick_primary_metric(field_map: dict[str, str]) -> str | None:
    for business_field in ("revenue", "conversion", "orders", "sessions", "aov"):
        if business_field in field_map:
            return business_field
    return None


def pick_metric_for_question(field_map: dict[str, str], question: str) -> str | None:
    question_lower = question.lower()
    priority_by_keyword = (
        ("conversion", ("conversion", "convert", "checkout")),
        ("revenue", ("revenue", "sales", "gmv")),
        ("orders", ("orders", "purchases")),
        ("sessions", ("sessions", "traffic", "visits")),
        ("aov", ("aov", "average order value", "avg order value")),
    )

    for metric, keywords in priority_by_keyword:
        if metric in field_map and any(keyword in question_lower for keyword in keywords):
            return metric

    return pick_primary_metric(field_map)


def metric_format_for_field(business_field: str) -> str:
    if business_field in {"revenue", "aov"}:
        return "currency"
    if business_field == "conversion":
        return "percentage"
    if business_field in {"orders", "sessions"}:
        return "integer"
    return "number"


def summarize_kpis(
    dataframe: pd.DataFrame,
    field_map: dict[str, str],
) -> list[dict[str, Any]]:
    kpis: list[dict[str, Any]] = []
    date_column = field_map.get("date")

    for business_field in ("revenue", "orders", "sessions", "conversion", "aov"):
        column = field_map.get(business_field)
        if not column or column not in dataframe.columns:
            continue

        series = dataframe[column].dropna()
        if series.empty:
            continue

        value = float(series.mean()) if business_field in {"conversion", "aov"} else float(series.sum())
        delta_pct = None

        if date_column and dataframe[date_column].notna().any():
            dated = dataframe[[date_column, column]].dropna().sort_values(date_column)
            dated["period"] = dated[date_column].dt.to_period("M")
            period_summary = (
                dated.groupby("period")[column].mean()
                if business_field in {"conversion", "aov"}
                else dated.groupby("period")[column].sum()
            )
            if len(period_summary) >= 2:
                previous = float(period_summary.iloc[-2])
                current = float(period_summary.iloc[-1])
                if not pd.isna(previous) and previous != 0:
                    delta_pct = round(((current - previous) / previous) * 100, 2)
                value = current

        kpis.append(
            {
                "label": business_field.replace("_", " ").title(),
                "value": round(value, 4) if business_field == "conversion" else round(value, 2),
                "format": metric_format_for_field(business_field),
                "delta_pct": delta_pct,
                "comparison_label": "vs prior period" if delta_pct is not None else None,
            }
        )

    return kpis
