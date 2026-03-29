import { lazy } from "react";
import { createBrowserRouter } from "react-router-dom";

import { App } from "./App";

const LandingPage = lazy(async () => {
  const module = await import("../pages/LandingPage");
  return { default: module.LandingPage };
});

const WorkspacePage = lazy(async () => {
  const module = await import("../pages/WorkspacePage");
  return { default: module.WorkspacePage };
});

const ResultsPage = lazy(async () => {
  const module = await import("../pages/ResultsPage");
  return { default: module.ResultsPage };
});

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <LandingPage />,
      },
      {
        path: "workspace",
        element: <WorkspacePage />,
      },
      {
        path: "results",
        element: <ResultsPage />,
      },
    ],
  },
]);
