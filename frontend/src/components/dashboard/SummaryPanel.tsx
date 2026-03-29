import type { ExecutiveSummary } from "../../types/contracts";

export function SummaryPanel({ summary }: { summary: ExecutiveSummary }) {
  return (
    <section className="surface-card summary-panel">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Executive summary</p>
          <h2>Decision-ready narrative</h2>
        </div>
      </div>

      <div className="summary-panel__content">
        <div>
          <h3>What happened</h3>
          <p>{summary.what_happened}</p>
        </div>
        <div>
          <h3>Why it likely happened</h3>
          <p>{summary.why_it_likely_happened}</p>
        </div>
        {summary.assumptions.length > 0 ? (
          <div>
            <h3>Assumptions</h3>
            <ul className="summary-list">
              {summary.assumptions.slice(0, 2).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  );
}
