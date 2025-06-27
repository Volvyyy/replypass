"""
Core Security Utilities for FastAPI 2025
Provides security helper functions and validators
"""

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    argon2__rounds=4,
    argon2__memory_cost=65536,
    argon2__parallelism=2,
)


class SecurityUtils:
    """
    Security utility functions
    """

    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a secure CSRF token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_csrf_token(token: str, session_token: str) -> bool:
        """Verify CSRF token using constant-time comparison"""
        return secrets.compare_digest(token, session_token)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using Argon2"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent XSS and injection
        """
        # Remove null bytes
        text = text.replace("\x00", "")

        # Limit length
        text = text[:max_length]

        # Remove control characters except newlines and tabs
        text = "".join(
            char
            for char in text
            if char == "\n"
            or char == "\t"
            or (ord(char) >= 32 and ord(char) <= 126)
            or ord(char) >= 128
        )

        # HTML entity encoding for special characters
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }

        for char, escape in html_escape_table.items():
            text = text.replace(char, escape)

        return text.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def generate_secure_filename(filename: str) -> str:
        """
        Generate secure filename to prevent path traversal
        """
        # Remove path components
        filename = filename.split("/")[-1].split("\\")[-1]

        # Remove special characters
        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")

        return (
            f"{name}_{timestamp}_{secrets.token_hex(4)}.{ext}"
            if ext
            else f"{filename}_{timestamp}_{secrets.token_hex(4)}"
        )

    @staticmethod
    def create_jwt_token(
        user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT token with user data
        """
        to_encode = user_data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                seconds=settings.jwt_expiration_seconds
            )

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "jti": secrets.token_urlsafe(16),  # JWT ID for revocation
            }
        )

        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm="HS256")

    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        """
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify webhook signature (Stripe-style)
        """
        expected_signature = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()

        return secrets.compare_digest(signature, expected_signature)

    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """
        Mask sensitive data for logging
        """
        if len(data) <= visible_chars * 2:
            return "*" * len(data)

        return f"{data[:visible_chars]}{'*' * (len(data) - visible_chars * 2)}{data[-visible_chars:]}"
