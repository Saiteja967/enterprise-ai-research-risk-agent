import { useState, type ReactNode } from "react";
import { Activity, ArrowUpRight, Inbox } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { Period } from "./types";
import { money } from "./domain";
export function Panel({
  title,
  sub,
  action,
  children,
}: {
  title: string;
  sub?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          {sub && <p>{sub}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="empty">
      <Inbox size={25} />
      <p>{children}</p>
    </div>
  );
}
export function Badge({ value }: { value: string }) {
  return (
    <span className={"badge " + value}>
      <i />
      {value}
    </span>
  );
}
export function Metric({
  label,
  value,
  foot,
  icon: Icon = Activity,
  tone = "mint",
}: {
  label: string;
  value: string | number;
  foot: string;
  icon?: LucideIcon;
  tone?: string;
}) {
  return (
    <div className="metric">
      <div className="metric-top">
        <span>{label}</span>
        <span className={"tile " + tone}>
          <Icon size={17} />
        </span>
      </div>
      <strong>{value}</strong>
      <small>{foot}</small>
    </div>
  );
}
export function More({
  children,
  onClick,
}: {
  children: ReactNode;
  onClick: () => void;
}) {
  return (
    <button className="text-btn" onClick={onClick}>
      {children}
      <ArrowUpRight size={14} />
    </button>
  );
}
export function Trend({ periods }: { periods: Period[] }) {
  const [range, setRange] = useState(6);
  const [active, setActive] = useState<number | null>(null);
  const series = periods.slice(-range);
  const values = series.map((p) =>
    p.amount ? (100 * p.overdue) / p.amount : 0,
  );
  if (!series.length) return <Empty>No receivable periods available.</Empty>;
  const high = Math.max(4, Math.ceil(Math.max(...values) / 4) * 4);
  const w = 660,
    h = 165,
    l = 38,
    r = 18,
    t = 12,
    b = 24;
  const y = (n: number) => h - b - (n / high) * (h - b - t);
  const coords = values.map((v, i) => [
    l + ((w - l - r) * i) / Math.max(1, values.length - 1),
    y(v),
  ]);
  const line = coords
    .map(([x, y], i) => (i ? "L" : "M") + x.toFixed(2) + "," + y.toFixed(2))
    .join(" ");
  const idx =
    active === null ? series.length - 1 : Math.min(active, series.length - 1);
  const selected = series[idx];
  return (
    <Panel
      title="Receivables at risk"
      sub="Overdue balance as a share of total receivables"
      action={
        <select
          aria-label="Chart range"
          value={range}
          onChange={(e) => {
            setRange(Number(e.target.value));
            setActive(null);
          }}
        >
          <option value={6}>6 months</option>
          <option value={3}>3 months</option>
        </select>
      }
    >
      <div className="chart-value">
        <strong>
          {values[idx].toFixed(1)}
          <span>%</span>
        </strong>
        <small>
          {money(selected.overdue)} overdue · {selected.period}
        </small>
      </div>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="trend"
        role="img"
        aria-label={
          "Overdue receivables percentage by month. " +
          series
            .map((p, i) => p.period + " " + values[i].toFixed(1) + " percent")
            .join(", ")
        }
      >
        <defs>
          <linearGradient id="fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#19a98c" stopOpacity=".27" />
            <stop offset="100%" stopColor="#19a98c" stopOpacity=".015" />
          </linearGradient>
        </defs>
        {[0, 1, 2, 3, 4].map((n) => (
          <g key={n}>
            <line
              x1={l}
              x2={w - r}
              y1={y((high * n) / 4)}
              y2={y((high * n) / 4)}
              className="gridline"
            />
            <text x={1} y={y((high * n) / 4) + 4}>
              {(high * n) / 4}%
            </text>
          </g>
        ))}
        <path
          d={
            line +
            " L" +
            coords.at(-1)![0] +
            "," +
            (h - b) +
            " L" +
            l +
            "," +
            (h - b) +
            " Z"
          }
          fill="url(#fill)"
        />
        <path
          d={line}
          fill="none"
          stroke="#159b80"
          strokeWidth="3.2"
          strokeLinejoin="round"
        />
        {coords.map(([x, y], i) => (
          <g key={i}>
            <circle
              cx={x}
              cy={y}
              r={idx === i ? 5 : 3.3}
              fill="#159b80"
              stroke="var(--panel)"
              strokeWidth="2"
            />
            <text x={x} y={h - 4} textAnchor="middle">
              {new Date(series[i].period + "-15T12:00Z").toLocaleString(
                "en-US",
                { month: "short", timeZone: "UTC" },
              )}
            </text>
          </g>
        ))}
      </svg>
      <div className="chart-months" aria-label="Inspect chart period">
        {series.map((p, i) => (
          <button
            key={p.period}
            aria-pressed={idx === i}
            onClick={() => setActive(i)}
          >
            {p.period.slice(5)}
          </button>
        ))}
      </div>
    </Panel>
  );
}
