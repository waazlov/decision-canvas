import { useWorkspace } from "../app/WorkspaceContext";

export function useDatasetAnalysis() {
  return useWorkspace();
}
