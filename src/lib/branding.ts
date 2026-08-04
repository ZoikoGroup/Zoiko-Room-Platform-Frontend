const LOGO_KEY = "zoiko_logo_url";
export const LOGO_UPDATED_EVENT = "zoiko:logo-updated";

export function getLogoUrl(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(LOGO_KEY) ?? "";
}

export function setLogoUrl(url: string) {
  if (typeof window === "undefined") return;
  if (url) window.localStorage.setItem(LOGO_KEY, url);
  else window.localStorage.removeItem(LOGO_KEY);
  window.dispatchEvent(new Event(LOGO_UPDATED_EVENT));
}
