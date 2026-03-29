import type { DashboardPayload, DatasetProfile } from "../types/contracts";

function resolveApiBaseUrl(): string {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }

  if (typeof window !== "undefined") {
    const { hostname } = window.location;
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return "http://127.0.0.1:8000";
    }
  }

  if (import.meta.env.DEV) {
    return "http://localhost:8000";
  }

  return "";
}

const API_BASE_URL = resolveApiBaseUrl();

function assertApiBaseUrl() {
  if (!API_BASE_URL) {
    throw new Error(
      "DecisionCanvas is missing VITE_API_BASE_URL. Set it before running the production frontend.",
    );
  }
}

async function request<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep the fallback message if the response is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export async function profileDataset(file: File): Promise<DatasetProfile> {
  assertApiBaseUrl();
  const formData = new FormData();
  formData.append("file", file);

  return request<DatasetProfile>(`${API_BASE_URL}/datasets/profile`, {
    method: "POST",
    body: formData,
  });
}

export async function analyzeDataset(
  file: File,
  question: string,
): Promise<DashboardPayload> {
  assertApiBaseUrl();
  const formData = new FormData();
  formData.append("file", file);
  formData.append("question", question);

  return request<DashboardPayload>(`${API_BASE_URL}/analysis/dashboard`, {
    method: "POST",
    body: formData,
  });
}

export async function loadSampleDatasetFile(): Promise<File> {
  const response = await fetch("/sample/ecommerce_demo.csv");
  if (!response.ok) {
    throw new Error("Unable to load the sample dataset.");
  }

  const blob = await response.blob();
  return new File([blob], "ecommerce_demo.csv", { type: "text/csv" });
}
