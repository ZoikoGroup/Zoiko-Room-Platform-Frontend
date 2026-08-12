import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { AdminProfile } from "@/lib/auth";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

/** Server-only fetch helper: forwards the browser's auth cookie to the FastAPI backend. */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const cookieStore = await cookies();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      Cookie: cookieStore.toString(),
      ...init?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? `Request to ${path} failed with ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

/** Server-only guard: redirects non-super-admins away from a page. Call at the top of the page component. */
export async function requireSuperAdmin(redirectTo = "/properties"): Promise<AdminProfile> {
  const admin = await apiFetch<AdminProfile>("/api/auth/me");
  if (admin.role !== "super_admin") {
    redirect(redirectTo);
  }
  return admin;
}
