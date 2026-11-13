import type { Alert, Overview, Report } from "./types";
export type Page =
  | "overview"
  | "research"
  | "alerts"
  | "documents"
  | "workflow"
  | "evaluation"
  | "approvals"
  | "audit";
export interface Doc {
  id: string;
  company: string;
  title: string;
  kind: string;
  added: string;
  chunks: number;
}
export interface Proposal {
  id: string;
  company: string;
  at: string;
  title: string;
  kind: string;
  status: string;
  preview: string;
}
export interface EventRow {
  id: string;
  at: string;
  event: string;
  subject: string;
  request_id: string;
}
export interface Evaluation {
  id: string;
  at: string;
  cases: {
    company: string;
    question: string;
    recall: number;
    exact_support: number;
    retrieval_ok: boolean;
    matched: number;
    expected: number;
    latency_ms: number;
  }[];
  mean_recall: number;
  mean_support: number;
  retrieval_accuracy: number;
  p50_ms: number;
  p95_ms: number;
  tokens: number;
  cost_usd: number;
}
export interface Workspace {
  overview: Overview;
  reports: Report[];
  documents: Doc[];
  approvals: Proposal[];
  audit: EventRow[];
  evaluation: Evaluation | null;
}
export const money = (v: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(v);
export const date = (s: string) =>
  new Date(s.length === 10 ? s + "T12:00:00Z" : s).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
export const openAlerts = (x: Alert[]) => x.filter((a) => a.status === "open");
export const companyName = (d: Overview, id: string) =>
  d.companies.find((c) => c.id === id)?.name ?? id;
export const pct = (v: number) => Math.round(v * 100) + "%";
export type Go = (p: Page) => void;
