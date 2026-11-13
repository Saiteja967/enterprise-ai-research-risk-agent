import {
  ArrowRight,
  BriefcaseBusiness,
  CircleDollarSign,
  FileStack,
  OctagonAlert,
  Radar,
  ScanLine,
} from "lucide-react";
import { Badge, Empty, Metric, More, Panel, Trend } from "./ui";
import {
  type Workspace,
  type Go,
  companyName,
  openAlerts,
  money,
} from "./domain";
export function Dashboard({
  data,
  go,
  inspect,
  research,
}: {
  data: Workspace;
  go: Go;
  inspect: (id: string) => void;
  research: (c: string) => void;
}) {
  const d = data.overview,
    alerts = openAlerts(d.alerts),
    latest = d.periods.at(-1),
    top = alerts.find((a) => a.severity === "high") ?? alerts[0];
  return (
    <>
      <div className="metrics">
        <Metric
          label="Total receivables"
          value={money(latest?.amount ?? 0)}
          foot="June portfolio balance"
          icon={CircleDollarSign}
        />
        <Metric
          label="Monitored companies"
          value={d.companies.length}
          foot="Across the synthetic portfolio"
          icon={BriefcaseBusiness}
          tone="blue"
        />
        <Metric
          label="Open risk alerts"
          value={alerts.length}
          foot={
            alerts.filter((a) => a.severity === "high").length +
            " high severity"
          }
          icon={OctagonAlert}
          tone="amber"
        />
        <Metric
          label="Knowledge sources"
          value={d.documents}
          foot="Approved for research"
          icon={FileStack}
          tone="purple"
        />
      </div>
      <div className="dash-grid">
        <Trend periods={d.periods} />
        <section className="spotlight">
          <div className="spot-kicker">
            <ScanLine size={15} /> Investigation spotlight
          </div>
          <div className="radar-art" aria-hidden="true">
            <Radar size={126} strokeWidth={0.65} />
          </div>
          {top ? (
            <>
              <div className="spot-body">
                <span className="spot-id">
                  {top.company} / {top.id}
                </span>
                <h2>{companyName(d, top.company)}</h2>
                <p>
                  {top.title}. {top.detail.split(". ")[0]}.
                </p>
              </div>
              <button onClick={() => research(top.company)}>
                Open research workspace <ArrowRight size={15} />
              </button>
            </>
          ) : (
            <p>All open investigations have been reviewed.</p>
          )}
        </section>
      </div>
      <Panel
        title="Risk alert register"
        sub="Recent signals across monitored companies"
        action={<More onClick={() => go("alerts")}>View all alerts</More>}
      >
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Signal</th>
                <th>Company</th>
                <th>Severity</th>
                <th>Opened</th>
                <th aria-label="Action" />
              </tr>
            </thead>
            <tbody>
              {alerts.slice(0, 5).map((a) => (
                <tr key={a.id}>
                  <td>
                    <b>{a.title}</b>
                    <small className="mono">{a.id}</small>
                  </td>
                  <td>
                    <span className="ticker">{a.company}</span>
                  </td>
                  <td>
                    <Badge value={a.severity} />
                  </td>
                  <td>{a.opened}</td>
                  <td>
                    <button
                      className="icon-btn"
                      aria-label={"Investigate " + a.title}
                      onClick={() => inspect(a.id)}
                    >
                      <ArrowRight size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!alerts.length && <Empty>No open alerts.</Empty>}
      </Panel>
    </>
  );
}
