import type { KPI } from "../../types/contracts";

const KPI_MARKS: Record<string, string> = {
  Revenue: "$",
  Orders: "#",
  Sessions: "S",
  Conversion: "%",
  Aov: "A",
  Performance: "P",
};

function formatValue(value: KPI["value"], format: KPI["format"]) {
  if (typeof value !== "number") {
    return String(value);
  }
  if (format === "currency") {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  }
  if (format === "percentage") {
    return `${(value * 100).toFixed(1)}%`;
  }
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: format === "integer" ? 0 : 1,
  }).format(value);
}

export function KpiGrid({ kpis }: { kpis: KPI[] }) {
  return (
    <section className="kpi-grid">
      {kpis.map((kpi) => (
        <article className="surface-card kpi-card" key={kpi.label}>
          <div className="kpi-card__header">
            <p className="kpi-card__label">{kpi.label}</p>
            <span className="kpi-card__mark">{KPI_MARKS[kpi.label] ?? kpi.label.charAt(0)}</span>
          </div>
          <h3>{formatValue(kpi.value, kpi.format)}</h3>
          <p
            className={`kpi-card__delta ${
              (kpi.delta_pct ?? 0) < 0 ? "is-negative" : "is-positive"
            }`}
          >
            {kpi.delta_pct != null ? `${kpi.delta_pct > 0 ? "+" : ""}${kpi.delta_pct}%` : "Stable"}
            {kpi.comparison_label ? ` ${kpi.comparison_label}` : ""}
          </p>
        </article>
      ))}
    </section>
  );
}
