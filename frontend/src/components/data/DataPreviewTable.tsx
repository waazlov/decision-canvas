import type { DatasetProfile } from "../../types/contracts";

interface DataPreviewTableProps {
  profile: DatasetProfile | null;
}

export function DataPreviewTable({ profile }: DataPreviewTableProps) {
  const rows = profile?.preview_rows ?? [];
  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];

  return (
    <section className="surface-card">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Preview</p>
          <h2>Dataset sample</h2>
        </div>
        {profile ? <span className="pill">{profile.row_count.toLocaleString()} rows</span> : null}
      </div>

      {rows.length === 0 ? (
        <div className="empty-panel">
          <p>No dataset loaded yet. Upload a CSV to preview the first rows.</p>
        </div>
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  {columns.map((column) => (
                    <td key={column}>{String(row[column] ?? "—")}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
