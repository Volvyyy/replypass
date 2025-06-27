"""
Supabase JWT Authentication Bearer for FastAPI
Compatible with Supabase Auth 2025 and @supabase/ssr

@description JWT Bearer authentication class for validating Supabase JWT tokens
@security Implements 2025 security best practices for JWT validation
"""

import logging
import os
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    """
    Supabase JWT Bearer authentication

    Validates JWT tokens issued by Supabase Auth against the project's JWT secret.
    Ensures proper audience and issuer validation for enhanced security.
    """

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme. Bearer token required.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token_payload = self.verify_jwt(credentials.credentials)
            if not token_payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or expired token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_jwt(self, token: str) -> Optional[dict]:
        """
        Verify Supabase JWT token

        @param token: JWT token from Authorization header
        @returns: Token payload if valid, None if invalid
        @security Validates audience, issuer, and algorithm for Supabase tokens
        """
        try:
            jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
            if not jwt_secret:
                logger.error("SUPABASE_JWT_SECRET environment variable not set")
                return None

            # Supabase JWT validation with enhanced security
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],  # Supabase uses HS256
                audience="authenticated",  # Required for Supabase Auth
                issuer=os.getenv("SUPABASE_URL"),  # Optional: validate issuer
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iat": True,
                    "verify_exp": True,
                    "verify_nbf": False,
                    "verify_iss": True if os.getenv("SUPABASE_URL") else False,
                    "require_aud": True,
                    "require_iat": True,
                    "require_exp": True,
                },
            )

            # Additional validation for Supabase tokens
            if payload.get("aud") != "authenticated":
                logger.warning("Invalid audience in JWT token")
                return None

            # Ensure user ID exists
            if not payload.get("sub"):
                logger.warning("Missing user ID (sub) in JWT token")
                return None

            return payload

        except JWTError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during JWT validation: {str(e)}")
            return None
