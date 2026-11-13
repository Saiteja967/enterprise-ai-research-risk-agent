import { test, expect } from "@playwright/test";
import path from "node:path";
test("research, inspect a citation, approve a change and measure the suite", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Portfolio overview" }),
  ).toBeVisible();
  await expect(
    page.getByText("Aster Bridge Components", { exact: true }),
  ).toBeVisible();
  if (process.env.CAPTURE_SHOTS)
    await page.screenshot({ path: path.resolve("../docs/overview.png") });
  await page.getByRole("button", { name: "New research" }).click();
  await page.getByRole("button", { name: "Run and save research" }).click();
  await expect(page.getByText("Simulated response")).toBeVisible();
  await page.getByRole("button", { name: "AL-1048", exact: true }).click();
  await expect(page.locator(".source-box")).toContainText("Receivables aging");
  await page.getByRole("button", { name: "Inspect workflow" }).click();
  await expect(page.getByText("mcp / retrieve_evidence")).toBeVisible();
  await page.getByRole("link", { name: "Knowledge base" }).click();
  await page
    .getByLabel("Document · up to 2 MiB")
    .setInputFiles(path.resolve("../data/sample_upload.csv"));
  await page.getByRole("button", { name: "Submit for approval" }).click();
  await expect(page.getByRole("status")).toContainText("Document submitted");
  await page.getByRole("link", { name: /Approval queue/ }).click();
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await expect(page.locator(".badge.approved")).toBeVisible();
  await page.getByRole("link", { name: "Knowledge base" }).click();
  await expect(page.getByText("sample_upload.csv")).toBeVisible();
  await page.getByRole("link", { name: "Evaluation" }).click();
  await page.getByRole("button", { name: "Run evaluation" }).click();
  await expect(
    page.getByRole("heading", { name: "Case results" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Audit log" }).click();
  await expect(page.getByText("approval.approved")).toBeVisible();
  expect(errors).toEqual([]);
});
test("mobile navigation and dark theme", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Use dark theme" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: /Risk alerts/ }).click();
  await expect(
    page.getByRole("heading", { name: "Risk alerts", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
});
