import { Suspense } from "react";
import { Outlet } from "react-router-dom";

import { WorkspaceProvider } from "./WorkspaceContext";
import { AppShell } from "../components/layout/AppShell";
import { ScrollToTop } from "../components/layout/ScrollToTop";

export function App() {
  return (
    <WorkspaceProvider>
      <AppShell>
        <ScrollToTop />
        <Suspense fallback={<div className="status-banner">Loading workspace...</div>}>
          <Outlet />
        </Suspense>
      </AppShell>
    </WorkspaceProvider>
  );
}
