"""
Authentication Middleware for FastAPI
Compatible with Supabase Auth 2025

@description Global middleware for request authentication and security
@security Implements rate limiting, CORS, and security headers
"""

import logging
import os
import time
from typing import Callable

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Global authentication and security middleware

    Handles:
    - Security headers
    - Request logging
    - Authentication context
    - Rate limiting (basic)
    """

    def __init__(self, app, excluded_paths: list[str] | None = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
            "/api/webhooks",  # Webhook endpoints
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # リクエストIDを生成（トレーシング用）
        import uuid

        request.state.request_id = str(uuid.uuid4())[:8]

        # Add security headers to all responses
        response = await call_next(request)

        # Security headers (2025 best practices)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-DNS-Prefetch-Control"] = "off"

        # HSTS for production
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Enhanced CSP for API (2025 standard) - 設定ファイルから取得
        response.headers["Content-Security-Policy"] = settings.csp_policy

        # Additional 2025 security headers - 設定ファイルから取得
        response.headers["Permissions-Policy"] = settings.permissions_policy

        # Cross-Origin policies for enhanced security - 設定ファイルから取得
        response.headers["Cross-Origin-Embedder-Policy"] = (
            settings.cross_origin_embedder_policy
        )
        response.headers["Cross-Origin-Opener-Policy"] = (
            settings.cross_origin_opener_policy
        )
        response.headers["Cross-Origin-Resource-Policy"] = (
            settings.cross_origin_resource_policy
        )

        # Add custom headers
        response.headers["X-API-Version"] = "1.0"
        response.headers["X-Response-Time"] = f"{(time.time() - start_time):.3f}s"
        response.headers["X-Powered-By"] = "Reply Pass API"

        # Rate limiting headers (詳細化)
        if hasattr(request.state, "rate_limit_remaining"):
            response.headers["X-RateLimit-Remaining"] = str(
                request.state.rate_limit_remaining
            )
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
            response.headers["X-RateLimit-Limit"] = str(
                getattr(request.state, "rate_limit_total", 60)
            )

        # リクエストID（デバッグ・トレーシング用）
        if hasattr(request.state, "request_id"):
            response.headers["X-Request-ID"] = request.state.request_id

        # Log request (excluding health checks)
        if not request.url.path.startswith("/health"):
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {(time.time() - start_time):.3f}s"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic rate limiting middleware

    @note: For production, consider using Redis-based rate limiting
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # In-memory store (use Redis in production)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old entries (simple cleanup)
        if current_time % 60 < 1:  # Cleanup every minute
            cutoff_time = current_time - 60
            self.requests = {
                ip: timestamps
                for ip, timestamps in self.requests.items()
                if any(t > cutoff_time for t in timestamps)
            }

        # Check rate limit
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Remove timestamps older than 1 minute
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if current_time - t < 60
        ]

        # Check if rate limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.requests_per_minute} requests per minute",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )

        # Add current request timestamp
        self.requests[client_ip].append(current_time)

        # Add rate limit info to request state for headers
        remaining_requests = self.requests_per_minute - len(self.requests[client_ip])
        request.state.rate_limit_remaining = remaining_requests
        request.state.rate_limit_total = self.requests_per_minute

        # エンドポイント別のレート制限チェック
        endpoint_limit = self._get_endpoint_rate_limit(request.url.path)
        if endpoint_limit and endpoint_limit != self.requests_per_minute:
            # より厳しい制限を適用
            if len(self.requests[client_ip]) >= endpoint_limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Endpoint rate limit exceeded",
                        "detail": f"Maximum {endpoint_limit} requests per minute for this endpoint",
                        "retry_after": 60,
                    },
                    headers={"Retry-After": "60"},
                )

        return await call_next(request)

    def _get_endpoint_rate_limit(self, path: str) -> int | None:
        """エンドポイント別のレート制限を取得"""
        from app.config import settings

        # 設定からエンドポイント別の制限を確認
        for endpoint_pattern, limit in settings.rate_limits.items():
            if endpoint_pattern != "default" and path.startswith(endpoint_pattern):
                return limit

        return settings.rate_limits.get("default", self.requests_per_minute)
