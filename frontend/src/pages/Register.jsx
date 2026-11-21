import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { ThemeToggle } from "../components/Layout";
import { ErrorNote, Field } from "../components/ui";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({ name: "", gender: "male", email: "", password: "" });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register({ ...form, name: form.name.trim(), email: form.email.trim() });
      nav("/");
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-theme"><ThemeToggle /></div>
      <div className="auth-card">
        <span className="brand">Argus<small>Observe risk. Understand it. Act on it.</small></span>
        <form className="card" onSubmit={submit}>
          <h2>Create your account</h2>
          <ErrorNote error={error} />
          <Field label="Full name">
            <input value={form.name} onChange={set("name")} required autoFocus />
          </Field>
          <Field label="Gender">
            <select value={form.gender} onChange={set("gender")}>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </Field>
          <Field label="Email">
            <input type="email" value={form.email} onChange={set("email")} required />
          </Field>
          <Field label="Password (8 characters or more)">
            <input type="password" value={form.password} onChange={set("password")} minLength={8} maxLength={128} required />
          </Field>
          <button className="btn btn-primary" style={{ width: "100%" }} disabled={busy}>
            {busy ? "Creating…" : "Create account"}
          </button>
        </form>
        <p className="auth-foot">Already registered? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  );
}
