import type { ReactNode } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Funnel,
  FunnelChart,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ChartSpec } from "../../types/contracts";

const SERIES_COLORS = ["#0f62fe", "#12b76a", "#f79009", "#7a5af8"];

function renderBarSeries(chart: ChartSpec) {
  return chart.series.map((series, index) => (
    <Bar dataKey={series.field} fill={SERIES_COLORS[index % SERIES_COLORS.length]} key={series.field} radius={[8, 8, 0, 0]} />
  ));
}

function renderLineSeries(chart: ChartSpec) {
  return chart.series.map((series, index) => (
    <Line
      dataKey={series.field}
      dot={false}
      key={series.field}
      stroke={SERIES_COLORS[index % SERIES_COLORS.length]}
      strokeWidth={3}
      type="monotone"
    />
  ));
}

export function ChartRenderer({ chart }: { chart: ChartSpec }) {
  const xField = chart.x_axis?.field ?? "x";
  const yField = chart.y_axis?.field ?? "y";

  if (chart.data.length === 0) {
    return (
      <article className="surface-card chart-card">
        <div className="chart-card__header">
          <div>
            <h3>{chart.title}</h3>
            {chart.subtitle ? <p>{chart.subtitle}</p> : null}
          </div>
          <span className="pill pill--neutral">{chart.template.replace("_", " ")}</span>
        </div>
        <div className="empty-panel">
          <p>This chart was recommended, but there was not enough data to render it.</p>
        </div>
      </article>
    );
  }

  let content: ReactNode = (
    <div className="empty-panel">
      <p>Unsupported chart template: {chart.template}</p>
    </div>
  );

  if (chart.template === "line") {
    content = (
      <ResponsiveContainer height={280} width="100%">
        <LineChart data={chart.data}>
          <CartesianGrid stroke="rgba(15, 23, 42, 0.08)" vertical={false} />
          <XAxis dataKey={xField} tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <Tooltip />
          {renderLineSeries(chart)}
        </LineChart>
      </ResponsiveContainer>
    );
  } else if (chart.template === "bar" || chart.template === "grouped_bar") {
    content = (
      <ResponsiveContainer height={280} width="100%">
        <BarChart data={chart.data}>
          <CartesianGrid stroke="rgba(15, 23, 42, 0.08)" vertical={false} />
          <XAxis dataKey={xField} tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <Tooltip />
          {chart.template === "grouped_bar" ? <Legend /> : null}
          {renderBarSeries(chart)}
        </BarChart>
      </ResponsiveContainer>
    );
  } else if (chart.template === "scatter") {
    content = (
      <ResponsiveContainer height={280} width="100%">
        <ScatterChart>
          <CartesianGrid stroke="rgba(15, 23, 42, 0.08)" />
          <XAxis dataKey={xField} tickLine={false} axisLine={false} />
          <YAxis dataKey={yField} tickLine={false} axisLine={false} />
          <Tooltip />
          <Scatter data={chart.data} fill={SERIES_COLORS[0]} />
        </ScatterChart>
      </ResponsiveContainer>
    );
  } else if (chart.template === "funnel") {
    content = (
      <ResponsiveContainer height={280} width="100%">
        <FunnelChart>
          <Tooltip />
          <Funnel data={chart.data} dataKey={yField} isAnimationActive={false} nameKey={xField} />
        </FunnelChart>
      </ResponsiveContainer>
    );
  }

  return (
    <article className="surface-card chart-card">
      <div className="chart-card__header">
        <div>
          <h3>{chart.title}</h3>
          {chart.subtitle ? <p>{chart.subtitle}</p> : null}
        </div>
        <span className="pill pill--neutral">{chart.template.replace("_", " ")}</span>
      </div>

      <div className="chart-meta">
        <span>{chart.x_axis?.label ?? "X-axis"}</span>
        <span>{chart.y_axis?.label ?? "Y-axis"}</span>
      </div>

      {content}

      <div className="chart-footer">
        <p>{chart.reason_for_selection}</p>
        {chart.annotation ? <p className="chart-annotation">{chart.annotation.label}</p> : null}
      </div>
    </article>
  );
}
