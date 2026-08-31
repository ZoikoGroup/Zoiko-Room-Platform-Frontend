import { apiClientFetch } from "@/lib/api-client";
import { AppNotification } from "@/lib/types";

/**
 * Shared client for the notification bell, used by both the Admin and USER
 * topbars against their own base path -- the backend scopes every query to the
 * authenticated caller, so there's no cross-role data risk in sharing this file.
 */
export const ADMIN_NOTIFICATIONS_BASE = "/api/notifications";
export const USER_NOTIFICATIONS_BASE = "/api/users/notifications";

export function listNotifications(basePath: string): Promise<AppNotification[]> {
  return apiClientFetch<AppNotification[]>(basePath);
}

export function getUnreadNotificationCount(basePath: string): Promise<{ count: number }> {
  return apiClientFetch<{ count: number }>(`${basePath}/unread-count`);
}

export function markNotificationRead(basePath: string, id: number): Promise<AppNotification> {
  return apiClientFetch<AppNotification>(`${basePath}/${id}/read`, { method: "PATCH" });
}

export function markAllNotificationsRead(basePath: string): Promise<{ updated: number }> {
  return apiClientFetch<{ updated: number }>(`${basePath}/read-all`, { method: "PATCH" });
}
