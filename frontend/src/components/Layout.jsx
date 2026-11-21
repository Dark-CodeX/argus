import { NavLink, Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth";
import { useTheme } from "../hooks";

export function ThemeToggle() {
  const [theme, toggle] = useTheme();
  return (
    <button className="btn btn-sm" onClick={toggle} aria-label="Toggle colour theme">
      {theme === "light" ? "Dark mode" : "Light mode"}
    </button>
  );
}

export default function Layout() {
  const { user, logout } = useAuth();
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <img src="/lively-logo.svg" width="100" height="100" alt="Argus logo" className="auth-logo" />
          <Link to="/" className="brand">
            Argus
            <small>Financial risk intelligence</small>
          </Link>
          <nav className="nav">
            <NavLink to="/" end>Portfolios</NavLink>
            <NavLink to="/markets">Markets</NavLink>
          </nav>
          <div className="topbar-end">
            <span>{user?.name}</span>
            <ThemeToggle />
            <button className="btn btn-sm" onClick={logout}>Sign out</button>
          </div>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}
