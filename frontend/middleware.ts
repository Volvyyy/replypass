/**
 * Next.js 15 Middleware with Supabase Auth Integration
 *
 * @description Handles authentication, security headers, and route protection
 * @security Implements 2025 security best practices with Supabase SSR
 */

import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/middleware";

export async function middleware(request: NextRequest) {
  const { supabase, response } = await createClient(request);

  // CRITICAL: Always use getUser() for security on server side
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Add security headers (2025 best practices)
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-XSS-Protection", "1; mode=block");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set("X-DNS-Prefetch-Control", "off");

  // HSTS header for HTTPS (production only)
  if (process.env.NODE_ENV === "production") {
    response.headers.set(
      "Strict-Transport-Security",
      "max-age=31536000; includeSubDomains; preload"
    );
  }

  // Content Security Policy (basic)
  response.headers.set(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
  );

  const url = request.nextUrl.clone();

  // Protected routes that require authentication
  const protectedRoutes = ["/dashboard", "/settings", "/profile", "/cases"];
  const authRoutes = ["/auth/login", "/auth/signup", "/auth/reset-password"];

  const isProtectedRoute = protectedRoutes.some((route) =>
    url.pathname.startsWith(route)
  );
  const isAuthRoute = authRoutes.some((route) =>
    url.pathname.startsWith(route)
  );

  // Redirect unauthenticated users from protected routes
  if (isProtectedRoute && !user) {
    url.pathname = "/auth/login";
    url.searchParams.set("redirectTo", request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }

  // Redirect authenticated users from auth routes to dashboard
  if (isAuthRoute && user) {
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - api/webhooks (webhook endpoints should not be protected)
     * - Images and static assets
     */
    "/((?!_next/static|_next/image|favicon.ico|api/webhooks|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)",
  ],
};
