import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAsync } from "../hooks";
import PortfolioForm from "../components/PortfolioForm";
import { Empty, ErrorNote, fmtDate, fmtMoney, Loading, PageHead, tone } from "../components/ui";

// Each card quietly loads its own valuation; if that fails (no holdings/prices) it just shows nothing.
function PortfolioCard({ p }) {
  const { data: v } = useAsync(() => api.portfolios.valuation(p.id).catch(() => null), [p.id]);
  return (
    <Link to={`/portfolios/${p.id}`} className="card card-link">
      <h3>{p.name}</h3>
      <p className="desc">{p.description || "No description."}</p>
      <div className="card-foot">
        <span className="muted">Created {fmtDate(p.created_at)}</span>
        {v && (
          <span>
            {fmtMoney(v.total_market_value)}{" "}
            <span className={tone(v.total_pnl)}>({fmtMoney(v.total_pnl)})</span>
          </span>
        )}
      </div>
    </Link>
  );
}

export default function Portfolios() {
  const nav = useNavigate();
  const { data, error, loading, reload } = useAsync(() => api.portfolios.list(), []);
  const [creating, setCreating] = useState(false);

  return (
    <>
      <PageHead title="Your portfolios" sub="Each portfolio tracks its own holdings, transactions and risk.">
        <button className="btn btn-primary" onClick={() => setCreating(true)}>New portfolio</button>
      </PageHead>

      <ErrorNote error={error} onRetry={reload} />
      {loading && <Loading />}

      {data && data.length === 0 && (
        <Empty title="No portfolios yet">
          <p>Create your first portfolio, then record a few transactions to see valuation and risk.</p>
          <button className="btn btn-primary" onClick={() => setCreating(true)}>Create a portfolio</button>
        </Empty>
      )}

      {data && data.length > 0 && (
        <div className="grid-cards">
          {data.map((p) => <PortfolioCard key={p.id} p={p} />)}
        </div>
      )}

      {creating && (
        <PortfolioForm
          onClose={() => setCreating(false)}
          onSaved={(p) => nav(`/portfolios/${p.id}`)}
        />
      )}
    </>
  );
}
