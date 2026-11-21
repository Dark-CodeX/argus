// All communication with the FastAPI backend lives in this file.
const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "argus_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) =>
  t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY);

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// FastAPI sends `detail` as a string (our HTTPExceptions) or a list (validation errors).
function readableDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((d) => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`).join("; ");
  return "Something went wrong.";
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  if (auth && getToken()) headers.Authorization = `Bearer ${getToken()}`;

  let res;
  try {
    res = await fetch(BASE + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Cannot reach the Argus API. Is the backend running and CORS enabled?", 0);
  }

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const expired = res.status === 401 || (res.status === 403 && data?.detail === "Not authenticated");
    if (auth && expired) {
      setToken(null);
      window.dispatchEvent(new Event("argus:logout"));
    }
    throw new ApiError(readableDetail(data?.detail), res.status);
  }
  return data;
}

const qs = (params) => {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString();
  return q ? `?${q}` : "";
};

export const api = {
  register: (d) => request("/auth/register", { method: "POST", body: d, auth: false }),
  login: (email, password) =>
    request("/auth/login", { method: "POST", body: { email, password }, auth: false }),
  me: () => request("/users/me"),

  portfolios: {
    list: () => request("/portfolios"),
    get: (id) => request(`/portfolios/${id}`),
    create: (d) => request("/portfolios", { method: "POST", body: d }),
    update: (id, d) => request(`/portfolios/${id}`, { method: "PATCH", body: d }),
    remove: (id) => request(`/portfolios/${id}`, { method: "DELETE" }),
    holdings: (id) => request(`/portfolios/${id}/holdings`),
    valuation: (id) => request(`/portfolios/${id}/valuation`),
    risk: (id) => request(`/portfolios/${id}/risk`),
  },

  transactions: {
    list: (pid) => request(`/portfolios/${pid}/transactions`),
    create: (pid, d) => request(`/portfolios/${pid}/transactions`, { method: "POST", body: d }),
  },

  assets: {
    list: () => request("/assets"),
    prices: (symbol, start_date, end_date) =>
      request(`/assets/${encodeURIComponent(symbol)}/prices${qs({ start_date, end_date })}`),
  },
};
