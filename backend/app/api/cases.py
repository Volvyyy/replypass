"""
Case API endpoints
Handles case CRUD operations with pagination and filtering
"""

import logging
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_async_session
from app.repositories.case import CaseRepository
from app.schemas.case import (
    CaseFilters,
    CaseListResponse,
    CaseResponse,
    PaginationMeta,
    PaginationParams,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cases", tags=["Cases"])


async def get_case_repository(
    db_session: AsyncSession = Depends(get_async_session),
) -> CaseRepository:
    """Get case repository instance"""
    return CaseRepository(db_session)


@router.get(
    "",
    response_model=CaseListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's cases with pagination and filtering",
    description="""
    Retrieve a paginated list of cases for the authenticated user.
    
    Features:
    - Pagination with configurable page size (max 100 per page)
    - Search by case name, partner name, or conversation purpose
    - Filter by partner type
    - Soft-deleted cases excluded by default
    - Ordered by most recently updated first
    """,
)
async def get_cases(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    limit: int = Query(
        20, ge=1, le=100, description="Number of items per page (max 100)"
    ),
    # Filter parameters
    partner_type: str = Query(None, description="Filter by partner type"),
    search: str = Query(
        None, min_length=1, description="Search term for name, partner name, or purpose"
    ),
    include_deleted: bool = Query(False, description="Include soft-deleted cases"),
    # Dependencies
    current_user: Dict[str, Any] = Depends(get_current_user),
    case_repo: CaseRepository = Depends(get_case_repository),
) -> CaseListResponse:
    """
    Get paginated list of cases for the authenticated user

    Args:
        page: Page number (starting from 1)
        limit: Number of items per page (max 100)
        partner_type: Filter by partner type
        search: Search term for name, partner name, or purpose
        include_deleted: Include soft-deleted cases
        current_user: Current authenticated user from JWT
        case_repo: Case repository instance

    Returns:
        CaseListResponse with paginated cases and metadata

    Raises:
        HTTPException: 401 if user not authenticated, 500 for system errors
    """
    try:
        user_id = UUID(current_user["user_id"])

        # Create pagination parameters
        pagination = PaginationParams(page=page, limit=limit)

        # Get cases based on search/filter parameters
        if search:
            # Use search functionality
            cases = await case_repo.search_cases(
                user_id=user_id,
                search_query=search,
                limit=pagination.limit,
                offset=pagination.offset,
            )

            # Count total search results
            # Note: In production, you might want to optimize this with a separate count query
            all_search_results = await case_repo.search_cases(
                user_id=user_id,
                search_query=search,
                limit=10000,  # Large limit to get all results for counting
                offset=0,
            )
            total_count = len(all_search_results)

        else:
            # Use regular get_user_cases with filters
            cases = await case_repo.get_user_cases(
                user_id=user_id,
                limit=pagination.limit,
                offset=pagination.offset,
                partner_type=partner_type,
                include_deleted=include_deleted,
            )

            # Get total count
            total_count = await case_repo.count_user_cases(
                user_id=user_id,
                include_deleted=include_deleted,
            )

            # Apply partner_type filter to count if specified
            if partner_type and not search:
                # For partner_type filtering, we need a custom count
                # This is a simplified implementation - in production, optimize this
                all_cases = await case_repo.get_user_cases(
                    user_id=user_id,
                    limit=10000,  # Large limit to get all cases for counting
                    offset=0,
                    partner_type=partner_type,
                    include_deleted=include_deleted,
                )
                total_count = len(all_cases)

        # Convert model instances to response schemas
        case_responses = [CaseResponse.model_validate(case) for case in cases]

        # Create pagination metadata
        pagination_meta = PaginationMeta.create(
            total=total_count,
            page=page,
            limit=limit,
        )

        logger.info(
            f"Retrieved {len(cases)} cases for user {user_id} "
            f"(page {page}, limit {limit}, total {total_count})"
        )

        return CaseListResponse(
            cases=case_responses,
            pagination=pagination_meta,
        )

    except ValueError as e:
        logger.error(f"Invalid user ID format: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    except Exception as error:
        logger.error(
            f"Error retrieving cases for user {current_user.get('user_id')}: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cases",
        )
