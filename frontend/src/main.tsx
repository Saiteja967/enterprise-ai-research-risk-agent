import { createRoot } from "react-dom/client";
import { useEffect, useState } from "react";
import {
  Activity,
  BookOpen,
  ChevronRight,
  ClipboardCheck,
  FileClock,
  FlaskConical,
  Layers3,
  LayoutDashboard,
  Menu,
  Moon,
  Network,
  OctagonAlert,
  Plus,
  Radio,
  Search,
  Sun,
  X,
} from "lucide-react";
import "@fontsource/inter/latin-400.css";
import "@fontsource/inter/latin-500.css";
import "@fontsource/inter/latin-600.css";
import "@fontsource/inter/latin-700.css";
import "@fontsource/ibm-plex-mono/latin-500.css";
import "./style.css";
import { api } from "./api";
import type { Report, Overview } from "./types";
import {
  date,
  type Workspace,
  type Page,
  type Doc,
  type Proposal,
  type EventRow,
  type Evaluation,
} from "./domain";
import { Dashboard } from "./Overview";
import { Research } from "./Research";
import {
  Alerts,
  Library,
  Approvals,
  Trace,
  Evaluations,
  Audit,
  type Act,
} from "./Operations";
const sections = [
  {
    title: "Workspace",
    items: [
      { id: "overview", name: "Overview", icon: LayoutDashboard },
      { id: "research", name: "Research workspace", icon: Search },
      { id: "alerts", name: "Risk alerts", icon: OctagonAlert },
      { id: "documents", name: "Knowledge base", icon: BookOpen },
    ],
  },
  {
    title: "Operations",
    items: [
      { id: "workflow", name: "Workflow activity", icon: Network },
      { id: "evaluation", name: "Evaluation", icon: FlaskConical },
      { id: "approvals", name: "Approval queue", icon: ClipboardCheck },
      { id: "audit", name: "Audit log", icon: FileClock },
    ],
  },
] as const;
const titles: Record<Page, [string, string]> = {
  overview: [
    "Portfolio overview",
    "Monitor exposure, investigate signals, and trace the evidence behind each finding.",
  ],
  research: [
    "Research workspace",
    "Investigate a company and build a report from its source records.",
  ],
  alerts: [
    "Risk alerts",
    "Investigate signals and request a review of the underlying records.",
  ],
  documents: [
    "Knowledge base",
    "Manage the documents available to company research.",
  ],
  workflow: [
    "Workflow activity",
    "Inspect each step from research request to validated report.",
  ],
  evaluation: [
    "Evaluation",
    "Measure how reliably the agent retrieves and cites the expected evidence.",
  ],
  approvals: [
    "Approval queue",
    "Review proposed changes to documents and risk alerts.",
  ],
  audit: [
    "Audit log",
    "Trace workspace changes to their originating requests.",
  ],
};
const pageFromHash = (): Page => {
  const hash = location.hash.slice(1);
  return Object.hasOwn(titles, hash) ? (hash as Page) : "overview";
};
async function load(): Promise<Workspace> {
  const [overview, reports, documents, approvals, audit, evaluation] =
    await Promise.all([
      api<Overview>("overview"),
      api<Report[]>("reports"),
      api<Doc[]>("documents"),
      api<Proposal[]>("approvals"),
      api<EventRow[]>("audit"),
      api<Evaluation | null>("evaluations"),
    ]);
  return { overview, reports, documents, approvals, audit, evaluation };
}
const initialQuestion =
  "Analyze receivables aging, summarize key changes, identify risk signals, and recommend follow-up actions.";
