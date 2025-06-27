"""
Authentication Dependencies for FastAPI Routes
Compatible with Supabase Auth 2025

@description Provides dependency injection for user authentication and authorization
@security Implements secure user context extraction from JWT tokens
"""

import logging
import os
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# Security scheme for automatic documentation
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Extract current user information from JWT token

    @param credentials: Authorization credentials from request header
    @returns: User context dictionary with user_id, email, role, etc.
    @raises HTTPException: If authentication fails or token is invalid
    @security Validates Supabase JWT and extracts user claims safely
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
        )

    try:
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not jwt_secret:
            logger.error("SUPABASE_JWT_SECRET environment variable not set")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication configuration error",
            )

        # Decode and validate JWT token
        payload = jwt.decode(
            credentials.credentials,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iat": True,
                "verify_exp": True,
                "require_aud": True,
                "require_exp": True,
            },
        )

        # Extract user information from JWT payload
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "authenticated")

        # Validate required fields
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        # Extract additional user metadata
        user_metadata = payload.get("user_metadata", {})
        app_metadata = payload.get("app_metadata", {})

        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "user_metadata": user_metadata,
            "app_metadata": app_metadata,
            "aud": payload.get("aud"),
            "iss": payload.get("iss"),
            "iat": payload.get("iat"),
            "exp": payload.get("exp"),
        }

    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication processing error",
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """
    Extract current user information from JWT token (optional)

    @param credentials: Authorization credentials from request header
    @returns: User context dictionary if authenticated, None if not authenticated
    @note: Does not raise exceptions for missing authentication
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_roles(*required_roles: str):
    """
    Dependency factory for role-based access control

    @param required_roles: List of roles that are allowed to access the endpoint
    @returns: Dependency function that validates user role
    @example: @app.get("/admin", dependencies=[Depends(require_roles("admin", "moderator"))])
    """

    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role", "authenticated")

        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}",
            )

        return current_user

    return role_checker


def require_user_id(user_id_field: str = "user_id"):
    """
    Dependency factory for user-specific resource access control

    @param user_id_field: Field name in the path parameters containing the user ID
    @returns: Dependency function that validates user owns the resource
    @example: @app.get("/users/{user_id}/profile", dependencies=[Depends(require_user_id())])
    """

    async def user_id_checker(
        path_user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        if current_user["user_id"] != path_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: can only access your own resources",
            )

        return current_user

    return user_id_checker
