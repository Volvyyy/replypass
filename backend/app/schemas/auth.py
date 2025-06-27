"""
Authentication schemas for request/response validation
"""

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserProfileCreate(BaseModel):
    """User profile data for registration"""

    display_name: str = Field(
        ..., min_length=1, max_length=100, description="User display name"
    )
    timezone: Optional[str] = Field(default="UTC", description="User timezone")
    language: Optional[str] = Field(default="ja", description="User preferred language")

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Display name cannot be empty")
        return v.strip()

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        if v is None:
            return "UTC"
        # Basic timezone validation - in production, use pytz
        valid_timezones = [
            "UTC",
            "Asia/Tokyo",
            "America/New_York",
            "Europe/London",
            "America/Los_Angeles",
            "Asia/Shanghai",
            "Europe/Paris",
        ]
        if v not in valid_timezones:
            return "UTC"  # Default to UTC for invalid timezones
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if v is None:
            return "ja"
        valid_languages = ["ja", "en", "ko", "zh"]
        if v not in valid_languages:
            return "ja"  # Default to Japanese
        return v


class UserRegistrationRequest(BaseModel):
    """User registration request schema"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )
    confirm_password: str = Field(..., description="Password confirmation")
    profile: UserProfileCreate = Field(..., description="User profile information")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")

        # Check for uppercase letter
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for lowercase letter
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for digit
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")

        return v

    @model_validator(mode="after")
    def passwords_match(self):
        """Validate that passwords match"""
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class EmailConfirmationRequest(BaseModel):
    """Email confirmation request schema"""

    email: EmailStr = Field(..., description="User email address")
    token: str = Field(
        ..., min_length=6, max_length=6, description="6-digit confirmation token"
    )

    @field_validator("token")
    @classmethod
    def validate_token_format(cls, v):
        """Validate token is 6 digits"""
        if not re.match(r"^\d{6}$", v):
            raise ValueError("Token must be exactly 6 digits")
        return v


class UserResponse(BaseModel):
    """User response schema"""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    email_confirmed_at: Optional[str] = Field(
        None, description="Email confirmation timestamp"
    )
    created_at: str = Field(..., description="Account creation timestamp")


class UserRegistrationResponse(BaseModel):
    """User registration response schema"""

    message: str = Field(..., description="Success message")
    user: UserResponse = Field(..., description="Created user information")
    confirmation_required: bool = Field(
        ..., description="Whether email confirmation is required"
    )


class EmailConfirmationResponse(BaseModel):
    """Email confirmation response schema"""

    message: str = Field(..., description="Success message")
    user: UserResponse = Field(..., description="Confirmed user information")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetResponse(BaseModel):
    """Password reset response schema"""

    message: str = Field(..., description="Success message")
    email: str = Field(..., description="Email where reset link was sent")


class PasswordUpdateRequest(BaseModel):
    """Password update request schema"""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )
    confirm_new_password: str = Field(..., description="New password confirmation")

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v):
        """Validate new password meets security requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")

        # Check for uppercase letter
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for lowercase letter
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for digit
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")

        return v

    @model_validator(mode="after")
    def new_passwords_match(self):
        """Validate that new passwords match"""
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match")
        return self


class UserProfileResponse(BaseModel):
    """User profile response schema"""

    id: str = Field(..., description="Profile ID")
    auth_id: str = Field(..., description="Auth user ID")
    email: str = Field(..., description="User email")
    profile: dict = Field(..., description="Profile data")
    created_at: str = Field(..., description="Profile creation timestamp")
    updated_at: str = Field(..., description="Profile last update timestamp")
