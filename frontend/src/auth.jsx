import { createContext, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  // On first load: if a token is stored, ask the API who we are.
  useEffect(() => {
    let alive = true;
    if (!getToken()) {
      setReady(true);
      return;
    }
    api
      .me()
      .then((u) => alive && setUser(u))
      .catch(() => setToken(null))
      .finally(() => alive && setReady(true));
    return () => {
      alive = false;
    };
  }, []);

  // api.js fires this event when the token is rejected (expired / invalid).
  useEffect(() => {
    const onLogout = () => setUser(null);
    window.addEventListener("argus:logout", onLogout);
    return () => window.removeEventListener("argus:logout", onLogout);
  }, []);

  const login = async (email, password) => {
    const { access_token } = await api.login(email, password);
    setToken(access_token);
    setUser(await api.me());
  };

  const register = async (data) => {
    await api.register(data);
    await login(data.email, data.password);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