function App() {
  const [data, setData] = useState<Workspace>(),
    [page, setPage] = useState<Page>(pageFromHash),
    [dark, setDark] = useState(
      () => localStorage.getItem("meridian-theme") === "dark",
    ),
    [menu, setMenu] = useState(false),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState(""),
    [error, setError] = useState(""),
    [focus, setFocus] = useState("AL-1048"),
    [company, setCompany] = useState("ABC"),
    [question, setQuestion] = useState(initialQuestion),
    [reportId, setReportId] = useState("");
  useEffect(() => {
    load()
      .then(setData)
      .catch((e) => setError(String(e.message)));
    const handle = () => {
      setPage(pageFromHash());
      setMenu(false);
      setNotice("");
    };
    window.addEventListener("hashchange", handle);
    return () => window.removeEventListener("hashchange", handle);
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem("meridian-theme", dark ? "dark" : "light");
  }, [dark]);
  const go = (p: Page) => {
    location.hash = p;
    setMenu(false);
  };
  const act: Act = async (work, message) => {
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await work();
      setData(await load());
      setNotice(message);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed.");
    } finally {
      setBusy(false);
    }
  };
  const research = (id: string, q = initialQuestion) => {
    setCompany(id);
    setQuestion(q);
    go("research");
  };
  const report =
    data?.reports.find((r) => r.id === reportId) ?? data?.reports[0];
  const d = data?.overview;
  return (
    <div className="shell">
      <a
        className="skip"
        href="#content"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("content")?.focus();
        }}
      >
        Skip to content
      </a>
      {menu && (
        <button
          className="scrim"
          aria-label="Close navigation"
          onClick={() => setMenu(false)}
        />
      )}
      <aside className={"sidebar " + (menu ? "shown" : "")}>
        <div className="brand">
          <span className="brand-mark">
            <Activity size={25} strokeWidth={2.4} />
          </span>
          <span>
            Meridian<small>Risk intelligence</small>
          </span>
        </div>
        <nav aria-label="Main navigation">
          {sections.map((s) => (
            <div className="nav-group" key={s.title}>
              <h2>{s.title}</h2>
              {s.items.map((i) => (
                <a
                  key={i.id}
                  href={"#" + i.id}
                  aria-current={page === i.id ? "page" : undefined}
                  onClick={() => setMenu(false)}
                >
                  <i.icon size={17} />
                  {i.name}
                  {i.id === "alerts" && d && (
                    <small>
                      {d.alerts.filter((a) => a.status === "open").length}
                    </small>
                  )}
                  {i.id === "approvals" && !!d?.pending && (
                    <small>{d.pending}</small>
                  )}
                </a>
              ))}
            </div>
          ))}
        </nav>
        <div className="side-foot">
          <div className="env-dot" />
          <div>
            <b>Local workspace</b>
            <small>Synthetic financial data</small>
          </div>
        </div>
      </aside>
      <div className="main">
        <header className="top">
          <div>
            <button
              className="mobile-toggle icon-btn"
              aria-label="Open navigation"
              onClick={() => setMenu(true)}
            >
              <Menu size={20} />
            </button>
            <Layers3 size={16} />
            <span>Workspace</span>
            <ChevronRight size={13} />
            <b>
              {
                sections.flatMap((s) => [...s.items]).find((i) => i.id === page)
                  ?.name
              }
            </b>
          </div>
          <div>
            <span className="mode">
              <Radio size={13} />
              {d?.mode === "live" ? "Live model" : "Demo mode"}
            </span>
            <button
              className="icon-btn"
              aria-label={dark ? "Use light theme" : "Use dark theme"}
              onClick={() => setDark(!dark)}
            >
              {dark ? <Sun size={17} /> : <Moon size={17} />}
            </button>
          </div>
        </header>
        <main id="content" tabIndex={-1}>
          <div className="page-heading">
            <div>
              <div className="eyebrow">
                <span />
                {page === "overview"
                  ? "Intelligence desk"
                  : sections.find((s) => s.items.some((i) => i.id === page))
                      ?.title}
              </div>
              <h1>{titles[page][0]}</h1>
              <p>{titles[page][1]}</p>
            </div>
            {page === "overview" && (
              <button className="primary" onClick={() => research("ABC")}>
                <Plus size={16} /> New research
              </button>
            )}
          </div>
          {error && (
            <div role="alert" className="notice err">
              {error}
              {!data && (
                <button
                  onClick={() => act(async () => {}, "Workspace loaded.")}
                >
                  Retry
                </button>
              )}
              <button aria-label="Dismiss error" onClick={() => setError("")}>
                <X size={14} />
              </button>
            </div>
          )}
          {notice && (
            <div role="status" className="notice">
              {notice}
              <button
                aria-label="Dismiss notification"
                onClick={() => setNotice("")}
              >
                <X size={14} />
              </button>
            </div>
          )}
          {!data ? (
            <p aria-live="polite">
              {error ? "Workspace unavailable." : "Loading workspace…"}
            </p>
          ) : (
            <>
              {page === "overview" && (
                <Dashboard
                  data={data}
                  go={go}
                  inspect={(id) => {
                    setFocus(id);
                    go("alerts");
                  }}
                  research={research}
                />
              )}
              {page === "research" && (
                <Research
                  data={data}
                  company={company}
                  setCompany={setCompany}
                  question={question}
                  setQuestion={setQuestion}
                  report={report}
                  select={(r) => setReportId(r.id)}
                  busy={busy}
                  go={go}
                  run={() =>
                    act(async () => {
                      const r = await api<Report>("reports", {
                        company,
                        question,
                        confirm: true,
                      });
                      setReportId(r.id);
                    }, "Research report saved.")
                  }
                />
              )}
              {page === "alerts" && (
                <Alerts {...{ data, focus, setFocus, research, act, busy }} />
              )}
              {page === "documents" && <Library {...{ data, act, busy }} />}
              {page === "approvals" && <Approvals {...{ data, act, busy }} />}
              {page === "workflow" && (
                <Trace
                  reports={data.reports}
                  report={report}
                  select={(r) => setReportId(r.id)}
                />
              )}
              {page === "evaluation" && (
                <Evaluations {...{ data, act, busy }} />
              )}
              {page === "audit" && <Audit data={data} />}
              <footer>
                <span>
                  <span className="foot-dot" /> Synthetic portfolio · As of{" "}
                  {date(data.overview.as_of)}
                </span>
                <span>Meridian research console</span>
              </footer>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
