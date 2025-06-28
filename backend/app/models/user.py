"""
User model for Reply Pass
"""

from typing import Optional, Dict, Any

from sqlalchemy import String, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class User(BaseModel):
    """
    User model representing users in the system

    Links to Supabase Auth for authentication
    """

    __tablename__ = "users"

    # Email address (unique)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Supabase Auth ID (unique)
    auth_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Profile information as JSON (JSONB for PostgreSQL, JSON for others)
    profile: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=lambda: {}, server_default="{}"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_auth_id", "auth_id"),
        Index("idx_users_created_at", "created_at"),
    )

    def __init__(self, **kwargs):
        """Initialize User with default profile if not provided"""
        if "profile" not in kwargs or kwargs["profile"] is None:
            kwargs["profile"] = {}
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """String representation of the User"""
        return f"<User(id={self.id}, email={self.email})>"

    def get_display_name(self) -> str:
        """Get display name from profile or fallback to email"""
        if self.profile and "display_name" in self.profile:
            return self.profile["display_name"]
        return self.email.split("@")[0]

    def get_avatar_url(self) -> Optional[str]:
        """Get avatar URL from profile"""
        if self.profile and "avatar_url" in self.profile:
            return self.profile["avatar_url"]
        return None

    def get_timezone(self) -> str:
        """Get timezone from profile or default to UTC"""
        if self.profile and "timezone" in self.profile:
            return self.profile["timezone"]
        return "UTC"

    def get_locale(self) -> str:
        """Get locale from profile or default to en"""
        if self.profile and "locale" in self.profile:
            return self.profile["locale"]
        return "en"
