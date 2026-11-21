import { useState } from "react";
import { api } from "../api";
import { useAsync } from "../hooks";
import { LineChart } from "../components/Charts";
import { Empty, ErrorNote, fmtDate, fmtMoney, fmtNum, fmtPct, Loading, PageHead, Stat, tone } from "../components/ui";

const RANGES = { "1M": 30, "3M": 90, "6M": 182, "1Y": 365, All: null };

function startFor(range) {
  const days = RANGES[range];
  if (!days) return undefined;
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

export default function Markets() {
  const assets = useAsync(() => api.assets.list(), []);
  const [picked, setPicked] = useState(null);
  const [range, setRange] = useState("6M");

  const symbol = picked ?? assets.data?.[0]?.symbol ?? null;
  const prices = useAsync(
    () => (symbol ? api.assets.prices(symbol, startFor(range)) : Promise.resolve([])),
    [symbol, range]
  );

  if (assets.loading) return <Loading />;
  if (assets.error) return <ErrorNote error={assets.error} onRetry={assets.reload} />;
  if (assets.data.length === 0)
    return (
      <>
        <PageHead title="Markets" />
        <Empty title="No assets yet">
          <p>Add assets to the database (see <code>seed_assets.py</code>), then load their prices.</p>
        </Empty>
      </>
    );

  const rows = prices.data ?? [];
  const first = rows[0];
  const last = rows[rows.length - 1];
  const change = first && last ? Number(last.close) / Number(first.close) - 1 : null;
  const asset = assets.data.find((a) => a.symbol === symbol);

  return (
    <>
      <PageHead title="Markets" sub="Daily closing prices stored in your database.">
        <select value={symbol ?? ""} onChange={(e) => setPicked(e.target.value)} aria-label="Asset" style={{ minWidth: 220 }}>
          {assets.data.map((a) => (
            <option key={a.id} value={a.symbol}>{a.symbol} — {a.name}</option>
          ))}
        </select>
      </PageHead>

      <div style={{ marginBottom: "var(--s3)" }}>
        <div className="seg" role="group" aria-label="Date range">
          {Object.keys(RANGES).map((k) => (
            <button key={k} className={range === k ? "on" : ""} onClick={() => setRange(k)}>{k}</button>
          ))}
        </div>
      </div>

      <ErrorNote error={prices.error} onRetry={prices.reload} />
      {prices.loading && <Loading />}

      {!prices.loading && !prices.error && rows.length === 0 && (
        <Empty title={`No prices stored for ${symbol}`}>
          <p>Load history with <code>python insertDataDB.py</code> and enter {symbol} when prompted.</p>
        </Empty>
      )}

      {rows.length > 0 && (
        <>
          <div className="stats">
            <Stat label="Latest close" value={fmtMoney(last.close)} hint={fmtDate(last.date)} />
            <Stat label="Change over range" value={fmtPct(change)} kind={tone(change)} />
            <Stat label="Period high" value={fmtMoney(Math.max(...rows.map((r) => Number(r.high))))} />
            <Stat label="Period low" value={fmtMoney(Math.min(...rows.map((r) => Number(r.low))))} />
          </div>

          <section className="section">
            <h3>{asset?.name}</h3>
            <p className="lede">Closing price. Hover the chart to read a day.</p>
            <div className="card chart-box">
              <LineChart points={rows.map((r) => ({ label: fmtDate(r.date), value: Number(r.close) }))} />
            </div>
          </section>

          <section className="section">
            <h3>Recent sessions</h3>
            <div className="table-wrap" style={{ marginTop: "var(--s2)" }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th className="num">Open</th>
                    <th className="num">High</th>
                    <th className="num">Low</th>
                    <th className="num">Close</th>
                    <th className="num">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(-12).reverse().map((r) => (
                    <tr key={r.date}>
                      <td>{fmtDate(r.date)}</td>
                      <td className="num">{fmtMoney(r.open)}</td>
                      <td className="num">{fmtMoney(r.high)}</td>
                      <td className="num">{fmtMoney(r.low)}</td>
                      <td className="num">{fmtMoney(r.close)}</td>
                      <td className="num">{fmtNum(r.volume, 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </>
  );
}
