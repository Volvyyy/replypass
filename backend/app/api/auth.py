"""
Authentication API endpoints
Handles user registration, email confirmation, and profile management
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    EmailConfirmationRequest,
    EmailConfirmationResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserResponse,
)
from app.supabase_client import get_supabase_client
from supabase import AuthApiError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    registration_data: UserRegistrationRequest,
) -> UserRegistrationResponse:
    """
    Register a new user with email/password authentication

    Creates both Supabase Auth user and profile record in users table.
    Requires email confirmation before account activation.

    Args:
        registration_data: User registration information including email, password, and profile

    Returns:
        UserRegistrationResponse with user info and confirmation requirement status

    Raises:
        HTTPException: 409 if user already exists, 400 for validation errors, 500 for system errors
    """
    supabase = get_supabase_client()

    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up(
            {
                "email": registration_data.email,
                "password": registration_data.password,
                "options": {
                    "data": {"display_name": registration_data.profile.display_name}
                },
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed",
            )

        user_id = auth_response.user.id

        try:
            # Create user profile in users table
            profile_data = {
                "auth_id": user_id,
                "email": registration_data.email,
                "profile": {
                    "display_name": registration_data.profile.display_name,
                    "timezone": registration_data.profile.timezone or "UTC",
                    "language": registration_data.profile.language or "ja",
                },
            }

            profile_response = supabase.table("users").insert(profile_data).execute()

            if not profile_response.data:
                raise Exception("Profile creation failed")

        except Exception as profile_error:
            # Rollback: Delete the auth user if profile creation fails
            logger.error(f"Profile creation failed for user {user_id}: {profile_error}")
            try:
                supabase.auth.admin.delete_user(user_id)
            except Exception as rollback_error:
                logger.error(
                    f"Failed to rollback auth user {user_id}: {rollback_error}"
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User registration failed: profile creation error",
            )

        # Prepare response
        user_response = UserResponse(
            id=user_id,
            email=auth_response.user.email,
            email_confirmed_at=auth_response.user.email_confirmed_at,
            created_at=auth_response.user.created_at,
        )

        confirmation_required = auth_response.session is None

        logger.info(f"User registered successfully: {registration_data.email}")

        return UserRegistrationResponse(
            message="Registration successful. Please check your email for confirmation.",
            user=user_response,
            confirmation_required=confirmation_required,
        )

    except AuthApiError as auth_error:
        error_message = str(auth_error).lower()

        if "already" in error_message or "exists" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        else:
            logger.error(f"Supabase Auth error during registration: {auth_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(auth_error)}",
            )

    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise

    except Exception as error:
        logger.error(f"Unexpected error during user registration: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed due to internal error",
        )


@router.post("/confirm", response_model=EmailConfirmationResponse)
async def confirm_email(
    confirmation_data: EmailConfirmationRequest,
) -> EmailConfirmationResponse:
    """
    Confirm user email with OTP token

    Verifies the 6-digit token sent to user's email and activates the account.
    Returns JWT tokens for immediate authentication after confirmation.

    Args:
        confirmation_data: Email and 6-digit confirmation token

    Returns:
        EmailConfirmationResponse with user info and JWT tokens

    Raises:
        HTTPException: 400 for invalid token, 404 if user not found
    """
    supabase = get_supabase_client()

    try:
        # Verify OTP token
        auth_response = supabase.auth.verify_otp(
            {
                "email": confirmation_data.email,
                "token": confirmation_data.token,
                "type": "signup",
            }
        )

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email confirmation failed",
            )

        user_response = UserResponse(
            id=auth_response.user.id,
            email=auth_response.user.email,
            email_confirmed_at=auth_response.user.email_confirmed_at,
            created_at=auth_response.user.created_at,
        )

        logger.info(f"Email confirmed successfully for user: {confirmation_data.email}")

        return EmailConfirmationResponse(
            message="Email confirmed successfully",
            user=user_response,
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
        )

    except AuthApiError as auth_error:
        error_message = str(auth_error).lower()

        if "invalid" in error_message or "expired" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired confirmation token",
            )
        elif "not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        else:
            logger.error(f"Supabase Auth error during email confirmation: {auth_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email confirmation failed: {str(auth_error)}",
            )

    except Exception as error:
        logger.error(f"Unexpected error during email confirmation: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email confirmation failed due to internal error",
        )


@router.post("/resend-confirmation")
async def resend_confirmation_email(email_data: Dict[str, str]) -> Dict[str, str]:
    """
    Resend email confirmation

    Sends a new confirmation email to the user if their email is not yet confirmed.
    Rate limited to prevent abuse.

    Args:
        email_data: Dictionary containing user email

    Returns:
        Success message

    Raises:
        HTTPException: 400 for invalid email, 429 for rate limiting
    """
    supabase = get_supabase_client()
    email = email_data.get("email")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required"
        )

    try:
        supabase.auth.resend({"type": "signup", "email": email})

        logger.info(f"Confirmation email resent to: {email}")

        return {"message": "Confirmation email sent successfully"}

    except AuthApiError as auth_error:
        logger.error(f"Failed to resend confirmation email: {auth_error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send confirmation email",
        )

    except Exception as error:
        logger.error(f"Unexpected error during email resend: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send confirmation email due to internal error",
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest,
) -> PasswordResetResponse:
    """
    Request password reset

    Sends password reset email to the user if the email exists in the system.
    Always returns success to prevent email enumeration attacks.

    Args:
        reset_data: Password reset request with email

    Returns:
        PasswordResetResponse with success message
    """
    supabase = get_supabase_client()

    try:
        supabase.auth.reset_password_email(reset_data.email)

        logger.info(f"Password reset email sent to: {reset_data.email}")

        return PasswordResetResponse(
            message="If an account with this email exists, a password reset link has been sent",
            email=reset_data.email,
        )

    except Exception as error:
        # Always return success to prevent email enumeration
        logger.warning(f"Password reset request for {reset_data.email}: {error}")

        return PasswordResetResponse(
            message="If an account with this email exists, a password reset link has been sent",
            email=reset_data.email,
        )


@router.get("/profile")
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user's profile

    Returns the authenticated user's profile information from the users table.
    Requires valid JWT token.

    Args:
        current_user: Current authenticated user from JWT

    Returns:
        User profile data

    Raises:
        HTTPException: 404 if profile not found
    """
    supabase = get_supabase_client()

    try:
        # Get user profile from users table
        profile_response = (
            supabase.table("users")
            .select("*")
            .eq("auth_id", current_user["user_id"])
            .execute()
        )

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        profile = profile_response.data[0]

        return {
            "id": profile["id"],
            "auth_id": profile["auth_id"],
            "email": profile["email"],
            "profile": profile["profile"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"],
        }

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Error fetching user profile: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile",
        )
