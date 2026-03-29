import type { ChartSpec } from "../../types/contracts";
import { ChartRenderer } from "./ChartRenderer";

export function ChartsSection({ charts }: { charts: ChartSpec[] }) {
  return (
    <section className={`charts-grid${charts.length === 1 ? " charts-grid--single" : ""}`}>
      {charts.map((chart) => (
        <ChartRenderer chart={chart} key={chart.id} />
      ))}
    </section>
  );
}
