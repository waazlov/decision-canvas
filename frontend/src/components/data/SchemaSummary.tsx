import type { DatasetProfile } from "../../types/contracts";

interface SchemaSummaryProps {
  profile: DatasetProfile | null;
}

export function SchemaSummary({ profile }: SchemaSummaryProps) {
  return (
    <section className="surface-card surface-card--contained">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Schema</p>
          <h2>Detected business structure</h2>
        </div>
      </div>

      <div className="schema-summary">
        <div className="schema-group">
          <h3>Candidate metrics</h3>
          <div className="tag-list">
            {(profile?.candidate_metrics ?? []).map((metric) => (
              <span className="tag" key={metric}>
                {metric}
              </span>
            ))}
            {!profile?.candidate_metrics.length ? <span className="tag tag--muted">Awaiting upload</span> : null}
          </div>
        </div>

        <div className="schema-group">
          <h3>Candidate dimensions</h3>
          <div className="tag-list">
            {(profile?.candidate_dimensions ?? []).map((dimension) => (
              <span className="tag" key={dimension}>
                {dimension}
              </span>
            ))}
            {!profile?.candidate_dimensions.length ? <span className="tag tag--muted">Awaiting upload</span> : null}
          </div>
        </div>

        <div className="schema-group">
          <h3>Quality notes</h3>
          <ul className="summary-list">
            {(profile?.data_quality_issues ?? []).slice(0, 4).map((issue) => (
              <li key={`${issue.type}-${issue.column ?? "all"}`}>{issue.message}</li>
            ))}
            {!profile?.data_quality_issues.length ? (
              <li>No material data quality issues surfaced yet.</li>
            ) : null}
          </ul>
        </div>
      </div>
    </section>
  );
}
