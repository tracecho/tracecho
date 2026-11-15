import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { type AuthUser, getMe } from "@/lib/api";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user?: AuthUser) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "regintel_token";
const USER_KEY = "regintel_user";

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_KEY)
  );
  const [user, setUser] = useState<AuthUser | null>(() => {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as AuthUser;
    } catch {
      return null;
    }
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const refreshUser = useCallback(async () => {
    const currentToken = localStorage.getItem(TOKEN_KEY);
    if (!currentToken) {
      setUser(null);
      return;
    }
    try {
      const u = await getMe();
      setUser(u);
      localStorage.setItem(USER_KEY, JSON.stringify(u));
    } catch {
      // If fetching me fails (e.g., token expired), keep user or clear
    }
  }, []);

  const login = useCallback(
    async (newToken: string, newUser?: AuthUser) => {
      localStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
      if (newUser) {
        localStorage.setItem(USER_KEY, JSON.stringify(newUser));
        setUser(newUser);
      } else {
        try {
          setIsLoading(true);
          const u = await getMe();
          localStorage.setItem(USER_KEY, JSON.stringify(u));
          setUser(u);
        } catch {
          // Token valid, user details will be populated later
        } finally {
          setIsLoading(false);
        }
      }
    },
    []
  );

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  }, []);

  // Sync state if token cleared elsewhere
  useEffect(() => {
    const handler = (e: StorageEvent) => {
      if (e.key === TOKEN_KEY && !e.newValue) {
        setToken(null);
        setUser(null);
      }
    };
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: !!token,
      isLoading,
      login,
      logout,
      refreshUser,
    }),
    [user, token, isLoading, login, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }
  return ctx;
}

export default AuthContext;
