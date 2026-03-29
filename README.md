# DecisionCanvas

DecisionCanvas turns raw business data into decision-ready dashboards, insights, and executive recommendations in minutes.

## Overview

DecisionCanvas is an analytics copilot for teams that need fast answers from business data without building a full analytics stack first. A user uploads a CSV, asks a business question in plain language, and receives a structured output: profiled data, KPI summaries, prioritized findings, recommended charts, an executive summary, and next-step actions.

It is built for e-commerce teams, product managers, growth analysts, and strategy teams that regularly need to answer questions like:

- Why did conversion drop last month?
- Which segments drive the most revenue?
- Where in the funnel are users dropping off?
- Which regions or categories underperform?

The product solves a common workflow gap: many teams have data, but not the time, tooling, or analytics coverage needed to quickly convert it into a clear business decision.

## Key Features

- Automated dataset profiling for CSV uploads, including type inference, candidate metrics, candidate dimensions, and data quality checks
- Deterministic business analysis for trends, segment underperformance, anomalies, and funnel drop-off
- Structured insight generation with confidence levels, assumptions, and uncertainty notes
- Decision recommendations tied to real business actions such as UX changes, targeting adjustments, pricing review, or retention investigation
- Adaptive dashboard generation that selects only approved visualization templates based on findings
- Schema-validated backend responses so the frontend renders trusted, predictable output instead of arbitrary AI code

## How It Works

1. Upload a CSV dataset.
2. DecisionCanvas profiles the data and infers business-relevant fields such as revenue, orders, sessions, date, device, region, and category.
3. The system validates quality and identifies usable metrics and dimensions.
4. The user asks a business question in natural language.
5. The backend runs deterministic analysis to evaluate trends, segment performance, anomalies, and funnel behavior.
6. Structured findings are generated with evidence, confidence, assumptions, and recommended actions.
7. The visualization planner maps those findings to approved chart templates.
8. The frontend renders a clean executive dashboard with KPIs, findings, charts, summary, and recommendations.

## Architecture

DecisionCanvas is organized as a schema-first analytics pipeline:

- Frontend: React + TypeScript + Vite
  Renders the landing page, analysis workspace, and results dashboard
- Backend: FastAPI + pandas + numpy
  Handles upload, profiling, deterministic analysis, report generation, and API delivery
- Analysis layer
  Separates profiling, metric inference, analysis, insight generation, and executive summary generation
- Visualization layer
  Converts findings into structured chart specifications using approved templates only
- Shared contracts
  Keeps frontend and backend aligned through strict JSON response shapes

## Example Output

For a question like "Why did conversion drop last month?", DecisionCanvas produces:

- KPI cards for revenue, orders, sessions, and conversion
- A prioritized finding such as a month-over-month conversion decline
- A chart selected to match that finding, such as a trend line or segment comparison
- An executive summary that explains what happened, why it likely happened, and what to do next
- Recommended actions such as reviewing mobile checkout friction, campaign quality, or segment mix

## Setup Instructions

### Backend

1. Use Python 3.11+.
2. From `backend/`, install dependencies:

```bash
python -m pip install -e .[dev]
```

3. Start the API:

```bash
python -m uvicorn app.main:app --reload
```

The backend runs on `http://localhost:8000`.

### Frontend

1. Use Node.js 20+.
2. From `frontend/`, install dependencies:

```bash
npm install
```

3. Start the frontend:

```bash
npm run dev
```

The frontend runs on `http://localhost:5173`.

### Demo Data

Use the sample dataset at [`data/ecommerce_demo.csv`](C:\Users\waazlov\Documents\Work\Codex Project\decision-canvas\data\ecommerce_demo.csv).

### Demo Mode

For the most reliable judging flow, use the **Use sample dataset** button in the workspace. The default question is already pre-filled:

`Why did conversion drop last month?`

This is the strongest demo path in the current MVP because it consistently produces KPI movement, a clear finding, a supporting chart, an executive summary, and a recommended action.

## Deployment

DecisionCanvas is set up for:

- Frontend on Vercel
- Backend on Render

### Backend Deployment on Render

This repo includes:

- [`backend/requirements.txt`](C:\Users\waazlov\Documents\Work\Codex Project\decision-canvas\backend\requirements.txt)
- [`backend/runtime.txt`](C:\Users\waazlov\Documents\Work\Codex Project\decision-canvas\backend\runtime.txt)
- [`render.yaml`](C:\Users\waazlov\Documents\Work\Codex Project\decision-canvas\render.yaml)

You can deploy with the Render blueprint or configure manually:

1. Push the repo to GitHub.
2. In Render, create a new Web Service from the repository.
3. Use these settings:

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/system/health`

4. Set environment variables:

- `PYTHON_VERSION=3.11.9`
- `CORS_ORIGINS=["https://your-frontend.vercel.app"]`

5. After deployment, your backend URL should look like:

- `https://decisioncanvas-api.onrender.com`

6. Confirm the health endpoint works:

- `https://decisioncanvas-api.onrender.com/system/health`

Expected response:

```json
{"status":"ok","app":"DecisionCanvas API"}
```

### Frontend Deployment on Vercel

This repo includes:

- [`frontend/.env.example`](C:\Users\waazlov\Documents\Work\Codex Project\decision-canvas\frontend\.env.example)

Deploy with these steps:

1. Import the GitHub repository into Vercel.
2. Use these settings:

- Root Directory: `frontend`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`

3. Set the required environment variable:

- `VITE_API_BASE_URL=https://decisioncanvas-api.onrender.com`

4. Deploy the project.

5. Your frontend URL should look like:

- `https://decisioncanvas.vercel.app`

### Final Live Check

After both apps are deployed:

1. Open the Vercel frontend URL.
2. Click **Use sample dataset**.
3. Keep the default question: `Why did conversion drop last month?`
4. Run the dashboard generation.

You should see:

- profiled dataset details
- KPI cards
- at least one key finding
- a rendered chart
- an executive summary
- a recommendation section

The submission URL should be the Vercel frontend URL.

## Assumptions & Limitations

- The system works best when the dataset includes core business fields such as time, revenue, orders, sessions, or meaningful segment dimensions.
- Some business metrics are derived when not explicitly present, for example conversion rate from orders and sessions.
- Recommendations are directional and evidence-based, but they do not claim causal certainty.
- Visualization is intentionally constrained to approved templates to keep the output stable and demo-safe.
- The current MVP is optimized for CSV-driven analysis rather than live warehouse connectivity or large-scale BI workflows.

## Future Improvements

- Support multi-file and warehouse-backed data ingestion
- Expand semantic field inference across more business domains
- Add richer funnel modeling and cohort analysis
- Introduce saved workspaces and shareable report links
- Add benchmark comparisons and scenario simulation
- Improve chart density and layout selection for broader dataset shapes
