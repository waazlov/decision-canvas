import type { Finding } from "../../types/contracts";

export function FindingsPanel({ findings }: { findings: Finding[] }) {
  return (
    <section className="surface-card">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Key findings</p>
          <h2>What matters most</h2>
        </div>
      </div>

      {findings.length === 0 ? (
        <div className="empty-panel">
          <p>No high-confidence findings yet for this question.</p>
        </div>
      ) : (
        <div className="finding-list">
          {findings.map((finding) => (
            <article className="finding-card" key={finding.id}>
              <div className="finding-card__header">
                <h3>{finding.title}</h3>
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
