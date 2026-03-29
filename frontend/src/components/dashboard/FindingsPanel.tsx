import type { Finding } from "../../types/contracts";

export function FindingsPanel({ findings }: { findings: Finding[] }) {
  return (
    <section className="surface-card findings-panel">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Supporting findings</p>
          <h2>What else matters</h2>
        </div>
      </div>

      {findings.length === 0 ? (
        <div className="empty-panel">
          <p>No high-confidence findings yet for this question.</p>
        </div>
      ) : (
        <div className="finding-list">
          {findings.slice(0, 4).map((finding) => (
            <article className="finding-card" key={finding.id}>
              <div className="finding-card__header">
                <div>
                  <p className="finding-card__eyebrow">{finding.type.replace(/_/g, " ")}</p>
                  <h3>{finding.title}</h3>
                </div>
                <span className={`pill pill--${finding.confidence}`}>
                  {finding.confidence} confidence
                </span>
              </div>
              <p>{finding.explanation}</p>
              {finding.recommended_action ? (
                <p className="finding-card__action">{finding.recommended_action}</p>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
