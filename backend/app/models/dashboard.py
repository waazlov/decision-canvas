from __future__ import annotations

from pydantic import Field

from app.models.base import StrictBaseModel
from app.models.charts import ChartSpec, KPI
from app.models.dataset import DatasetProfile
from app.models.findings import Finding
from app.models.question import QuestionInterpretation


class ExecutiveSummary(StrictBaseModel):
    what_happened: str
    why_it_likely_happened: str
    what_to_do_next: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)


class DashboardPayload(StrictBaseModel):
    dashboard_title: str
    question: str
    interpreted_question: QuestionInterpretation
    dataset_profile: DatasetProfile
    kpis: list[KPI] = Field(default_factory=list, max_length=8)
    findings: list[Finding] = Field(default_factory=list, max_length=10)
    charts: list[ChartSpec] = Field(default_factory=list, max_length=5)
    executive_summary: ExecutiveSummary
