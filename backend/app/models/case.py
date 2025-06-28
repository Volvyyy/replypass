"""
Case model for Reply Pass
"""

from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy import String, Text, Index, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Case(BaseModel):
    """
    Case model representing conversation cases/contexts

    Each case represents a specific conversation context with a partner
    """

    __tablename__ = "cases"

    # Foreign key to users table
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Case name
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Partner information
    partner_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    partner_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )

    # User's position/role in this conversation
    my_position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Purpose/context of the conversation
    conversation_purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Additional metadata as JSON (using case_metadata to avoid SQLAlchemy reserved word)
    case_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=lambda: {}, server_default="{}"
    )

    # Soft delete timestamp
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_cases_user_id", "user_id"),
        Index("idx_cases_name", "name"),
        Index("idx_cases_partner_name", "partner_name"),
        Index("idx_cases_partner_type", "partner_type"),
        Index("idx_cases_created_at", "created_at"),
        Index("idx_cases_updated_at", "updated_at"),
        Index("idx_cases_deleted_at", "deleted_at"),
        Index("idx_cases_user_id_deleted_at", "user_id", "deleted_at"),
        Index("idx_cases_user_id_created_at", "user_id", "created_at"),
        Index("idx_cases_name_text_search", "name"),  # For text search
        Index("idx_cases_partner_name_text_search", "partner_name"),  # For text search
        Index(
            "idx_cases_case_metadata", "case_metadata", postgresql_using="gin"
        ),  # For JSONB search
    )

    def __init__(self, **kwargs):
        """Initialize Case with default metadata if not provided"""
        if "case_metadata" not in kwargs or kwargs["case_metadata"] is None:
            kwargs["case_metadata"] = {}
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """String representation of the Case"""
        return f"<Case(id={self.id}, name={self.name})>"

    @property
    def is_deleted(self) -> bool:
        """Check if the case is soft deleted"""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Soft delete the case"""
        if self.deleted_at is None:
            self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft deleted case"""
        self.deleted_at = None

    def get_display_info(self) -> Dict[str, Any]:
        """Get display information for the case"""
        return {
            "id": str(self.id),
            "name": self.name,
            "partner": self.partner_name,
            "type": self.partner_type,
            "position": self.my_position,
            "purpose": self.conversation_purpose,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_deleted": self.is_deleted,
        }

    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata value"""
        if self.case_metadata is None:
            self.case_metadata = {}
        # Create a new dict to trigger SQLAlchemy change detection
        new_metadata = dict(self.case_metadata)
        new_metadata[key] = value
        self.case_metadata = new_metadata

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value"""
        if self.case_metadata is None:
            return default
        return self.case_metadata.get(key, default)
