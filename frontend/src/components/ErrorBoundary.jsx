import { Component } from "react";

export default class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Argus UI error:", error, info.componentStack);
  }

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;
    return (
      <div className="container">
        <div className="note error" role="alert">
          <strong>{error.name}: {error.message}</strong>
          <pre style={{ whiteSpace: "pre-wrap", margin: "0.75rem 0 0", fontSize: "0.85rem" }}>
            {String(error.stack || "")}
          </pre>
        </div>
        <button className="btn" onClick={() => (window.location.href = "/")}>
          Back to portfolios
        </button>
      </div>
    );
  }
}