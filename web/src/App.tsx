import { useEffect, useMemo, useState } from "react";

type Group = { name: string; customers: number; revenue: number; revenue_share: number; recency: number; frequency: number; monetary: number };
type Customer = { CustomerID: number; Recency: number; Frequency: number; Monetary: number; Country: string; RFMscore: string; Segment: string; Cluster: string };
type Summary = { transactions: number; customers: number; revenue: number; period: string[]; n_clusters: number; silhouette: number; avg_order_value: number; monthly_revenue: Record<string, number> };
type Cohorts = { cohorts: string[]; sizes: number[]; retention: (number | null)[][] };
type Assigned = { R: number; F: number; M: number; rfm_score: string; segment: string; cluster: string };

const API = "/api";
const get = <T,>(p: string): Promise<T> => fetch(API + p).then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); });
const gbp = (n: number) => "£" + n.toLocaleString("en-GB", { maximumFractionDigits: 0 });
const PALETTE = ["#818cf8", "#34d399", "#fbbf24", "#f87171", "#38bdf8", "#c084fc"];
const CLUSTER_ORDER = ["Champions", "Loyal Regulars", "Potential", "Hibernating", "Lost", "Dormant"];
const colorOf = (c: string) => PALETTE[Math.max(0, CLUSTER_ORDER.indexOf(c)) % PALETTE.length];

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return <div className="card kpi"><div className="muted">{label}</div><div className="big">{value}</div>{sub && <div className="muted small">{sub}</div>}</div>;
}

function SegmentBars({ data }: { data: Group[] }) {
  const max = Math.max(...data.map((d) => d.customers));
  return (
    <div className="bars">
      {data.map((d) => (
        <div key={d.name} className="barrow">
          <span className="barlabel">{d.name}</span>
          <div className="bartrack"><div className="bar" style={{ width: `${(100 * d.customers) / max}%` }} /></div>
          <span className="barval">{d.customers.toLocaleString()} <span className="muted">· {(100 * d.revenue_share).toFixed(1)}% rev</span></span>
        </div>
      ))}
    </div>
  );
}

function Scatter({ points }: { points: Customer[] }) {
  const W = 560, H = 300, P = 36;
  const lx = (v: number) => Math.log10(v + 1);
  const maxR = 380, maxM = Math.max(...points.map((p) => lx(p.Monetary)));
  const x = (r: number) => P + (r / maxR) * (W - 2 * P);
  const y = (m: number) => H - P - (lx(m) / maxM) * (H - 2 * P);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart">
      <line x1={P} y1={H - P} x2={W - P} y2={H - P} stroke="#475569" />
      <line x1={P} y1={P} x2={P} y2={H - P} stroke="#475569" />
      {[0, 90, 180, 270, 360].map((t) => <text key={t} x={x(t)} y={H - P + 16} className="tick" textAnchor="middle">{t}</text>)}
      {[10, 100, 1000, 10000, 100000].filter((t) => lx(t) <= maxM).map((t) => <text key={t} x={P - 4} y={y(t) + 4} className="tick" textAnchor="end">{t >= 1000 ? `${t / 1000}k` : t}</text>)}
      <text x={W / 2} y={H - 4} className="tick" textAnchor="middle">Recency (days since last order)</text>
      <text x={10} y={P - 12} className="tick">Spend £ (log)</text>
      {points.map((p) => <circle key={p.CustomerID} cx={x(p.Recency)} cy={y(p.Monetary)} r={2.6} fill={colorOf(p.Cluster)} opacity={0.7} />)}
    </svg>
  );
}

function RevenueLine({ monthly }: { monthly: Record<string, number> }) {
  const entries = Object.entries(monthly);
  const W = 1100, H = 220, P = 36, max = Math.max(...entries.map((e) => e[1]));
  const pts = entries.map(([, v], i) => [P + (i / (entries.length - 1)) * (W - 2 * P), H - P - (v / max) * (H - 2 * P)]);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart">
      <polyline points={pts.map((p) => p.join(",")).join(" ")} fill="none" stroke="#818cf8" strokeWidth={2.5} />
      {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r={3} fill="#818cf8" />)}
      {entries.map(([k], i) => i % 2 === 0 && <text key={k} x={pts[i][0]} y={H - 10} className="tick" textAnchor="middle">{k}</text>)}
      <text x={P} y={16} className="tick">peak {gbp(max)}</text>
    </svg>
  );
}

