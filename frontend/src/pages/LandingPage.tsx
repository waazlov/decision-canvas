import { useNavigate } from "react-router-dom";

import { BrandMark } from "../components/layout/BrandMark";
import { useWorkspace } from "../app/WorkspaceContext";

export function LandingPage() {
  const navigate = useNavigate();
  const { prepareDemoWorkspace } = useWorkspace();

  return (
    <div className="stack-xl">
      <section className="hero surface-card surface-card--hero">
        <div className="hero__content">
          <div className="hero__badge">
            <BrandMark mode="icon" />
            <span>Decision-ready analytics for lean teams</span>
          </div>
          <p className="eyebrow">AI analytics copilot</p>
          <h1>From data to decisions, instantly.</h1>
          <p className="hero__lede">
            Upload business data, uncover what changed, and generate decision-ready dashboards,
            insights, and recommendations.
          </p>
          <div className="hero__actions">
            <button className="button button--primary" type="button" onClick={() => navigate("/workspace")}>
              Upload dataset
            </button>
            <button
              className="button button--secondary"
              type="button"
              onClick={async () => {
                await prepareDemoWorkspace();
                navigate("/workspace");
              }}
            >
              Try demo
            </button>
          </div>
          <div className="hero__metrics">
            <div className="hero-metric">
              <strong>Upload</strong>
              <span>CSV business data</span>
            </div>
            <div className="hero-metric">
              <strong>Analyze</strong>
              <span>Deterministic drivers and anomalies</span>
            </div>
            <div className="hero-metric">
              <strong>Present</strong>
              <span>Executive-ready dashboard output</span>
            </div>
          </div>
        </div>

        <div className="hero__visual surface-card">
          <div className="hero-visual__header">
            <span className="pill pill--neutral">Live decision brief</span>
            <span className="hero-visual__label">DecisionCanvas</span>
          </div>
          <div className="hero-visual__kpis">
            <div>
              <span>Conversion</span>
              <strong>4.3%</strong>
            </div>
            <div>
              <span>Revenue</span>
              <strong>$518k</strong>
            </div>
            <div>
              <span>Largest driver</span>
              <strong>Mobile checkout</strong>
            </div>
          </div>
          <div className="hero-visual__chart">
            <div className="hero-visual__grid" />
            <svg aria-hidden="true" viewBox="0 0 280 120">
              <path
                d="M0 88L42 70L82 73L124 38L164 55L206 60L246 28L280 22"
                fill="none"
                stroke="var(--accent-violet)"
                strokeLinecap="round"
                strokeWidth="4"
              />
              <circle cx="246" cy="28" fill="var(--accent)" r="5" />
            </svg>
          </div>
          <div className="hero-visual__insight">
            <p>What changed</p>
            <strong>Conversion declined in the latest period, led by mobile checkout friction.</strong>
          </div>
        </div>
      </section>

      <section className="landing-section">
        <div className="section-heading landing-section__heading">
          <div>
            <p className="section-heading__eyebrow">How it works</p>
            <h2>Structured analysis, not generic chat output</h2>
          </div>
          <p className="landing-section__copy">
            DecisionCanvas profiles the data, maps the question to a supported analysis path, and
            assembles a presentation-ready dashboard with clear assumptions.
          </p>
        </div>
        <div className="feature-strip">
          <article className="surface-card feature-card">
            <span className="feature-card__step">01</span>
            <h2>Profile the dataset</h2>
            <p>Detect metrics, dimensions, data quality issues, and likely business fields in seconds.</p>
          </article>
          <article className="surface-card feature-card">
            <span className="feature-card__step">02</span>
            <h2>Surface what changed</h2>
            <p>Run deterministic analysis for trends, segment performance, anomalies, and funnel loss.</p>
          </article>
          <article className="surface-card feature-card">
            <span className="feature-card__step">03</span>
            <h2>Present a decision brief</h2>
            <p>Package the findings into charts, summaries, and next actions that leadership can use.</p>
          </article>
        </div>
      </section>

      <section className="landing-grid">
        <article className="surface-card value-card">
          <p className="section-heading__eyebrow">What you get</p>
          <h2>Dashboard output built for fast business review</h2>
          <ul className="summary-list">
            <li>Schema-aware KPI row and key metrics</li>
            <li>Prioritized findings with confidence and evidence</li>
            <li>Approved chart templates chosen to match the question</li>
            <li>Executive summary and recommended actions</li>
          </ul>
        </article>
        <article className="surface-card value-card value-card--accent">
          <p className="section-heading__eyebrow">Why it matters</p>
          <h2>Useful before a BI team exists, credible when one does.</h2>
          <p>
            The product is designed for operators, PMs, analysts, and strategy teams who need a
            decision-ready view fast, without waiting on a custom analytics workflow.
          </p>
          <div className="value-card__callout">
            Strongest demo path: sample dataset + "Why did conversion drop last month?"
          </div>
        </article>
      </section>
    </div>
  );
}
