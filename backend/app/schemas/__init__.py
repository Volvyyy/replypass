"""
Pydantic schemas for request/response validation
"""

from .auth import (
    EmailConfirmationRequest,
    EmailConfirmationResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordUpdateRequest,
    UserProfileCreate,
    UserProfileResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserResponse,
)
from .case import (
    CaseBase,
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseListResponse,
    CaseCreateResponse,
    CaseUpdateResponse,
    CaseDeleteResponse,
    PaginationParams,
    CaseFilters,
    PaginationMeta,
)

__all__ = [
    # Auth schemas
    "UserProfileCreate",
    "UserRegistrationRequest",
    "EmailConfirmationRequest",
    "UserResponse",
    "UserRegistrationResponse",
    "EmailConfirmationResponse",
    "PasswordResetRequest",
    "PasswordResetResponse",
    "PasswordUpdateRequest",
    "UserProfileResponse",
    # Case schemas
    "CaseBase",
    "CaseCreate",
    "CaseUpdate",
    "CaseResponse",
    "CaseListResponse",
    "CaseCreateResponse",
    "CaseUpdateResponse",
    "CaseDeleteResponse",
    "PaginationParams",
    "CaseFilters",
    "PaginationMeta",
]
