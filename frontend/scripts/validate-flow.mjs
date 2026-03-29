import { chromium } from "playwright";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const browser = await chromium.launch({
  channel: "msedge",
  headless: true,
});

const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });

try {
  await page.goto("http://127.0.0.1:4173/workspace", { waitUntil: "networkidle" });

  await page.getByRole("button", { name: "Use sample dataset" }).click();
  await page.waitForSelector('[data-testid="dataset-ready"]', { timeout: 15000 });

  await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes("/analysis/dashboard") && response.status() === 200,
      { timeout: 15000 },
    ),
    page.getByRole("button", { name: "Generate dashboard" }).click(),
  ]);
  await page.waitForURL("**/results", { timeout: 15000 });
  await page.waitForLoadState("networkidle");
  await page.waitForSelector(".kpi-card", { timeout: 15000 });
  await page.waitForSelector(".chart-card", { timeout: 15000 });
  await page.waitForSelector(".finding-card", { timeout: 15000 });

  const errorCount = await page.locator(".error-banner").count();
  if (errorCount > 0) {
    throw new Error("The UI displayed an error banner during the end-to-end flow.");
  }

  const kpiCount = await page.locator(".kpi-card").count();
  const chartCount = await page.locator(".chart-card").count();
  const findingCount = await page.locator(".finding-card").count();

  if (kpiCount < 1) {
    throw new Error("No KPI cards rendered on the results dashboard.");
  }
  if (chartCount < 1) {
    throw new Error("No charts rendered on the results dashboard.");
  }
  if (findingCount < 1) {
    throw new Error("No findings rendered on the results dashboard.");
  }

  await page.screenshot({
    path: path.resolve(__dirname, "../dist/e2e-results.png"),
    fullPage: true,
  });

  console.log(
    JSON.stringify({
      ok: true,
      kpis: kpiCount,
      charts: chartCount,
      findings: findingCount,
      screenshot: path.resolve(__dirname, "../dist/e2e-results.png"),
    }),
  );
} catch (error) {
  await page.screenshot({
    path: path.resolve(__dirname, "../dist/e2e-failure.png"),
    fullPage: true,
  });
  throw error;
} finally {
  await browser.close();
}