function Heatmap({ c }: { c: Cohorts }) {
  const cols = Math.max(...c.retention.map((r) => r.length));
  return (
    <div className="heat">
      <table>
        <thead><tr><th>Cohort</th><th>Size</th>{Array.from({ length: cols }, (_, i) => <th key={i}>M{i}</th>)}</tr></thead>
        <tbody>
          {c.cohorts.map((name, i) => (
            <tr key={name}><td>{name}</td><td className="muted">{c.sizes[i]}</td>
              {Array.from({ length: cols }, (_, j) => {
                const v = c.retention[i][j];
                if (v == null) return <td key={j} />;
                const a = j === 0 ? 0.9 : Math.min(1, v / 0.5);
                return <td key={j} style={{ background: `rgba(52,211,153,${a})`, color: a > 0.5 ? "#0f172a" : "#e2e8f0" }}>{Math.round(v * 100)}%</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AssignForm() {
  const [form, setForm] = useState({ recency: 12, frequency: 6, monetary: 2100 });
  const [res, setRes] = useState<Assigned | null>(null);
  const [err, setErr] = useState("");
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setErr("");
    const r = await fetch(API + "/assign", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
    if (!r.ok) { setErr("Check the inputs: recency ≥ 0, frequency ≥ 1, spend > 0"); setRes(null); return; }
    setRes(await r.json());
  };
  const field = (k: keyof typeof form, label: string) => (
    <label>{label}<input type="number" value={form[k]} onChange={(e) => setForm({ ...form, [k]: Number(e.target.value) })} /></label>
  );
  return (
    <form onSubmit={submit} className="assign">
      {field("recency", "Days since last order")}
      {field("frequency", "Number of orders")}
      {field("monetary", "Total spend (£)")}
      <button type="submit">Assign segment</button>
      {err && <div className="err">{err}</div>}
      {res && (
        <div className="result">
          <div><span className="muted">RFM score</span><div className="big">{res.rfm_score}</div><div className="muted small">R{res.R} · F{res.F} · M{res.M} (1 = best)</div></div>
          <div><span className="muted">Segment</span><div className="big">{res.segment}</div></div>
          <div><span className="muted">Cluster</span><div className="big" style={{ color: colorOf(res.cluster) }}>{res.cluster}</div></div>
        </div>
      )}
    </form>
  );
}

export default function App() {
  const [summary, setSummary] = useState<Summary>();
  const [segments, setSegments] = useState<Group[]>([]);
  const [clusters, setClusters] = useState<Group[]>([]);
  const [cohorts, setCohorts] = useState<Cohorts>();
  const [sample, setSample] = useState<Customer[]>([]);
  const [segFilter, setSegFilter] = useState("Best Customers");
  const [top, setTop] = useState<Customer[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([get<Summary>("/summary"), get<Group[]>("/segments"), get<Group[]>("/clusters"), get<Cohorts>("/cohorts"), get<Customer[]>("/customers?sample=true&limit=500")])
      .then(([s, sg, cl, co, sa]) => { setSummary(s); setSegments(sg); setClusters(cl); setCohorts(co); setSample(sa); })
      .catch((e) => setError(String(e)));
  }, []);
  useEffect(() => { get<Customer[]>(`/customers?limit=8&segment=${encodeURIComponent(segFilter)}`).then(setTop).catch(() => setTop([])); }, [segFilter]);
  const sortedClusters = useMemo(() => [...clusters].sort((a, b) => CLUSTER_ORDER.indexOf(a.name) - CLUSTER_ORDER.indexOf(b.name)), [clusters]);

  if (error) return <div className="page"><div className="card err">Could not reach the API: {error}</div></div>;
  if (!summary || !cohorts) return <div className="page"><div className="muted">Loading…</div></div>;

  return (
    <div className="page">
      <header>
        <h1>Customer Segmentation</h1>
        <p className="muted">UCI Online Retail · {summary.period[0]} → {summary.period[1]} · RFM scoring + K-Means (k={summary.n_clusters}, silhouette {summary.silhouette})</p>
      </header>

      <section className="kpis">
        <Kpi label="Customers" value={summary.customers.toLocaleString()} />
        <Kpi label="Revenue" value={gbp(summary.revenue)} />
        <Kpi label="Transactions" value={summary.transactions.toLocaleString()} sub="line items after cleaning" />
        <Kpi label="Avg order value" value={gbp(summary.avg_order_value)} />
      </section>

      <section>
        <h2>Behavioural clusters</h2>
        <div className="clusters">
          {sortedClusters.map((c) => (
            <div key={c.name} className="card cluster" style={{ borderTopColor: colorOf(c.name) }}>
              <div className="cname" style={{ color: colorOf(c.name) }}>{c.name}</div>
              <div className="big">{c.customers.toLocaleString()}</div>
              <div className="muted small">{(100 * c.revenue_share).toFixed(1)}% of revenue</div>
              <dl><dt>Median recency</dt><dd>{c.recency} days</dd><dt>Median orders</dt><dd>{c.frequency}</dd><dt>Median spend</dt><dd>{gbp(c.monetary)}</dd></dl>
            </div>
          ))}
        </div>
      </section>

      <section className="grid2">
        <div className="card"><h3>Recency vs spend (500 sampled customers)</h3><Scatter points={sample} />
          <div className="legend">{sortedClusters.map((c) => <span key={c.name}><i style={{ background: colorOf(c.name) }} />{c.name}</span>)}</div></div>
        <div className="card"><h3>RFM segments</h3><SegmentBars data={segments} /></div>
      </section>

      <section className="grid2">
        <div className="card"><h3>Assign a customer</h3><p className="muted small">Score a new or hypothetical customer against the fitted quartiles and K-Means model.</p><AssignForm /></div>
        <div className="card"><h3>Top customers by spend</h3>
          <select value={segFilter} onChange={(e) => setSegFilter(e.target.value)}>{segments.map((s) => <option key={s.name}>{s.name}</option>)}</select>
          <table className="list"><thead><tr><th>ID</th><th>Country</th><th>Recency</th><th>Orders</th><th>Spend</th><th>RFM</th><th>Cluster</th></tr></thead>
            <tbody>{top.map((c) => <tr key={c.CustomerID}><td>{c.CustomerID}</td><td>{c.Country}</td><td>{c.Recency}d</td><td>{c.Frequency}</td><td>{gbp(c.Monetary)}</td><td>{c.RFMscore}</td><td style={{ color: colorOf(c.Cluster) }}>{c.Cluster}</td></tr>)}</tbody></table>
        </div>
      </section>

      <section className="card"><h3>Monthly revenue</h3><p className="muted small">Dec 2011 is a partial month (data ends 9 Dec).</p><RevenueLine monthly={summary.monthly_revenue} /></section>
      <section className="card"><h3>Monthly cohort retention</h3><p className="muted small">Share of each first-purchase cohort that bought again N months later.</p><Heatmap c={cohorts} /></section>
    </div>
  );
}
