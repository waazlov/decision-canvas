import { Link, useLocation } from "react-router-dom";
import type { PropsWithChildren } from "react";
import { useNavigate } from "react-router-dom";

import { BrandMark } from "./BrandMark";
import { useWorkspace } from "../../app/WorkspaceContext";

function NavLink({ to, label }: { to: string; label: string }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link className={`nav-link${isActive ? " active" : ""}`} to={to}>
      {label}
    </Link>
  );
}

export function AppShell({ children }: PropsWithChildren) {
  const navigate = useNavigate();
  const { prepareDemoWorkspace } = useWorkspace();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__inner">
          <Link className="brand" to="/">
            <BrandMark />
          </Link>

          <nav className="topbar__nav" aria-label="Primary">
            <NavLink to="/" label="Overview" />
            <NavLink to="/workspace" label="Workspace" />
            <NavLink to="/results" label="Results" />
          </nav>

          <div className="topbar__actions">
            <button
              className="button button--ghost button--compact"
              type="button"
              onClick={async () => {
                await prepareDemoWorkspace();
                navigate("/workspace");
              }}
            >
              Try demo
            </button>
            <Link className="button button--primary button--compact" to="/workspace">
              Upload dataset
            </Link>
          </div>
        </div>
      </header>

      <main className="page-frame">{children}</main>
    </div>
  );
}
