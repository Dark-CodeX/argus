import { api } from "../../api";
import { useAsync } from "../../hooks";
import { Empty, ErrorNote, fmtMoney, fmtNum, Loading, Stat, tone } from "../../components/ui";

export default function Overview({ portfolioId }) {
  const { data: v, error, loading, reload } = useAsync(() => api.portfolios.valuation(portfolioId), [portfolioId]);

  if (loading || (!v && !error)) return <Loading />;
  if (error) return <ErrorNote error={error} onRetry={reload} />;

  return (
    <>
      <div className="stats">
        <Stat label="Market value" value={fmtMoney(v.total_market_value)} hint="What your holdings are worth at the latest stored close." />
        <Stat label="Cost basis" value={fmtMoney(v.total_cost_basis)} hint="What you paid, fees included." />
        <Stat label="Unrealized P&L" value={fmtMoney(v.total_unrealized_pnl)} kind={tone(v.total_unrealized_pnl)} hint="Gain or loss on positions you still hold." />
        <Stat label="Realized P&L" value={fmtMoney(v.total_realized_pnl)} kind={tone(v.total_realized_pnl)} hint="Gain or loss locked in by selling." />
        <Stat label="Total P&L" value={fmtMoney(v.total_pnl)} kind={tone(v.total_pnl)} hint="Realized plus unrealized." />
      </div>

      <section className="section">
        <h3>Positions</h3>
        <p className="lede">Valued at each asset’s most recent closing price.</p>
        {(v.holdings ?? []).length === 0 ? (
          <Empty title="Nothing to value yet">
            <p>Record a BUY transaction, and make sure market data has been loaded for that asset.</p>
          </Empty>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Asset</th>
                  <th className="num">Quantity</th>
                  <th className="num">Avg. cost</th>
                  <th className="num">Price</th>
                  <th className="num">Market value</th>
                  <th className="num">Unrealized P&L</th>
                </tr>
              </thead>
              <tbody>
                {(v.holdings ?? []).map((h) => (
                  <tr key={h.holding_id}>
                    <td><strong>{h.symbol}</strong></td>
                    <td className="num">{fmtNum(h.quantity)}</td>
                    <td className="num">{fmtMoney(h.average_cost)}</td>
                    <td className="num">{fmtMoney(h.current_price)}</td>
                    <td className="num">{fmtMoney(h.market_value)}</td>
                    <td className={`num ${tone(h.unrealized_pnl)}`}>{fmtMoney(h.unrealized_pnl)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
