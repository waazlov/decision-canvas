from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_upload_to_dashboard_api_flow() -> None:
    csv_path = Path(__file__).resolve().parents[2] / "data" / "ecommerce_demo.csv"
    client = TestClient(app)

    with csv_path.open("rb") as csv_file:
        response = client.post(
            "/analysis/dashboard",
            files={"file": ("ecommerce_demo.csv", csv_file, "text/csv")},
            data={"question": "Why did conversion drop last month?"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dashboard_title"] == "Why Did Conversion Drop Last Month"
    assert payload["findings"]
    assert 1 <= len(payload["charts"]) <= 5
