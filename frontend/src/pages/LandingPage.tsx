import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <div className="stack-xl">
      <section className="hero surface-card surface-card--hero">
        <div className="hero__content">
          <p className="eyebrow">AI analytics copilot</p>
          <h1>From data to decisions instantly</h1>
          <p className="hero__lede">
            Upload business data, ask a high-value question, and get a structured executive dashboard with insights, charts, and actions.
          </p>
          <div className="hero__actions">
            <Link className="button button--primary" to="/workspace">
              Upload dataset
            </Link>
            <Link className="button button--secondary" to="/results">
              View dashboard layout
            </Link>
          </div>
        </div>
      </section>

      <section className="feature-strip">
        <article className="surface-card feature-card">
          <h2>Profile the data</h2>
          <p>Infer business fields, detect issues, and establish trustworthy analysis inputs.</p>
        </article>
        <article className="surface-card feature-card">
          <h2>Surface the drivers</h2>
          <p>Highlight trends, segment underperformance, anomalies, and funnel loss with confidence.</p>
        </article>
        <article className="surface-card feature-card">
          <h2>Present the decision</h2>
          <p>Package KPIs, charts, findings, and recommendations into a clean executive-ready dashboard.</p>
        </article>
      </section>
    </div>
  );
}
