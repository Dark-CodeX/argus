import { useState } from "react";
import { api } from "../api";
import { ErrorNote, Field, Modal } from "./ui";

// Used for both creating (no `initial`) and editing (`initial` = existing portfolio).
export default function PortfolioForm({ initial, onClose, onSaved }) {
  const [name, setName] = useState(initial?.name ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const body = { name: name.trim(), description: description.trim() || null };
      const saved = initial
        ? await api.portfolios.update(initial.id, body)
        : await api.portfolios.create(body);
      onSaved(saved);
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  };

  return (
    <Modal title={initial ? "Edit portfolio" : "New portfolio"} onClose={onClose}>
      <form onSubmit={submit}>
        <ErrorNote error={error} />
        <Field label="Name">
          <input value={name} onChange={(e) => setName(e.target.value)} maxLength={100} required autoFocus />
        </Field>
        <Field label="Description (optional)">
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} maxLength={500} />
        </Field>
        <div className="form-actions">
          <button type="button" className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={busy || !name.trim()}>
            {busy ? "Saving…" : initial ? "Save changes" : "Create portfolio"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
