import {
  createContext,
  useContext,
  useEffect,
  useState,
  type PropsWithChildren,
} from "react";

import { analyzeDataset, loadSampleDatasetFile, profileDataset } from "../services/api";
import type { DashboardPayload, DatasetProfile } from "../types/contracts";
import { sampleDashboard } from "../types/mockData";

const STORAGE_KEY = "decisioncanvas.workspace";
type WorkspaceMode = "live" | "demo";

interface StoredWorkspaceState {
  mode: WorkspaceMode;
  fileName: string | null;
  question: string;
  profile: DatasetProfile | null;
  dashboard: DashboardPayload | null;
}

interface WorkspaceContextValue {
  mode: WorkspaceMode;
  file: File | null;
  fileName: string | null;
  question: string;
  profile: DatasetProfile | null;
  dashboard: DashboardPayload | null;
  error: string | null;
  isProfiling: boolean;
  isAnalyzing: boolean;
  setQuestion: (question: string) => void;
  selectFile: (file: File | null) => Promise<void>;
  useSampleDataset: () => Promise<void>;
  startDemoMode: () => void;
  runAnalysis: () => Promise<DashboardPayload | null>;
  resetWorkspace: () => void;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

function loadStoredState(): StoredWorkspaceState {
  if (typeof window === "undefined") {
    return { mode: "live", fileName: null, question: "", profile: null, dashboard: null };
  }

  const raw = window.sessionStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { mode: "live", fileName: null, question: "", profile: null, dashboard: null };
  }

  try {
    return JSON.parse(raw) as StoredWorkspaceState;
  } catch {
    return { mode: "live", fileName: null, question: "", profile: null, dashboard: null };
  }
}

export function WorkspaceProvider({ children }: PropsWithChildren) {
  const initial = loadStoredState();
  const [mode, setMode] = useState<WorkspaceMode>(initial.mode ?? "live");
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string | null>(initial.fileName);
  const [question, setQuestion] = useState<string>(
    initial.question || "Why did conversion drop last month?",
  );
  const [profile, setProfile] = useState<DatasetProfile | null>(initial.profile);
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(initial.dashboard);
  const [error, setError] = useState<string | null>(null);
  const [isProfiling, setIsProfiling] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const snapshot: StoredWorkspaceState = {
      mode,
      fileName,
      question,
      profile,
      dashboard,
    };
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
  }, [dashboard, fileName, mode, profile, question]);

  async function selectFile(nextFile: File | null) {
    setMode("live");
    setFile(nextFile);
    setFileName(nextFile?.name ?? null);
    setDashboard(null);
    setError(null);

    if (!nextFile) {
      setProfile(null);
      return;
    }

    setIsProfiling(true);
    try {
      const nextProfile = await profileDataset(nextFile);
      setProfile(nextProfile);
    } catch (nextError) {
      setProfile(null);
      setError(
        nextError instanceof Error ? nextError.message : "Unable to profile the dataset.",
      );
    } finally {
      setIsProfiling(false);
    }
  }

  async function runAnalysis() {
    if (!file) {
      setError("Upload a CSV dataset before generating a dashboard.");
      return null;
    }
    if (!question.trim()) {
      setError("Enter a business question before generating a dashboard.");
      return null;
    }

    setIsAnalyzing(true);
    setError(null);
    setMode("live");
    try {
      const nextDashboard = await analyzeDataset(file, question);
      setDashboard(nextDashboard);
      return nextDashboard;
    } catch (nextError) {
      setError(
        nextError instanceof Error ? nextError.message : "Unable to generate the dashboard.",
      );
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function useSampleDataset() {
    const sampleFile = await loadSampleDatasetFile();
    await selectFile(sampleFile);
  }

  function startDemoMode() {
    setMode("demo");
    setFile(null);
    setFileName(sampleDashboard.dataset_profile.dataset_name);
    setQuestion(sampleDashboard.question);
    setProfile(sampleDashboard.dataset_profile);
    setDashboard(sampleDashboard);
    setError(null);
    setIsProfiling(false);
    setIsAnalyzing(false);
  }

  function resetWorkspace() {
    setMode("live");
    setFile(null);
    setFileName(null);
    setProfile(null);
    setDashboard(null);
    setError(null);
    setQuestion("Why did conversion drop last month?");
    if (typeof window !== "undefined") {
      window.sessionStorage.removeItem(STORAGE_KEY);
    }
  }

  return (
    <WorkspaceContext.Provider
      value={{
        mode,
        file,
        fileName,
        question,
        profile,
        dashboard,
        error,
        isProfiling,
        isAnalyzing,
        setQuestion,
        selectFile,
        useSampleDataset,
        startDemoMode,
        runAnalysis,
        resetWorkspace,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const value = useContext(WorkspaceContext);
  if (!value) {
    throw new Error("useWorkspace must be used within WorkspaceProvider.");
  }
  return value;
}
