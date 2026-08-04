const AUTH_KEY = "zoiko_admin_auth";

export function setAdminAuth(email: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(AUTH_KEY, JSON.stringify({ email, at: Date.now() }));
}

export function isAdminAuthed() {
  if (typeof window === "undefined") return false;
  return Boolean(window.localStorage.getItem(AUTH_KEY));
}

export function getAdminEmail() {
  if (typeof window === "undefined") return "";
  const raw = window.localStorage.getItem(AUTH_KEY);
  if (!raw) return "";
  try {
    return JSON.parse(raw).email ?? "";
  } catch {
    return "";
  }
}

export function clearAdminAuth() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(AUTH_KEY);
}
