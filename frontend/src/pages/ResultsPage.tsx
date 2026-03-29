import { Link } from "react-router-dom";

import { PageHeader } from "../components/layout/PageHeader";
import { FindingsPanel } from "../components/dashboard/FindingsPanel";
import { KpiGrid } from "../components/dashboard/KpiGrid";
import { SummaryPanel } from "../components/dashboard/SummaryPanel";
import { ChartsSection } from "../components/dashboard/ChartsSection";
import { RecommendationsPanel } from "../components/dashboard/RecommendationsPanel";
import { useWorkspace } from "../app/WorkspaceContext";
import { sampleDashboard } from "../types/mockData";

export function ResultsPage() {
  const { dashboard, profile } = useWorkspace();
  const activeDashboard = dashboard ?? sampleDashboard;
  const hasCharts = activeDashboard.charts.length > 0;
  const hasFindings = activeDashboard.findings.length > 0;

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

      {!dashboard ? (
        <div className="status-banner">
          Showing the sample dashboard layout. Upload a dataset and run analysis to see live results.
        </div>
      ) : null}

      <KpiGrid kpis={activeDashboard.kpis} />

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

      <div className="results-top-grid results-top-grid--priority">
        <FindingsPanel findings={activeDashboard.findings} />
        <SummaryPanel summary={activeDashboard.executive_summary} />
      </div>

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
