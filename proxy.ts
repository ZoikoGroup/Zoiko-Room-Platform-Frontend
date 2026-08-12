import { NextRequest, NextResponse } from "next/server";

const AUTH_COOKIE = "zoiko_admin_token";

export function proxy(request: NextRequest) {
  const hasSession = Boolean(request.cookies.get(AUTH_COOKIE));

  if (!hasSession) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/bookings/:path*",
    "/guests/:path*",
    "/properties/:path*",
    "/payments/:path*",
    "/reviews/:path*",
    "/team/:path*",
    "/settings/:path*",
  ],
};
