"""
Advanced CORS Middleware for FastAPI 2025
Dynamic origin validation and optimized preflight handling
"""

import fnmatch
from typing import Callable, Set
from urllib.parse import urlparse

from fastapi import Request, Response, status
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class AdvancedCORSMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with dynamic origin validation
    and optimized preflight response handling
    """

    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = set(settings.allowed_origins)
        self.allow_credentials = True
        self.allow_methods = set(settings.cors_allow_methods)
        self.allow_headers = set(settings.cors_allow_headers)
        self.expose_headers = set(settings.cors_expose_headers)
        self.max_age = 86400  # 24 hours

    def is_allowed_origin(self, origin: str) -> bool:
        """
        Check if origin is allowed with wildcard support
        """
        if origin in self.allowed_origins:
            return True

        # Check wildcard patterns
        for allowed in self.allowed_origins:
            if "*" in allowed and fnmatch.fnmatch(origin, allowed):
                return True

        # Allow same-origin in development
        if settings.environment == "development":
            parsed = urlparse(origin)
            if parsed.hostname in ["localhost", "127.0.0.1", "::1"]:
                return True

        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get("origin")

        # Handle preflight requests
        if request.method == "OPTIONS":
            if origin and self.is_allowed_origin(origin):
                response = PlainTextResponse("OK", status_code=200)

                # CORS headers for preflight
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = ", ".join(
                    self.allow_methods
                )
                response.headers["Access-Control-Allow-Headers"] = ", ".join(
                    self.allow_headers
                )
                response.headers["Access-Control-Max-Age"] = str(self.max_age)

                # Vary header for caching
                response.headers["Vary"] = "Origin, Access-Control-Request-Headers"

                return response
            else:
                # Reject preflight from unauthorized origins
                return PlainTextResponse("CORS preflight rejected", status_code=403)

        # Process actual request
        response = await call_next(request)

        # Add CORS headers to response
        if origin and self.is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = ", ".join(
                self.expose_headers
            )
            response.headers["Vary"] = "Origin"

        return response
