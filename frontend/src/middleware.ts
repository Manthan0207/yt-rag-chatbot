import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

export const runtime = "experimental-edge";

const PUBLIC_PATH = "/";
const PROTECTED_PATH = "/chat";
const SECRET = new TextEncoder().encode(process.env.SECRET_KEY);

async function isValidToken(token: string): Promise<boolean> {
  try {
    await jwtVerify(token, SECRET);
    return true;
  } catch {
    return false;
  }
}

export async function middleware(req: NextRequest) {
  const token = req.cookies.get("token")?.value;
  const { pathname } = req.nextUrl;

  const valid = token ? await isValidToken(token) : false;

  if (!valid && pathname.startsWith(PROTECTED_PATH)) {
    const res = NextResponse.redirect(new URL(PUBLIC_PATH, req.url));
    res.cookies.delete("token");
    return res;
  }

  if (valid && pathname === PUBLIC_PATH) {
    return NextResponse.redirect(new URL(PROTECTED_PATH, req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/chat", "/chat/:path*"],
};
