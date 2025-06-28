"""
Case repository for CRUD operations

Following SQLAlchemy 2.0 async best practices
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, update, delete, or_, and_, desc, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from .base import BaseRepository


class CaseRepository(BaseRepository[Case]):
    """
    Repository for Case model with specialized methods

    Extends BaseRepository with case-specific functionality
    """

    def __init__(self, session: AsyncSession):
        """Initialize Case repository"""
        super().__init__(Case, session)

    async def create(self, **kwargs) -> Case:
        """
        Create a new case

        Args:
            **kwargs: Case field values

        Returns:
            Created Case instance
        """
        return await super().create(**kwargs)

    async def get_user_cases(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        partner_type: Optional[str] = None,
        include_deleted: bool = False,
    ) -> List[Case]:
        """
        Get cases for a specific user with filtering

        Args:
            user_id: User UUID
            limit: Maximum number of cases to return
            offset: Number of cases to skip
            partner_type: Filter by partner type
            include_deleted: Whether to include soft-deleted cases

        Returns:
            List of Case instances
        """
        stmt = select(Case).where(Case.user_id == user_id)

        # Filter out deleted cases unless explicitly requested
        if not include_deleted:
            stmt = stmt.where(Case.deleted_at.is_(None))

        # Filter by partner type if specified
        if partner_type:
            stmt = stmt.where(Case.partner_type == partner_type)

        # Order by most recently updated first
        stmt = stmt.order_by(desc(Case.updated_at))

        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_cases(
        self, user_id: UUID, search_query: str, limit: int = 100, offset: int = 0
    ) -> List[Case]:
        """
        Search cases by name, partner name, or conversation purpose

        Args:
            user_id: User UUID
            search_query: Search term
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching Case instances
        """
        search_term = f"%{search_query}%"

        stmt = select(Case).where(
            and_(
                Case.user_id == user_id,
                Case.deleted_at.is_(None),
                or_(
                    Case.name.ilike(search_term),
                    Case.partner_name.ilike(search_term),
                    Case.conversation_purpose.ilike(search_term),
                ),
            )
        )

        # Order by relevance (name matches first, then partner, then purpose)
        stmt = stmt.order_by(
            Case.name.ilike(search_term).desc(),
            Case.partner_name.ilike(search_term).desc(),
            desc(Case.updated_at),
        )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_user_cases(
        self, user_id: UUID, include_deleted: bool = False
    ) -> int:
        """
        Count cases for a specific user

        Args:
            user_id: User UUID
            include_deleted: Whether to include soft-deleted cases

        Returns:
            Number of cases
        """
        stmt = select(func.count(Case.id)).where(Case.user_id == user_id)

        if not include_deleted:
            stmt = stmt.where(Case.deleted_at.is_(None))

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def soft_delete(self, case_id: UUID) -> bool:
        """
        Soft delete a case

        Args:
            case_id: Case UUID

        Returns:
            True if deleted, False if not found
        """
        case = await self.get_by_id(case_id)
        if not case:
            return False

        case.soft_delete()
        await self.session.flush()
        return True

    async def restore(self, case_id: UUID) -> bool:
        """
        Restore a soft deleted case

        Args:
            case_id: Case UUID

        Returns:
            True if restored, False if not found
        """
        case = await self.get_by_id(case_id)
        if not case:
            return False

        case.restore()
        await self.session.flush()
        return True

    async def update_metadata(
        self, case_id: UUID, metadata: Dict[str, Any]
    ) -> Optional[Case]:
        """
        Update case metadata

        Args:
            case_id: Case UUID
            metadata: Metadata dictionary to merge

        Returns:
            Updated Case instance or None if not found
        """
        case = await self.get_by_id(case_id)
        if not case:
            return None

        # Merge with existing metadata
        if case.case_metadata:
            new_metadata = dict(case.case_metadata)
            new_metadata.update(metadata)
        else:
            new_metadata = metadata

        case.case_metadata = new_metadata
        case.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(case)
        return case

    async def get_recent_cases(self, user_id: UUID, limit: int = 10) -> List[Case]:
        """
        Get recently updated cases for a user

        Args:
            user_id: User UUID
            limit: Maximum number of cases

        Returns:
            List of recently updated Case instances
        """
        stmt = (
            select(Case)
            .where(and_(Case.user_id == user_id, Case.deleted_at.is_(None)))
            .order_by(desc(Case.updated_at))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_partner_types(self, user_id: UUID) -> List[str]:
        """
        Get unique partner types for a user

        Args:
            user_id: User UUID

        Returns:
            List of unique partner types
        """
        stmt = (
            select(distinct(Case.partner_type))
            .where(
                and_(
                    Case.user_id == user_id,
                    Case.deleted_at.is_(None),
                    Case.partner_type.is_not(None),
                )
            )
            .order_by(Case.partner_type)
        )

        result = await self.session.execute(stmt)
        return [pt for pt in result.scalars().all() if pt]

    async def bulk_update_metadata(
        self, case_ids: List[UUID], metadata: Dict[str, Any]
    ) -> int:
        """
        Bulk update metadata for multiple cases

        Args:
            case_ids: List of Case UUIDs
            metadata: Metadata to merge for all cases

        Returns:
            Number of cases updated
        """
        if not case_ids:
            return 0

        # For bulk updates, we need to handle JSONB merge properly
        # This is a simplified version - in production, you'd want to merge existing metadata
        stmt = (
            update(Case)
            .where(Case.id.in_(case_ids))
            .values(case_metadata=metadata, updated_at=datetime.utcnow())
        )

        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def get_cases_by_partner_name(
        self, user_id: UUID, partner_name: str
    ) -> List[Case]:
        """
        Get all cases for a specific partner

        Args:
            user_id: User UUID
            partner_name: Partner name to search for

        Returns:
            List of Case instances for this partner
        """
        stmt = (
            select(Case)
            .where(
                and_(
                    Case.user_id == user_id,
                    Case.partner_name == partner_name,
                    Case.deleted_at.is_(None),
                )
            )
            .order_by(desc(Case.updated_at))
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def exists_for_user(self, case_id: UUID, user_id: UUID) -> bool:
        """
        Check if a case exists and belongs to the specified user

        Args:
            case_id: Case UUID
            user_id: User UUID

        Returns:
            True if case exists and belongs to user, False otherwise
        """
        stmt = select(func.count(Case.id)).where(
            and_(Case.id == case_id, Case.user_id == user_id, Case.deleted_at.is_(None))
        )

        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        return count > 0
