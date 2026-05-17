'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { fetchCurrentUser, loginRequest } from '@/lib/api/endpoints';
import type { AuthTokens, CurrentUser } from '@/lib/api/types';
import { clearStoredTokens, readStoredTokens, storeTokens } from './token-store';

type AuthStatus = 'loading' | 'authenticated' | 'anonymous';

type AuthContextValue = {
  status: AuthStatus;
  user: CurrentUser | null;
  tokens: AuthTokens | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [tokens, setTokens] = useState<AuthTokens | null>(() => readStoredTokens());
  const [status, setStatus] = useState<AuthStatus>(() => (tokens ? 'loading' : 'anonymous'));
  const [user, setUser] = useState<CurrentUser | null>(null);

  const logout = useCallback(() => {
    clearStoredTokens();
    setTokens(null);
    setUser(null);
    setStatus('anonymous');
  }, []);

  useEffect(() => {
    let mounted = true;

    if (!tokens) {
      return;
    }

    fetchCurrentUser(tokens.access)
      .then((currentUser) => {
        if (!mounted) {
          return;
        }
        setUser(currentUser);
        setStatus('authenticated');
      })
      .catch(() => {
        if (!mounted) {
          return;
        }
        logout();
      });

    return () => {
      mounted = false;
    };
  }, [logout, tokens]);

  const login = useCallback(async (email: string, password: string) => {
    setStatus('loading');
    const nextTokens = await loginRequest(email, password);
    const currentUser = await fetchCurrentUser(nextTokens.access);
    storeTokens(nextTokens);
    setTokens(nextTokens);
    setUser(currentUser);
    setStatus('authenticated');
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ status, user, tokens, login, logout }),
    [status, user, tokens, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);

  if (!value) {
    throw new Error('useAuth must be used inside AuthProvider');
  }

  return value;
}
