import { useState } from "react";
import {
  Check,
  ClipboardCheck,
  FilePlus2,
  FlaskConical,
  GitBranch,
  Search,
  ShieldCheck,
  Timer,
  Wallet,
  X,
} from "lucide-react";
import { Badge, Empty, Metric, Panel } from "./ui";
import { companyName, date, pct, type Workspace } from "./domain";
import type { Report } from "./types";
import { api } from "./api";
export type Act = (work: () => Promise<void>, message: string) => void;
export function Alerts({
  data,
  focus,
  setFocus,
  research,
  act,
  busy,
}: {
  data: Workspace;
  focus: string;
  setFocus: (v: string) => void;
  research: (v: string, q: string) => void;
  act: Act;
  busy: boolean;
}) {
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const rows = data.overview.alerts.filter(
    (a) =>
      (filter === "all" || a.severity === filter) &&
      (a.title + " " + a.id + " " + a.company)
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const item = data.overview.alerts.find((a) => a.id === focus);
  return (
    <div className="work-grid">
      <Panel
        title="Investigation register"
        sub="Select a signal to inspect the evidence."
      >
        <div className="filters">
          <label className="search">
            <Search size={15} />
            <input
              aria-label="Search alerts"
              placeholder="Search alerts"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
          <select
            aria-label="Severity"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            {["all", "high", "medium", "low"].map((s) => (
              <option key={s} value={s}>
                {s === "all" ? "All severities" : s}
              </option>
            ))}
          </select>
        </div>
        <div className="list">
          {rows.map((a) => (
            <button
              className="list-row"
              key={a.id}
              onClick={() => setFocus(a.id)}
              aria-pressed={a.id === focus}
            >
              <span>
                <b>{a.title}</b>
                <small>
                  {a.id} · {a.company} · {a.status}
                </small>
              </span>
              <Badge value={a.severity} />
            </button>
          ))}
          {!rows.length && <Empty>No matching alerts.</Empty>}
        </div>
      </Panel>
      <Panel title="Alert investigation">
        {item ? (
          <div className="detail">
            <Badge value={item.severity} />
            <h3>{item.title}</h3>
            <p>{item.detail}</p>
            <dl>
              <dt>Company</dt>
              <dd>{companyName(data.overview, item.company)}</dd>
              <dt>Opened</dt>
              <dd>{date(item.opened)}</dd>
              <dt>Status</dt>
              <dd>{item.status}</dd>
            </dl>
            <button
              className="primary"
              onClick={() =>
                research(
                  item.company,
                  "Investigate " +
                    item.title +
                    " and suggest follow-up actions.",
                )
              }
            >
              <Search size={15} /> Research signal
            </button>
            {item.status === "open" && (
              <button
                className="secondary"
                disabled={busy}
                onClick={() =>
                  act(async () => {
                    await api("alert-reviews", {
                      alert: item.id,
                      confirm: true,
                    });
                  }, "Review request added to the approval queue.")
                }
              >
                <ClipboardCheck size={15} /> Request review approval
              </button>
            )}
          </div>
        ) : (
          <Empty>Select an alert to see its details.</Empty>
        )}
      </Panel>
    </div>
  );
}
export function Library({
  data,
  act,
  busy,
}: {
  data: Workspace;
  act: Act;
  busy: boolean;
}) {
  const [company, setCompany] = useState("ABC"),
    [file, setFile] = useState<File | null>(null),
    [version, setVersion] = useState(0);
  return (
    <div className="work-grid">
      <Panel
        title="Approved sources"
        sub="Documents available to the research agent."
      >
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Document</th>
                <th>Company</th>
                <th>Chunks</th>
              </tr>
            </thead>
            <tbody>
              {data.documents.map((d) => (
                <tr key={d.id}>
                  <td>
                    <b>{d.title}</b>
                    <small>
                      {d.kind} · {date(d.added)}
                    </small>
                  </td>
                  <td>
                    <span className="ticker">{d.company}</span>
                  </td>
                  <td>{d.chunks}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Panel
        title="Submit a source"
        sub="Submit synthetic text-based PDFs or UTF-8 CSVs for review."
      >
        <form
          className="form"
          onSubmit={(e) => {
            e.preventDefault();
            if (!file) return;
            const form = new FormData();
            form.set("company", company);
            form.set("confirm", "true");
            form.set("file", file);
            act(async () => {
              await api("documents", form);
              setFile(null);
              setVersion((v) => v + 1);
            }, "Document submitted. Approve it in the queue to make it searchable.");
          }}
        >
          <label>
            Company
            <select
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            >
              {data.overview.companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.id} · {c.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Document · up to 2 MiB
            <input
              key={version}
              type="file"
              accept=".pdf,.csv"
              required
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
          <button className="primary" disabled={!file || busy}>
            <FilePlus2 size={16} /> Submit for approval
          </button>
        </form>
      </Panel>
    </div>
  );
}
export function Approvals({
  data,
  act,
  busy,
}: {
  data: Workspace;
  act: Act;
  busy: boolean;
}) {
  return (
    <Panel
      title="Change requests"
      sub="Approve a proposed change to apply it to the workspace."
    >
      {!data.approvals.length ? (
        <Empty>
          Document submissions and alert review requests will appear here.
        </Empty>
      ) : (
        <div className="list">
          {data.approvals.map((p) => (
            <article className="approval-row" key={p.id}>
              <div>
                <small className="mono">
                  {p.company} / {p.kind}
                </small>
                <h3>{p.title}</h3>
                <p>{p.preview}</p>
                <small>
                  {date(p.at)} · {p.id}
                </small>
              </div>
              <div className="decision">
                <Badge value={p.status} />
                {p.status === "pending" && (
                  <div className="actions">
                    {(["approve", "reject"] as const).map((a) => (
                      <button
                        key={a}
                        className={a === "approve" ? "primary" : "secondary"}
                        disabled={busy}
                        onClick={() =>
                          act(
                            async () => {
                              await api("approvals/" + p.id, {
                                decision: a,
                                confirm: true,
                              });
                            },
                            a === "approve"
                              ? "Change approved."
                              : "Change rejected.",
                          )
                        }
                      >
                        {a === "approve" ? (
                          <Check size={15} />
                        ) : (
                          <X size={15} />
                        )}{" "}
                        {a === "approve" ? "Approve" : "Reject"}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </Panel>
  );
}
export function Trace({
  reports,
  report,
  select,
}: {
  reports: Report[];
  report: Report | undefined;
  select: (r: Report) => void;
}) {
  return (
    <Panel
      title="Execution trace"
      sub="Node timings, tool calls and model usage for a saved run."
      action={
        report && (
          <select
            aria-label="Select run"
            value={report.id}
            onChange={(e) => {
              const r = reports.find((r) => r.id === e.target.value);
              if (r) select(r);
            }}
          >
            {reports.map((r) => (
              <option key={r.id} value={r.id}>
                {r.company} · {r.id.slice(-6)}
              </option>
            ))}
          </select>
        )
      }
    >
      {report ? (
        <div className="detail">
          <div className="report-meta">
            <Badge value={report.status} />
            <span>{report.model}</span>
            <span>{report.latency_ms.toFixed(1)} ms</span>
          </div>
          <ol className="trace">
            {report.steps.map((s) => (
              <li key={s.node}>
                <i>
                  <GitBranch size={15} />
                </i>
                <div>
                  <b>{s.node}</b>
                  <p>{s.detail}</p>
                  {s.tool && <code>mcp / {s.tool}</code>}
                </div>
                <span>
                  <Badge value={s.status} />
                  <small>{s.ms.toFixed(1)} ms</small>
                </span>
              </li>
            ))}
          </ol>
          <p>
            Input tokens {report.usage.input_tokens ?? "unknown"} · Output
            tokens {report.usage.output_tokens ?? "unknown"} · Estimated cost{" "}
            {report.usage.cost_usd === null
              ? "unavailable"
              : "$" + report.usage.cost_usd.toFixed(6)}
          </p>
        </div>
      ) : (
        <Empty>Run and save a research brief to inspect its workflow.</Empty>
      )}
    </Panel>
  );
}
export function Evaluations({
  data,
  act,
  busy,
}: {
  data: Workspace;
  act: Act;
  busy: boolean;
}) {
  const e = data.evaluation;
  return (
    <>
      <Panel
        title="Synthetic evaluation suite"
        sub="Seven labeled cases run on a fresh copy of the seed dataset."
        action={
          <button
            className="primary"
            disabled={busy}
            onClick={() =>
              act(async () => {
                await api("evaluations", { confirm: true });
              }, "Evaluation completed and saved.")
            }
          >
            <FlaskConical size={16} /> Run evaluation
          </button>
        }
      >
        {!e && (
          <Empty>
            Run the suite to calculate evidence coverage, retrieval accuracy,
            latency and cost.
          </Empty>
        )}
      </Panel>
      {e && (
        <>
          <div className="metrics">
            <Metric
              label="Finding recall"
              value={pct(e.mean_recall)}
              foot="Mean expected citations found"
              icon={Search}
            />
            <Metric
              label="Exact support"
              value={pct(e.mean_support)}
              foot="Findings matching source text"
              icon={ShieldCheck}
            />
            <Metric
              label="P95 latency"
              value={e.p95_ms.toFixed(1) + " ms"}
              foot={"Median " + e.p50_ms.toFixed(1) + " ms"}
              icon={Timer}
            />
            <Metric
              label="Provider cost"
              value={"$" + e.cost_usd.toFixed(2)}
              foot={e.tokens + " tokens · deterministic mode"}
              icon={Wallet}
            />
          </div>
          <Panel
            title="Case results"
            sub={
              "Retrieval accuracy " +
              pct(e.retrieval_accuracy) +
              " · measured " +
              date(e.at)
            }
          >
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Research question</th>
                    <th>Company</th>
                    <th>Expected citations found</th>
                    <th>Retrieval</th>
                    <th>Latency</th>
                  </tr>
                </thead>
                <tbody>
                  {e.cases.map((c) => (
                    <tr key={c.question}>
                      <td>{c.question}</td>
                      <td>{c.company}</td>
                      <td>
                        {c.matched} / {c.expected}
                      </td>
                      <td>{c.retrieval_ok ? "Matched" : "Missed"}</td>
                      <td>{c.latency_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </>
      )}
    </>
  );
}
export function Audit({ data }: { data: Workspace }) {
  return (
    <Panel
      title="Audit events"
      sub="Committed changes with a request identifier for correlation."
    >
      {!data.audit.length ? (
        <Empty>
          Saved reports, evaluation runs and approval decisions appear here.
        </Empty>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Event</th>
                <th>Subject</th>
                <th>Time (UTC)</th>
                <th>Request ID</th>
              </tr>
            </thead>
            <tbody>
              {data.audit.map((e) => (
                <tr key={e.id}>
                  <td>
                    <b>{e.event}</b>
                  </td>
                  <td className="mono">{e.subject}</td>
                  <td>{e.at.replace("T", " ").slice(0, 19)}</td>
                  <td className="mono">{e.request_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Panel>
  );
}
