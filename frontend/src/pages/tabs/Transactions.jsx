import { useState } from "react";
import { api } from "../../api";
import { useAsync } from "../../hooks";
import {
  Empty, ErrorNote, Field, fmtDateTime, fmtMoney, fmtNum, Loading, Modal, tone,
} from "../../components/ui";

// <input type="datetime-local"> wants "YYYY-MM-DDTHH:mm" in local time.
const nowLocal = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16);

function TransactionForm({ portfolioId, assets, onClose, onSaved }) {
  const [f, setF] = useState({
    asset_id: assets[0]?.id ?? "",
    transaction_type: "BUY",
    quantity: "",
    price: "",
    fees: "0",
    executed_at: nowLocal(),
  });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.transactions.create(portfolioId, {
        ...f,
        fees: f.fees || "0",
        executed_at: new Date(f.executed_at).toISOString(),
      });
      onSaved();
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  };

  return (
    <Modal title="Record a transaction" onClose={onClose}>
      <form onSubmit={submit}>
        <ErrorNote error={error} />
        <Field label="Asset">
          <select value={f.asset_id} onChange={set("asset_id")} required>
            {assets.map((a) => (
              <option key={a.id} value={a.id}>{a.symbol} — {a.name}</option>
            ))}
          </select>
        </Field>
        <div className="row">
          <Field label="Type">
            <select value={f.transaction_type} onChange={set("transaction_type")}>
              <option value="BUY">Buy</option>
              <option value="SELL">Sell</option>
            </select>
          </Field>
          <Field label="Date and time">
            <input type="datetime-local" value={f.executed_at} onChange={set("executed_at")} required />
          </Field>
        </div>
        <div className="row">
          <Field label="Quantity">
            <input type="number" step="any" min="0" value={f.quantity} onChange={set("quantity")} required />
          </Field>
          <Field label="Price per unit">
            <input type="number" step="any" min="0" value={f.price} onChange={set("price")} required />
          </Field>
        </div>
        <Field label="Fees">
          <input type="number" step="any" min="0" value={f.fees} onChange={set("fees")} />
        </Field>
        <div className="form-actions">
          <button type="button" className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : "Record transaction"}</button>
        </div>
      </form>
    </Modal>
  );
}

export default function Transactions({ portfolioId }) {
  const tx = useAsync(() => api.transactions.list(portfolioId), [portfolioId]);
  const assets = useAsync(() => api.assets.list(), []);
  const [adding, setAdding] = useState(false);

  if (tx.loading || assets.loading) return <Loading />;
  if (tx.error) return <ErrorNote error={tx.error} onRetry={tx.reload} />;

  const symbolOf = Object.fromEntries((assets.data ?? []).map((a) => [a.id, a.symbol]));
  const canAdd = (assets.data ?? []).length > 0;

  return (
    <>
      <div className="page-head" style={{ marginBottom: "var(--s3)" }}>
        <p className="muted" style={{ margin: 0 }}>
          Transactions are the source of truth — holdings and realized P&L are derived from them.
        </p>
        <button className="btn btn-primary" disabled={!canAdd} onClick={() => setAdding(true)}>
          Record transaction
        </button>
      </div>

      {!canAdd && (
        <div className="note">
          No assets exist yet. Add some to the assets table first (see <code>seed_assets.py</code>).
        </div>
      )}

      {tx.data.length === 0 ? (
        <Empty title="No transactions yet">
          <p>Record your first BUY to open a position.</p>
        </Empty>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Executed</th>
                <th>Asset</th>
                <th>Type</th>
                <th className="num">Quantity</th>
                <th className="num">Price</th>
                <th className="num">Fees</th>
                <th className="num">Realized P&L</th>
              </tr>
            </thead>
            <tbody>
              {tx.data.map((t) => (
                <tr key={t.id}>
                  <td>{fmtDateTime(t.executed_at)}</td>
                  <td><strong>{symbolOf[t.asset_id] ?? "—"}</strong></td>
                  <td><span className={`pill ${t.transaction_type === "BUY" ? "buy" : "sell"}`}>{t.transaction_type === "BUY" ? "Buy" : "Sell"}</span></td>
                  <td className="num">{fmtNum(t.quantity)}</td>
                  <td className="num">{fmtMoney(t.price)}</td>
                  <td className="num">{fmtMoney(t.fees)}</td>
                  <td className={`num ${tone(t.realized_pnl)}`}>
                    {t.transaction_type === "SELL" ? fmtMoney(t.realized_pnl) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {adding && (
        <TransactionForm
          portfolioId={portfolioId}
          assets={assets.data}
          onClose={() => setAdding(false)}
          onSaved={() => {
            setAdding(false);
            tx.reload();
          }}
        />
      )}
    </>
  );
}
