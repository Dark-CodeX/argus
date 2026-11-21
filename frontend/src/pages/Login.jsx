import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { ThemeToggle } from "../components/Layout";
import { ErrorNote, Field } from "../components/ui";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email.trim(), password);
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
          <h2>Welcome back</h2>
          <ErrorNote error={error} />
          <Field label="Email">
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
          </Field>
          <Field label="Password">
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </Field>
          <button className="btn btn-primary" style={{ width: "100%" }} disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="auth-foot">New to Argus? <Link to="/register">Create an account</Link></p>
      </div>
    </div>
  );
}
