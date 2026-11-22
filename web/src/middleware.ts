import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SSO_LOGIN_URL =
  process.env.NEXT_PUBLIC_SSO_LOGIN_URL ||
  "https://workspace.dutai.io.vn/login";

/**
 * Fast Edge token expiration check.
 */
function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return false;
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    const payload = JSON.parse(jsonPayload);
    if (payload.exp && typeof payload.exp === "number") {
      return payload.exp * 1000 < Date.now();
    }
    return false;
  } catch {
    return false;
  }
}

export function middleware(request: NextRequest) {
  const { pathname, href } = request.nextUrl;
  const token = request.cookies.get("access_token")?.value;

  // Bỏ qua các file tĩnh và API public / auth endpoints
  const isPublicRoute =
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api/public") ||
    pathname.startsWith("/api/auth/logout") ||
    pathname.startsWith("/api/auth/me") ||
    pathname === "/login" ||
    pathname === "/register" ||
    pathname === "/" ||
    pathname.includes("favicon.ico");

  if (isPublicRoute) {
    return NextResponse.next();
  }

  // Nếu chưa đăng nhập hoặc token đã hết hạn, chuyển hướng sang Workspace Login
  if (!token || isTokenExpired(token)) {
    const loginUrl = new URL(SSO_LOGIN_URL);
    loginUrl.searchParams.set("redirect", href);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
