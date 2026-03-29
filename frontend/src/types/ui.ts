import type { DashboardPayload, DatasetProfile } from "./contracts";

export interface ExampleQuestion {
  id: string;
  label: string;
}

export interface WorkspaceState {
  file: File | null;
  profile: DatasetProfile | null;
  question: string;
  dashboard: DashboardPayload | null;
}
