import { api } from "../../api";
import { useAsync } from "../../hooks";
import { Empty, ErrorNote, fmtDate, fmtMoney, fmtNum, Loading } from "../../components/ui";

export default function Holdings({ portfolioId }) {
  const { data, error, loading, reload } = useAsync(() => api.portfolios.holdings(portfolioId), [portfolioId]);

  if (loading) return <Loading />;
  if (error) return <ErrorNote error={error} onRetry={reload} />;
  if (data.length === 0)
    return (
      <Empty title="No holdings">
        <p>Holdings are built automatically from your transactions. Record a BUY to open a position.</p>
      </Empty>
    );

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Asset</th>
            <th>Type</th>
            <th>Exchange</th>
            <th className="num">Quantity</th>
            <th className="num">Average cost</th>
            <th className="num">Last updated</th>
          </tr>
        </thead>
        <tbody>
          {data.map((h) => (
            <tr key={h.id}>
              <td><strong>{h.asset.symbol}</strong><small>{h.asset.name}</small></td>
              <td>{h.asset.asset_type}</td>
              <td>{h.asset.exchange || "—"}</td>
              <td className="num">{fmtNum(h.quantity)}</td>
              <td className="num">{fmtMoney(h.average_cost)}</td>
              <td className="num">{fmtDate(h.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
