import { useState } from "react";
import {
  BookOpen,
  Check,
  ChevronRight,
  FileText,
  Play,
  Workflow,
} from "lucide-react";
import { Badge, Empty, Panel } from "./ui";
import type { Report } from "./types";
import type { Workspace, Go } from "./domain";
import { date } from "./domain";
export function Research({
  data,
  company,
  setCompany,
  question,
  setQuestion,
  report,
  select,
  run,
  busy,
  go,
}: {
  data: Workspace;
  company: string;
  setCompany: (s: string) => void;
  question: string;
  setQuestion: (s: string) => void;
  report: Report | undefined;
  select: (r: Report) => void;
  run: () => void;
  busy: boolean;
  go: Go;
}) {
  const [source, setSource] = useState("");
  const picked = report?.sources.find((s) => s.id === source);
  return (
    <>
      <div className="work-grid">
        <Panel
          title="Research brief"
          sub="Choose a company and define the question to investigate."
        >
          <form
            className="form"
            onSubmit={(e) => {
              e.preventDefault();
              setSource("");
              run();
            }}
          >
            <label>
              Company
              <select
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              >
                {data.overview.companies.map((c) => (
                  <option value={c.id} key={c.id}>
                    {c.id} · {c.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Research question
              <textarea
                minLength={8}
                maxLength={600}
                required
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={3}
              />
            </label>
            <button className="primary" disabled={busy}>
              <Play size={15} />
              {busy ? "Working…" : "Run and save research"}
            </button>
          </form>
        </Panel>
        <Panel title="Saved reports" sub="Most recent investigations">
          <div className="history">
            {data.reports.length ? (
              data.reports.slice(0, 8).map((r) => (
                <button
                  key={r.id}
                  aria-pressed={r.id === report?.id}
                  onClick={() => {
                    select(r);
                    setSource("");
                  }}
                >
                  <FileText size={17} />
                  <span>
                    <b>{r.company} research report</b>
                    <small>
                      {date(r.at)} · {r.status}
                    </small>
                  </span>
                  <ChevronRight size={15} />
                </button>
              ))
            ) : (
              <Empty>Run a research brief to save your first report.</Empty>
            )}
          </div>
        </Panel>
      </div>
      {report && (
        <Panel
          title={report.company + " research report"}
          sub={report.question}
          action={<Badge value={report.status} />}
        >
          <div className="report-body">
            <div className="report-meta">
              <span>
                {report.mode === "demo" ? "Simulated response" : report.model}
              </span>
              <span>{report.confidence}</span>
            </div>
            {report.summary && (
              <>
                <h3>Period summary</h3>
                <p>{report.summary}</p>
              </>
            )}
            {report.risk_factors.length > 0 && (
              <>
                <h3>Risk factors</h3>
                <ul>
                  {report.risk_factors.map((f) => (
                    <li key={f.citation}>
                      <b>{f.title}</b> · {f.severity} severity{" "}
                      <button
                        className="citation"
                        aria-label={"Inspect risk source " + f.citation}
                        onClick={() => setSource(f.citation)}
                      >
                        {f.citation}
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            )}
            <h3>Findings</h3>
            {report.findings.map((f) => (
              <div className="finding" key={f.citation}>
                <Check size={16} />
                <div>
                  {f.text}
                  <button
                    className="citation"
                    onClick={() => setSource(f.citation)}
                  >
                    <BookOpen size={12} />
                    {f.citation}
                  </button>
                </div>
              </div>
            ))}
            {!report.findings.length && (
              <p>No validated findings were available.</p>
            )}
            {picked && (
              <aside className="source-box" aria-live="polite">
                <b>{picked.title}</b>
                <small>
                  {picked.locator} · {picked.id}
                </small>
                <p>{picked.body}</p>
              </aside>
            )}
            <h3>Follow-up actions</h3>
            {report.recommendations.length ? (
              <ul>
                {report.recommendations.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            ) : (
              <p>Inspect the available evidence before taking action.</p>
            )}
            <h3>Uncertainty</h3>
            <ul>
              {report.uncertainties.map((u) => (
                <li key={u}>{u}</li>
              ))}
            </ul>
            <details>
              <summary>All source records ({report.sources.length})</summary>
              {report.sources.map((s) => (
                <p key={s.id}>
                  <b>{s.title}</b> · {s.locator}
                  <br />
                  {s.body}
                </p>
              ))}
            </details>
            <button className="secondary" onClick={() => go("workflow")}>
              <Workflow size={16} /> Inspect workflow
            </button>
          </div>
        </Panel>
      )}
    </>
  );
}
