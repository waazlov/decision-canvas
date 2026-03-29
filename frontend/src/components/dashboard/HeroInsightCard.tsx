import type { Finding } from "../../types/contracts";

export function HeroInsightCard({ finding }: { finding: Finding | null }) {
  if (!finding) {
    return null;
  }

  return (
    <section className="hero-insight surface-card">
      <div className="hero-insight__header">
        <div>
          <p className="section-heading__eyebrow">Primary insight</p>
          <h2>{finding.title}</h2>
        </div>
        <span className={`pill pill--${finding.confidence}`}>{finding.confidence} confidence</span>
      </div>

      <p className="hero-insight__lede">{finding.explanation}</p>

      {finding.recommended_action ? (
        <div className="hero-insight__action">
          <span>Recommended next move</span>
          <strong>{finding.recommended_action}</strong>
        </div>
      ) : null}
    </section>
  );
}
