import type { Finding, ExecutiveSummary } from "../../types/contracts";

interface RecommendationsPanelProps {
  summary: ExecutiveSummary;
  findings: Finding[];
}

export function RecommendationsPanel({
  summary,
  findings,
}: RecommendationsPanelProps) {
  const recommendations = Array.from(
    new Set([...summary.what_to_do_next, ...findings.map((finding) => finding.recommended_action)]),
  ).slice(0, 5);

  return (
    <section className="surface-card">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Recommended actions</p>
          <h2>Suggested next moves</h2>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <div className="empty-panel">
          <p>No recommendation is available until the analysis surfaces evidence-backed findings.</p>
        </div>
      ) : (
        <ol className="recommendation-list">
          {recommendations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
      )}
    </section>
  );
}
