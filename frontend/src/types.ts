export interface Company {
  id: string;
  name: string;
  sector: string;
}
export interface Alert {
  id: string;
  company: string;
  title: string;
  severity: "high" | "medium" | "low";
  detail: string;
  status: string;
  opened: string;
}
export interface Period {
  period: string;
  amount: number;
  overdue: number;
}
export interface Overview {
  as_of: string;
  companies: Company[];
  alerts: Alert[];
  periods: Period[];
  reports: number;
  documents: number;
  pending: number;
  mode: string;
}
export interface Evidence {
  id: string;
  title: string;
  locator: string;
  body: string;
  kind: string;
}
export interface Step {
  node: string;
  status: string;
  detail: string;
  ms: number;
  tool: string | null;
}
export interface Report {
  id: string;
  at: string;
  company: string;
  question: string;
  mode: string;
  model: string;
  status: string;
  findings: { citation: string; text: string }[];
  sources: Evidence[];
  recommendations: string[];
  confidence: string;
  uncertainties: string[];
  steps: Step[];
  usage: {
    input_tokens: number | null;
    cached_tokens: number | null;
    output_tokens: number | null;
    cost_usd: number | null;
  };
  latency_ms: number;
}
