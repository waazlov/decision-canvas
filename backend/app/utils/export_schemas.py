from __future__ import annotations

import json
from pathlib import Path

from app.models.charts import ChartSpec
from app.models.dashboard import DashboardPayload, ExecutiveSummary
from app.models.dataset import DatasetProfile
from app.models.findings import Finding


SCHEMA_EXPORTS = {
    "dataset-profile.schema.json": DatasetProfile,
    "finding.schema.json": Finding,
    "chart-spec.schema.json": ChartSpec,
    "executive-summary.schema.json": ExecutiveSummary,
    "dashboard.schema.json": DashboardPayload,
}


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    schema_dir = root / "shared" / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)

    for filename, model in SCHEMA_EXPORTS.items():
        schema_path = schema_dir / filename
        schema_path.write_text(
            json.dumps(model.model_json_schema(), indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
