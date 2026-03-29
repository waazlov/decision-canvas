import { useNavigate } from "react-router-dom";

import { PageHeader } from "../components/layout/PageHeader";
import { UploadPanel } from "../components/upload/UploadPanel";
import { DataPreviewTable } from "../components/data/DataPreviewTable";
import { SchemaSummary } from "../components/data/SchemaSummary";
import { QuestionComposer } from "../components/questions/QuestionComposer";
import { useWorkspace } from "../app/WorkspaceContext";

const exampleQuestions = [
  { id: "q1", label: "Why did conversion drop last month?" },
  { id: "q2", label: "Which region performs best?" },
  { id: "q3", label: "Where in the funnel are users dropping off?" },
  { id: "q4", label: "What changed recently?" },
];

export function WorkspacePage() {
  const navigate = useNavigate();
  const {
    mode,
    fileName,
    question,
    profile,
    error,
    isProfiling,
    isAnalyzing,
    setQuestion,
    selectFile,
    startDemoMode,
    useSampleDataset,
    runAnalysis,
    resetWorkspace,
  } = useWorkspace();

  async function handleSubmit() {
    const dashboard = await runAnalysis();
    if (dashboard) {
      navigate("/results");
    }
  }

  return (
    <div className="stack-lg">
      <PageHeader
        eyebrow="Workspace"
        title="Upload, inspect, and frame the question"
        description="Move from raw CSV to a decision-ready dashboard through one guided workflow."
        actions={
          fileName ? (
            <button className="button button--secondary" type="button" onClick={resetWorkspace}>
              Reset flow
            </button>
          ) : undefined
        }
      />

      <div className="workspace-grid">
        <div className="stack-lg">
          <UploadPanel
            fileName={fileName ?? undefined}
            isLoading={isProfiling}
            onFileSelect={selectFile}
            onStartDemoMode={() => {
              startDemoMode();
              navigate("/results");
            }}
            onUseSample={useSampleDataset}
          />
          {mode === "demo" ? (
            <div className="status-banner">
              Demo mode is active. The dashboard can be shown instantly without waiting for the backend to wake up.
            </div>
          ) : null}
          {isProfiling ? (
            <div className="status-banner">Profiling dataset and validating inferred fields...</div>
          ) : null}
          {profile ? (
            <div className="status-banner status-banner--subtle" data-testid="dataset-ready">
              Ready to analyze {profile.dataset_name} with {profile.row_count.toLocaleString()} rows and{" "}
              {profile.column_count} columns.
            </div>
          ) : null}
          <QuestionComposer
            exampleQuestions={exampleQuestions}
            isSubmitting={isAnalyzing}
            question={question}
            onQuestionChange={setQuestion}
            onSubmit={handleSubmit}
          />
          {isAnalyzing ? (
            <div className="status-banner">Generating decision-ready dashboard...</div>
          ) : null}
          {error ? <div className="error-banner">{error}</div> : null}
          {error ? (
            <button
              className="button button--secondary"
              type="button"
              onClick={() => {
                startDemoMode();
                navigate("/results");
              }}
            >
              Continue in demo mode
            </button>
          ) : null}
        </div>

        <div className="stack-lg">
          <DataPreviewTable profile={profile} />
          <SchemaSummary profile={profile} />
        </div>
      </div>
    </div>
  );
}
