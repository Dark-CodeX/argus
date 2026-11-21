import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import { useAsync } from "../hooks";
import PortfolioForm from "../components/PortfolioForm";
import { ErrorNote, Loading, PageHead, Tabs } from "../components/ui";
import Overview from "./tabs/Overview";
import Holdings from "./tabs/Holdings";
import Transactions from "./tabs/Transactions";
import Risk from "./tabs/Risk";

const TABS = [
  ["overview", "Overview"],
  ["holdings", "Holdings"],
  ["transactions", "Transactions"],
  ["risk", "Risk analysis"],
];

export default function PortfolioDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const { data: p, error, loading, reload } = useAsync(() => api.portfolios.get(id), [id]);
  const [tab, setTab] = useState("overview");
  const [editing, setEditing] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const remove = async () => {
    if (!window.confirm(`Delete “${p.name}”? Its holdings and transactions will be removed too.`)) return;
    try {
      await api.portfolios.remove(id);
      nav("/");
    } catch (err) {
      setDeleteError(err);
    }
  };

  if (loading || (!p && !error)) return <Loading />;
  if (error)
    return (
      <>
        <ErrorNote error={error} onRetry={reload} />
        <Link to="/">Back to portfolios</Link>
      </>
    );

  return (
    <>
      <p><Link to="/">← All portfolios</Link></p>
      <PageHead title={p.name} sub={p.description}>
        <button className="btn" onClick={() => setEditing(true)}>Edit</button>
        <button className="btn btn-danger" onClick={remove}>Delete</button>
      </PageHead>
      <ErrorNote error={deleteError} />

      <Tabs tabs={TABS} value={tab} onChange={setTab} />

      {tab === "overview" && <Overview portfolioId={id} />}
      {tab === "holdings" && <Holdings portfolioId={id} />}
      {tab === "transactions" && <Transactions portfolioId={id} />}
      {tab === "risk" && <Risk portfolioId={id} />}

      {editing && (
        <PortfolioForm
          initial={p}
          onClose={() => setEditing(false)}
          onSaved={() => {
            setEditing(false);
            reload();
          }}
        />
      )}
    </>
  );
}
