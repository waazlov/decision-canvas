interface UploadPanelProps {
  fileName?: string;
  isLoading?: boolean;
  onStartDemoMode?: () => void;
  onUseSample?: () => void;
  onFileSelect?: (file: File | null) => void;
}

export function UploadPanel({
  fileName,
  isLoading = false,
  onStartDemoMode,
  onUseSample,
  onFileSelect,
}: UploadPanelProps) {
  return (
    <section className="surface-card upload-panel">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Step 1</p>
          <h2>Upload a CSV dataset</h2>
          <p className="upload-panel__lede">
            Start with a business dataset that includes time, metrics, and a few segment dimensions.
          </p>
        </div>
        <div className="upload-panel__actions">
          <span className="pill">CSV only</span>
          {onUseSample ? (
            <button className="button button--secondary button--compact" type="button" onClick={onUseSample}>
              Use sample dataset
            </button>
          ) : null}
          {onStartDemoMode ? (
            <button className="button button--secondary button--compact" type="button" onClick={onStartDemoMode}>
              Demo mode
            </button>
          ) : null}
        </div>
      </div>

      <label className="upload-dropzone">
        <input
          accept=".csv,text/csv"
          className="sr-only"
          type="file"
          onChange={(event) => onFileSelect?.(event.target.files?.[0] ?? null)}
        />
        <span className="upload-dropzone__title">Drop a CSV here or click to browse</span>
        <span className="upload-dropzone__body">
          DecisionCanvas profiles fields, validates quality, and prepares the dataset for analysis.
        </span>
        <span className="upload-dropzone__hint">
          Best for revenue, orders, conversion, session, channel, region, category, team, or performance data.
        </span>
        <span className="upload-dropzone__meta">
          {isLoading
            ? "Profiling sample or uploaded dataset..."
            : fileName
              ? `Selected: ${fileName}`
              : "No file selected yet"}
        </span>
      </label>
    </section>
  );
}
