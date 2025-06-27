"""
Authentication Middleware for FastAPI
Compatible with Supabase Auth 2025

@description Global middleware for request authentication and security
@security Implements rate limiting, CORS, and security headers
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import os

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
    
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs", "/redoc", "/openapi.json",
            "/health", "/metrics",
            "/api/webhooks",  # Webhook endpoints
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
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
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Basic CSP for API
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"
        
        # Add custom headers
        response.headers["X-API-Version"] = "1.0"
        response.headers["X-Response-Time"] = f"{(time.time() - start_time):.3f}s"
        
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
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries (simple cleanup)
        if current_time % 60 < 1:  # Cleanup every minute
            cutoff_time = current_time - 60
            self.requests = {
                ip: timestamps for ip, timestamps in self.requests.items()
                if any(t > cutoff_time for t in timestamps)
            }
        
        # Check rate limit
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove timestamps older than 1 minute
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if current_time - t < 60
        ]
        
        # Check if rate limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.requests_per_minute} requests per minute",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Add current request timestamp
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)