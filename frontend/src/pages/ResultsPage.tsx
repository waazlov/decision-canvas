import { Link } from "react-router-dom";

import { PageHeader } from "../components/layout/PageHeader";
import { FindingsPanel } from "../components/dashboard/FindingsPanel";
import { KpiGrid } from "../components/dashboard/KpiGrid";
import { SummaryPanel } from "../components/dashboard/SummaryPanel";
import { ChartsSection } from "../components/dashboard/ChartsSection";
import { RecommendationsPanel } from "../components/dashboard/RecommendationsPanel";
import { HeroInsightCard } from "../components/dashboard/HeroInsightCard";
import { useWorkspace } from "../app/WorkspaceContext";
import { sampleDashboard } from "../types/mockData";

function formatLabel(value: string | null | undefined) {
  if (!value) {
    return null;
  }
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function ResultsPage() {
  const { dashboard, mode, profile } = useWorkspace();
  const activeDashboard = dashboard ?? sampleDashboard;
  const hasCharts = activeDashboard.charts.length > 0;
  const hasFindings = activeDashboard.findings.length > 0;
  const leadFinding = activeDashboard.findings[0] ?? null;
  const supportingFindings = activeDashboard.findings.slice(1);
  const interpretation = activeDashboard.interpreted_question;
  const interpretationParts = [
    `Detected intent: ${formatLabel(interpretation.intent)}`,
    interpretation.metric ? `Metric: ${formatLabel(interpretation.metric)}` : null,
    !interpretation.metric && interpretation.requested_metric
      ? `Requested metric: ${formatLabel(interpretation.requested_metric)}`
      : null,
    interpretation.dimension ? `Dimension: ${formatLabel(interpretation.dimension)}` : null,
    !interpretation.dimension && interpretation.requested_dimension
      ? `Requested dimension: ${formatLabel(interpretation.requested_dimension)}`
      : null,
    interpretation.time_scope !== "unspecified"
      ? `Time scope: ${formatLabel(interpretation.time_scope)}`
      : null,
    interpretation.fallback_used ? "Fallback path used" : null,
  ].filter(Boolean);

  return (
    <div className="stack-lg">
      <PageHeader
        eyebrow="Results dashboard"
        title={activeDashboard.dashboard_title}
        description={activeDashboard.question}
        actions={
          dashboard ? undefined : (
            <Link className="button button--secondary" to="/workspace">
              Run live analysis
            </Link>
          )
        }
      />

      {mode === "demo" ? (
        <div className="status-banner">
          Demo mode is active. This dashboard is rendered from bundled sample output and does not require a live backend.
        </div>
      ) : !dashboard ? (
        <div className="status-banner">
          Showing the sample dashboard layout. Upload a dataset and run analysis to see live results.
        </div>
      ) : null}

      <section className="surface-card dataset-context">
        <div>
          <p className="section-heading__eyebrow">Question interpretation</p>
          <h2>{interpretationParts.join(" | ")}</h2>
        </div>
        {interpretation.notes.length > 0 ? (
          <div className="dataset-context__stats dataset-context__stats--stacked">
            {interpretation.notes.map((note) => (
              <span key={note}>{note}</span>
            ))}
          </div>
        ) : null}
      </section>

      <KpiGrid kpis={activeDashboard.kpis} />
      <HeroInsightCard finding={leadFinding} />

      {profile ? (
        <section className="surface-card dataset-context">
          <div>
            <p className="section-heading__eyebrow">Analysis context</p>
            <h2>{profile.dataset_name}</h2>
          </div>
          <div className="dataset-context__stats">
            <span>{profile.row_count.toLocaleString()} rows</span>
            <span>{profile.candidate_metrics.length} metrics</span>
            <span>{profile.candidate_dimensions.length} dimensions</span>
          </div>
        </section>
      ) : null}

      {hasCharts ? (
        <ChartsSection charts={activeDashboard.charts} />
      ) : (
        <section className="surface-card">
          <div className="section-heading">
            <div>
              <p className="section-heading__eyebrow">Charts</p>
              <h2>No visualizations were recommended</h2>
            </div>
          </div>
          <div className="empty-panel">
            <p>
              The current analysis did not produce enough structured evidence for a chart. Try a
              more specific question or verify the dataset includes time, segment, and metric
              fields.
            </p>
          </div>
        </section>
      )}

      <div className="results-top-grid results-top-grid--priority">
        <FindingsPanel findings={supportingFindings} />
        <SummaryPanel summary={activeDashboard.executive_summary} />
      </div>

      <RecommendationsPanel
        findings={activeDashboard.findings}
        summary={activeDashboard.executive_summary}
      />

      {!hasFindings ? (
        <section className="surface-card">
          <div className="section-heading">
            <div>
              <p className="section-heading__eyebrow">Coverage note</p>
              <h2>DecisionCanvas did not surface strong findings</h2>
            </div>
          </div>
          <div className="empty-panel">
            <p>
              This dataset was uploaded successfully, but the current question did not map cleanly
              to a high-confidence insight. Use a question tied to trends, segments, anomalies, or
              funnel performance.
            </p>
          </div>
        </section>
      ) : null}
    </div>
  );
}
