import { Link, useLocation } from "react-router-dom";
import type { PropsWithChildren } from "react";

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
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__inner">
          <Link className="brand" to="/">
            <span className="brand__mark">DC</span>
            <span className="brand__text">DecisionCanvas</span>
          </Link>

          <nav className="topbar__nav" aria-label="Primary">
            <NavLink to="/" label="Overview" />
            <NavLink to="/workspace" label="Workspace" />
            <NavLink to="/results" label="Results" />
          </nav>

          <Link className="button button--primary button--compact" to="/workspace">
            Upload dataset
          </Link>
        </div>
      </header>

      <main className="page-frame">{children}</main>
    </div>
  );
}
