export type DetectedColumnType =
  | "string"
  | "integer"
  | "float"
  | "boolean"
  | "date"
  | "datetime"
  | "unknown";

export type SemanticRole =
  | "time_dimension"
  | "dimension"
  | "metric"
  | "identifier"
  | "funnel_stage"
  | "unknown";

export type ConfidenceLevel = "low" | "medium" | "high";
export type QuestionIntent =
  | "trend_analysis"
  | "segment_best"
  | "segment_worst"
  | "anomaly_detection"
  | "funnel_dropoff"
  | "metric_comparison"
  | "overview";

export type QuestionDirection =
  | "best"
  | "worst"
  | "drop"
  | "growth"
  | "increase"
  | "decrease"
  | "compare"
  | "neutral";

export type QuestionTimeScope =
  | "last_week"
  | "last_month"
  | "recent"
  | "over_time"
  | "all_time"
  | "unspecified";

export type ChartTemplate =
  | "kpi_card"
  | "line"
  | "bar"
  | "grouped_bar"
  | "scatter"
  | "funnel"
  | "heatmap";

export type ValueFormat = "number" | "currency" | "percentage" | "integer" | "string";

export interface ColumnProfile {
  name: string;
  detected_type: DetectedColumnType;
  semantic_role: SemanticRole;
  null_pct: number;
  unique_count: number;
  sample_values: string[];
}

export interface DataQualityIssue {
  type:
    | "missing_values"
    | "mixed_types"
    | "duplicates"
    | "date_parse"
    | "high_cardinality"
    | "unsupported";
  column?: string | null;
  severity: "low" | "medium" | "high";
  message: string;
}

export interface DatasetProfile {
  dataset_name: string;
  row_count: number;
  column_count: number;
  preview_rows: Array<Record<string, unknown>>;
  columns: ColumnProfile[];
  candidate_metrics: string[];
  candidate_dimensions: string[];
  data_quality_issues: DataQualityIssue[];
  assumptions: string[];
}

export interface TimeWindow {
  current_start?: string | null;
  current_end?: string | null;
  comparison_start?: string | null;
  comparison_end?: string | null;
}

export interface Finding {
  id: string;
  type:
    | "trend_drop"
    | "trend_growth"
    | "segment_outperformance"
    | "segment_underperformance"
    | "anomaly"
    | "funnel_dropoff"
    | "relationship";
  title: string;
  metric: string;
  dimension?: string | null;
  segment?: string | null;
  time_window?: TimeWindow | null;
  value?: number | null;
  comparison_value?: number | null;
  magnitude_pct?: number | null;
  confidence: ConfidenceLevel;
  explanation: string;
  recommended_action: string;
  evidence: string[];
  assumptions: string[];
  uncertainty_notes: string[];
}

export interface AxisSpec {
  field: string;
  label: string;
  format: ValueFormat;
}

export interface ChartSeries {
  name: string;
  field: string;
}

export interface ChartAnnotation {
  label: string;
  x_value?: string | number | null;
  y_value?: number | null;
}

export interface ChartSpec {
  id: string;
  template: ChartTemplate;
  title: string;
  subtitle?: string | null;
  reason_for_selection: string;
  x_axis?: AxisSpec | null;
  y_axis?: AxisSpec | null;
  series: ChartSeries[];
  data: Array<Record<string, unknown>>;
  annotation?: ChartAnnotation | null;
}

export interface KPI {
  label: string;
  value: string | number;
  format: ValueFormat;
  delta_pct?: number | null;
  comparison_label?: string | null;
}

export interface ExecutiveSummary {
  what_happened: string;
  why_it_likely_happened: string;
  what_to_do_next: string[];
  assumptions: string[];
  uncertainty_notes: string[];
}

export interface QuestionInterpretation {
  raw_question: string;
  intent: QuestionIntent;
  metric?: string | null;
  dimension?: string | null;
  direction: QuestionDirection;
  time_scope: QuestionTimeScope;
  comparison_targets: string[];
  confidence: ConfidenceLevel;
  fallback_used: boolean;
  notes: string[];
}

export interface DashboardPayload {
  dashboard_title: string;
  question: string;
  interpreted_question: QuestionInterpretation;
  dataset_profile: DatasetProfile;
  kpis: KPI[];
  findings: Finding[];
  charts: ChartSpec[];
  executive_summary: ExecutiveSummary;
}
