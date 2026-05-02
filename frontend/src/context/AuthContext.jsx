import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api, setToken } from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setAuthToken] = useState(() => localStorage.getItem("trustlens_token"));
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("trustlens_user");
    return raw ? JSON.parse(raw) : null;
  });

  useEffect(() => {
    setToken(token);
  }, [token]);

  async function login(email, password) {
    const data = await api("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    persistSession(data);
  }

  async function signup(name, email, password) {
    const data = await api("/auth/signup", {
      method: "POST",
      body: { name, email, password },
    });
    persistSession(data);
  }

  function persistSession(data) {
    setAuthToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("trustlens_token", data.access_token);
    localStorage.setItem("trustlens_user", JSON.stringify(data.user));
  }

  function logout() {
    setAuthToken(null);
    setUser(null);
    localStorage.removeItem("trustlens_token");
    localStorage.removeItem("trustlens_user");
  }

  const value = useMemo(() => ({ token, user, login, signup, logout }), [token, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
