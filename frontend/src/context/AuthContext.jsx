import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api, getApiError } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("cdss_access_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(token));
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadUser() {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await api.get("/users/me");
        if (active) {
          setUser(response.data);
          setError("");
        }
      } catch (err) {
        if (active) {
          localStorage.removeItem("cdss_access_token");
          setToken(null);
          setUser(null);
          setError(getApiError(err, "Session expired"));
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadUser();
    return () => {
      active = false;
    };
  }, [token]);

  async function login(email, password) {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);

    const response = await api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    localStorage.setItem("cdss_access_token", response.data.access_token);
    setToken(response.data.access_token);
    setError("");
  }

  function logout() {
    localStorage.removeItem("cdss_access_token");
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      error,
      isAuthenticated: Boolean(token),
      login,
      logout,
    }),
    [token, user, loading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
