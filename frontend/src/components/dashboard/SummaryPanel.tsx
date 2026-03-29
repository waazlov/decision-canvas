import type { ExecutiveSummary } from "../../types/contracts";

export function SummaryPanel({ summary }: { summary: ExecutiveSummary }) {
  return (
    <section className="surface-card summary-panel">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Executive summary</p>
          <h2>Decision brief</h2>
        </div>
      </div>

      <div className="summary-panel__content">
        <div className="summary-panel__block">
          <h3>What happened</h3>
          <p>{summary.what_happened}</p>
        </div>
        <div className="summary-panel__block">
          <h3>Why it likely happened</h3>
          <p>{summary.why_it_likely_happened}</p>
        </div>
        {summary.what_to_do_next.length > 0 ? (
          <div className="summary-panel__block">
            <h3>What to do next</h3>
            <ul className="summary-list">
              {summary.what_to_do_next.slice(0, 3).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {summary.assumptions.length > 0 ? (
          <div className="summary-panel__block">
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
