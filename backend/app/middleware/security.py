"""
Enhanced Security Middleware for FastAPI 2025
Implements comprehensive security headers and policies
"""

import hashlib
import secrets
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security headers middleware
    Implements OWASP recommendations and 2025 best practices
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate nonce for CSP
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response = await call_next(request)

        # Security headers based on environment
        if settings.environment == "production":
            # Strict Transport Security
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )

            # Content Security Policy with nonce
            response.headers["Content-Security-Policy"] = (
                f"default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                f"style-src 'self' 'unsafe-inline'; "
                f"img-src 'self' data: https:; "
                f"font-src 'self'; "
                f"connect-src 'self' {' '.join(settings.allowed_origins)}; "
                f"frame-ancestors 'none'; "
                f"base-uri 'self'; "
                f"form-action 'self';"
            )
        else:
            # Development CSP (more permissive)
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' *; "
                "frame-ancestors 'none';"
            )

        # Standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"  # Modern browsers disable this
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-DNS-Prefetch-Control"] = "off"
        response.headers["X-Download-Options"] = "noopen"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Feature/Permissions Policy (2025 standard)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
            "battery=(), camera=(), cross-origin-isolated=(), "
            "display-capture=(), document-domain=(), encrypted-media=(), "
            "execution-while-not-rendered=(), execution-while-out-of-viewport=(), "
            "fullscreen=(), geolocation=(), gyroscope=(), keyboard-map=(), "
            "magnetometer=(), microphone=(), midi=(), navigation-override=(), "
            "payment=(), picture-in-picture=(), publickey-credentials-get=(), "
            "screen-wake-lock=(), sync-xhr=(), usb=(), web-share=(), "
            "xr-spatial-tracking=(), clipboard-read=(), clipboard-write=(), "
            "gamepad=(), speaker-selection=(), conversion-measurement=(), "
            "focus-without-user-activation=(), hid=(), idle-detection=(), "
            "interest-cohort=(), serial=(), sync-script=(), "
            "trust-token-redemption=(), window-placement=(), "
            "vertical-scroll=()"
        )

        # Cross-Origin policies
        response.headers["Cross-Origin-Embedder-Policy"] = (
            settings.cross_origin_embedder_policy
        )
        response.headers["Cross-Origin-Opener-Policy"] = (
            settings.cross_origin_opener_policy
        )
        response.headers["Cross-Origin-Resource-Policy"] = (
            settings.cross_origin_resource_policy
        )

        # Remove server identification (use del for MutableHeaders)
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        # Cache control for sensitive endpoints
        if request.url.path.startswith("/api/auth/") or request.url.path.startswith(
            "/api/users/"
        ):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, private"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response
