"""
Case schemas for request/response validation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CaseBase(BaseModel):
    """Base schema for Case models"""

    name: str = Field(..., min_length=1, max_length=100, description="Case name")
    partner_name: str = Field(
        ..., min_length=1, max_length=100, description="Partner name"
    )
    partner_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Partner type (colleague, client, friend, etc.)",
    )
    my_position: Optional[str] = Field(
        None, max_length=50, description="User's position/role in this conversation"
    )
    conversation_purpose: Optional[str] = Field(
        None, description="Purpose/context of the conversation"
    )
    case_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata as JSON"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Case name cannot be empty")
        return v.strip()

    @field_validator("partner_name")
    @classmethod
    def validate_partner_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Partner name cannot be empty")
        return v.strip()

    @field_validator("partner_type")
    @classmethod
    def validate_partner_type(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return None

    @field_validator("my_position")
    @classmethod
    def validate_my_position(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return None


class CaseCreate(CaseBase):
    """Schema for creating a new case"""

    pass


class CaseUpdate(BaseModel):
    """Schema for updating an existing case"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Case name"
    )
    partner_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Partner name"
    )
    partner_type: Optional[str] = Field(None, max_length=50, description="Partner type")
    my_position: Optional[str] = Field(
        None, max_length=50, description="User's position/role"
    )
    conversation_purpose: Optional[str] = Field(
        None, description="Purpose/context of the conversation"
    )
    case_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Case name cannot be empty")
        return v.strip() if v else None

    @field_validator("partner_name")
    @classmethod
    def validate_partner_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Partner name cannot be empty")
        return v.strip() if v else None


class CaseResponse(CaseBase):
    """Schema for case response"""

    id: UUID = Field(..., description="Case unique identifier")
    user_id: UUID = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")
    is_deleted: bool = Field(..., description="Whether the case is soft deleted")

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(default=1, ge=1, description="Page number (starting from 1)")
    limit: int = Field(
        default=20, ge=1, le=100, description="Number of items per page (max 100)"
    )

    @property
    def offset(self) -> int:
        """Calculate offset from page and limit"""
        return (self.page - 1) * self.limit


class CaseFilters(BaseModel):
    """Filters for case list queries"""

    partner_type: Optional[str] = Field(None, description="Filter by partner type")
    search: Optional[str] = Field(
        None, min_length=1, description="Search term for name, partner name, or purpose"
    )
    include_deleted: bool = Field(
        default=False, description="Include soft-deleted cases"
    )

    @field_validator("search")
    @classmethod
    def validate_search(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return None


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")

    @classmethod
    def create(cls, total: int, page: int, limit: int) -> "PaginationMeta":
        """Create pagination metadata"""
        total_pages = (total + limit - 1) // limit  # Ceiling division
        return cls(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_previous=page > 1,
            has_next=page < total_pages,
        )


class CaseListResponse(BaseModel):
    """Schema for paginated case list response"""

    cases: List[CaseResponse] = Field(..., description="List of cases")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


class CaseCreateResponse(BaseModel):
    """Schema for case creation response"""

    message: str = Field(..., description="Success message")
    case: CaseResponse = Field(..., description="Created case")


class CaseUpdateResponse(BaseModel):
    """Schema for case update response"""

    message: str = Field(..., description="Success message")
    case: CaseResponse = Field(..., description="Updated case")


class CaseDeleteResponse(BaseModel):
    """Schema for case deletion response"""

    message: str = Field(..., description="Success message")
    case_id: UUID = Field(..., description="Deleted case ID")
