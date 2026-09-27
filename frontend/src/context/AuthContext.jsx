import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, TOKEN_KEY } from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // null = checking, false = signed out

  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) { setUser(false); return; }
    api.get("/auth/me").then(({ data }) => setUser(data)).catch(() => { localStorage.removeItem(TOKEN_KEY); setUser(false); });
  }, []);

  const finish = ({ data }) => { localStorage.setItem(TOKEN_KEY, data.token); setUser(data.user); return data.user; };
  const login = useCallback((email, password) => api.post("/auth/login", { email, password }).then(finish), []);
  const register = useCallback((name, email, password) => api.post("/auth/register", { name, email, password }).then(finish), []);
  const logout = useCallback(() => { localStorage.removeItem(TOKEN_KEY); setUser(false); }, []);

  return <AuthContext.Provider value={{ user, login, register, logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
