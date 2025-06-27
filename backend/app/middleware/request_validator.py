"""
Request Validation Middleware for FastAPI 2025
Validates and sanitizes incoming requests
"""

import re
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validates incoming requests for security threats
    """

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bor\b\s*\d+\s*=\s*\d+)",
        r"(\band\b\s*\d+\s*=\s*\d+)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_file_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "Request too large",
                    "detail": f"Maximum size is {settings.max_file_size} bytes",
                },
            )

        # Validate Content-Type for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")

            # Check for required content types
            valid_content_types = [
                "application/json",
                "multipart/form-data",
                "application/x-www-form-urlencoded",
            ]

            if not any(ct in content_type for ct in valid_content_types):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": "Unsupported media type",
                        "detail": f"Content-Type must be one of: {valid_content_types}",
                    },
                )

        # Check query parameters for injection attempts
        query_string = str(request.url.query)
        if query_string:
            if self._contains_sql_injection(query_string) or self._contains_xss(
                query_string
            ):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Invalid request",
                        "detail": "Potentially malicious content detected",
                    },
                )

        # Check path for directory traversal
        if "../" in request.url.path or "..%2F" in request.url.path.upper():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Invalid request",
                    "detail": "Path traversal attempt detected",
                },
            )

        # Validate headers
        for header_name, header_value in request.headers.items():
            if len(header_value) > 8192:  # 8KB header limit
                return JSONResponse(
                    status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE,
                    content={
                        "error": "Header too large",
                        "detail": f"Header '{header_name}' exceeds maximum size",
                    },
                )

        return await call_next(request)

    def _contains_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns"""
        text_lower = text.lower()
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    def _contains_xss(self, text: str) -> bool:
        """Check for XSS patterns"""
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
