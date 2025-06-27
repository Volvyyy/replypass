"""
Structured Logging Middleware for FastAPI 2025
Provides comprehensive request/response logging with security context
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured logging with security event tracking
    """

    def __init__(self, app):
        super().__init__(app)
        self.sensitive_paths = [
            "/api/auth/",
            "/api/users/",
            "/api/payment/",
        ]
        self.excluded_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Collect request data
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "content_length": request.headers.get("content-length"),
        }

        # Add user context if available
        if hasattr(request.state, "user_id"):
            log_data["user_id"] = request.state.user_id

        # Process request
        response = None
        error_data = None

        try:
            response = await call_next(request)
        except Exception as e:
            error_data = {
                "error_type": type(e).__name__,
                "error_message": str(e),
            }
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Add response data
            log_data.update(
                {
                    "duration_ms": round(duration * 1000, 2),
                    "status_code": response.status_code if response else 500,
                    "response_size": (
                        response.headers.get("content-length", 0) if response else 0
                    ),
                }
            )

            # Add error data if present
            if error_data:
                log_data["error"] = error_data

            # Check if this is a sensitive operation
            is_sensitive = any(
                request.url.path.startswith(path) for path in self.sensitive_paths
            )

            # Log level based on status code and sensitivity
            if response and response.status_code >= 500:
                logger.error(f"Server error: {json.dumps(log_data)}")
            elif response and response.status_code >= 400:
                logger.warning(f"Client error: {json.dumps(log_data)}")
            elif is_sensitive:
                logger.info(f"Sensitive operation: {json.dumps(log_data)}")
            else:
                logger.info(f"Request processed: {json.dumps(log_data)}")

            # Log security events
            if response and response.status_code == 401:
                auth_failure_data = {
                    "request_id": request_id,
                    "path": request.url.path,
                    "client_host": log_data["client_host"],
                    "user_agent": log_data["user_agent"],
                }
                logger.warning(
                    f"Authentication failure: {json.dumps(auth_failure_data)}"
                )
            elif response and response.status_code == 403:
                authz_failure_data = {
                    "request_id": request_id,
                    "path": request.url.path,
                    "user_id": log_data.get("user_id"),
                    "client_host": log_data["client_host"],
                }
                logger.warning(
                    f"Authorization failure: {json.dumps(authz_failure_data)}"
                )
            elif response and response.status_code == 429:
                rate_limit_data = {
                    "request_id": request_id,
                    "path": request.url.path,
                    "client_host": log_data["client_host"],
                }
                logger.warning(f"Rate limit exceeded: {json.dumps(rate_limit_data)}")

        return response
