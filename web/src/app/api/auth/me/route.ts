import { NextRequest, NextResponse } from "next/server";
import {
  fetchCurrentSsoUser,
  SsoServiceUnavailableError,
} from "@/lib/auth-sso";

export async function GET(request: NextRequest) {
  const token =
    request.cookies.get("access_token")?.value ||
    request.headers.get("authorization")?.replace("Bearer ", "");

  if (!token) {
    return NextResponse.json(
      { detail: "Chưa đăng nhập (thiếu token)" },
      { status: 401 }
    );
  }

  try {
    // Gọi trực tiếp IdP Manage, tuyệt đối không dùng fallback decode claims
    const user = await fetchCurrentSsoUser(token);
    if (!user) {
      return NextResponse.json(
        { detail: "Phiên đăng nhập không hợp lệ hoặc đã hết hạn" },
        { status: 401 }
      );
    }
    return NextResponse.json(user);
  } catch (error) {
    if (error instanceof SsoServiceUnavailableError) {
      return NextResponse.json({ detail: error.message }, { status: 503 });
    }
    const message =
      error instanceof Error ? error.message : "Lỗi kết nối máy chủ xác thực";
    return NextResponse.json({ detail: message }, { status: 502 });
  }
}
