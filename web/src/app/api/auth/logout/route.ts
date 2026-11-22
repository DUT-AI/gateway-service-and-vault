import { NextResponse } from "next/server";
import { SSO_LOGIN_URL } from "@/lib/auth-urls";

export async function POST() {
  const response = NextResponse.json({
    is_success: true,
    message: "Đăng xuất thành công",
    redirect_url: SSO_LOGIN_URL,
  });

  // Xóa cookie chia sẻ toàn hệ thống .dutai.io.vn
  response.cookies.set({
    name: "access_token",
    value: "",
    domain: ".dutai.io.vn",
    path: "/",
    maxAge: 0,
    httpOnly: true,
    sameSite: "lax",
    secure: true,
  });

  response.cookies.set({
    name: "refresh_token",
    value: "",
    domain: ".dutai.io.vn",
    path: "/",
    maxAge: 0,
    httpOnly: true,
    sameSite: "lax",
    secure: true,
  });

  // Xóa thêm cookie ở host cục bộ (cho localhost development)
  response.cookies.set({
    name: "access_token",
    value: "",
    path: "/",
    maxAge: 0,
    httpOnly: true,
  });

  response.cookies.set({
    name: "refresh_token",
    value: "",
    path: "/",
    maxAge: 0,
    httpOnly: true,
  });

  return response;
}
