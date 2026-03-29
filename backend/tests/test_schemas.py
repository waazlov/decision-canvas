from __future__ import annotations

from app.models.charts import ChartSpec
from app.models.dashboard import DashboardPayload, ExecutiveSummary
from app.models.dataset import DatasetProfile
from app.models.findings import Finding


def test_models_export_object_json_schemas() -> None:
    for model in (DatasetProfile, Finding, ChartSpec, ExecutiveSummary, DashboardPayload):
        schema = model.model_json_schema()
        assert schema["type"] == "object"
