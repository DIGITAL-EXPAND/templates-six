import type { AuthTokens } from '@/lib/api/types';

const tokenKey = 'stageos.tokens';

export function readStoredTokens(): AuthTokens | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const raw = window.localStorage.getItem(tokenKey);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as AuthTokens;
  } catch {
    window.localStorage.removeItem(tokenKey);
    return null;
  }
}

export function storeTokens(tokens: AuthTokens) {
  window.localStorage.setItem(tokenKey, JSON.stringify(tokens));
}

export function clearStoredTokens() {
  window.localStorage.removeItem(tokenKey);
}
