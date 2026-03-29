import type { ChartSpec } from "../../types/contracts";
import { ChartRenderer } from "./ChartRenderer";

export function ChartsSection({ charts }: { charts: ChartSpec[] }) {
  const [primary, ...secondary] = charts;

  return (
    <section className="charts-layout">
      {primary ? (
        <div className="charts-layout__primary">
          <ChartRenderer chart={primary} />
        </div>
      ) : null}
      {secondary.length > 0 ? (
        <div className={`charts-grid${secondary.length === 1 ? " charts-grid--single" : ""}`}>
          {secondary.map((chart) => (
            <ChartRenderer chart={chart} key={chart.id} />
          ))}
        </div>
      ) : null}
    </section>
  );
}
