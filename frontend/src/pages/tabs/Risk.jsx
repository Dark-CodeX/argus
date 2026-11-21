import { api } from "../../api";
import { useAsync } from "../../hooks";
import { BarList, RangeBar } from "../../components/Charts";
import { Empty, ErrorNote, fmtMoney, fmtNum, fmtPct, Loading, Stat, tone } from "../../components/ui";

export default function Risk({ portfolioId }) {
  const { data: r, error, loading, reload } = useAsync(() => api.portfolios.risk(portfolioId), [portfolioId]);

  if (loading) return <Loading text="Running the risk engine…" />;
  if (error)
    return (
      <>
        <ErrorNote error={error} onRetry={reload} />
        <Empty title="Risk analysis needs data">
          <p>
            You need at least two assets with a current price and recent price history (the last 90 days).
            Load prices with <code>python insertDataDB.py</code>, then try again.
          </p>
        </Empty>
      </>
    );

  const { portfolio: pf, performance: perf, volatility: vol, drawdown, tail_risk: tail, stress_testing: stress, monte_carlo: mc } = r;

  const weightItems = Object.entries(r.portfolio_weights).map(([k, w]) => ({ label: k, value: w, text: fmtPct(w, 1) }));
  const riskItems = Object.entries(r.risk_contribution).map(([k, c]) => ({
    label: k, value: c.risk_contribution_pct, text: fmtPct(c.risk_contribution_pct, 1),
  }));

  const tailRows = [
    ["Historical VaR", tail.historical_var, tail.historical_var_amount, "The loss level exceeded on only 5% of past days."],
    ["Parametric VaR", tail.parametric_var, tail.parametric_var_amount, "The same idea, assuming returns follow a bell curve."],
    ["Historical CVaR", tail.historical_cvar, tail.historical_cvar_amount, "The average loss on those worst 5% of days."],
  ];

  return (
    <>
      {pf.excluded_assets.length > 0 && (
        <div className="note">
          Left out of the analysis for lack of price history: <strong>{pf.excluded_assets.join(", ")}</strong>.
          Figures cover {fmtMoney(pf.analyzed_value)} of {fmtMoney(pf.value)}.
        </div>
      )}

      <div className="stats">
        <Stat label="Analyzed value" value={fmtMoney(pf.analyzed_value)} hint="Current market value of the assets included." />
        <Stat label="Sharpe ratio" value={fmtNum(perf.sharpe_ratio, 2)} hint="Return earned per unit of risk, annualized. Higher is better." />
        <Stat label="Sortino ratio" value={fmtNum(perf.sortino_ratio, 2)} hint="Like Sharpe, but only penalizes downside swings." />
        <Stat label="Maximum drawdown" value={fmtPct(drawdown.maximum)} kind="loss" hint="The largest fall from a peak to a trough in the period." />
      </div>

      <section className="section">
        <h3>Volatility</h3>
        <p className="lede">How much the portfolio’s value moves around. Higher means a bumpier ride.</p>
        <div className="stats">
          <Stat label="Daily" value={fmtPct(vol.daily)} hint="Typical day-to-day swing." />
          <Stat label="Annualized" value={fmtPct(vol.annualized)} hint="Daily figure scaled to a year (× √252)." />
          <Stat label="Mean daily return" value={fmtPct(perf.mean_return, 3)} kind={tone(perf.mean_return)} hint="Average one-day return over the period." />
        </div>
      </section>

      <section className="section">
        <h3>Tail risk</h3>
        <p className="lede">
          What a bad day could look like, at {fmtPct(tail.confidence_level, 0)} confidence.
        </p>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr><th>Measure</th><th className="num">Return</th><th className="num">Potential loss</th></tr>
            </thead>
            <tbody>
              {tailRows.map(([name, ret, amt, hint]) => (
                <tr key={name}>
                  <td><strong>{name}</strong><small>{hint}</small></td>
                  <td className="num loss">{fmtPct(ret)}</td>
                  <td className="num">{fmtMoney(amt)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="section">
        <h3>Allocation and risk</h3>
        <p className="lede">An asset can be a small slice of your money but a large slice of your risk.</p>
        <div className="split">
          <div className="card">
            <h3 style={{ marginBottom: "var(--s3)" }}>Share of value</h3>
            <BarList items={weightItems} />
          </div>
          <div className="card">
            <h3 style={{ marginBottom: "var(--s3)" }}>Share of risk</h3>
            <BarList items={riskItems} />
          </div>
        </div>
      </section>

      <section className="section">
        <h3>Stress test</h3>
        <p className="lede">What happens if every asset falls 10% at once.</p>
        <div className="stats">
          <Stat label="Before" value={fmtMoney(stress.original_value)} />
          <Stat label="After" value={fmtMoney(stress.stressed_value)} />
          <Stat label="Impact" value={fmtMoney(stress.pnl)} kind={tone(stress.pnl)} hint={fmtPct(stress.pnl_percentage)} />
        </div>
      </section>

      <section className="section">
        <h3>Monte Carlo simulation</h3>
        <p className="lede">
          {fmtNum(mc.simulations, 0)} simulated one-day outcomes. The shaded band holds the middle 90%.
        </p>
        <div className="card">
          <RangeBar
            min={mc.minimum_value}
            max={mc.maximum_value}
            low={mc.percentile_5}
            high={mc.percentile_95}
            median={mc.median_value}
            start={pf.analyzed_value}
            format={fmtMoney}
          />
          <div className="stats" style={{ marginTop: "var(--s3)" }}>
            <Stat label="5th percentile" value={fmtMoney(mc.percentile_5)} kind="loss" hint="Only 5% of outcomes were worse." />
            <Stat label="Median" value={fmtMoney(mc.median_value)} />
            <Stat label="95th percentile" value={fmtMoney(mc.percentile_95)} kind="gain" hint="Only 5% of outcomes were better." />
          </div>
        </div>
      </section>
    </>
  );
}
