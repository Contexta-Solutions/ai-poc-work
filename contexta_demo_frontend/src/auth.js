// Demo password gate, browser side. The backend owns the password and signs the
// pass (see contexta_demo_backend/auth.py); this file only stores the pass,
// attaches it to API calls, and tracks wrong tries for the lockout screen.
//
// localStorage, not sessionStorage: the landing cards open each app in a new
// tab, and every tab should share one login.

const API_URL = import.meta.env.VITE_API_URL || '';
const PASS_KEY = 'contexta-pass';
const TRIES_KEY = 'contexta-tries';
const LOCKED_EVENT = 'contexta-locked';

export const MAX_TRIES = 3;
const LOCKOUT_MS = 15 * 60 * 1000;

// Storage can throw (private mode, blocked site data); treat that as empty.
const read = (key) => { try { return localStorage.getItem(key); } catch { return null; } };
const write = (key, value) => { try { localStorage.setItem(key, value); } catch { /* not remembered */ } };
const remove = (key) => { try { localStorage.removeItem(key); } catch { /* nothing to remove */ } };

// The pass is "<expiry seconds>.<signature>"; only the server can check the
// signature, but the expiry saves a round trip to a 401 for a stale pass.
export function hasPass() {
  const exp = Number((read(PASS_KEY) || '').split('.')[0]);
  return exp * 1000 > Date.now();
}

export function onLocked(handler) {
  window.addEventListener(LOCKED_EVENT, handler);
  return () => window.removeEventListener(LOCKED_EVENT, handler);
}

// Drop-in for fetch() on backend calls. A 401 means the pass is missing,
// expired, or the password was changed, so send the app back to the gate.
export async function authFetch(url, options = {}) {
  const headers = new Headers(options.headers);
  const pass = read(PASS_KEY);
  if (pass) headers.set('Authorization', `Bearer ${pass}`);
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    remove(PASS_KEY);
    window.dispatchEvent(new Event(LOCKED_EVENT));
  }
  return res;
}

export function getTries() {
  try {
    return { fails: 0, lockedUntil: 0, ...JSON.parse(read(TRIES_KEY) || '{}') };
  } catch {
    return { fails: 0, lockedUntil: 0 };
  }
}

const saveTries = (tries) => { write(TRIES_KEY, JSON.stringify(tries)); return tries; };

// Resolves to { ok: true } or { ok: false, tries, error? }. A wrong password
// has no error text -- the updated tries say it. The server keeps its own per-IP
// count; this one exists so the screen can show "2 tries left".
export async function login(password) {
  let res;
  try {
    res = await fetch(`${API_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    });
  } catch {
    // Not a wrong password, so it doesn't use up a try.
    return { ok: false, tries: getTries(), error: "Can't reach the server. Check your connection and try again." };
  }

  if (res.ok) {
    const { token } = await res.json();
    write(PASS_KEY, token);
    remove(TRIES_KEY);
    return { ok: true };
  }

  if (res.status === 429) {
    const { detail } = await res.json().catch(() => ({}));
    const wait = (detail?.retry_after || LOCKOUT_MS / 1000) * 1000;
    return { ok: false, tries: saveTries({ fails: 0, lockedUntil: Date.now() + wait }) };
  }

  if (res.status === 401) {
    const fails = getTries().fails + 1;
    const tries = fails >= MAX_TRIES
      ? { fails: 0, lockedUntil: Date.now() + LOCKOUT_MS }
      : { fails, lockedUntil: 0 };
    return { ok: false, tries: saveTries(tries) };
  }

  return { ok: false, tries: getTries(), error: 'Something went wrong. Try again in a moment.' };
}
