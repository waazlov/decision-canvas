from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.services.profiling_service import profile_dataset


def test_profile_dataset_infers_expected_business_fields() -> None:
    dataframe = pd.read_csv(
        Path(__file__).resolve().parents[2] / "data" / "ecommerce_demo.csv"
    )

    profile = profile_dataset(dataframe, dataset_name="ecommerce_demo.csv")

    assert profile.row_count == 16
    assert "revenue" in profile.candidate_metrics
    assert "device" in profile.candidate_dimensions
    assert any(column.name == "date" and column.semantic_role == "time_dimension" for column in profile.columns)
