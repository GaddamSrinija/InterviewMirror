
  import { createContext, useContext, useState, useEffect } from "react";
  import api from "../api/client";

  const AuthContext = createContext(null);

  export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      const stored = localStorage.getItem("user");
      if (stored) {
        setUser(JSON.parse(stored));
      }
      setLoading(false);
    }, []);

    const login = async (email, password) => {
      const res = await api.post("/api/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      setUser(res.data.user);
    };

    const register = async (email, username, password) => {
      const res = await api.post("/api/auth/register", { email, username, password });
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      setUser(res.data.user);
    };

    const logout = () => {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setUser(null);
    };

    return (
      <AuthContext.Provider value={{ user, loading, login, register, logout }}>
        {children}
      </AuthContext.Provider>
    );
  }

  export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be inside AuthProvider");
    return ctx;
  }
